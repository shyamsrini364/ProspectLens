"""Streamlit components; all calculations come from market_metrics."""

from dataclasses import asdict
from html import escape

import pandas as pd
import streamlit as st

from src.market_charts import ai_adoption_heatmap, ai_adoption_donut, bar_chart, label, pain_heatmap
from src.market_charts import survey_bar_chart, survey_bar_summary, outcome_column_chart
from src.market_data import SurveyLoadError, load_survey
from src.market_menu import render_menu_actions
from src.shared_data import manage_data_dialog, migrate_dataset_state, market_bundle
from src.market_metrics import (
    FILTER_FIELDS, MINIMUM_GROUP_SIZE, filter_options, filter_survey,
    frequency, market_kpis, quality_summary, ai_adoption_by_industry,
)
from src.market_style import dashboard_css, theme_tokens
from src.filter_help import AI_ADOPTION_HELP

FILTER_NAMES = {"industry":"Industry", "employee_band":"Business size",
                "primary_pain_point":"Primary pain point", "ai_adoption":"AI adoption level"}


@st.fragment(run_every="1s")
def sync_appearance(rendered_mode):
    """Native theme changes do not themselves rerun Python in Streamlit 1.65.

    This tiny fragment checks browser context; only a changed theme reruns the
    full page. CSV loading and chart calculations do not repeat on each tick.
    """
    if (st.context.theme.type or "light") != rendered_mode:
        st.rerun()


def reset_filters():
    for field in FILTER_FIELDS:
        st.session_state[f"filter_{field}"] = []


def render_filters(frame):
    with st.container(key="filters"):
        st.subheader("Filters")
        st.caption("Combine filters to focus the whole view. An empty filter includes all answers, including missing answers.")
        selections = {}
        for field, column in zip(FILTER_FIELDS, st.columns(4)):
            options = filter_options(frame, field)
            key = f"filter_{field}"
            # A refreshed CSV can remove a previously selected category.
            if key in st.session_state:
                retained = [code for code in st.session_state[key] if code in options]
                if retained != st.session_state[key]:
                    st.session_state[key] = retained
            with column:
                selections[field] = st.multiselect(FILTER_NAMES[field], options,
                    format_func=lambda code, field=field: label(field, code), key=key, placeholder="All answers",
                    help=AI_ADOPTION_HELP if field == 'ai_adoption' else None)
        st.button("Reset filters", on_click=reset_filters)
    return filter_survey(frame, selections)


def render_kpis(frame):
    values = market_kpis(frame)
    specs = [
        ("Total survey responses", str(values["responses"]), f"{values['prospects']} distinct prospects",
         "Each response_id counts once. Repeated submissions by the same prospect remain separate responses."),
        ("Industries represented", str(values["industries"]), f"{values['industry_missing']} missing industry answers",
         "Distinct nonmissing S04 categories; Other counts as one category."),
    ]
    for title, key, help_text in [
        ("High-impact problems", "high_impact", "S09 rating 4 or 5, divided by responses with a recorded impact rating."),
        ("Currently using AI", "using_ai", "S14 regular use or specific-task use, divided by answered S14. Experimented is separate; Not sure remains in the denominator."),
        ("Interested in follow-up", "followup", "S18 Yes only, divided by answered S18. Maybe is separate. Interest does not establish consent to contact."),
    ]:
        rate = values[key]
        specs.append((title, f"{rate.percentage:.1f}%" if rate.percentage is not None else "—",
                      f"{rate.count} / {rate.denominator} answered · {rate.missing} missing", help_text))
    with st.container(key="kpis"):
        for column, (title,value,detail,help_text) in zip(st.columns(5),specs):
            with column:
                st.metric(title,value,delta=detail,delta_color="off",delta_arrow="off",help=help_text)
    st.caption(f"Follow-up: {values['followup_maybe']} additional respondents answered Maybe. "
               f"AI adoption: {values['ai_unsure']} answered Not sure. Interest is not contact consent.")
    return values


def display_table(table, field, group_by=None):
    output = table.copy()
    output["category"] = output["category"].map(lambda code:label(field,code))
    if group_by:
        output[group_by] = output[group_by].map(lambda code:label(group_by,code))
        output = output[[group_by,*[c for c in output if c != group_by]]]
    return output.rename(columns={"category":"Answer", "count":"Respondents", "denominator":"Answered denominator",
        "percentage":"Percent", "missing":"Missing answers", "group_total":"Filtered group responses",
        "small_sample":"Small sample (<5)", "industry":"Industry"})


def render_chart(title, field, frame, tokens, key, group_by=None, kind="bar", ordered=False):
    table = ai_adoption_by_industry(frame) if kind == "ai" else frequency(frame,field,group_by)
    with st.container(key=f"chart_{key}"):
        st.subheader(title)
        multi = field in ("pain_points","ai_concerns")
        if group_by:
            st.caption("Percentages use answered responses within each industry. Hover for respondent counts and denominators.")
            summary = table.drop_duplicates(group_by)
            small = summary.loc[summary["small_sample"],group_by].tolist()
            zero = summary.loc[summary["denominator"].eq(0),group_by].tolist()
            if small:
                st.warning("Fewer than 5 answers: " + ", ".join(label(group_by,g,short=True) for g in small) + ". Treat these as small samples.")
            if zero:
                st.info("No recorded answers: " + ", ".join(label(group_by,g,short=True) for g in zero) + ". No percentage is calculated.")
            st.caption(f"{int(summary['denominator'].sum())} answered · {int(summary['missing'].sum())} missing in this selection.")
        else:
            denominator = int(table.iloc[0]["denominator"])
            st.caption(f"{denominator} answered / {len(frame)} filtered responses · {len(frame)-denominator} missing.")
            if 0 < denominator < MINIMUM_GROUP_SIZE:
                st.warning("Small sample: fewer than 5 answered responses.")
        if multi:
            st.caption("Multi-select: each respondent counts once per category. Percentages can total more than 100%.")
        if field in ('pain_points','employee_band') and not group_by:
            st.html('<div class="pl-survey-insight"><strong>Sample insight</strong><p>' +
                    escape(survey_bar_summary(table,field)) + '</p></div>')
        if not table["denominator"].gt(0).any():
            st.info("No recorded answers for this question in the selected sample.")
        if kind == "ai":
            render_ai_visualisation(table,tokens)
        elif table["denominator"].gt(0).any():
            if kind == "heatmap":
                st.caption("On narrow screens, scroll the heatmap horizontally or open its data table below.")
                with st.container(key="heatmap_scroll"):
                    st.plotly_chart(pain_heatmap(table,tokens),width=1080,theme=None,key=key,
                        config={"displayModeBar":False},alt=title + ". Values are also available in the data table below.")
            elif field == 'desired_outcome':
                st.caption('On narrow screens, scroll horizontally to see every outcome. Hover for full category names and counts.')
                with st.container(key='outcome_columns_scroll'):
                    st.plotly_chart(outcome_column_chart(table,tokens),width='stretch',theme=None,key=key,
                        config={'displayModeBar':False},alt=title + '. Values are also available in the data table below.')
            else:
                chart = survey_bar_chart if field in ('pain_points','employee_band') else bar_chart
                fig = (survey_bar_chart(table,field,tokens,highlight_token='survey-iris') if field == 'ai_concerns'
                       else chart(table,field,tokens,ordered))
                st.plotly_chart(fig,width="stretch",theme=None,key=key,config={"displayModeBar":False},
                    alt=title + ". Values are also available in the data table below.")
        with st.expander("View counts and denominators"):
            st.dataframe(display_table(table,field,group_by),hide_index=True,width="stretch",
                         column_config={"Percent":st.column_config.NumberColumn(format="%.1f%%")})


def render_ai_visualisation(table,tokens):
    st.caption("Sorted by answered S14 responses, largest first. Not sure is separate from Not using AI. "
               "0% means no respondents selected that category; N/A means no answered S14 responses.")
    view = st.radio("AI adoption visualisation",["Heatmap","Donut charts"],horizontal=True,key="ai_visualisation")
    if view == "Heatmap":
        st.caption("On narrow screens, scroll horizontally to keep all five category labels readable.")
        with st.container(key="ai_heatmap_scroll"):
            st.plotly_chart(ai_adoption_heatmap(table,tokens),width="stretch",theme=None,key="ai_industry",
                config={"displayModeBar":False},alt="AI adoption by industry: percentages, answered sample sizes and small-sample labels. Full values are in the table below.")
    else:
        # One shared categorical key; the charts use the same sorted table.
        from html import escape
        from src.schema import SURVEY_LABELS
        colors=("ai-regular","ai-specific","ai-experimented","ai-not-using","ai-unsure")
        st.html('<div class="pl-ai-legend">' + ''.join(
            f'<span><i style="background:{tokens[color]}"></i>{escape(label("ai_adoption",code,short=True))}</span>'
            for code,color in zip(SURVEY_LABELS["ai_adoption"],colors)) + '</div>')
        groups=table["industry"].drop_duplicates().tolist()
        with st.container(key="ai_donuts"):
            for start in range(0,len(groups),3):
                for column,group in zip(st.columns(3),groups[start:start+3]):
                    rows=table.loc[table["industry"].eq(group)]
                    first=rows.iloc[0]
                    with column:
                        st.markdown(f"**{label('industry',group,short=True)}**")
                        st.caption(f"n={first.denominator} answered · {first.missing} missing" +
                                   (" · Small sample (<5)" if first.small_sample else ""))
                        st.plotly_chart(ai_adoption_donut(rows,tokens),theme=None,width="stretch",key=f"ai_donut_{group}",
                            config={"displayModeBar":False},alt=f"AI adoption for {label('industry',group)}; full percentages in the table below.")


def render_quality(frame, validation, synthetic=True):
    ids = set(frame["response_id"])
    warnings = [issue for issue in validation.warnings if issue.row_id in ids]
    with st.container(key="quality"):
        st.subheader("Data quality & interpretation")
        st.write(f"**{len(frame)} valid responses in this selection** · {len(warnings)} validation warnings in the selection.")
        st.caption("Warnings flag incomplete or inconsistent answers; they do not invalidate a response. "
                   "Blank answers are excluded from that question's denominator. Not sure remains a recorded answer; "
                   "No significant concerns is a recorded S15 choice. Empty multi-select lists count as missing.")
        with st.expander("Answer completeness and validation warnings"):
            st.dataframe(quality_summary(frame),hide_index=True,width="stretch")
            if warnings:
                st.dataframe(pd.DataFrame([asdict(issue) for issue in warnings]),hide_index=True,width="stretch")
            else:
                st.write("No validation warnings in this selection.")
        provenance = "Synthetic demonstration only. " if synthetic else "Uploaded survey; source and representativeness have not been verified. "
        st.caption(provenance + "These selected survey responses do not establish broader market findings. "
                   "Small sample means fewer than 5 answered responses; it is a caution, not a statistical significance test. "
                   "Charts count survey responses, not discovery assessments. No contact data is loaded.")


def main():
    migrate_dataset_state()
    active=st.session_state.get('active_lens','Market Intelligence')
    st.set_page_config(page_title="ProspectLens · "+active,page_icon="◎",layout="wide")
    mode = st.context.theme.type or "light"
    sync_appearance(mode)
    tokens = theme_tokens(mode)
    st.html("<style>" + dashboard_css(mode) + "</style>")
    st.html('<div class="pl-brand"><span class="pl-logo" aria-hidden="true">◎</span>prospectlens'
            '<small>Your business intelligence workspace</small></div>')
    with st.container(key="navigation",horizontal=True):
        for lens in ('Market Intelligence','Opportunity Intelligence'):
            st.button(lens,type='primary' if active==lens else 'secondary',key='nav_'+lens,
                on_click=lambda name:st.session_state.update(active_lens=name),args=(lens,))
    if active=='Opportunity Intelligence':
        from src.opportunity_ui import render_opportunity
        render_opportunity(tokens)
        return
    st.html('<section class="pl-hero"><h1>Market Intelligence</h1>'
            '<p>ProspectLens brings survey responses together to show the operational challenges businesses report, '
            'how they use AI, the outcomes they want, and their concerns about AI and automation.</p>'
            '<p>Use <strong>Filters</strong> to explore an industry, business size, primary pain point or AI adoption level; '
            'all figures and charts update to match your selection. '
            'Hover over a chart or open <strong>View counts and denominators</strong> to see the full answers and respondent counts. '
            'Percentages show the share of respondents who answered that question within the displayed group, '
            'so check the sample sizes and missing answers when interpreting results.</p></section>')
    if st.button("Manage data",key="market_manage_data"):
        manage_data_dialog()
    try:
        # The file is small. Loading on each rerun avoids stale cache results after CSV edits.
        data = market_bundle(st.session_state["dataset_bundle"]) if "dataset_bundle" in st.session_state else load_survey()
    except SurveyLoadError as exc:
        st.error(str(exc))
        if exc.issues:
            st.dataframe(pd.DataFrame([asdict(issue) for issue in exc.issues]),hide_index=True,width="stretch")
        st.info("The dashboard will not substitute or generate data automatically. Check the existing survey and generation manifest.")
        render_menu_actions()
        st.stop()
    provenance = "Synthetic survey fingerprint verified." if data.synthetic_verified else "Uploaded survey · source not independently verified."
    st.caption(f"Validated source: {len(data.frame)} responses · {len(data.validation.errors)} errors · "
               f"{len(data.validation.warnings)} warnings · {provenance}")
    frame = render_filters(data.frame)
    render_menu_actions(frame,data.synthetic_verified)
    st.write(f"**{len(frame)} of {len(data.frame)} valid responses selected**")
    render_kpis(frame)
    if frame.empty:
        st.info("No responses match these filters." if len(data.frame) else "The survey file has a valid header but contains no response rows.")
        st.button("Clear all filters",on_click=reset_filters)
    else:
        if len(frame) < MINIMUM_GROUP_SIZE:
            st.warning("Small subgroup: fewer than 5 responses are selected. Percentages can change sharply with one answer.")
        with st.container(key="chart_pair"):
            left,right = st.columns([1.2,1])
            with left:
                render_chart("Operational pain points","pain_points",frame,tokens,"pain")
            with right:
                render_chart("Business size","employee_band",frame,tokens,"size",ordered=True)
        render_chart("Pain points across industries","pain_points",frame,tokens,"pain_industry",group_by="industry",kind="heatmap")
        render_chart("AI adoption by industry","ai_adoption",frame,tokens,"ai_industry",group_by="industry",kind="ai")
        # Separate full-width panels keep long, original outcome/concern labels legible.
        render_chart("Most desired business outcomes","desired_outcome",frame,tokens,"outcomes")
        render_chart("Concerns about AI & automation","ai_concerns",frame,tokens,"concerns")
    render_quality(frame,data.validation,data.synthetic_verified)
