"""Check AI visualisations against hand-counted examples and independent CSV counts."""

from collections import Counter
import csv
from pathlib import Path
import unittest

import pandas as pd

from src.market_charts import ai_adoption_donut, ai_adoption_heatmap, label
from src.market_data import load_survey
from src.market_metrics import MISSING, ai_adoption_by_industry, filter_survey
from src.market_style import theme_tokens
from src.schema import SURVEY_LABELS
from test_market_intelligence import fixture_frame

CSV = Path(__file__).resolve().parents[1] / 'data/synthetic/survey_responses.csv'


class AIAdoptionTests(unittest.TestCase):
    def test_sort_uses_answered_count_not_total_rows(self):
        frame=fixture_frame()
        # Retail has more submissions, but only two answered S14; healthcare has three.
        extra=frame.iloc[[2,5,5]].copy()
        extra['response_id']=['extra1','extra2','extra3']
        table=ai_adoption_by_industry(pd.concat([frame,extra],ignore_index=True))
        summary=table.drop_duplicates('industry')
        self.assertEqual(summary['industry'].tolist(),['healthcare_allied','retail_ecommerce',MISSING])
        self.assertEqual(summary['denominator'].tolist(),[3,2,1])
        self.assertEqual(summary['group_total'].tolist(),[3,5,1])
        for _,rows in table.groupby('industry',sort=False):
            self.assertEqual(rows['category'].tolist(),list(SURVEY_LABELS['ai_adoption']))
            self.assertAlmostEqual(rows['percentage'].sum(),100)

    def test_zero_missing_and_unsure_have_distinct_meanings(self):
        frame=fixture_frame()
        frame.loc[frame['industry'].eq('retail_ecommerce'),'ai_adoption']=None
        table=ai_adoption_by_industry(frame)
        retail=table.loc[table['industry'].eq('retail_ecommerce')]
        self.assertTrue(retail['denominator'].eq(0).all())
        self.assertTrue(retail['percentage'].isna().all())
        health=table.loc[table['industry'].eq('healthcare_allied')].set_index('category')
        self.assertEqual(health.loc['unsure','percentage'],50)
        self.assertEqual(health.loc['not_using','percentage'],0)
        fig=ai_adoption_heatmap(table,theme_tokens('dark'))
        self.assertEqual(sum(a.text=='N/A' for a in fig.layout.annotations),5)
        self.assertTrue(any(a.text=='0%' for a in fig.layout.annotations))
        self.assertTrue(any('n=0' in y and 'no answers' in y for y in fig.data[0].y))

    def test_sample_size_boundary_and_row_labels(self):
        frame=pd.concat([fixture_frame().iloc[[0]]]*5,ignore_index=True)
        frame['response_id']=[f'unique{i}' for i in range(5)]
        for n in (4,5):
            table=ai_adoption_by_industry(frame.iloc[:n])
            chart=ai_adoption_heatmap(table,theme_tokens('dark'))
            self.assertIn(f'n={n}',chart.data[0].y[0])
            self.assertEqual('small sample' in chart.data[0].y[0],n<5)

    def test_cells_hover_and_donuts_use_the_same_counts(self):
        table=ai_adoption_by_industry(fixture_frame())
        for mode in ('light','dark'):
            heat=ai_adoption_heatmap(table,theme_tokens(mode))
            self.assertEqual(heat.data[0].type,'heatmap')
            self.assertEqual((heat.data[0].zmin,heat.data[0].zmax),(0,100))
            for i,(industry,rows) in enumerate(table.groupby('industry',sort=False)):
                donut=ai_adoption_donut(rows,theme_tokens(mode))
                self.assertEqual(list(donut.data[0].values),rows['count'].tolist())
                for j,row in enumerate(rows.itertuples()):
                    self.assertAlmostEqual(heat.data[0].z[i][j],row.count/row.denominator*100)
                    self.assertEqual(list(heat.data[0].customdata[i][j]),[
                        label('industry',industry),label('ai_adoption',row.category),row.count,
                        row.denominator,f'{row.percentage:.1f}%',row.missing])

    def test_zero_denominator_donut_does_not_invent_a_slice(self):
        table=ai_adoption_by_industry(fixture_frame().iloc[[5]])
        donut=ai_adoption_donut(table,theme_tokens('dark'))
        self.assertEqual(len(donut.data),0)
        self.assertIn('N/A',donut.layout.annotations[0].text)

    @unittest.skipUnless(CSV.exists(),'Local synthetic survey CSV is not present')
    def test_every_csv_cell_matches_independent_counts_before_and_after_filters(self):
        with CSV.open(encoding='utf-8-sig',newline='') as handle:
            raw=list(csv.DictReader(handle))
        frame=load_survey().frame
        cases=[{}, {'industry':['professional_services']}, {'employee_band':['solo']},
               {'ai_adoption':['unsure','not_using']},
               {'industry':['retail_ecommerce'],'employee_band':['2_5']}]
        for filters in cases:
            expected=[r for r in raw if all(r[field] in choices for field,choices in filters.items())]
            table=ai_adoption_by_industry(filter_survey(frame,filters))
            heat=ai_adoption_heatmap(table,theme_tokens('dark'))
            for i,(industry,rows) in enumerate(table.groupby('industry',sort=False)):
                source=[r for r in expected if (r['industry'] or MISSING)==industry]
                counts=Counter(r['ai_adoption'] for r in source if r['ai_adoption'])
                denominator=sum(counts.values())
                for j,row in enumerate(rows.itertuples()):
                    with self.subTest(filters=filters,industry=industry,category=row.category):
                        self.assertEqual(row.count,counts[row.category])
                        self.assertEqual(row.denominator,denominator)
                        self.assertEqual(row.missing,len(source)-denominator)
                        if denominator:
                            self.assertAlmostEqual(heat.data[0].z[i][j],100*counts[row.category]/denominator)
                        else:
                            self.assertTrue(pd.isna(heat.data[0].z[i][j]))
