"""Small hand-counted examples test dashboard maths independently of generation."""

import csv
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest

import pandas as pd

from src.data_validation import validate_dataset
from src.market_data import SurveyLoadError, export_survey_csv, load_survey, load_uploaded_survey
from src.market_metrics import MISSING, filter_options, filter_survey, frequency, market_kpis, quality_summary
from src.market_charts import ai_stacked_chart, bar_chart, pain_heatmap
from src.market_style import theme_tokens
from src.schema import SURVEY_COLUMNS


def raw_rows():
    choices = [
        dict(industry="retail_ecommerce",employee_band="solo",pain_points='["manual_data_entry","sales_followup","manual_data_entry"]',
             primary_pain_point="manual_data_entry",impact_rating="5",ai_adoption="regular_multiple",followup_interest="yes",ai_concerns='["cost_roi","privacy_security"]',desired_outcome="save_time"),
        dict(industry="retail_ecommerce",employee_band="2_5",pain_points='["sales_followup"]',primary_pain_point="sales_followup",
             impact_rating="4",ai_adoption="limited_tasks",followup_interest="maybe",ai_concerns='["none"]',desired_outcome="reduce_costs"),
        dict(industry="healthcare_allied",employee_band="solo",pain_points="[]",impact_rating="2",ai_adoption="experimented",followup_interest="not_now"),
        dict(industry="healthcare_allied",employee_band="6_20",pain_points="",impact_rating="",ai_adoption="unsure",followup_interest="yes"),
        dict(industry="",employee_band="",pain_points='["manual_data_entry"]',primary_pain_point="manual_data_entry",impact_rating="1",ai_adoption="not_using",followup_interest=""),
        dict(industry="retail_ecommerce",employee_band="solo",pain_points="",impact_rating="",ai_adoption="",followup_interest="maybe"),
    ]
    rows=[]
    for i,values in enumerate(choices):
        row=dict.fromkeys(SURVEY_COLUMNS,"")
        row.update(response_id=f"R{i}",prospect_id=f"P{i}",dataset_version="1.0",questionnaire_version="1.0",**values)
        rows.append(row)
    return rows


def fixture_frame():
    result=validate_dataset(raw_rows())
    result.require_valid()
    return pd.DataFrame(result.survey,columns=SURVEY_COLUMNS)


class MarketMetricTests(unittest.TestCase):
    def setUp(self):
        self.frame=fixture_frame()

    def test_hand_calculated_kpis(self):
        k=market_kpis(self.frame)
        self.assertEqual((k['responses'],k['industries'],k['industry_missing']),(6,2,1))
        self.assertEqual((k['high_impact'].count,k['high_impact'].denominator,k['high_impact'].missing),(2,4,2))
        self.assertEqual(k['high_impact'].percentage,50)
        self.assertEqual(k['using_ai'].percentage,40) # 2/5; experimented/unsure are not use.
        self.assertEqual(k['followup'].percentage,40) # 2/5; maybe excluded from numerator.
        self.assertEqual((k['followup_maybe'],k['ai_unsure']),(2,1))

    def test_repeated_prospect_is_still_separate_submission(self):
        self.frame.loc[1,'prospect_id']=self.frame.loc[0,'prospect_id']
        k=market_kpis(self.frame)
        self.assertEqual((k['responses'],k['prospects']),(6,5))

    def test_multiselect_counts_distinct_responses_before_explosion(self):
        table=frequency(self.frame,'pain_points').set_index('category')
        self.assertEqual(table.loc['manual_data_entry','count'],2)
        self.assertEqual(table.loc['sales_followup','count'],2)
        self.assertEqual(table.loc['manual_data_entry','denominator'],3)
        self.assertAlmostEqual(table.loc['manual_data_entry','percentage'],200/3)
        self.assertGreater(table['percentage'].sum(),100)
        self.assertEqual(table['count'].sum(),4) # duplicate selection never adds another respondent.

    def test_no_concerns_is_answered_and_empty_lists_are_missing(self):
        table=frequency(self.frame,'ai_concerns').set_index('category')
        self.assertEqual(table.loc['none','count'],1)
        self.assertTrue(table['denominator'].eq(2).all())
        self.assertTrue(table['missing'].eq(4).all())

    def test_outcomes_are_single_select(self):
        table=frequency(self.frame,'desired_outcome')
        self.assertEqual(table['count'].sum(),2)
        self.assertEqual(table['percentage'].sum(),100)

    def test_or_within_and_across_filters_and_no_input_mutation(self):
        original=self.frame.copy(deep=True)
        selected=filter_survey(self.frame,{'industry':['retail_ecommerce','healthcare_allied'],'employee_band':['solo'],
                                         'primary_pain_point':['manual_data_entry'],'ai_adoption':['regular_multiple']})
        self.assertEqual(selected['response_id'].tolist(),['R0'])
        pd.testing.assert_frame_equal(original,self.frame)
        self.assertEqual(len(filter_survey(self.frame,{'industry':[]})),6)

    def test_missing_filter_keeps_missing_distinct_from_unsure(self):
        self.assertEqual(filter_survey(self.frame,{'ai_adoption':[MISSING]})['response_id'].tolist(),['R5'])
        self.assertEqual(filter_survey(self.frame,{'ai_adoption':['unsure']})['response_id'].tolist(),['R3'])
        self.assertIn(MISSING,filter_options(self.frame,'industry'))

    def test_filter_applies_to_all_six_chart_tables(self):
        selected=filter_survey(self.frame,{'industry':['retail_ecommerce'],'employee_band':['solo']})
        self.assertEqual(market_kpis(selected)['responses'],2)
        for field,group in [('pain_points',None),('pain_points','industry'),('ai_adoption','industry'),
                            ('employee_band',None),('desired_outcome',None),('ai_concerns',None)]:
            with self.subTest(field=field,group=group):
                table=frequency(selected,field,group)
                self.assertTrue(table['group_total'].eq(2).all())
                self.assertTrue(table['denominator'].eq(2 if field=='employee_band' else 1).all())

    def test_group_denominators_missing_industry_and_small_samples(self):
        table=frequency(self.frame,'pain_points','industry')
        retail=table.loc[table['industry'].eq('retail_ecommerce')]
        self.assertTrue(retail['denominator'].eq(2).all())
        self.assertTrue(retail['missing'].eq(1).all())
        self.assertTrue(retail['small_sample'].all())
        health=table.loc[table['industry'].eq('healthcare_allied')]
        self.assertTrue(health['percentage'].isna().all())
        self.assertIn(MISSING,table['industry'].tolist())

    def test_ai_stacks_total_one_hundred_per_answered_group(self):
        table=frequency(self.frame,'ai_adoption','industry')
        for _,group in table.groupby('industry'):
            self.assertAlmostEqual(group['percentage'].sum(),100)
        health=table.loc[table['industry'].eq('healthcare_allied')].set_index('category')
        self.assertEqual(health.loc['unsure','percentage'],50)

    def test_empty_and_all_missing_are_unavailable_not_zero_percent(self):
        for frame in [self.frame.iloc[0:0],self.frame.iloc[[5]]]:
            values=market_kpis(frame)
            self.assertIsNone(values['using_ai'].percentage)
            table=frequency(frame,'pain_points')
            self.assertTrue(table['percentage'].isna().all())
        self.assertTrue(frequency(self.frame.iloc[0:0],'pain_points','industry').empty)
        self.assertEqual(quality_summary(self.frame)['Missing'].sum(),20)

    def test_small_sample_boundary_five_is_not_flagged(self):
        rows=pd.concat([self.frame.iloc[[0]]]*5,ignore_index=True)
        rows['response_id']=[f'T{i}' for i in range(5)]
        self.assertFalse(frequency(rows,'pain_points')['small_sample'].any())

    def test_figures_use_aggregated_values_in_both_palettes(self):
        for mode in ['light','dark']:
            tokens=theme_tokens(mode)
            table=frequency(self.frame,'pain_points')
            chart=bar_chart(table,'pain_points',tokens)
            self.assertEqual(list(chart.data[0].x),table.sort_values('count',ascending=False,kind='stable')['percentage'].tolist())
            self.assertEqual(chart.layout.paper_bgcolor,tokens['surface'])
            heat=pain_heatmap(frequency(self.frame,'pain_points','industry'),tokens)
            self.assertEqual(len(heat.data[0].z),3)
            ai=ai_stacked_chart(frequency(self.frame,'ai_adoption','industry'),tokens)
            self.assertEqual(len(ai.data),5)


class MarketLoaderTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path=Path(self.temp.name)/'survey.csv'

    def write(self,rows=None,columns=SURVEY_COLUMNS):
        with self.path.open('w',encoding='utf-8',newline='') as handle:
            writer=csv.DictWriter(handle,fieldnames=columns)
            writer.writeheader()
            writer.writerows(raw_rows() if rows is None else rows)

    def test_valid_loader_reuses_typed_validator_rows(self):
        self.write()
        loaded=load_survey(self.path,None)
        self.assertEqual(loaded.frame.loc[0,'impact_rating'],5)
        self.assertIsInstance(loaded.frame.loc[0,'pain_points'],list)
        self.assertTrue(loaded.validation.warnings)
        self.assertFalse(loaded.synthetic_verified)

    def test_export_filtered_rows_round_trip_through_validator(self):
        frame=filter_survey(fixture_frame(),{'industry':['retail_ecommerce']})
        frame.loc[0,'additional_comments']='Quoted "detail", with a comma\nand Unicode: café'
        frame['email']='must-not-export@example.invalid'
        self.path.write_bytes(export_survey_csv(frame))
        loaded=load_survey(self.path,None)
        self.assertEqual(loaded.frame['response_id'].tolist(),['R0','R1','R5'])
        self.assertEqual(loaded.frame.loc[0,'additional_comments'],frame.loc[0,'additional_comments'])
        self.assertEqual(loaded.frame.loc[0,'pain_points'],frame.loc[0,'pain_points'])
        self.assertNotIn('must-not-export',self.path.read_text(encoding='utf-8-sig'))
        self.assertEqual(loaded.frame.loc[0,'impact_rating'],5)

    def test_export_preserves_missing_and_empty_lists(self):
        rows=list(csv.DictReader(io.StringIO(export_survey_csv(fixture_frame()).decode('utf-8-sig'))))
        self.assertEqual(rows[2]['pain_points'],'[]')
        self.assertEqual(rows[3]['pain_points'],'')
        self.assertEqual(rows[3]['impact_rating'],'')
        self.assertEqual(rows[0]['impact_rating'],'5')

    def test_empty_export_has_exact_header_and_no_rows(self):
        self.path.write_bytes(export_survey_csv(fixture_frame().iloc[:0]))
        self.assertTrue(load_survey(self.path,None).frame.empty)
        self.assertEqual(next(csv.reader(io.StringIO(self.path.read_text(encoding='utf-8-sig')))),SURVEY_COLUMNS)

    def test_upload_reuses_validation_in_memory_without_synthetic_claim(self):
        payload=export_survey_csv(fixture_frame())
        loaded=load_uploaded_survey(payload)
        self.assertEqual(len(loaded.frame),6)
        self.assertFalse(loaded.synthetic_verified)
        self.assertTrue(loaded.validation.warnings)
        self.assertEqual(list(Path(self.temp.name).iterdir()),[])
        self.assertTrue(load_uploaded_survey(export_survey_csv(fixture_frame().iloc[:0])).frame.empty)

    def test_upload_rejects_wrong_headers_bad_rows_and_contact_files(self):
        for payload in [b'email,contact_name\nuser@example.invalid,Name\n', b'broken\n',
                        export_survey_csv(fixture_frame()).replace(b'retail_ecommerce',b'unknown_industry'),
                        (','.join(SURVEY_COLUMNS)+'\nonly,three,cells\n').encode()]:
            with self.subTest(payload=payload[:40]):
                with self.assertRaises(SurveyLoadError) as context:
                    load_uploaded_survey(payload)
                self.assertTrue(context.exception.issues)

    def test_upload_encoding_and_size_limit(self):
        with self.assertRaisesRegex(SurveyLoadError,'UTF-8'):
            load_uploaded_survey(b'\xff\xfe')
        with self.assertRaisesRegex(SurveyLoadError,'5 MB'):
            load_uploaded_survey(b'x'*(5*1024*1024+1))

    def test_exact_header_enforced(self):
        self.write([],list(reversed(SURVEY_COLUMNS)))
        with self.assertRaises(SurveyLoadError) as context:
            load_survey(self.path,None)
        self.assertEqual(context.exception.issues[0].row_id,'header')

    def test_invalid_rating_category_json_and_duplicate_ids_block_analysis(self):
        for key,value in [('impact_rating','6'),('industry','unrecognised'),('pain_points','not json'),('response_id','R1')]:
            with self.subTest(key=key):
                rows=raw_rows()
                rows[0][key]=value
                self.write(rows)
                with self.assertRaises(SurveyLoadError):
                    load_survey(self.path,None)

    def test_missing_file_has_actionable_error(self):
        with self.assertRaisesRegex(SurveyLoadError,'missing'):
            load_survey(self.path,None)

    def test_header_only_file_is_valid_empty_data(self):
        self.write([])
        self.assertTrue(load_survey(self.path,None).frame.empty)

    def test_manifest_verification_and_changed_csv(self):
        self.write()
        manifest=Path(self.temp.name)/'generation_manifest.json'
        manifest.write_text(json.dumps({'disclaimer':'SYNTHETIC DATA - NOT REAL MARKET FINDINGS',
                           'sha256':{self.path.name:hashlib.sha256(self.path.read_bytes()).hexdigest()}}),encoding='utf-8')
        self.assertTrue(load_survey(self.path,manifest).synthetic_verified)
        rows=raw_rows()
        rows[0]['impact_rating']='4'
        self.write(rows)
        with self.assertRaisesRegex(SurveyLoadError,'manifest'):
            load_survey(self.path,manifest)

    def test_malformed_or_missing_manifest_is_clear_error(self):
        self.write()
        manifest=Path(self.temp.name)/'generation_manifest.json'
        for content in ['{', '[]', '{"sha256":[]}']:
            manifest.write_text(content,encoding='utf-8')
            with self.assertRaises(SurveyLoadError):
                load_survey(self.path,manifest)
        with self.assertRaises(SurveyLoadError):
            load_survey(self.path,manifest.with_name('absent.json'))


if __name__ == '__main__':
    unittest.main()
