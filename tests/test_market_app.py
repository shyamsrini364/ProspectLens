"""Exercise the actual Streamlit script, including widget reruns and failures."""

from pathlib import Path
import unittest
from unittest.mock import patch

import pandas as pd
from streamlit.testing.v1 import AppTest

from src.data_validation import validate_dataset
from src.market_data import SurveyData, SurveyLoadError
from src.schema import SURVEY_COLUMNS
from test_market_intelligence import raw_rows

APP = Path(__file__).resolve().parents[1] / 'app.py'


def loaded(rows):
    result=validate_dataset(rows)
    result.require_valid()
    return SurveyData(pd.DataFrame(result.survey,columns=SURVEY_COLUMNS),result,True)


class MarketAppTests(unittest.TestCase):
    def setUp(self):
        self.loader=patch('src.market_ui.load_survey',return_value=loaded(raw_rows())).start()
        self.addCleanup(patch.stopall)

    def start(self):
        app=AppTest.from_file(str(APP),default_timeout=30).run()
        self.assertFalse(app.exception)
        return app

    def test_initial_render_has_five_metrics_six_charts_and_opportunity_navigation(self):
        app=self.start()
        self.assertEqual(len(app.metric),5)
        self.assertEqual(app.metric[0].value,'6')
        self.assertEqual(app.metric[2].value,'50.0%')
        self.assertEqual(len(app.get('plotly_chart')),6)
        self.assertFalse(next(b for b in app.button if 'Opportunity' in b.label).disabled)

    def test_all_four_filters_update_metrics_charts_and_tables(self):
        app=self.start()
        choices={'industry':['retail_ecommerce'],'employee_band':['solo'],
                 'primary_pain_point':['manual_data_entry'],'ai_adoption':['regular_multiple']}
        for field,values in choices.items():
            app.multiselect(key=f'filter_{field}').set_value(values).run()
            self.assertFalse(app.exception)
        self.assertEqual(app.metric[0].value,'1')
        self.assertEqual(app.metric[2].value,'100.0%')
        self.assertEqual(len(app.get('plotly_chart')),6)
        for table in app.dataframe:
            if 'Filtered group responses' in table.value:
                self.assertTrue(table.value['Filtered group responses'].eq(1).all())
        self.assertTrue(any('Small subgroup' in warning.value for warning in app.warning))
        next(b for b in app.button if b.label=='Reset filters').click().run()
        self.assertEqual(app.metric[0].value,'6')
        self.assertTrue(all(not x.value for x in app.multiselect))

    def test_no_matching_rows_and_reset(self):
        app=self.start()
        app.multiselect(key='filter_industry').set_value(['retail_ecommerce']).run()
        app.multiselect(key='filter_ai_adoption').set_value(['unsure']).run()
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[0].value,'0')
        self.assertEqual(app.metric[2].value,'—')
        self.assertEqual(len(app.get('plotly_chart')),0)
        self.assertTrue(any('No responses match' in item.value for item in app.info))
        next(b for b in app.button if b.label=='Clear all filters').click().run()
        self.assertEqual(app.metric[0].value,'6')

    def test_header_only_dataset_shows_empty_state(self):
        self.loader.return_value=loaded([])
        app=self.start()
        self.assertEqual(app.metric[0].value,'0')
        self.assertTrue(any('valid header' in item.value for item in app.info))

    def test_all_optional_answers_missing(self):
        row=dict.fromkeys(SURVEY_COLUMNS,'')
        row.update(response_id='R0',prospect_id='P0',dataset_version='1.0')
        self.loader.return_value=loaded([row])
        app=self.start()
        self.assertEqual(app.metric[2].value,'—')
        self.assertEqual(len(app.get('plotly_chart')),1) # AI heatmap explicitly shows N/A cells.
        self.assertEqual(sum('No recorded answers for this question' in item.value for item in app.info),6)

    def test_ai_view_selector_preserves_metrics_and_filters(self):
        app=self.start()
        self.assertEqual(app.radio(key='ai_visualisation').value,'Heatmap')
        before=[metric.value for metric in app.metric]
        app.radio(key='ai_visualisation').set_value('Donut charts').run()
        self.assertFalse(app.exception)
        self.assertEqual(len(app.get('plotly_chart')),8) # Five other charts + three industries.
        self.assertEqual([metric.value for metric in app.metric],before)
        app.multiselect(key='filter_industry').set_value(['retail_ecommerce']).run()
        self.assertEqual(app.metric[0].value,'3')
        self.assertEqual(len(app.get('plotly_chart')),6)
        app.radio(key='ai_visualisation').set_value('Heatmap').run()
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[0].value,'3')
        self.assertEqual(app.multiselect(key='filter_industry').value,['retail_ecommerce'])

    def test_validation_failure_stops_before_metrics(self):
        self.loader.side_effect=SurveyLoadError('Survey validation failed. Correct the listed issues before analysis.')
        app=self.start()
        self.assertIn('validation failed',app.error[0].value)
        self.assertEqual(len(app.metric),0)

    def test_missing_prerequisite_does_not_generate_data(self):
        self.loader.side_effect=SurveyLoadError('Survey dataset is missing. Complete synthetic dataset generation before opening this view.')
        app=self.start()
        self.assertIn('dataset is missing',app.error[0].value)
        self.assertEqual(len(app.get('plotly_chart')),0)

    def test_uploaded_session_replaces_demo_without_synthetic_label(self):
        data=loaded(raw_rows()[:2])
        data.synthetic_verified=False
        app=AppTest.from_file(str(APP),default_timeout=30)
        app.session_state['uploaded_survey']=data
        app.run()
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[0].value,'2')
        self.assertTrue(any('Uploaded survey' in caption.value for caption in app.caption))
        self.assertFalse(any('fingerprint verified' in caption.value for caption in app.caption))
        self.loader.assert_not_called()

    def test_upload_action_opens_dialog_even_when_demo_is_missing(self):
        self.loader.side_effect=SurveyLoadError('Survey dataset is missing.')
        app=self.start()
        app.button(key='menu_upload').click().run()
        self.assertFalse(app.exception)
        self.assertEqual(len(app.get('file_uploader')),3)


if __name__=='__main__':
    unittest.main()
