"""Pure Python scoring. Unknown evidence never becomes a neutral or zero score."""

from math import isfinite
from src.opportunity_config import CONFIG


def known(value):
    if value is None or value == '':
        return False
    if isinstance(value, (float, int)):
        return isfinite(value)
    return True


def score_band(score, config=CONFIG):
    if not known(score):
        return 'Not assessed'
    if not 0 <= score <= 100:
        raise ValueError('Scores must be between 0 and 100.')
    return next(name for floor,name in config['bands'] if score >= floor)


def value_score(survey, prevalence, config=CONFIG):
    primary = survey.get('primary_pain_point')
    pain = survey.get('pain_points')
    additional = len(set(pain)-{primary}) if isinstance(pain,list) and pain and primary in pain else None
    values = {
        'impact': config['impact_points'].get(survey.get('impact_rating')),
        'workload': config['workload_points'].get(survey.get('weekly_hours_band')),
        'recurrence': prevalence.get(primary),
        'additional': min(additional,config['additional_cap'])/config['additional_cap']*100 if additional is not None else None,
    }
    sources = {'impact':'S09 impact_rating', 'workload':'S08 weekly_hours_band (ordinal points, not hours)',
               'recurrence':'S06 prevalence of the S07 primary category in the full loaded business sample',
               'additional':'S06 distinct additional reported problems; S07 must be one of the selections'}
    parts = [{'component':k,'source':sources[k],'points':v,'weight':config['value_weights'][k],
              'contribution':v*config['value_weights'][k] if v is not None else None} for k,v in values.items()]
    missing = [k for k,v in values.items() if v is None]
    return (None if missing else sum(p['contribution'] for p in parts)), parts, missing


def commercial_score(assessment, config=CONFIG):
    if assessment is None:
        return None, [], ['No discovery qualification; survey interest alone is insufficient']
    parts, missing = [], []
    for field,weight in config['commercial_weights'].items():
        answer = assessment.get(field)
        points = config['commercial_points'][field].get(answer)
        parts.append({'component':field,'source':answer,'points':points,'weight':weight,
                      'contribution':None if points is None else points*weight})
        if points is None:
            missing.append(field)
    if assessment.get('evidence_status') not in config['qualified_evidence']:
        missing.append('Consultant-assessed or validated evidence status')
    if not assessment.get('assessment_evidence'):
        missing.append('Assessment rationale')
    if assessment.get('decision_authority') not in config['known_authority']:
        missing.append('Identify the investment approver (does not prove their involvement)')
    if not assessment.get('assessment_date') or not assessment.get('workflow_name'):
        missing.append('Dated, named workflow assessment')
    return (None if missing else sum(p['contribution'] for p in parts)), parts, missing


def composite_score(value, commercial, config=CONFIG):
    if not known(value) or not known(commercial):
        return None
    if not 0 <= value <= 100 or not 0 <= commercial <= 100:
        raise ValueError('Composite inputs must be between 0 and 100.')
    return value*config['overall_weights']['value_score'] + commercial*config['overall_weights']['commercial_score']


def completed_assessment(row):
    """Operational completion proxy; the schema has no completion-status field."""
    return bool(row.get('assessment_date') and row.get('workflow_name') and row.get('assessment_evidence')
                and row.get('evidence_status') in ('self_reported','consultant_assessed','validated'))


def primary_assessment(assessments, config=CONFIG):
    """Latest record per workflow, then highest documented impact; no score sums."""
    latest = {}
    for row in sorted(assessments,key=lambda r:(r.get('assessment_date') or '',r['assessment_id'])):
        latest[row['workflow_id']] = row
    if not latest:
        return None
    # Incomplete latest records do not fall back to an older, favourable score.
    return max(latest.values(), key=lambda r:(
        config['impact_priority'].get(r.get('business_impact_assessment'),0),
        r.get('assessment_date') or '',r['assessment_id']))
