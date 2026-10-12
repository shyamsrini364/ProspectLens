"""Generated-data invariants; the v1.0 validator is reused unchanged."""

import csv
import hashlib
import json
import random
import tempfile
import unittest
from collections import Counter
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

from scripts.generate_synthetic_data import (
    AI_ASSISTANTS, AI_SECONDARY_USES, AI_TASKS_BY_PAIN,
    FILENAMES, GenerationConfig, generate_datasets, write_datasets,
)
from src.data_validation import contact_ready_response_ids, validate_csv_files, validate_dataset
from src.schema import ARRAY_FIELDS, COLUMNS, ENUMS, REQUIRED


class SyntheticDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = GenerationConfig()
        cls.data = generate_datasets(cls.config)
        cls.result = validate_dataset(**cls.data)

    def test_default_counts_and_unique_prospects(self):
        self.assertEqual({k: len(v) for k, v in self.data.items()}, {"survey": 150, "discovery": 35, "contacts": 150})
        self.assertEqual(len({r["prospect_id"] for r in self.data["survey"]}), 150)

    def test_valid_without_weakening_validator(self):
        self.assertEqual(self.result.errors, [])
        self.assertGreater(len(self.result.warnings), 0)
        self.assertTrue(all(i.issue == "Recommended analytical answer is missing." for i in self.result.warnings))

    def test_required_fields_and_exact_headers(self):
        for kind, rows in self.data.items():
            for row in rows:
                self.assertEqual(list(row), COLUMNS[kind])
                for column in REQUIRED[kind]:
                    self.assertTrue(row[column])

    def test_all_generated_enums_valid(self):
        for kind, rows in self.data.items():
            for row in rows:
                for column in set(row) & set(ENUMS):
                    if row[column]:
                        codes = json.loads(row[column]) if column in ARRAY_FIELDS else [row[column]]
                        self.assertTrue(set(codes).issubset(ENUMS[column]))

    def test_unique_keys_and_correct_relationships(self):
        survey = {r["response_id"]: r["prospect_id"] for r in self.data["survey"]}
        self.assertEqual(len(survey), 150)
        self.assertEqual(len({r["assessment_id"] for r in self.data["discovery"]}), 35)
        self.assertEqual(len({r["response_id"] for r in self.data["contacts"]}), 150)
        for row in self.data["discovery"]:
            self.assertIn(row["prospect_id"], survey.values())
            self.assertRegex(row["assessment_id"], r"^D\d{4}$")
            self.assertRegex(row["workflow_id"], r"^W\d{4}$")
        for row in self.data["contacts"]:
            self.assertEqual(survey[row["response_id"]], row["prospect_id"])

    def test_discovery_subset_multiple_workflows_and_distinct_workflow_keys(self):
        counts = Counter(r["prospect_id"] for r in self.data["discovery"])
        self.assertEqual(len(counts), 27)
        self.assertTrue(any(count > 1 for count in counts.values()))
        keys = [(r["prospect_id"], r["workflow_id"]) for r in self.data["discovery"]]
        self.assertEqual(len(set(keys)), 35)
        for prospect in counts:
            names = [r["workflow_name"] for r in self.data["discovery"] if r["prospect_id"] == prospect]
            self.assertEqual(len(names), len(set(names)))

    def test_multiselect_json_and_selection_semantics(self):
        for kind, rows in self.data.items():
            for row in rows:
                for field in set(row) & set(ARRAY_FIELDS):
                    if row[field]:
                        values = json.loads(row[field])
                        self.assertIsInstance(values, list)
                        self.assertTrue(all(isinstance(value, str) for value in values))
                        self.assertEqual(len(values), len(set(values)))
        for row in self.data["survey"]:
            if row["pain_points"]:
                pain = json.loads(row["pain_points"])
                self.assertLessEqual(len(pain), 3)
                self.assertIn(row["primary_pain_point"], pain)
            for column, exclusive in (("business_systems", "none_paper"), ("ai_concerns", "none")):
                values = json.loads(row[column])
                if exclusive in values:
                    self.assertEqual(values, [exclusive])

    def test_missing_unknown_and_unassessed_are_preserved(self):
        self.assertTrue(any(r["weekly_hours_band"] == "" for r in self.data["survey"]))
        self.assertTrue(any(r["weekly_hours_band"] == "unsure" for r in self.data["survey"]))
        self.assertTrue(any(r["implementation_complexity"] is None for r in self.result.discovery))
        self.assertTrue(any(r["technical_feasibility"] == "unknown" for r in self.result.discovery))
        self.assertTrue(any(r["technical_feasibility"] is None for r in self.result.discovery))
        self.assertTrue(any(r["followup_consent"] is None for r in self.result.contacts))
        self.assertTrue(any(r["minutes_per_instance"] is None for r in self.result.discovery))

    def test_ai_answers_name_tools_and_concrete_contextual_tasks(self):
        answers = [r for r in self.data["survey"] if r["ai_tools_and_uses"]]
        tools = set(AI_ASSISTANTS) | {tool for tool, _ in AI_SECONDARY_USES}
        used_tools = set()
        for row in answers:
            text = row["ai_tools_and_uses"]
            named = {tool for tool in tools if tool + " to " in text}
            self.assertTrue(named, text)
            used_tools.update(named)
            if row["primary_pain_point"]:
                self.assertTrue(any(task in text for task in AI_TASKS_BY_PAIN[row["primary_pain_point"]]), text)
            self.assertNotIn("Example writing assistant", text)
        self.assertGreaterEqual(len(used_tools), 6)
        self.assertGreater(len({r["ai_tools_and_uses"] for r in answers}), 50)

    def test_ai_followup_respects_adoption_and_optional_blanks(self):
        for row in self.data["survey"]:
            text, adoption = row["ai_tools_and_uses"], row["ai_adoption"]
            if adoption not in {"regular_multiple", "limited_tasks", "experimented"}:
                self.assertEqual(text, "")
            elif text:
                if adoption == "regular_multiple":
                    self.assertIn("regularly use", text)
                    self.assertGreaterEqual(text.count(" to "), 2)
                elif adoption == "limited_tasks":
                    self.assertIn("occasional, specific task", text)
                else:
                    self.assertIn("We tried", text)
                    self.assertIn("not made this part of our regular work", text)
        self.assertTrue(any(r["ai_adoption"] in {"regular_multiple", "limited_tasks", "experimented"}
                            and not r["ai_tools_and_uses"] for r in self.data["survey"]))

    def test_ai_description_draws_do_not_reshuffle_other_data(self):
        def alternative_description(rng, row):
            # Even a future wording change consuming many draws stays isolated.
            for _ in range(100):
                rng.random()
            return "Alternative fictional tool description"

        with patch("scripts.generate_synthetic_data.describe_ai_use", side_effect=alternative_description):
            changed = generate_datasets(self.config)
        self.assertEqual(changed["discovery"], self.data["discovery"])
        self.assertEqual(changed["contacts"], self.data["contacts"])
        for before, after in zip(self.data["survey"], changed["survey"]):
            self.assertEqual({k: v for k, v in before.items() if k != "ai_tools_and_uses"},
                             {k: v for k, v in after.items() if k != "ai_tools_and_uses"})
            self.assertEqual(bool(before["ai_tools_and_uses"]), bool(after["ai_tools_and_uses"]))

    def test_same_configuration_is_reproducible_and_seed_changes_data(self):
        self.assertEqual(generate_datasets(self.config), self.data)
        changed = generate_datasets(GenerationConfig(seed=21))
        self.assertNotEqual(changed["survey"], self.data["survey"])
        self.assertTrue(validate_dataset(**changed).valid)

    def test_no_global_random_state_changes(self):
        before = random.getstate()
        generate_datasets(self.config)
        self.assertEqual(before, random.getstate())

    def test_discovery_count_does_not_change_survey_or_contacts(self):
        other = generate_datasets(GenerationConfig(discovery_count=7))
        self.assertEqual(other["survey"], self.data["survey"])
        self.assertEqual(other["contacts"], self.data["contacts"])

    def test_configurable_counts_including_survey_only_and_empty(self):
        for survey_count, discovery_count in ((7, 2), (1, 20), (8, 0), (0, 0), (50, 80)):
            with self.subTest(survey=survey_count, discovery=discovery_count):
                data = generate_datasets(GenerationConfig(survey_count=survey_count, discovery_count=discovery_count))
                self.assertEqual(len(data["survey"]), survey_count)
                self.assertEqual(len(data["contacts"]), survey_count)
                self.assertEqual(len(data["discovery"]), discovery_count)
                self.assertTrue(validate_dataset(**data).valid)

    def test_invalid_configuration_fails(self):
        for config in (GenerationConfig(survey_count=-1), GenerationConfig(discovery_count=-1),
                       GenerationConfig(survey_count=0), GenerationConfig(seed=True), GenerationConfig(currency="")):
            with self.assertRaises(ValueError):
                generate_datasets(config)

    def test_contacts_are_obviously_fictional_and_reserved_domain_only(self):
        for row in self.data["contacts"]:
            self.assertRegex(row["contact_name"], r"^Fictional [A-Za-z]+ [A-Za-z]+ \d{4}$")
            self.assertTrue(row["business_name"].startswith("Fictional "))
            if row["email"]:
                self.assertRegex(row["email"], r"^person\d{4}@example\.invalid$")

    def test_contact_fields_and_values_absent_from_analytical_data(self):
        analytical = json.dumps([self.data["survey"], self.data["discovery"]])
        for private in ("contact_name", "business_name", "email", "marketing_consent", "followup_consent"):
            self.assertNotIn(f'"{private}"', analytical)
        for row in self.data["contacts"]:
            self.assertNotIn(row["contact_name"], analytical)
            self.assertNotIn(row["business_name"], analytical)
            if row["email"]:
                self.assertNotIn(row["email"], analytical)

    def test_consent_exceptions_and_eligibility(self):
        eligible = set(contact_ready_response_ids(self.result))
        self.assertTrue({"R0003", "R0004"}.issubset(eligible))
        self.assertTrue({"R0001", "R0002", "R0005", "R0006", "R0007"}.isdisjoint(eligible))
        contacts = {r["response_id"]: r for r in self.result.contacts}
        for row in self.result.survey:
            if row["response_id"] in eligible:
                self.assertIn(row["followup_interest"], {"yes", "maybe"})
                self.assertIs(contacts[row["response_id"]]["followup_consent"], True)

    def test_variation_and_counterexamples(self):
        industries = Counter(r["industry"] for r in self.data["survey"])
        self.assertEqual(set(industries), set(ENUMS["industry"]))
        self.assertGreater(max(industries.values()), 3 * min(industries.values()))
        self.assertEqual({r["employee_band"] for r in self.data["survey"]} - {""}, set(ENUMS["employee_band"]))
        self.assertEqual({r["ai_adoption"] for r in self.data["survey"]} - {""}, set(ENUMS["ai_adoption"]))
        self.assertTrue(any(r["commercial_potential"] == "high" and r["implementation_complexity"] in {"4", "5"} for r in self.data["discovery"]))
        self.assertEqual(self.data["survey"][1]["ai_adoption"], "regular_multiple")
        self.assertEqual(self.data["survey"][1]["impact_rating"], "5")

    def test_similar_pain_can_have_different_workflows_and_integration_evidence(self):
        first, second = self.data["discovery"][:2]
        self.assertNotEqual(first["workflow_name"], second["workflow_name"])
        self.assertEqual(first["integration_capability"], "manual_only")
        self.assertEqual(second["integration_capability"], "confirmed_api")
        self.assertIn("Synthetic", second["integration_evidence"])

    def test_numerical_consistency_no_staff_multiplier(self):
        for row in self.result.discovery:
            staff = row["staff_count"]
            reported = row["reported_staff_hours_per_week"]
            if reported is not None:
                self.assertLessEqual(reported, staff * 35)
            if row["activity_volume"] is not None and row["minutes_per_instance"] is not None:
                modelled = row["activity_volume"] * row["minutes_per_instance"] / 60
                self.assertGreater(modelled, 0)
                if reported is not None:
                    self.assertLessEqual(abs(reported - modelled) / modelled, Decimal("0.37"))
            if row["target_value"] is not None:
                self.assertLess(row["target_value"], row["current_baseline"])
            if row["labour_cost_per_hour"] is not None or row["indicative_budget"] is not None:
                self.assertEqual(row["currency"], "AUD")

    def test_solo_business_staff_and_dates(self):
        survey = {r["prospect_id"]: r for r in self.data["survey"]}
        for row in self.data["discovery"]:
            source = survey[row["prospect_id"]]
            if source["employee_band"] == "solo":
                self.assertEqual(row["staff_count"], "1")
            self.assertGreaterEqual(datetime.fromisoformat(row["assessment_date"]).date(),
                                    datetime.fromisoformat(source["submitted_at"]).date())

    def test_many_seeds_remain_valid(self):
        for seed in (0, 1, 42, 2026):
            self.assertTrue(validate_dataset(**generate_datasets(GenerationConfig(seed=seed))).valid)

    def test_serialized_files_validate_and_are_byte_reproducible(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            write_datasets(self.data, a, self.config)
            write_datasets(generate_datasets(self.config), b, self.config)
            for filename in [*FILENAMES.values(), "generation_manifest.json"]:
                self.assertEqual((Path(a) / filename).read_bytes(), (Path(b) / filename).read_bytes())
            result = validate_csv_files(*(Path(a) / FILENAMES[k] for k in ("survey", "discovery", "contacts")))
            self.assertTrue(result.valid)
            manifest = json.loads((Path(a) / "generation_manifest.json").read_text())
            for kind, filename in FILENAMES.items():
                self.assertEqual(hashlib.sha256((Path(a) / filename).read_bytes()).hexdigest(), manifest["sha256"][filename])
                with (Path(a) / filename).open(encoding="utf-8", newline="") as handle:
                    reader = csv.DictReader(handle)
                    self.assertEqual(reader.fieldnames, COLUMNS[kind])
                    self.assertEqual(len(list(reader)), len(self.data[kind]))


if __name__ == "__main__":
    unittest.main()
