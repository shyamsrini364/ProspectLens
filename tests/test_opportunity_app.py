"""Run both actual Streamlit lenses with controlled evidence and widget reruns."""
import unittest
from pathlib import Path
from unittest.mock import patch
from streamlit.testing.v1 import AppTest

from src.market_data import SurveyData, SurveyLoadError
from test_opportunity import bundle, survey, discovery

APP=Path(__file__).resolve().parents[1]/'app.py'


class OpportunityAppTests(unittest.TestCase):
    def setUp(self):
        self.data=bundle([survey(),survey('R2','P2',industry='hospitality')],[discovery(),discovery('D2',workflow='W2')])
        self.loader=patch('src.opportunity_ui.load_opportunities',return_value=self.data).start()
        patch('src.market_ui.load_survey',return_value=SurveyData(self.data.survey,self.data.validation,False)).start()
        self.addCleanup(patch.stopall)

    def start(self):
        app=AppTest.from_file(str(APP),default_timeout=40)
        app.session_state['active_lens']='Opportunity Intelligence'
        app.run()
        self.assertFalse(app.exception)
        return app

    def test_navigation_preserves_market_lens(self):
        app=self.start()
        self.assertEqual(app.metric[0].value,'2')
        self.assertEqual(len(app.get('plotly_chart')),3)
        app.button(key='nav_Market Intelligence').click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[0].label,'Total survey responses')
        app.button(key='nav_Opportunity Intelligence').click().run()
        self.assertEqual(app.metric[0].label,'Businesses analysed')

    def test_all_six_filters_and_search_then_reset(self):
        app=self.start()
        values={'industry':'retail_ecommerce','employee_band':'2_5','primary_pain_point':'manual_data_entry',
                'ai_adoption':'limited_tasks','stage':'Discovery Enriched','score_band':'High'}
        for field,value in values.items():
            app.multiselect(key='opp_filter_'+field).set_value([value]).run()
            self.assertFalse(app.exception)
        self.assertEqual(app.metric[0].value,'1')
        self.assertEqual(app.metric[2].value,'1')
        app.text_input(key='opp_search').set_value('NO_MATCH').run()
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[0].value,'0')
        self.assertTrue(any('No businesses match' in x.value for x in app.info))
        app.button[ next(i for i,b in enumerate(app.button) if b.label=='Reset opportunity filters') ].click().run()
        self.assertEqual(app.metric[0].value,'2')

    def test_methodology_dialog_has_algorithm_and_config(self):
        app=self.start()
        app.button(key='opp_methodology').click().run()
        self.assertFalse(app.exception)
        text=' '.join(x.value for x in app.markdown)
        self.assertIn('0.60',text)
        self.assertIn('45%',text)
        self.assertTrue(app.get('dialog'))

    def test_business_dialog_preserves_all_assessments(self):
        app=self.start()
        app.button(key='opp_detail_open').click().run()
        self.assertFalse(app.exception)
        labels=[x.label for x in app.expander]
        self.assertTrue(any('D1' in x for x in labels))
        self.assertTrue(any('D2' in x for x in labels))

    def test_survey_only_and_missing_commercial_have_clear_states(self):
        self.loader.return_value=bundle()
        app=self.start()
        self.assertEqual(app.metric[4].value,'—')
        self.assertTrue(any('Survey-only evidence' in x.value for x in app.info))
        self.assertTrue(any('1 omitted' in x.value for x in app.caption))

    def test_empty_dataset_and_trend_controls(self):
        app=self.start()
        app.selectbox(key='opp_period').set_value('Monthly').run()
        app.radio(key='opp_trend_mode').set_value('New Per Period').run()
        self.assertFalse(app.exception)
        self.loader.return_value=bundle([])
        app.run()
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[0].value,'0')

    def test_validation_failure_stops_analytics_but_allows_upload(self):
        self.loader.side_effect=SurveyLoadError('Opportunity dataset validation failed.')
        app=self.start()
        self.assertEqual(len(app.metric),0)
        self.assertTrue(app.error)
        app.button(key='opp_load').click().run()
        self.assertFalse(app.exception)
        self.assertEqual(len(app.get('file_uploader')),3)

    def test_market_upload_does_not_mix_with_synthetic_discovery(self):
        app=AppTest.from_file(str(APP),default_timeout=40)
        app.session_state['active_lens']='Opportunity Intelligence'
        app.session_state['uploaded_survey']=SurveyData(self.data.survey,self.data.validation,False)
        app.run()
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[2].value,'0')
        self.loader.assert_not_called()

    def test_shared_bundle_survives_navigation_in_both_directions(self):
        app=AppTest.from_file(str(APP),default_timeout=40)
        app.session_state['dataset_bundle']=bundle([survey()],[discovery()])
        app.run()
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[0].value,'1')
        app.button(key='nav_Opportunity Intelligence').click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[0].value,'1')
        self.assertEqual(app.metric[2].value,'1')
        self.loader.assert_not_called()
        app.button(key='nav_Market Intelligence').click().run()
        self.assertEqual(app.metric[0].value,'1')

    def test_restore_demo_clears_shared_upload_and_both_filter_sets(self):
        app=AppTest.from_file(str(APP),default_timeout=40)
        app.session_state['dataset_bundle']=bundle([survey()])
        app.session_state['filter_industry']=['retail_ecommerce']
        app.session_state['opp_filter_industry']=['retail_ecommerce']
        app.run()
        app.button(key='market_manage_data').click().run()
        next(b for b in app.button if b.label=='Restore synthetic demo for both dashboards').click().run()
        app.run()  # Flush the full rerun requested from the dialog fragment.
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[0].value,'2')
        self.assertEqual(app.session_state['filter_industry'],[])
        self.assertEqual(app.session_state['opp_filter_industry'],[])
        app.button(key='nav_Opportunity Intelligence').click().run()
        self.assertEqual(app.metric[2].value,'1')

    def test_legacy_opportunity_upload_is_shared_with_market(self):
        app=AppTest.from_file(str(APP),default_timeout=40)
        app.session_state['opportunity_upload']=bundle([survey()],[discovery()])
        app.run()
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[0].value,'1')
        self.assertEqual(len(app.session_state['dataset_bundle'].discovery),1)
