"""Independent raw-CSV reconciliation of the provisional v1 export model.

These expected calculations intentionally do not call the scoring/aggregation
helpers. Change them only after reviewing an intentional model revision.
"""
import csv
import io
import json
import unittest
from collections import Counter
from pathlib import Path

from src.opportunity_data import load_opportunities
from src.opportunity_metrics import build_businesses, filter_businesses
from src.opportunity_reports import ranking_table, shortlist, csv_bytes, decision_brief
from src.schema import SURVEY_LABELS

ROOT=Path(__file__).resolve().parents[1]


def raw(name):
    with (ROOT/'data/synthetic'/name).open(encoding='utf-8-sig',newline='') as file:
        return list(csv.DictReader(file))


def independent_records():
    latest={}
    for s in sorted(raw('survey_responses.csv'),key=lambda s:(s['submitted_at'][:10],s['response_id'])):
        latest[s['prospect_id']]=s
    respondents=[json.loads(s['pain_points']) for s in latest.values() if s['pain_points'] and json.loads(s['pain_points'])]
    counts=Counter(c for selections in respondents for c in set(selections))
    discovery=raw('discovery_assessments.csv')
    result={}
    for pid,s in latest.items():
        pain=json.loads(s['pain_points']) if s['pain_points'] else []
        primary=s['primary_pain_point']
        value=None
        hours={'under_2':0,'2_5':25,'6_10':50,'11_20':75,'over_20':100}
        if s['impact_rating'] and s['weekly_hours_band'] in hours and primary in pain:
            value=.45*(int(s['impact_rating'])-1)*25 + .35*hours[s['weekly_hours_band']]
            value+=.10*(100*counts[primary]/len(respondents)) + min(len(set(pain)-{primary}),2)*5
        assessments=[d for d in discovery if d['prospect_id']==pid]
        workflows={}
        for d in sorted(assessments,key=lambda d:(d['assessment_date'],d['assessment_id'])):
            workflows[d['workflow_id']]=d
        d=max(workflows.values(),key=lambda d:({'high':3,'medium':2,'low':1}.get(d['business_impact_assessment'],0),
                    d['assessment_date'],d['assessment_id'])) if workflows else None
        maps=[('budget_status',.35,{'approved':100,'indicative':65,'conditional_value_case':40,'none':0}),
              ('pilot_interest',.25,{'yes':100,'maybe':50,'no':0}),
              ('implementation_timeline',.20,{'within_1_month':100,'within_1_to_3_months':75,'within_3_to_6_months':50,'longer_term':25,'no_defined_timeline':0}),
              ('commercial_potential',.20,{'high':100,'medium':50,'low':0})]
        commercial=None
        if (d and d['evidence_status'] in ('consultant_assessed','validated') and d['assessment_evidence']
            and d['assessment_date'] and d['workflow_name']
            and d['decision_authority'] in ('interviewee','owner_director','department_manager','multiple_stakeholders')
            and all(d[field] in points for field,weight,points in maps)):
            commercial=sum(weight*points[d[field]] for field,weight,points in maps)
        overall=.60*value+.40*commercial if value is not None and commercial is not None else None
        completed=sum(bool(a['workflow_name'] and a['assessment_date'] and a['assessment_evidence']
            and a['evidence_status'] in ('self_reported','consultant_assessed','validated')) for a in assessments)
        result[pid]=dict(survey=s,value=value,commercial=commercial,overall=overall,primary=d,
            stage='Discovery Enriched' if assessments else 'Survey Only',count=len(assessments),completed=completed,
            band='Not assessed' if overall is None else next(name for floor,name in [(80,'High'),(60,'Promising'),(40,'Moderate'),(0,'Low')] if overall>=floor))
    return result


class ExportAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.expected=independent_records()
        cls.data=load_opportunities()
        cls.businesses=build_businesses(cls.data)

    def test_all_ranking_rows_scores_source_answers_and_missing_values(self):
        rows=list(csv.DictReader(io.StringIO(csv_bytes(ranking_table(self.businesses)).decode('utf-8-sig'))))
        self.assertEqual(len(rows),len(self.expected))
        self.assertEqual(len({r['Business / Prospect ID'] for r in rows}),len(rows))
        for row in rows:
            e=self.expected[row['Business / Prospect ID']]
            for field,key in [('Opportunity value score','value'),('Commercial potential score','commercial'),('Overall prospect score','overall')]:
                if e[key] is None:
                    self.assertEqual(row[field],'Not assessed')
                else:
                    self.assertAlmostEqual(float(row[field]),e[key],delta=.05000001)
            self.assertEqual(row['Score band'],e['band'])
            self.assertEqual(row['Assessment stage'],e['stage'])
            self.assertEqual(int(row['Discovery records']),e['count'])
            self.assertEqual(int(row['Completed assessments']),e['completed'])
            for field,source in [('Industry','industry'),('Business size','employee_band'),('Primary business problem','primary_pain_point'),('Weekly workload band','weekly_hours_band'),('AI adoption','ai_adoption'),('Follow-up interest','followup_interest')]:
                self.assertEqual(row[field],SURVEY_LABELS[source].get(e['survey'][source],'Not answered'))
            if e['overall'] is None:
                self.assertEqual(row['Rank within stage'],'Not assessed')

    def test_every_sort_and_filtered_cohort_preserves_business_order(self):
        for selections in ({},{'industry':['professional_services']},{'stage':['Survey Only']},{'score_band':['Promising']},{'industry':['does_not_exist']}):
            frame=filter_businesses(self.businesses,selections)
            ids=[pid for pid,e in self.expected.items() if all(
                (e['stage'] if f=='stage' else e['band'] if f=='score_band' else e['survey'][f]) in choices
                for f,choices in selections.items())]
            for sort in ('overall_score','value_score','commercial_score','impact_rating','implementation_complexity'):
                def key(pid):
                    e=self.expected[pid]
                    value=e[{'overall_score':'overall','value_score':'value','commercial_score':'commercial'}[sort]] if sort.endswith('_score') else (
                        e['survey']['impact_rating'] if sort=='impact_rating' else (e['primary'] or {}).get(sort))
                    value=float(value) if value not in ('',None) else None
                    return e['stage'],value is None,-value if value is not None else 0,pid
                self.assertEqual(ranking_table(frame,sort)['Business / Prospect ID'].tolist(),sorted(ids,key=key))

    def test_shortlist_membership_matches_interest_and_selected_workflow_actions(self):
        expected={pid for pid,e in self.expected.items() if e['survey']['followup_interest'] in ('yes','maybe')
                  and (e['primary'] or {}).get('recommended_next_action') not in ('defer','no_suitable_opportunity')}
        result=shortlist(self.businesses)
        self.assertEqual(set(result['Business / Prospect ID']),expected)
        self.assertTrue(result['Shortlist type'].str.startswith('Analytical only').all())
        self.assertTrue(result['Contact permission'].eq('Not assessed').all())
        self.assertFalse({'email','contact_name','business_name'} & set(result.columns))

    def test_brief_counts_coverage_means_and_recurring_denominators(self):
        for selections in ({},{'industry':['professional_services']},{'stage':['Survey Only']},{'industry':['does_not_exist']}):
            frame=filter_businesses(self.businesses,selections)
            evidence=[self.expected[pid] for pid in frame.prospect_id]
            brief=decision_brief(frame,self.data,selections)
            answered=[e for e in evidence if e['survey']['impact_rating']]
            high=sum(int(e['survey']['impact_rating'])>=4 for e in answered)
            self.assertIn(f'Businesses analysed: {len(evidence)}',brief)
            self.assertIn(f'High-impact businesses: {high}/{len(answered)}',brief)
            self.assertIn(f'Discovery coverage: {sum(e["completed"]>0 for e in evidence)}/{len(evidence)}',brief)
            for stage in ('Survey Only','Discovery Enriched'):
                group=[e for e in evidence if e['stage']==stage]
                scores=[e['overall'] for e in group if e['overall'] is not None]
                mean=f'{sum(scores)/len(scores):.1f}/100' if scores else 'Not assessed'
                self.assertIn(f'{stage}: {len(scores)}/{len(group)} score-eligible; average {mean}',brief)
            pains=[json.loads(e['survey']['pain_points']) for e in evidence if e['survey']['pain_points'] and json.loads(e['survey']['pain_points'])]
            counts=Counter(c for p in pains for c in set(p))
            # Check each actual problem sentence (top-five tie ordering is stable).
            for line in brief.splitlines():
                if '. Hypothesis:' in line:
                    code=next(c for c,label in SURVEY_LABELS['pain_points'].items() if line.startswith('- '+label+':'))
                    primary=sum(e['survey']['primary_pain_point']==code for e in evidence)
                    self.assertIn(f'{counts[code]}/{len(pains)} businesses ({100*counts[code]/len(pains):.1f}%); primary challenge for {primary}.',line)
