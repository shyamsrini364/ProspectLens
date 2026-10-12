"""Rendering preserves every aggregated CSV count in either reporting mode."""
import unittest
import pandas as pd
from src.opportunity_data import load_opportunities
from src.opportunity_metrics import discovery_trend
from src.opportunity_charts import trend_chart
from src.market_style import theme_tokens


class TrendChartTests(unittest.TestCase):
    def test_csv_values_unchanged_for_both_groupings_modes_themes_and_filters(self):
        data=load_opportunities()
        for ids in (set(data.survey.prospect_id),set(data.survey.prospect_id.iloc[:10])):
            for period in ('Weekly','Monthly'):
                counts,missing=discovery_trend(data.survey,data.discovery,ids,period,False)
                for cumulative in (False,True):
                    table,excluded=discovery_trend(data.survey,data.discovery,ids,period,cumulative)
                    original=table.copy(deep=True)
                    self.assertEqual(excluded,missing)
                    expected=counts.iloc[:,1:].cumsum() if cumulative else counts.iloc[:,1:]
                    pd.testing.assert_frame_equal(table.iloc[:,1:],expected)
                    for mode in ('light','dark'):
                        tokens=theme_tokens(mode)
                        fig=trend_chart(table,tokens,cumulative,period)
                        self.assertEqual(len(fig.data),3)
                        for trace,name,color in zip(fig.data,table.columns[1:],('primary','survey-highlight','ai-experimented')):
                            self.assertEqual(list(trace.y),table[name].tolist())
                            self.assertEqual(len(trace.x),len(table))
                            self.assertEqual(trace.line.shape,'linear')
                            self.assertEqual(trace.mode,'lines+markers')
                            self.assertEqual(trace.line.color,tokens[color])
                            self.assertIn(name,trace.hovertemplate)
                            self.assertIn('%{y:,.0f}',trace.hovertemplate)
                            dates=pd.DatetimeIndex(trace.x)
                            self.assertTrue(all(dates.dayofweek==6) if period=='Weekly' else all(dates.is_month_end))
                        pd.testing.assert_frame_equal(table,original)

    def test_hover_period_and_end_of_month_position(self):
        table=pd.DataFrame({'period':[pd.Timestamp('2026-02-01')],
                            'Survey responses':[7],'High-impact survey responses':[3],'Discovery assessments':[2]})
        fig=trend_chart(table,theme_tokens('dark'),True,'Monthly')
        self.assertEqual(fig.data[0].x[0],pd.Timestamp('2026-02-28'))
        self.assertEqual(fig.data[0].customdata[0],'01 Feb 2026 – 28 Feb 2026')
        self.assertIn('Cumulative total at period end',fig.data[0].hovertemplate)
        self.assertIn('New observations in period',trend_chart(table,theme_tokens('dark'),False,'Monthly').data[0].hovertemplate)
