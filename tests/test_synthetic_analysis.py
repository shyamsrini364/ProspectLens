"""Pandas examples: denominators, privacy boundary and file-derived reports."""

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from scripts.analyse_synthetic_data import (
    ai_by_business_size, complexity_vs_commercial, create_report,
    high_impact_contact_candidates, industry_high_impact,
    load_synthetic_files, missing_summary, pain_point_frequency, workload_comparison,
)
from scripts.generate_synthetic_data import FILENAMES, GenerationConfig, generate_datasets, write_datasets
from src.data_validation import contact_ready_response_ids, high_impact_prevalence, pain_point_prevalence, validate_dataset
from src.schema import COLUMNS


class SyntheticAnalysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = GenerationConfig()
        cls.data = generate_datasets(cls.config)
        cls.frames = {k: pd.DataFrame(v, columns=COLUMNS[k]) for k, v in cls.data.items()}
        cls.result = validate_dataset(**cls.data)

    def test_pain_counts_match_existing_distinct_response_helper(self):
        expected = pain_point_prevalence(self.result)
        table = pain_point_frequency(self.frames["survey"]).set_index("pain_point")
        for code, values in expected["categories"].items():
            self.assertEqual(table.loc[code, "respondents"], values["count"])
            self.assertEqual(table.loc[code, "answered_S06"], expected["denominator"])
            self.assertAlmostEqual(table.loc[code, "percentage"], values["percentage"])

    def test_filter_before_denominator(self):
        industry = "professional_services"
        expected = pain_point_prevalence(self.result, lambda r: r["industry"] == industry)
        actual = pain_point_frequency(self.frames["survey"], industry).set_index("pain_point")
        for code in expected["categories"]:
            self.assertEqual(actual.loc[code, "answered_S06"], expected["denominator"])
            self.assertEqual(actual.loc[code, "respondents"], expected["categories"][code]["count"])

    def test_duplicate_selections_count_once_and_empty_lists_excluded(self):
        frame = pd.DataFrame([{"response_id": "R1", "pain_points": '["manual_data_entry", "manual_data_entry"]'},
                              {"response_id": "R2", "pain_points": "[]"}, {"response_id": "R3", "pain_points": ""}])
        table = pain_point_frequency(frame).set_index("pain_point")
        self.assertEqual(table.loc["manual_data_entry", "respondents"], 1)
        self.assertEqual(table.loc["manual_data_entry", "answered_S06"], 1)

    def test_industry_denominators_match_validator_example(self):
        table = industry_high_impact(self.frames["survey"])
        for row in table.itertuples():
            expected = high_impact_prevalence(self.result, predicate=lambda r: r["industry"] == row.industry)
            self.assertEqual(row.answered_S09, expected["denominator"])
            self.assertEqual(row.high_impact, expected["count"])
            self.assertAlmostEqual(row.percentage, expected["percentage"])
            self.assertEqual(row.small_group_warning, row.answered_S09 < 5)

    def test_ai_counts_and_denominators_account_for_missing(self):
        survey = self.frames["survey"]
        table = ai_by_business_size(survey)
        self.assertEqual(int(table["respondents"].sum()), len(survey))
        for size, group in table.groupby("employee_band"):
            raw_size = "" if size == "missing" else size
            answered = survey.loc[survey["employee_band"].eq(raw_size) & survey["ai_adoption"].ne("")]
            self.assertTrue(group["answered_S14_in_size"].eq(len(answered)).all())
            self.assertTrue(group.loc[group["ai_adoption"].eq("missing"), "percentage"].isna().all())
            if len(answered):
                self.assertAlmostEqual(group["percentage"].sum(), 100)

    def test_contact_candidates_match_permission_helper_and_exclude_private_fields(self):
        expected = set(contact_ready_response_ids(self.result)) & {
            r["response_id"] for r in self.result.survey if r["impact_rating"] is not None and r["impact_rating"] >= 4}
        table = high_impact_contact_candidates(self.frames["survey"], self.frames["contacts"])
        self.assertEqual(set(table["response_id"]), expected)
        self.assertFalse(set(table.columns) & {"contact_name", "business_name", "email", "marketing_consent"})

    def test_no_contacts_gives_no_contact_candidates(self):
        contacts = pd.DataFrame(columns=COLUMNS["contacts"])
        self.assertTrue(high_impact_contact_candidates(self.frames["survey"], contacts).empty)

    def test_complexity_counts_assessments_including_unknowns(self):
        table = complexity_vs_commercial(self.frames["discovery"])
        self.assertEqual(int(table.iloc[:, 1:].to_numpy().sum()), 35)
        self.assertGreater(int(table.loc[table["implementation_complexity"].eq("unassessed")].iloc[:, 1:].to_numpy().sum()), 0)
        self.assertGreater(int(table["unknown"].sum()), 0)

    def test_weekly_baseline_unknowns_and_no_staff_multiplication(self):
        rows = pd.DataFrame([
            dict(assessment_id="D1", prospect_id="P1", activity_volume="40", volume_period="week", minutes_per_instance="15", reported_staff_hours_per_week="10", staff_count="3"),
            dict(assessment_id="D2", prospect_id="P1", activity_volume="40", volume_period="unknown", minutes_per_instance="15", reported_staff_hours_per_week="10", staff_count="3"),
            dict(assessment_id="D3", prospect_id="P2", activity_volume="", volume_period="week", minutes_per_instance="15", reported_staff_hours_per_week="", staff_count="1"),
            dict(assessment_id="D4", prospect_id="P2", activity_volume="40", volume_period="week", minutes_per_instance="15", reported_staff_hours_per_week="14", staff_count="3"),
        ])
        actual = workload_comparison(rows).set_index("assessment_id")
        self.assertEqual(actual.loc["D1", "modelled_staff_hours_per_week"], 10)
        self.assertTrue(pd.isna(actual.loc["D2", "modelled_staff_hours_per_week"]))
        self.assertTrue(pd.isna(actual.loc["D3", "modelled_staff_hours_per_week"]))
        self.assertTrue(actual.loc["D4", "review_difference_over_25_percent"])
        self.assertEqual(actual.loc["D4", "reported_staff_hours_per_week"], 14)

    def test_missing_summary_is_exact_blank_count(self):
        actual = missing_summary(self.frames).set_index(["dataset", "column"])
        for kind, rows in self.data.items():
            for column in COLUMNS[kind]:
                expected = sum(r[column] == "" for r in rows)
                if expected:
                    self.assertEqual(actual.loc[(kind, column), "blank_cells"], expected)
                else:
                    self.assertNotIn((kind, column), actual.index)

    def test_empty_denominators_do_not_become_zero_percent(self):
        survey = self.frames["survey"].iloc[0:0]
        self.assertTrue(pain_point_frequency(survey)["percentage"].isna().all())
        self.assertTrue(ai_by_business_size(survey)["percentage"].isna().all())
        self.assertTrue(industry_high_impact(survey).empty)
        self.assertEqual(int(complexity_vs_commercial(self.frames["discovery"].iloc[0:0]).iloc[:, 1:].to_numpy().sum()), 0)

    def test_saved_files_reloaded_and_report_reproducible(self):
        with tempfile.TemporaryDirectory() as path:
            write_datasets(self.data, path, self.config)
            frames, result, manifest = load_synthetic_files(path)
            self.assertTrue(result.valid)
            self.assertEqual(frames["survey"]["dataset_version"].iloc[0], "1.0")
            first = create_report(path)
            self.assertEqual(first, create_report(path))
            self.assertIn("150", first)
            self.assertIn("35 assessments cover 27", first)
            self.assertIn("NOT REAL MARKET FINDINGS", first)
            self.assertEqual(first.count("```python"), 5)
            for row in self.data["contacts"]:
                for column in ("contact_name", "business_name", "email"):
                    if row[column]:
                        self.assertNotIn(row[column], first)
            self.assertNotRegex(first.lower(), r"\btaa\b|agentdote|the ai architects")

    def test_report_uses_saved_values_not_regeneration(self):
        with tempfile.TemporaryDirectory() as path:
            data = generate_datasets(GenerationConfig(survey_count=12, discovery_count=3))
            for row in data["survey"]:
                row["industry"] = "education_training"
            write_datasets(data, path, GenerationConfig(survey_count=12, discovery_count=3))
            report = create_report(path)
            self.assertIn("| education_training | 12 | 100.00 |", report)
            self.assertIn("| survey | 12 | 12 |", report)

    def test_changed_csv_fingerprint_is_rejected(self):
        with tempfile.TemporaryDirectory() as path:
            write_datasets(self.data, path, self.config)
            survey_path = Path(path) / FILENAMES["survey"]
            survey_path.write_bytes(survey_path.read_bytes() + b"\n")
            with self.assertRaisesRegex(ValueError, "differs from the generation manifest"):
                load_synthetic_files(path)


if __name__ == "__main__":
    unittest.main()
