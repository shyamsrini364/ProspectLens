"""Check descriptive summaries and the chart's fixed denominator-based scale."""
import unittest

from src.market_charts import survey_bar_chart, survey_bar_summary, outcome_column_chart, label
from src.market_metrics import frequency, filter_survey
from src.market_style import theme_tokens
from test_market_intelligence import fixture_frame


class SurveyBarTests(unittest.TestCase):
    def test_outcome_columns_preserve_rank_values_and_full_hover_labels(self):
        rows=frequency(fixture_frame(),'desired_outcome').sort_values('count',ascending=False,kind='stable')
        for mode in ('light','dark'):
            tokens=theme_tokens(mode)
            fig=outcome_column_chart(rows,tokens)
            self.assertEqual(list(fig.data[0].y),rows['percentage'].tolist())
            self.assertEqual(fig.layout.yaxis.range,(0,65)) # 50% maximum plus headroom.
            self.assertEqual(len(fig.data[0].x),len(rows))
            for row,hover in zip(rows.itertuples(),fig.data[0].customdata):
                self.assertEqual(list(hover),[label('desired_outcome',row.category),row.count,row.denominator,row.percentage])
            self.assertEqual(list(fig.data[0].marker.color).count(tokens['survey-iris']),2)
            self.assertIn('0.0%',fig.data[1].text)

    def test_filtered_hundred_percent_outcome_caps_axis_and_keeps_visible_label(self):
        frame=fixture_frame().iloc[:1]
        fig=outcome_column_chart(frequency(frame,'desired_outcome'),theme_tokens('dark'))
        self.assertEqual(fig.data[0].y[0],100)
        self.assertEqual(fig.data[1].text[0],'100.0%')
        self.assertFalse(fig.data[1].cliponaxis)
        self.assertEqual(fig.layout.yaxis.range,(0,100))

    def test_outcome_axis_follows_peak_without_normalising_values(self):
        rows=frequency(fixture_frame(),'desired_outcome')
        for peak,expected in [(20,25),(40,50),(0,5)]:
            sample=rows.copy()
            sample['percentage']=0.0
            sample.loc[0,'percentage']=peak
            fig=outcome_column_chart(sample,theme_tokens('light'))
            self.assertEqual(fig.layout.yaxis.range,(0,expected))
            self.assertEqual(max(fig.data[0].y),peak)
        missing=frequency(fixture_frame().iloc[:0],'desired_outcome')
        self.assertEqual(outcome_column_chart(missing,theme_tokens('dark')).layout.yaxis.range,(0,5))

    def test_concerns_use_distinct_response_denominator_and_iris_highlight(self):
        rows=frequency(fixture_frame(),'ai_concerns').sort_values('count',ascending=False,kind='stable')
        tokens=theme_tokens('dark')
        fig=survey_bar_chart(rows,'ai_concerns',tokens,highlight_token='survey-iris')
        self.assertEqual(list(fig.data[1].x),rows['percentage'].tolist())
        self.assertTrue(all(c[2]==2 for c in fig.data[1].customdata))
        self.assertEqual(sum(fig.data[1].x),150) # Multi-select remains per respondent, not per selection.
        self.assertEqual(list(fig.data[1].marker.color).count(tokens['survey-iris']),3)
        self.assertEqual(fig.layout.xaxis2.range,(0,100))

    def test_all_categories_values_and_order_preserved(self):
        for field,ordered in [('pain_points',False),('employee_band',True)]:
            table=frequency(fixture_frame(),field)
            rows=table if ordered else table.sort_values('count',ascending=False,kind='stable')
            for mode in ('light','dark'):
                fig=survey_bar_chart(table,field,theme_tokens(mode),ordered)
                self.assertEqual(list(fig.data[0].x),[100]*len(rows))
                self.assertEqual(list(fig.data[1].x),rows['percentage'].tolist())
                self.assertEqual(fig.layout.xaxis.range,(0,100))
                self.assertEqual(fig.layout.xaxis2.range,(0,100))
                self.assertEqual([c[1] for c in fig.data[1].customdata],rows['count'].tolist())
                self.assertTrue(any(x==0 for x in fig.data[1].x))

    def test_summary_reports_ties_and_updates_after_filtering(self):
        frame=fixture_frame()
        text=survey_bar_summary(frequency(frame,'pain_points'),'pain_points')
        self.assertIn('Joint highest',text)
        self.assertIn('2 of 3 answered responses (66.7%) each',text)
        selected=filter_survey(frame,{'ai_adoption':['regular_multiple']})
        text=survey_bar_summary(frequency(selected,'pain_points'),'pain_points')
        self.assertIn('1 of 1 answered responses (100.0%) each',text)
        tokens=theme_tokens('light')
        fig=survey_bar_chart(frequency(selected,'pain_points'),'pain_points',tokens)
        self.assertEqual(list(fig.data[1].marker.color).count(tokens['survey-highlight']),2)

    def test_missing_answers_do_not_produce_a_top_category_claim(self):
        table=frequency(fixture_frame().iloc[:0],'employee_band')
        self.assertEqual(survey_bar_summary(table,'employee_band'),'No recorded answers in this selection.')
