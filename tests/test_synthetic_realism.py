"""Meaningful consistency checks for the richer fictional business scenarios."""

import json
import re
import unittest

from scripts.generate_synthetic_data import GenerationConfig, generate_datasets
from scripts.synthetic_profiles import PAID_CATEGORIES, PROCESS, context_for, installed_tools
from src.data_validation import validate_dataset


class SyntheticRealismTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = generate_datasets()
        cls.survey = {row["prospect_id"]: row for row in cls.data["survey"]}

    def test_underused_software_is_installed_and_matches_quantity(self):
        for row in self.data["survey"]:
            if row["underused_software_names"]:
                installed = installed_tools(row, context_for(row))
                named = row["underused_software_names"].split("; ")
                self.assertTrue(set(named).issubset({v for k, v in installed.items() if k in PAID_CATEGORIES}))
                if row["subscription_underuse"] == "several":
                    self.assertGreaterEqual(len(named), 3)
                else:
                    self.assertIn(len(named), (1, 2))

    def test_discovery_uses_software_from_the_same_business(self):
        for row in self.data["discovery"]:
            survey = self.survey[row["prospect_id"]]
            self.assertEqual(json.loads(row["systems_involved"]), list(installed_tools(survey, context_for(survey)).values()))
            if json.loads(survey["business_systems"]) == ["none_paper"]:
                self.assertEqual(row["integration_capability"], "manual_only")
                self.assertIn(row["information_storage"], ("partly_paper", "unknown"))

    def test_no_confirmed_feasibility_when_integration_not_investigated(self):
        for row in self.data["discovery"]:
            if row["integration_capability"] in {"not_investigated", "unknown"}:
                self.assertIn(row["technical_feasibility"], {"unknown", ""})
            if row["integration_capability"] == "confirmed_api":
                self.assertIn("sample record", row["integration_evidence"])
            elif row["integration_capability"] == "not_investigated":
                self.assertIn("no interface test", row["integration_evidence"])

    def test_recommendations_respect_pilot_budget_and_feasibility(self):
        for row in self.data["discovery"]:
            if row["pilot_interest"] == "no":
                self.assertEqual(row["recommended_next_action"], "defer")
            if row["recommended_next_action"] == "pilot_proposal":
                self.assertEqual(row["pilot_interest"], "yes")
                self.assertIn(row["budget_status"], {"approved", "indicative"})
                self.assertIn(row["technical_feasibility"], {"medium", "high"})
            if row["budget_status"] in {"none", "not_discussed"}:
                self.assertEqual(row["indicative_budget"], "")
                self.assertNotEqual(row["commercial_potential"], "high")

    def test_success_metrics_have_matching_units_and_reduction_targets(self):
        units = set()
        for row in self.data["discovery"]:
            units.add(row["target_unit"])
            if row["current_baseline"]:
                if row["target_unit"] == "percent requiring rework":
                    self.assertLessEqual(float(row["current_baseline"]), 100)
                    self.assertIn("returned for correction", row["success_metric"])
                    counts = re.search(r"(\d+) of (\d+) sampled [^;]*? cases needed correction", row["impact_evidence"])
                    self.assertIsNotNone(counts)
                    self.assertAlmostEqual(float(row["current_baseline"]), round(100 * int(counts[1]) / int(counts[2]), 2))
                elif row["target_unit"] == "elapsed hours":
                    self.assertIn("Elapsed time", row["success_metric"])
                else:
                    self.assertEqual(row["current_baseline"], row["minutes_per_instance"])
                if row["target_value"]:
                    self.assertLess(float(row["target_value"]), float(row["current_baseline"]))
            else:
                self.assertEqual(row["target_value"], "")
                self.assertIn("Establish a reliable baseline", row["success_metric"])
        self.assertEqual(units, {"person-minutes per occurrence", "elapsed hours", "percent requiring rework"})

    def test_workload_is_plausible_for_specific_workflow(self):
        for row in self.data["discovery"]:
            answer = self.survey[row["prospect_id"]]
            pain = answer["primary_pain_point"] or "manual_data_entry"
            if row["activity_volume"]:
                self.assertLessEqual(float(row["activity_volume"]), PROCESS[pain][-1])
            if row["minutes_per_instance"]:
                self.assertIn(int(row["minutes_per_instance"]), PROCESS[pain][-2])
            self.assertEqual(len(json.loads(row["stakeholders"])), int(row["staff_count"]))

    def test_reuse_and_safety_notes_match_their_context(self):
        for row in self.data["discovery"]:
            if row["workflow_reuse_observation"] == "business_specific":
                self.assertEqual(row["solution_reusability"], "low")
            elif row["workflow_reuse_observation"] == "unknown":
                self.assertEqual(row["solution_reusability"], "unknown")
                self.assertIn("No reusable components confirmed", row["reusable_components"])
            if self.survey[row["prospect_id"]]["industry"] == "healthcare_allied":
                self.assertIn("deidentified_test_data", json.loads(row["safety_requirements"]))
                self.assertIn("clinical decisions", row["safety_notes"])

    def test_text_diversity_comes_from_context_not_shared_placeholders(self):
        for field, minimum in (("underused_software_names", 10), ("main_concern_details", 15), ("additional_comments", 15)):
            self.assertGreaterEqual(len({r[field] for r in self.data["survey"] if r[field]}), minimum)
        for field in ("workflow_steps", "bottlenecks", "systems_involved", "impact_evidence", "integration_evidence", "customisation_needs"):
            self.assertGreaterEqual(len({r[field] for r in self.data["discovery"]}), 10, field)
        for row in self.data["discovery"]:
            self.assertNotIn("Example operations system", row["systems_involved"])
            self.assertIn(row["recommended_next_action"], row["assessment_evidence"])
            self.assertIn("complexity " + (row["implementation_complexity"] or "unassessed"), row["assessment_evidence"])

    def test_other_explanations_and_fictional_business_names_are_consistent(self):
        for row in self.data["discovery"]:
            if "invoice" in row["workflow_name"].lower():
                self.assertIn("invoice records", row["workflow_steps"])
        for row in self.data["survey"]:
            if row["primary_pain_point"] == "other":
                self.assertEqual(row["primary_pain_point_other"], row["pain_points_other"])
        for row in self.data["contacts"]:
            self.assertIn(context_for(self.survey[row["prospect_id"]])["suffix"], row["business_name"])
            self.assertTrue(row["business_name"].startswith("Fictional "))

    def test_realism_rules_remain_valid_across_seeds(self):
        for seed in (1, 21, 42):
            data = generate_datasets(GenerationConfig(seed=seed))
            self.assertTrue(validate_dataset(**data).valid)
            for row in data["discovery"]:
                if row["reported_staff_hours_per_week"]:
                    self.assertLessEqual(float(row["reported_staff_hours_per_week"]), int(row["staff_count"]) * 35)


if __name__ == "__main__":
    unittest.main()
