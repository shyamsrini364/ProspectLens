"""Opportunity lens: shared design, explicit evidence and inspectable calculations."""

from dataclasses import asdict
from html import escape
import json

import pandas as pd
import streamlit as st

from src.market_charts import label, survey_bar_chart
from src.market_data import ROOT, SurveyLoadError
from src.market_menu import render_menu_actions
from src.shared_data import manage_data_dialog
from src.market_metrics import FILTER_FIELDS, MISSING, filter_options
from src.opportunity_config import CONFIG, MODEL_VERSION
from src.filter_help import AI_ADOPTION_HELP, ASSESSMENT_STAGE_HELP, opportunity_band_help
from src.opportunity_data import load_opportunities, load_uploaded_opportunities, from_market_upload
from src.opportunity_metrics import (build_businesses, filter_businesses, opportunity_kpis,
    recurring_problems, discovery_trend, records)
from src.opportunity_charts import opportunity_matrix, trend_chart
from src.opportunity_reports import ranking_table, csv_bytes, shortlist, decision_brief

FILTER_NAMES={'industry':'Industry','employee_band':'Business size','primary_pain_point':'Primary business problem',
              'ai_adoption':'AI adoption','stage':'Assessment stage','score_band':'Opportunity score band'}
SORTS={'Overall score':'overall_score','Opportunity value':'value_score','Commercial potential':'commercial_score',
       'Business impact':'impact_rating','Implementation complexity':'implementation_complexity'}


def reset_opportunity_filters():
    for key in FILTER_NAMES:
        st.session_state['opp_filter_'+key]=[]
    st.session_state['opp_search']=''


@st.dialog('Opportunity Intelligence — scores and methodology',width='large')
def methodology_dialog():
    st.markdown((ROOT/'docs/opportunity_methodology.md').read_text(encoding='utf-8'))
    with st.expander('Exact active weights, mappings and thresholds'):
        st.json(CONFIG)


def show_record(row):
    # Literal text avoids interpreting uploaded evidence as HTML or instructions.
    cells=[{'Field':k,'Recorded answer':json.dumps(v,ensure_ascii=False,default=str) if isinstance(v,list)
            else 'Not recorded' if v is None else str(v)} for k,v in row.items()]
    st.dataframe(pd.DataFrame(cells),hide_index=True,width='stretch')


@st.dialog('Business evidence and score breakdown',width='large')
def business_dialog(prospect_id,businesses,data):
    r=records(businesses.loc[businesses['prospect_id'].eq(prospect_id)])[0]
    st.subheader(str(prospect_id))
    st.caption(f'{r["stage"]} · {MODEL_VERSION} · one business, {r["discovery_count"]} assessment records')
    for title,field,parts in [('Business Opportunity Value','value_score','value_breakdown'),
                              ('Commercial Potential','commercial_score','commercial_breakdown')]:
        st.markdown('**'+title+'**')
        st.write('Not assessed — insufficient evidence' if r[field] is None else f'{r[field]:.1f} / 100')
        if r[parts]:
            st.dataframe(pd.DataFrame(r[parts]),hide_index=True,width='stretch')
    weights=CONFIG['overall_weights']
    st.write('**Overall score:** '+('Not assessed' if r['overall_score'] is None else
        f'{weights["value_score"]:.2f} × {r["value_score"]:.2f} + {weights["commercial_score"]:.2f} × {r["commercial_score"]:.2f} = {r["overall_score"]:.2f}'))
    st.caption('Weights are provisional. Full-precision inputs are used before display rounding; no conversion probability is implied.')
    st.write('**Contact permission:** '+r['contact_permission'])
    st.write('**Suggested next action:** '+r['next_action'])
    st.write('**Suggested discovery question:** '+r['next_question'])
    st.write('**Missing qualification evidence:**')
    for gap in r['evidence_gaps']:
        st.text('• '+gap)
    if not r['evidence_gaps']:
        st.caption('Minimum scoring inputs are present; independent evidence review is still required.')
    with st.expander('All survey submissions and additional reported problems'):
        for s in records(data.survey.loc[data.survey['prospect_id'].eq(prospect_id)]):
            st.text('Survey '+str(s['response_id'])+(' — representative survey' if s['response_id']==r['response_id'] else ' — earlier/other submission'))
            show_record(s)
    st.markdown('**All linked workflow assessments**')
    st.caption('The selected workflow uses latest-per-workflow records, then highest D24 impact; ties use date and ID. Secondary opportunities are not added to the business score.')
    for d in records(data.discovery.loc[data.discovery['prospect_id'].eq(prospect_id)]):
        title=f'{d["assessment_id"]} · {d["workflow_id"]}' + (' · Selected primary workflow' if d['assessment_id']==r['primary_assessment_id'] else '')
        with st.expander(title):
            show_record(d)
    with st.expander('Algorithms, scoring assumptions and limitations'):
        st.markdown((ROOT/'docs/opportunity_methodology.md').read_text(encoding='utf-8'))


def render_filters(businesses):
    help_text = {'ai_adoption': AI_ADOPTION_HELP, 'stage': ASSESSMENT_STAGE_HELP,
                 'score_band': opportunity_band_help(CONFIG)}
    st.subheader('Filters')
    st.caption('Choose a business segment, assessment stage or score band. Empty selections include all answers; every panel and download uses the same selection.')
    selections={}
    columns=st.columns(3)
    for i,(field,name) in enumerate(FILTER_NAMES.items()):
        options=filter_options(businesses,field) if field in FILTER_FIELDS else sorted(businesses[field].dropna().unique().tolist())
        key='opp_filter_'+field
        if key in st.session_state:
            st.session_state[key]=[v for v in st.session_state[key] if v in options]
        with columns[i%3]:
            selections[field]=st.multiselect(name,options,key=key,placeholder='All answers',
                format_func=lambda v,f=field:label(f,v) if f in FILTER_FIELDS else v,
                help=help_text.get(field))
    search=st.text_input('Search business / prospect ID',key='opp_search',placeholder='For example: P0001')
    st.button('Reset opportunity filters',on_click=reset_opportunity_filters)
    return filter_businesses(businesses,selections,search),dict(selections,search=search)


def render_kpis(frame):
    k=opportunity_kpis(frame)
    enriched=k['means']['Discovery Enriched']
    specs=[('Businesses analysed',str(k['businesses']),'Unique prospect IDs'),
        ('High-impact businesses',str(k['high_impact']),f'{k["impact_answered"]} answered impact · {len(frame)-k["impact_answered"]} missing'),
        ('Discovery-assessed businesses',str(k['assessed']),f'{len(frame)} selected businesses'),
        ('Interested prospects',str(k['interested']),f'{k["interest_answered"]} answered · Yes only'),
        ('Average prospect score','—' if enriched['mean'] is None else f'{enriched["mean"]:.1f}',
         f'Discovery: {enriched["eligible"]}/{enriched["total"]} eligible')]
    with st.container(key='opp_kpis'):
        for col,(title,value,detail) in zip(st.columns(5),specs):
            with col:
                st.metric(title,value,delta=detail,delta_color='off',delta_arrow='off')
    st.caption('Average uses eligible Discovery Enriched businesses only. Survey-only commercial and overall scores are unassessed. Interest is not contact permission.')


def render_opportunity(tokens):
    st.html('<section class="pl-hero"><h1>Opportunity Intelligence</h1>'
        '<p>Compare individual businesses by the significance of their reported challenges and the strength of their commercial evidence, '
        'then explore the workflows that may merit further investigation.</p>'
        '<p>Use <strong>Filters</strong> to focus the whole lens, compare eligible businesses in the matrix and ranking, '
        'and open <strong>Business details</strong> to inspect every linked assessment. '
        'Select <strong>How scores work</strong> for the algorithms, weights, evidence requirements and limitations. '
        'Scores are provisional priorities for human review; missing commercial evidence stays unassessed, and interest is not permission to contact.</p></section>')
    a,b=st.columns([1,1])
    with a:
        if st.button('Manage data',key='opp_load'):
            manage_data_dialog()
    with b:
        if st.button('How scores work',key='opp_methodology'):
            methodology_dialog()
    try:
        if 'dataset_bundle' in st.session_state:
            data=st.session_state['dataset_bundle']
        else:
            data=load_opportunities()
    except SurveyLoadError as exc:
        st.error(str(exc))
        if exc.issues:
            st.dataframe(pd.DataFrame([asdict(i) for i in exc.issues]),hide_index=True)
        render_menu_actions(upload_action=manage_data_dialog)
        return
    businesses=build_businesses(data)
    st.caption(f'{data.name} · {len(data.survey)} valid survey submissions · {len(businesses)} unique businesses · '
               f'{len(data.discovery)} discovery records · {len(data.validation.warnings)} validation warnings')
    if data.synthetic:
        st.caption('SYNTHETIC DATA — NOT REAL MARKET FINDINGS · Loaded file fingerprints verified. Restricted demo contacts are not loaded.')
    if data.discovery.empty:
        st.info('Survey-only evidence: commercial qualification and overall scores are not assessed. Upload discovery evidence to enrich this lens.')
    with st.container(key='opp_filters'):
        frame,filters=render_filters(businesses)
    st.write(f'**{len(frame)} of {len(businesses)} businesses selected**')
    render_kpis(frame)
    sort=st.selectbox('Rank businesses by',list(SORTS),key='opp_sort')
    sort_by=SORTS[sort]
    ranking=ranking_table(frame,sort_by)
    render_menu_actions(upload_action=manage_data_dialog,export_data=csv_bytes(ranking),export_name='opportunity_intelligence_export.csv')
    if frame.empty:
        st.info('No businesses match these filters. Reset filters or load a survey containing response rows.')
    elif len(frame)<CONFIG['minimum_group']:
        st.warning('Small subgroup: fewer than five businesses. Treat percentages and scores cautiously.')
    with st.container(key='chart_opp_matrix'):
        st.subheader('Business Opportunity Matrix')
        st.caption('One bubble per eligible business. Click a bubble to open its evidence and scores. Axes are independent; lines at 50 and score bands are provisional guides, not validated boundaries.')
        missing=int(frame['overall_score'].isna().sum())
        st.caption(f'{len(frame)-missing}/{len(frame)} businesses plotted · {missing} omitted for insufficient evidence.')
        if frame['stage'].eq('Survey Only').any():
            st.info('Preliminary Commercial Potential: survey interest alone is insufficient for a numerical score. Survey-only businesses remain visible in the ranking.')
        size=st.checkbox('Size bubbles by business-size category',key='opp_bubble_size')
        if size:
            st.caption('Sizes represent ordered bands, not exact employee counts; missing size uses the smallest marker.')
        with st.container(key='opp_matrix_scroll'):
            event=st.plotly_chart(opportunity_matrix(frame,tokens,size),width='stretch',theme=None,key='opp_matrix',
                config={'displayModeBar':False},on_select='rerun',selection_mode='points',
                alt='One point per eligible business; all records are also in the ranking.')
        points=event.selection.points
        selected=points[-1].get('customdata',[None])[-1] if points else None
        if selected and selected in set(frame['prospect_id']) and selected!=st.session_state.get('opp_last_matrix_selection'):
            st.session_state['opp_last_matrix_selection']=selected
            business_dialog(selected,businesses,data)
        elif not selected:
            st.session_state.pop('opp_last_matrix_selection',None)
        with st.expander('What the quadrants mean'):
            st.markdown('- **High value / High commercial:** candidates for further commercial discovery.\n'
                '- **High value / Low commercial:** significant problems with weaker engagement evidence.\n'
                '- **Low value / High commercial:** clarify the problem and value proposition.\n'
                '- **Low value / Low commercial:** lower current investigation priority.')
    with st.container(key='chart_opp_ranking'):
        st.subheader('Business Opportunity Ranking')
        st.caption('One row per business; all selected businesses are retained. Ranks restart within each stage; missing composite scores have no composite rank. Scores are not probabilities.')
        st.dataframe(ranking,hide_index=True,width='stretch')
        if len(frame):
            prospect=st.selectbox('Select a business to inspect',frame['prospect_id'].tolist(),key='opp_detail_select')
            if st.button('Business details',key='opp_detail_open'):
                business_dialog(prospect,businesses,data)
    with st.container(key='chart_opp_recurring'):
        st.subheader('Recurring Business Problems')
        problems=recurring_problems(frame,data.discovery)
        n=int(problems.iloc[0]['denominator'])
        st.caption(f'{n}/{len(frame)} businesses answered S06 on their latest survey. Each business counts once per selected category; percentages may total above 100%.')
        st.caption('Solution families are hypotheses. Assessment counts refer to reporting businesses; category-matched workflows cannot be identified from this schema.')
        if n:
            st.plotly_chart(survey_bar_chart(problems,'pain_points',tokens),width='stretch',theme=None,
                config={'displayModeBar':False},key='opp_recurring')
        else:
            st.info('No recorded pain-point selections in this group.')
        with st.expander('Counts, impact, workload and solution hypotheses'):
            table=problems.copy()
            table['category']=table['category'].map(lambda c:label('pain_points',c))
            table['workload_distribution']=table['workload_distribution'].map(lambda x:json.dumps(x))
            st.dataframe(table,hide_index=True,width='stretch')
    with st.container(key='chart_opp_trend'):
        st.subheader('Opportunity Discovery Over Time')
        st.caption('Research activity for selected businesses, including their earlier submissions. Rising cumulative counts do not establish growing market demand.')
        period=st.selectbox('Group dates by',['Weekly','Monthly'],key='opp_period')
        mode=st.radio('Trend display',['Cumulative','New Per Period'],horizontal=True,key='opp_trend_mode')
        trend,missing_dates=discovery_trend(data.survey,data.discovery,set(frame['prospect_id']),period,mode=='Cumulative')
        st.caption('Excluded missing dates: '+', '.join(f'{k}: {v}' for k,v in missing_dates.items()))
        if trend.empty:
            st.info('No dated records for this selection.')
        else:
            st.plotly_chart(trend_chart(trend,tokens,mode=='Cumulative',period),width='stretch',theme=None,key='opp_trend',config={'displayModeBar':False})
            with st.expander('View period counts'):
                st.dataframe(trend,hide_index=True,width='stretch')
    with st.container(key='chart_opp_technical'):
        st.subheader('Commercial & Technical Evidence')
        d=data.discovery.loc[data.discovery['prospect_id'].isin(frame['prospect_id'])].copy()
        st.caption(f'{len(d)} assessments across {d["prospect_id"].nunique()} businesses; includes secondary workflows and reassessments. Complexity: 1–2 Simple, 3 Medium, 4–5 Complex.')
        fields=['prospect_id','assessment_id','workflow_id','assessment_date','budget_status','pilot_interest','decision_authority',
                'commercial_potential','business_impact_assessment','technical_feasibility','solution_reusability','implementation_complexity','evidence_status']
        st.dataframe(d[fields],hide_index=True,width='stretch')
    with st.container(key='chart_opp_downloads'):
        st.subheader('Decision outputs')
        st.caption('Downloads reflect the same filters. They contain pseudonymous identifiers and analytical fields, never personal contact details.')
        st.download_button('Download ranking CSV',csv_bytes(ranking),'opportunity_intelligence_export.csv','text/csv',on_click='ignore')
        st.download_button('Download Consultant Decision Brief',decision_brief(frame,data,filters,sort_by),
                           'opportunity_intelligence_decision_brief.md','text/markdown',on_click='ignore')
        short=shortlist(frame,data.contacts_supplied)
        st.caption(f'{len(short)} shortlisted businesses. '+('Only documented-permission records included; review before outreach.'
            if data.contacts_supplied else 'Analytical shortlist only — no contact permission has been assessed.'))
        st.download_button('Download follow-up shortlist',csv_bytes(short),'opportunity_intelligence_followup_shortlist.csv','text/csv',on_click='ignore')
    with st.expander('Data quality, coverage and limitations'):
        st.write(f'{len(businesses)} unique businesses from {len(data.survey)} valid survey submissions. Repeated prospects are consolidated, not discarded as errors.')
        st.caption('Latest-survey fields drive filters and scores; recurrence scoring uses the full loaded business sample. Detail views retain all original evidence. Unknown is never replaced by zero.')
        if data.validation.warnings:
            st.caption('Validation warnings below cover the full loaded dataset, before analytical filters.')
            st.dataframe(pd.DataFrame([asdict(i) for i in data.validation.warnings]),hide_index=True,width='stretch')
        st.caption('Synthetic findings are demonstration only. Uploaded records are not independently verified. Scores and category-level reuse hypotheses require human review.')
