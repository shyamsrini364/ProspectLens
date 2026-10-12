"""Deterministic, hand-counted scoring, relationship, filtering and export tests."""

import copy
import csv
from datetime import datetime, timezone
import io
import json
from pathlib import Path
import tempfile
import unittest

import pandas as pd

from src.data_validation import validate_dataset
from src.market_data import SurveyLoadError
from src.market_style import theme_tokens
from src.schema import SURVEY_COLUMNS, DISCOVERY_COLUMNS, CONTACT_COLUMNS
from src.opportunity_data import _bundle, load_opportunities, load_uploaded_opportunities
from src.opportunity_scoring import value_score, commercial_score, composite_score, score_band, primary_assessment
from src.opportunity_metrics import build_businesses, filter_businesses, opportunity_kpis, recurring_problems, discovery_trend
from src.opportunity_reports import ranking_table, csv_bytes, shortlist, decision_brief
from src.opportunity_charts import opportunity_matrix


def survey(response='R1',prospect='P1',**changes):
    row=dict.fromkeys(SURVEY_COLUMNS,'')
    row.update(response_id=response,prospect_id=prospect,dataset_version='1.0',submitted_at='2026-09-01',
        industry='retail_ecommerce',employee_band='2_5',pain_points='["manual_data_entry","sales_followup","reporting_analysis"]',
        primary_pain_point='manual_data_entry',weekly_hours_band='over_20',impact_rating='5',
        ai_adoption='limited_tasks',followup_interest='yes')
    row.update(changes)
    return row


def discovery(assessment='D1',prospect='P1',workflow='W1',**changes):
    row=dict.fromkeys(DISCOVERY_COLUMNS,'')
    row.update(assessment_id=assessment,prospect_id=prospect,workflow_id=workflow,dataset_version='1.0',
        assessment_date='2026-09-08',workflow_name='Invoice review',business_impact_assessment='high',
        commercial_potential='high',budget_status='approved',pilot_interest='yes',implementation_timeline='within_1_month',
        decision_authority='owner_director',evidence_status='consultant_assessed',assessment_evidence='Fixture rationale',
        technical_feasibility='medium',implementation_complexity='4')
    row.update(changes)
    return row


def contact(response='R1',prospect='P1',**changes):
    row=dict.fromkeys(CONTACT_COLUMNS,'')
    row.update(response_id=response,prospect_id=prospect,contact_name='PRIVATE_NAME',business_name='PRIVATE_BUSINESS',
        email='private@example.invalid',followup_consent='true',privacy_acknowledged='true',
        privacy_notice_version='v1',consent_recorded_at='2026-09-01')
    row.update(changes)
    return row


def bundle(s=None,d=None,c=None):
    return _bundle(validate_dataset(s if s is not None else [survey()],d,c),'Fixture',contacts_supplied=c is not None)


def payload(rows,columns):
    out=io.StringIO()
    writer=csv.DictWriter(out,fieldnames=columns);writer.writeheader();writer.writerows(rows)
    return out.getvalue().encode()


class OpportunityScoreTests(unittest.TestCase):
    def test_hand_calculated_value_commercial_and_composite(self):
        data=bundle(d=[discovery()]);frame=build_businesses(data);r=frame.iloc[0]
        self.assertEqual(r.value_score,100) # 45+35+10+10.
        self.assertEqual(r.commercial_score,100)
        self.assertEqual(r.overall_score,100)
        self.assertEqual(r.score_band,'High')
        self.assertEqual(composite_score(50,75),60)

    def test_value_is_independent_of_commercial_and_interest(self):
        original=build_businesses(bundle(d=[discovery()])).iloc[0]
        changed=build_businesses(bundle([survey(followup_interest='not_now')],[discovery(budget_status='none')])).iloc[0]
        self.assertEqual(original.value_score,changed.value_score)
        self.assertEqual(changed.commercial_score,65)

    def test_commercial_is_independent_of_survey_value(self):
        r=build_businesses(bundle([survey(impact_rating='1',weekly_hours_band='under_2')],[discovery()])).iloc[0]
        self.assertEqual(r.commercial_score,100)
        self.assertEqual(r.value_score,20)
        self.assertEqual(r.overall_score,52)

    def test_additional_problems_contribution_capped(self):
        s=validate_dataset([survey()]).survey[0]
        s['pain_points'] += ['finance_invoicing','customer_support']
        _,parts,_=value_score(s,{'manual_data_entry':100})
        self.assertEqual(next(p['contribution'] for p in parts if p['component']=='additional'),10)

    def test_survey_only_has_no_invented_commercial_or_composite(self):
        r=build_businesses(bundle()).iloc[0]
        self.assertIsNone(r.commercial_score)
        self.assertIsNone(r.overall_score)
        self.assertEqual(r.stage,'Survey Only')
        self.assertIsNone(r.implementation_complexity)

    def test_unknown_and_missing_do_not_turn_into_zero(self):
        for field,value in [('weekly_hours_band','unsure'),('impact_rating',''),('pain_points',''),('primary_pain_point','')]:
            with self.subTest(field=field):
                r=build_businesses(bundle([survey(**{field:value})],[discovery()])).iloc[0]
                self.assertIsNone(r.value_score)
                self.assertIsNone(r.overall_score)
        for field,value in [('budget_status','not_discussed'),('pilot_interest','not_discussed'),
                            ('commercial_potential','unknown'),('decision_authority','unknown'),
                            ('evidence_status','self_reported'),('assessment_evidence','')]:
            with self.subTest(field=field):
                r=build_businesses(bundle(d=[discovery(**{field:value})])).iloc[0]
                self.assertIsNone(r.commercial_score)

    def test_real_negative_answers_are_zero_components(self):
        r=build_businesses(bundle(d=[discovery(budget_status='none',pilot_interest='no',
            implementation_timeline='no_defined_timeline',commercial_potential='low')])).iloc[0]
        self.assertEqual(r.commercial_score,0)
        self.assertEqual(r.overall_score,60)

    def test_score_band_boundaries_use_unrounded_scores(self):
        for value,band in [(0,'Low'),(39.99,'Low'),(40,'Moderate'),(60,'Promising'),(79.99,'Promising'),(80,'High'),(100,'High')]:
            self.assertEqual(score_band(value),band)
        self.assertEqual(score_band(None),'Not assessed')
        with self.assertRaises(ValueError): score_band(101)

    def test_configurable_composite_and_missing_inputs(self):
        from src.opportunity_config import CONFIG
        config=copy.deepcopy(CONFIG);config['overall_weights']={'value_score':.5,'commercial_score':.5}
        self.assertEqual(composite_score(20,80,config),50)
        self.assertIsNone(composite_score(None,80))
        self.assertIsNone(composite_score(20,float('nan')))


class OpportunityMetricsTests(unittest.TestCase):
    def test_one_row_per_business_with_latest_whole_submission(self):
        data=bundle([survey(),survey('R2','P1',submitted_at='2026-09-15',impact_rating='')],[discovery(),discovery('D2',workflow='W2')])
        b=build_businesses(data)
        self.assertEqual(len(b),1)
        self.assertEqual(b.iloc[0].response_id,'R2')
        self.assertIsNone(b.iloc[0].value_score)
        self.assertEqual(b.iloc[0].discovery_count,2)
        self.assertEqual(len(data.survey),2)
        self.assertEqual(len(data.discovery),2)

    def test_primary_workflow_uses_latest_per_workflow_then_impact(self):
        rows=[discovery(),discovery('D2',assessment_date='2026-09-20',business_impact_assessment='low'),
              discovery('D3',workflow='W2',business_impact_assessment='medium',commercial_potential='low')]
        data=bundle(d=rows)
        self.assertEqual(primary_assessment(data.validation.discovery)['assessment_id'],'D3')
        self.assertEqual(build_businesses(data).iloc[0].primary_assessment_id,'D3')

    def test_latest_incomplete_assessment_does_not_reuse_old_qualification(self):
        b=build_businesses(bundle(d=[discovery(),discovery('D2',assessment_date='2026-09-30',budget_status='')]))
        self.assertIsNone(b.iloc[0].commercial_score)
        self.assertEqual(b.iloc[0].primary_assessment_id,'D2')

    def test_completion_proxy_and_stage_are_distinct(self):
        b=build_businesses(bundle(d=[discovery(assessment_evidence='')]))
        self.assertEqual(b.iloc[0].stage,'Discovery Enriched')
        self.assertEqual(opportunity_kpis(b)['assessed'],0)

    def test_filter_search_stage_band_and_stable_scores(self):
        b=build_businesses(bundle([survey(),survey('R2','P2',industry='hospitality')],[discovery()]))
        selected=filter_businesses(b,{'industry':['retail_ecommerce'],'stage':['Discovery Enriched'],'score_band':['High']},'p1')
        self.assertEqual(selected.prospect_id.tolist(),['P1'])
        self.assertEqual(selected.iloc[0].overall_score,b.iloc[0].overall_score)
        self.assertTrue(filter_businesses(b,{'stage':['Survey Only']},'P1').empty)

    def test_recurrence_deduplicates_selections_and_businesses(self):
        data=bundle([survey(pain_points='["manual_data_entry","manual_data_entry"]'),
            survey('R2','P1',submitted_at='2026-09-02',pain_points='["manual_data_entry"]'),
            survey('R3','P2',pain_points='["manual_data_entry","sales_followup"]')])
        table=recurring_problems(build_businesses(data),data.discovery).set_index('category')
        self.assertEqual(table.loc['manual_data_entry','count'],2)
        self.assertEqual(table.loc['manual_data_entry','denominator'],2)
        self.assertEqual(table.loc['sales_followup','percentage'],50)
        self.assertEqual(table['percentage'].sum(),150)

    def test_no_guessed_discovery_category_link(self):
        data=bundle(d=[discovery()]);table=recurring_problems(build_businesses(data),data.discovery)
        self.assertTrue(table['workflow_matched_assessments'].isna().all())
        self.assertEqual(table.iloc[0].assessments_at_reporting_businesses,1)

    def test_stage_separated_ranking_retains_unassessed(self):
        b=build_businesses(bundle([survey(),survey('R2','P2')],[discovery()]))
        table=ranking_table(b)
        self.assertEqual(len(table),2)
        self.assertTrue(pd.isna(table.loc[1,'Rank within stage']))
        self.assertEqual(table.loc[0,'Assessment stage'],'Discovery Enriched')
        self.assertEqual(opportunity_kpis(b)['means']['Discovery Enriched']['eligible'],1)
        self.assertIsNone(opportunity_kpis(b)['means']['Survey Only']['mean'])

    def test_matrix_has_one_point_per_eligible_business_not_assessment(self):
        data=bundle([survey(),survey('R2','P2')],[discovery(),discovery('D2',workflow='W2')])
        fig=opportunity_matrix(build_businesses(data),theme_tokens('dark'))
        self.assertEqual(sum(len(t.x) for t in fig.data),1)
        self.assertEqual(fig.data[0].customdata[0][0],'P1')
        self.assertEqual(fig.layout.xaxis.range,(0,100))

    def test_weekly_trend_counts_ids_and_fills_gaps(self):
        data=bundle([survey(),survey('R2','P1',submitted_at='2026-09-22',impact_rating='2'),
                     survey('R3','P2',submitted_at='')],[discovery(assessment_date='2026-09-15')])
        counts,missing=discovery_trend(data.survey,data.discovery,{'P1'},cumulative=False)
        self.assertEqual(counts['Survey responses'].tolist(),[1,0,0,1])
        self.assertEqual(counts['Discovery assessments'].tolist(),[0,0,1,0])
        cumulative,_=discovery_trend(data.survey,data.discovery,{'P1'})
        self.assertEqual(cumulative.iloc[-1]['Survey responses'],2)
        self.assertEqual(cumulative.iloc[-1]['High-impact survey responses'],1)
        _,missing=discovery_trend(data.survey,data.discovery,{'P1','P2'})
        self.assertEqual(missing['Survey responses'],1)

    def test_monthly_and_empty_trends(self):
        data=bundle([survey(),survey('R2','P2',submitted_at='2026-10-01')])
        table,_=discovery_trend(data.survey,data.discovery,{'P1','P2'},'Monthly',False)
        self.assertEqual(table['Survey responses'].tolist(),[1,1])
        empty,_=discovery_trend(data.survey,data.discovery,set())
        self.assertTrue(empty.empty)

    def test_empty_bundle_preserves_analytical_columns(self):
        data=bundle([]);frame=build_businesses(data)
        self.assertEqual(opportunity_kpis(frame)['businesses'],0)
        self.assertTrue(ranking_table(frame).empty)
        self.assertEqual(len(opportunity_matrix(frame,theme_tokens('light')).data),0)


class OpportunityPermissionAndLoaderTests(unittest.TestCase):
    def test_interest_is_not_permission(self):
        data=bundle(c=[contact(followup_consent='false')]);b=build_businesses(data)
        self.assertEqual(b.iloc[0].contact_permission,'Not contact-ready')
        self.assertTrue(shortlist(b,True).empty)

    def test_provenance_required_and_contact_data_discarded(self):
        data=bundle(c=[contact(privacy_notice_version='')]);b=build_businesses(data)
        self.assertEqual(b.iloc[0].contact_permission,'Review permission provenance')
        self.assertEqual(data.validation.contacts,[])
        self.assertNotIn('email',b.columns)
        self.assertTrue(shortlist(b,True).empty)

    def test_permission_aware_and_analytical_shortlists(self):
        data=bundle(c=[contact()]);b=build_businesses(data)
        self.assertEqual(len(shortlist(b,True)),1)
        self.assertIn('impact',shortlist(b,True).iloc[0]['Reason for investigation'])
        self.assertIn('Analytical only',shortlist(build_businesses(bundle()),False).iloc[0]['Shortlist type'])

    def test_latest_response_does_not_reuse_old_consent(self):
        data=bundle([survey(),survey('R2',submitted_at='2026-09-12')],c=[contact()])
        self.assertTrue(shortlist(build_businesses(data),True).empty)

    def test_deferred_business_excluded_from_shortlist(self):
        data=bundle(d=[discovery(recommended_next_action='defer')],c=[contact()])
        self.assertTrue(shortlist(build_businesses(data),True).empty)

    def test_valid_bundle_upload_and_orphan_rejection(self):
        s=payload([survey()],SURVEY_COLUMNS)
        data=load_uploaded_opportunities(s,payload([discovery()],DISCOVERY_COLUMNS),payload([contact()],CONTACT_COLUMNS))
        self.assertFalse(data.synthetic)
        self.assertEqual(len(data.discovery),1)
        with self.assertRaises(SurveyLoadError):
            load_uploaded_opportunities(s,payload([discovery(prospect='ORPHAN')],DISCOVERY_COLUMNS))

    def test_invalid_date_header_and_unknown_code_block_loading(self):
        for s in [survey(submitted_at='2026-02-30'),survey(industry='invented')]:
            with self.assertRaises(SurveyLoadError):
                load_uploaded_opportunities(payload([s],SURVEY_COLUMNS))
        with self.assertRaises(SurveyLoadError): load_uploaded_opportunities(b'wrong,header\n')

    def test_missing_discovery_file_is_supported_but_invalid_existing_file_blocks(self):
        with tempfile.TemporaryDirectory() as temp:
            s=Path(temp)/'survey.csv';d=Path(temp)/'discovery.csv'
            s.write_bytes(payload([survey()],SURVEY_COLUMNS))
            self.assertTrue(load_opportunities(s,d,None).discovery.empty)
            d.write_text('wrong,header\n',encoding='utf-8')
            with self.assertRaises(SurveyLoadError): load_opportunities(s,d,None)

    def test_demo_manifest_and_default_contacts_boundary(self):
        data=load_opportunities()
        self.assertTrue(data.synthetic)
        self.assertFalse(data.contacts_supplied)
        self.assertEqual(data.permission,{})
        self.assertEqual(len(data.survey),150)
        self.assertEqual(len(data.discovery),35)

    def test_exports_match_filters_and_exclude_private_fields(self):
        data=bundle([survey(),survey('R2','P2')],[discovery()],[contact()])
        b=filter_businesses(build_businesses(data),search='P1')
        text=csv_bytes(ranking_table(b)).decode('utf-8-sig')
        rows=list(csv.DictReader(io.StringIO(text)))
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]['Business / Prospect ID'],'P1')
        brief=decision_brief(b,data,{'search':'P1'},generated_at=datetime(2026,10,12,tzinfo=timezone.utc))
        for value in ('PRIVATE_NAME','PRIVATE_BUSINESS','private@example.invalid'):
            self.assertNotIn(value,text+brief)
        self.assertIn('Businesses analysed: 1',brief)
        self.assertIn('100.0/100',brief)
        self.assertEqual(brief,decision_brief(b,data,{'search':'P1'},generated_at=datetime(2026,10,12,tzinfo=timezone.utc)))

    def test_csv_formula_protection(self):
        text=csv_bytes(pd.DataFrame({'Business':['=HYPERLINK("evil")']})).decode('utf-8-sig')
        self.assertTrue(list(csv.DictReader(io.StringIO(text)))[0]['Business'].startswith("'="))
