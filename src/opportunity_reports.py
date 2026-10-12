"""Deterministic, allowlisted decision outputs; no personal contact columns."""

from datetime import datetime
from html import escape
from zoneinfo import ZoneInfo
import json

import pandas as pd

from src.market_charts import label
from src.opportunity_config import MODEL_VERSION
from src.opportunity_metrics import ranked, recurring_problems, opportunity_kpis

RANK_FIELDS = {
    'prospect_id':'Business / Prospect ID','industry':'Industry','employee_band':'Business size',
    'primary_pain_point':'Primary business problem','weekly_hours_band':'Weekly workload band',
    'impact_rating':'Business impact (1–5)','ai_adoption':'AI adoption','value_score':'Opportunity value score',
    'commercial_score':'Commercial potential score','overall_score':'Overall prospect score',
    'score_band':'Score band','stage':'Assessment stage','discovery_count':'Discovery records',
    'completed_count':'Completed assessments','implementation_complexity':'Implementation complexity (1–5)',
    'technical_feasibility':'Technical feasibility','followup_interest':'Follow-up interest',
    'contact_permission':'Contact permission','next_action':'Next recommended action','next_question':'Next discovery question',
}
LABEL_FIELDS=['industry','employee_band','primary_pain_point','weekly_hours_band','ai_adoption','followup_interest']


def ranking_table(frame, sort_by='overall_score'):
    ordered=ranked(frame,sort_by)
    out=ordered[list(RANK_FIELDS)].copy()
    for field in LABEL_FIELDS:
        out[field]=out[field].map(lambda x:label(field,x) if pd.notna(x) else 'Not answered')
    for field in ('value_score','commercial_score','overall_score'):
        out[field]=pd.to_numeric(out[field],errors='coerce').round(1)
    out.insert(0,'Rank within stage',ordered.groupby('stage').cumcount()+1)
    if sort_by=='overall_score':
        out.loc[ordered['overall_score'].isna(),'Rank within stage']=pd.NA
    return out.rename(columns=RANK_FIELDS).reset_index(drop=True)


def csv_bytes(table):
    """Neutralise spreadsheet formulas in externally supplied text identifiers."""
    safe=table.copy()
    for c in safe:
        safe[c]=safe[c].map(lambda x:"'"+x if isinstance(x,str) and x.lstrip().startswith(('=','+','-','@','\t','\r')) else x)
    return safe.to_csv(index=False,na_rep='Not assessed').encode('utf-8-sig')


def shortlist(frame, permission_supplied=False):
    eligible=frame['followup_interest'].isin(['yes','maybe']) & ~frame['next_action'].isin(['Defer','No suitable opportunity'])
    if permission_supplied:
        eligible &= frame['contact_permission'].eq('Permission documented')
    result=ranking_table(frame.loc[eligible])
    result['Reason for investigation']=[
        f'{r["Primary business problem"]}; impact {r["Business impact (1–5)"] if pd.notna(r["Business impact (1–5)"]) else "not assessed"}/5; '
        f'follow-up interest: {r["Follow-up interest"]}; {r["Assessment stage"]} evidence.'
        for r in result.to_dict('records')]
    result['Shortlist type']='Permission-aware follow-up' if permission_supplied else 'Analytical only — permission not assessed'
    return result


def _safe(value):
    return escape(str(value)).replace('|','\\|').replace('\n',' ').replace('`','\\`').replace('[','\\[').replace(']','\\]')


def decision_brief(frame, data, filters, sort_by='overall_score', generated_at=None):
    when=generated_at or datetime.now(ZoneInfo('Australia/Sydney'))
    k=opportunity_kpis(frame)
    problems=recurring_problems(frame,data.discovery)
    lines=['# ProspectLens — Consultant Decision Brief','',f'Generated: {when.isoformat()}',
        f'Dataset: {_safe(data.name)}',f'Method: {MODEL_VERSION}',
        'SYNTHETIC DATA — NOT REAL MARKET FINDINGS' if data.synthetic else 'Uploaded/local evidence — source and representativeness not verified.',
        '',f'Applied filters: {_safe(json.dumps(filters,ensure_ascii=False))}',
        f'Businesses analysed: {k["businesses"]}',
        f'High-impact businesses: {k["high_impact"]}/{k["impact_answered"]} answering impact.',
        f'Discovery coverage: {k["assessed"]}/{k["businesses"]} with a completed assessment.',
        '', '## Recurring problems and candidate solution hypotheses']
    for r in problems.loc[problems['count'].gt(0)].head(5).itertuples():
        lines.append(f'- {label("pain_points",r.category)}: {r.count}/{r.denominator} businesses ({r.percentage:.1f}%); '
                     f'primary challenge for {r.primary_count}. Hypothesis: {r.solution_hypothesis}.')
    if not len(frame):
        lines.append('No businesses match the current filters.')
    lines += ['', '## Commercial observations and investigation priorities']
    for stage,summary in k['means'].items():
        mean='Not assessed' if summary['mean'] is None else f'{summary["mean"]:.1f}/100'
        lines.append(f'- {stage}: {summary["eligible"]}/{summary["total"]} score-eligible; average {mean}.')
    eligible=ranked(frame,sort_by)
    for stage in ('Discovery Enriched','Survey Only'):
        lines.append(f'### {stage}')
        for r in eligible.loc[eligible['stage'].eq(stage)].head(5).itertuples():
            score='Not assessed' if pd.isna(r.overall_score) else f'{r.overall_score:.1f}'
            lines.append(f'- {_safe(r.prospect_id)}: {label("primary_pain_point",r.primary_pain_point) if pd.notna(r.primary_pain_point) else "Primary problem missing"}; '
                f'overall {score}; {_safe(r.next_action)}. Question: {_safe(r.next_question)}')
    ids=set(frame['prospect_id'])
    d=data.discovery.loc[data.discovery['prospect_id'].isin(ids)]
    lines += ['', '## Technical considerations and evidence gaps',
        f'{len(d)} assessment records across {d["prospect_id"].nunique()} selected businesses (records are not business counts).',
        f'{int(pd.to_numeric(d["implementation_complexity"],errors="coerce").ge(4).sum())} records report complexity 4–5; '
        f'{int(d["technical_feasibility"].isna().sum()+d["technical_feasibility"].eq("unknown").sum())} have unassessed feasibility.',
        f'{int(frame["overall_score"].isna().sum())} businesses lack enough evidence for an overall score.',
        '', '## Limitations and next investigations',
        '- Scores are provisional priorities, not probabilities, revenue forecasts or verified ROI.',
        '- Survey-only commercial potential is unassessed; follow-up interest does not prove budget or consent.',
        '- One latest survey represents each business; older responses remain in research-activity trends.',
        '- Recurrence is a category-level signal, not proof that one implementation works across businesses.',
        '- The schema has no discovery problem-category link; assessment counts at reporting businesses are not matched workflow counts.',
        '- Clarify missing impact/workload, investment approver, budget, pilot scope and supporting evidence.',
        '- Review technical feasibility, security requirements and baseline measurements before proposing delivery.',
        '- Small groups need caution; these selected responses cannot establish broader market findings.',
        '- No personal contact details are exported; permission flags require human review before any outreach.']
    return '\n'.join(lines)+'\n'
