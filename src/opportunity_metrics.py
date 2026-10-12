"""Business snapshots, filtered metrics and research-activity series."""

from collections import Counter
import pandas as pd

from src.market_metrics import FILTER_FIELDS, MISSING
from src.opportunity_config import CONFIG, MODEL_VERSION, SOLUTION_HYPOTHESES
from src.opportunity_scoring import value_score, commercial_score, composite_score, score_band, primary_assessment, completed_assessment
from src.schema import ENUMS

DERIVED = ['stage','discovery_count','completed_count','primary_assessment_id','workflow_id',
           'implementation_complexity','technical_feasibility','solution_reusability','commercial_readiness',
           'value_score','commercial_score','overall_score','score_band','value_breakdown','commercial_breakdown',
           'evidence_gaps','contact_permission','next_action','next_question','model_version']


def records(frame):
    return [{k:None if not isinstance(v,list) and pd.isna(v) else v for k,v in r.items()}
            for r in frame.to_dict('records')]


def latest_surveys(frame):
    # Calendar dates as recorded; never invent a timezone for naive timestamps.
    work=frame.copy()
    work['_date']=work['submitted_at'].fillna('').str[:10]
    return work.sort_values(['_date','response_id'],kind='stable').drop_duplicates('prospect_id',keep='last').drop(columns='_date')


def build_businesses(data, config=CONFIG):
    current=latest_surveys(data.survey)
    rows=records(current)
    answered=[r for r in rows if isinstance(r['pain_points'],list) and r['pain_points']]
    counts=Counter(c for r in answered for c in set(r['pain_points']))
    prevalence={c:100*counts[c]/len(answered) for c in ENUMS['pain_points']} if answered else {}
    discovery=records(data.discovery)
    output=[]
    for r in rows:
        assessments=[d for d in discovery if d['prospect_id']==r['prospect_id']]
        primary=primary_assessment(assessments,config)
        value,vparts,vgaps=value_score(r,prevalence,config)
        commercial,cparts,cgaps=commercial_score(primary,config)
        overall=composite_score(value,commercial,config)
        permission=data.permission.get(r['response_id'],'Not assessed')
        status='Discovery Enriched' if assessments else 'Survey Only'
        action=(primary or {}).get('recommended_next_action') or 'further_discovery'
        if action in ('defer','no_suitable_opportunity'):
            next_action=action.replace('_',' ').capitalize()
        elif permission!='Permission documented':
            next_action='Review evidence and contact permission'
        elif commercial is None:
            next_action='Qualify budget, approver, timing and pilot interest'
        else:
            next_action=action.replace('_',' ').capitalize()
        question=('Who approves investment, what budget is available, and would a scoped pilot be useful?'
                  if cgaps else 'What baseline and success measure would justify a small, human-reviewed pilot?')
        output.append(dict(r,stage=status,discovery_count=len(assessments),
            completed_count=sum(completed_assessment(d) for d in assessments),
            primary_assessment_id=(primary or {}).get('assessment_id'),workflow_id=(primary or {}).get('workflow_id'),
            implementation_complexity=(primary or {}).get('implementation_complexity'),
            technical_feasibility=(primary or {}).get('technical_feasibility'),
            solution_reusability=(primary or {}).get('solution_reusability'),
            commercial_readiness=(primary or {}).get('budget_status'),
            value_score=value,commercial_score=commercial,overall_score=overall,score_band=score_band(overall,config),
            value_breakdown=vparts,commercial_breakdown=cparts,evidence_gaps=vgaps+cgaps,
            contact_permission=permission,next_action=next_action,next_question=question,model_version=MODEL_VERSION))
    return pd.DataFrame(output,columns=[*data.survey.columns,*DERIVED])


def filter_businesses(frame, selections=None, search=''):
    result=frame.copy()
    for field,choices in (selections or {}).items():
        if field not in (*FILTER_FIELDS,'stage','score_band'):
            raise ValueError('Unsupported opportunity filter: '+field)
        if choices:
            result=result.loc[result[field].fillna(MISSING).isin(choices)]
    if search.strip():
        result=result.loc[result['prospect_id'].str.contains(search.strip(),case=False,regex=False)]
    return result.copy()


def ranked(frame, sort_by='overall_score'):
    if sort_by not in ('overall_score','value_score','commercial_score','impact_rating','implementation_complexity'):
        raise ValueError('Unsupported ranking field')
    # Stage separation is always explicit; missing scores are retained at the bottom.
    return frame.sort_values(['stage',sort_by,'prospect_id'],ascending=[True,False,True],na_position='last',kind='stable')


def opportunity_kpis(frame):
    impact=pd.to_numeric(frame['impact_rating'],errors='coerce')
    scores=pd.to_numeric(frame['overall_score'],errors='coerce')
    means={}
    for stage in ('Survey Only','Discovery Enriched'):
        s=scores.loc[frame['stage'].eq(stage)].dropna()
        means[stage]={'mean':float(s.mean()) if len(s) else None,'eligible':len(s),
                      'total':int(frame['stage'].eq(stage).sum())}
    return dict(businesses=len(frame),high_impact=int(impact.ge(CONFIG['high_impact']).sum()),
        impact_answered=int(impact.notna().sum()),assessed=int(frame['completed_count'].gt(0).sum()),
        interested=int(frame['followup_interest'].eq('yes').sum()),
        interest_answered=int(frame['followup_interest'].notna().sum()),means=means)


def recurring_problems(frame, discovery):
    rows=records(frame)
    answered=[r for r in rows if isinstance(r['pain_points'],list) and r['pain_points']]
    output=[]
    for code in ENUMS['pain_points']:
        group=[r for r in answered if code in set(r['pain_points'])]
        primary=[r for r in rows if r['primary_pain_point']==code]
        ratings=[r['impact_rating'] for r in primary if r['impact_rating'] is not None]
        ids={r['prospect_id'] for r in group}
        output.append(dict(category=code,count=len(group),denominator=len(answered),
            percentage=100*len(group)/len(answered) if answered else None,
            primary_count=len(primary),mean_primary_impact=sum(ratings)/len(ratings) if ratings else None,
            impact_denominator=len(ratings),workload_distribution=dict(Counter(r['weekly_hours_band'] or 'missing' for r in primary)),
            industries=sorted({r['industry'] for r in group if r['industry']}),
            assessments_at_reporting_businesses=int(discovery.loc[discovery['prospect_id'].isin(ids),'assessment_id'].nunique()),
            workflow_matched_assessments=None,solution_hypothesis=SOLUTION_HYPOTHESES[code],
            missing=len(frame)-len(answered),group_total=len(frame),small_sample=0<len(answered)<CONFIG['minimum_group']))
    return pd.DataFrame(output).sort_values('count',ascending=False,kind='stable')


def discovery_trend(survey, discovery, prospect_ids, period='Weekly', cumulative=True):
    """Count unique IDs on recorded calendar dates; include zero-activity periods."""
    if period not in ('Weekly','Monthly'):
        raise ValueError('Choose Weekly or Monthly')
    frequency='W-SUN' if period=='Weekly' else 'M'
    series={}
    missing={}
    survey=survey.loc[survey['prospect_id'].isin(prospect_ids)].drop_duplicates('response_id')
    discovery=discovery.loc[discovery['prospect_id'].isin(prospect_ids)].drop_duplicates('assessment_id')
    sources=[('Survey responses',survey,'submitted_at'),
             ('High-impact survey responses',survey.loc[pd.to_numeric(survey['impact_rating'],errors='coerce').ge(CONFIG['high_impact'])],'submitted_at'),
             ('Discovery assessments',discovery,'assessment_date')]
    for name,frame,date_field in sources:
        dates=pd.to_datetime(frame[date_field].str[:10],errors='coerce')
        missing[name]=int(dates.isna().sum())
        series[name]=dates.dropna().dt.to_period(frequency).value_counts().sort_index()
    nonempty=[s for s in series.values() if len(s)]
    if not nonempty:
        return pd.DataFrame(columns=['period',*series]),missing
    periods=pd.period_range(min(s.index.min() for s in nonempty),max(s.index.max() for s in nonempty),freq=frequency)
    result=pd.DataFrame({k:s.reindex(periods,fill_value=0).astype(int) for k,s in series.items()},index=periods)
    if cumulative:
        result=result.cumsum()
    result.insert(0,'period',periods.start_time)
    return result.reset_index(drop=True),missing
