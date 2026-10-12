"""One validated, session-only dataset bundle for both dashboard lenses."""

from dataclasses import asdict
import pandas as pd
import streamlit as st

from src.market_data import SurveyData, SurveyLoadError
from src.market_metrics import FILTER_FIELDS
from src.opportunity_data import load_uploaded_opportunities, from_market_upload


def reset_dataset_filters():
    for field in FILTER_FIELDS:
        st.session_state['filter_'+field] = []
    for field in (*FILTER_FIELDS, 'stage', 'score_band'):
        st.session_state['opp_filter_'+field] = []
    st.session_state['opp_search'] = ''
    st.session_state.pop('opp_last_matrix_selection', None)
    st.session_state.pop('opp_detail_select', None)


def apply_bundle(bundle):
    st.session_state['dataset_bundle'] = bundle
    reset_dataset_filters()


def restore_demo():
    st.session_state.pop('dataset_bundle', None)
    for key in ('shared_upload_survey', 'shared_upload_discovery', 'shared_upload_contacts'):
        st.session_state.pop(key, None)
    reset_dataset_filters()


def migrate_dataset_state():
    """Preserve an existing upload after upgrading an already-open session."""
    if 'dataset_bundle' not in st.session_state:
        if 'opportunity_upload' in st.session_state:
            apply_bundle(st.session_state['opportunity_upload'])
        elif 'uploaded_survey' in st.session_state:
            apply_bundle(from_market_upload(st.session_state['uploaded_survey']))
    for key in ('opportunity_upload', 'uploaded_survey', 'uploaded_survey_name', 'opportunity_use_demo'):
        st.session_state.pop(key, None)


def market_bundle(bundle):
    return SurveyData(bundle.survey, bundle.validation, bundle.synthetic)


@st.dialog('Manage data', width='large')
def manage_data_dialog():
    st.write('Load one collection of evidence for both dashboards. The survey powers Market Intelligence and Opportunity Intelligence; optional discovery assessments enrich Opportunity Intelligence.')
    st.caption('Survey required · Discovery optional · Contacts/consent optional. Files are validated together before replacing the active data for this session. Uploaded surveys are never joined to synthetic discovery records.')
    st.caption('Upload original template CSVs. A Market Intelligence export can be reloaded as survey data; an Opportunity Intelligence ranking export has different columns and cannot be used as a survey.')
    survey = st.file_uploader('Survey CSV — required', type='csv', key='shared_upload_survey')
    discovery = st.file_uploader('Discovery CSV — optional', type='csv', key='shared_upload_discovery')
    contacts = st.file_uploader('Contacts and consent CSV — optional, restricted', type='csv', key='shared_upload_contacts')
    st.caption('Contact details are used to check permission and are excluded from analytical exports.')
    if survey is not None:
        try:
            candidate = load_uploaded_opportunities(survey.getvalue(), discovery.getvalue() if discovery else None,
                                                   contacts.getvalue() if contacts else None)
        except SurveyLoadError as exc:
            st.error(str(exc))
            if exc.issues:
                st.dataframe(pd.DataFrame([asdict(i) for i in exc.issues]), hide_index=True)
        else:
            st.success(f'{len(candidate.survey)} valid survey responses · {len(candidate.discovery)} discovery assessments · {len(candidate.validation.warnings)} warnings')
            if st.button('Use data in both dashboards', type='primary', on_click=apply_bundle, args=(candidate,)):
                st.rerun()
    if st.button('Restore synthetic demo for both dashboards', on_click=restore_demo):
        st.rerun()
