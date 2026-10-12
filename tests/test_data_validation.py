"""Contract regression tests, using fictional in-memory records only."""

import csv
import json
import tempfile
import unittest
from dataclasses import asdict
from decimal import Decimal
from pathlib import Path

from src.data_validation import (
    contact_ready_response_ids, high_impact_prevalence, pain_point_prevalence,
    survey_with_discovery, valid_email, validate_csv_files, validate_dataset,
)
from src.schema import ARRAY_FIELDS, COLUMNS, ENUMS, NUMBER_FIELDS, RATING_FIELDS

ROOT = Path(__file__).resolve().parents[1]


def survey(**changes):
    row = dict(response_id="R0001", prospect_id="P0001", dataset_version="1.0",
               questionnaire_version="1.0", submitted_at="2026-10-10T09:00:00+11:00",
               industry="professional_services", pain_points='["manual_data_entry"]',
               primary_pain_point="manual_data_entry", weekly_hours_band="6_10",
               impact_rating="4", followup_interest="yes")
    return row | changes


def discovery(**changes):
    return dict(assessment_id="D0001", prospect_id="P0001", workflow_id="W0001",
                dataset_version="1.0", workflow_name="Invoice entry") | changes


def contact(**changes):
    return dict(response_id="R0001", prospect_id="P0001", contact_name="Fictional Respondent",
                business_name="Fictional Example Business", email="respondent@example.invalid",
                privacy_acknowledged="true", privacy_notice_version="EXAMPLE-1.0",
                followup_consent="true", marketing_consent="false",
                consent_recorded_at="2026-10-10T09:00:00+11:00") | changes


class ValidationTests(unittest.TestCase):
    def assert_issue(self, result, column, severity="error"):
        self.assertTrue(any(i.column == column and i.severity == severity for i in result.issues), result.issues)

    def test_valid_survey_only(self):
        result = validate_dataset([survey()])
        self.assertTrue(result.valid)
        self.assertEqual(result.warnings, [])
        self.assertEqual(result.discovery, [])
        self.assertEqual(result.contacts, [])

    def test_discovery_enriches_only_matching_prospect(self):
        result = validate_dataset([survey(), survey(response_id="R0002", prospect_id="P0002")], [discovery()])
        joined = survey_with_discovery(result)
        self.assertEqual(len(joined), 2)
        self.assertEqual(joined[0]["assessments"][0]["assessment_id"], "D0001")
        self.assertEqual(joined[1]["assessments"], [])

    def test_orphan_discovery_is_error(self):
        result = validate_dataset([survey()], [discovery(prospect_id="P404")])
        self.assert_issue(result, "prospect_id")
        with self.assertRaises(ValueError):
            survey_with_discovery(result)

    def test_duplicate_primary_keys(self):
        self.assert_issue(validate_dataset([survey(), survey()]), "response_id")
        self.assert_issue(validate_dataset([survey()], [discovery(), discovery()]), "assessment_id")
        self.assert_issue(validate_dataset([survey()], contacts=[contact(), contact()]), "response_id")

    def test_repeated_prospect_surveys_allowed(self):
        result = validate_dataset([survey(), survey(response_id="R0002")])
        self.assertTrue(result.valid)

    def test_multiple_workflows_and_reassessments_retained(self):
        records = [discovery(), discovery(assessment_id="D0002", workflow_id="W0002"),
                   discovery(assessment_id="D0003", assessment_date="2026-10-11")]
        result = validate_dataset([survey()], records)
        self.assertTrue(result.valid)
        self.assertEqual([r["assessment_id"] for r in survey_with_discovery(result)[0]["assessments"]],
                         ["D0001", "D0002", "D0003"])

    def test_workflow_ids_are_scoped_to_prospect(self):
        result = validate_dataset([survey(), survey(response_id="R0002", prospect_id="P0002")],
                                  [discovery(), discovery(assessment_id="D0002", prospect_id="P0002")])
        self.assertTrue(result.valid)

    def test_required_fields(self):
        for key in ("response_id", "prospect_id", "dataset_version"):
            with self.subTest(key=key):
                self.assert_issue(validate_dataset([survey(**{key: " "})]), key)
        for key in ("assessment_id", "prospect_id", "workflow_id", "dataset_version"):
            with self.subTest(key=key):
                self.assert_issue(validate_dataset([survey()], [discovery(**{key: ""})]), key)
        for key in ("response_id", "prospect_id"):
            self.assert_issue(validate_dataset([survey()], contacts=[contact(**{key: ""})]), key)

    def test_missing_optional_fields_remain_missing(self):
        result = validate_dataset([dict(response_id="R", prospect_id="P", dataset_version="1.0")],
                                  [discovery(prospect_id="P")])
        self.assertTrue(result.valid)
        self.assertEqual(len(result.warnings), 5)
        self.assertIsNone(result.survey[0]["impact_rating"])
        self.assertIsNone(result.discovery[0]["implementation_complexity"])

    def test_all_enum_codes_are_accepted_and_unknowns_rejected(self):
        for column, codes in ENUMS.items():
            for code in [*codes, "INVALID_CODE"]:
                value = json.dumps([code]) if column in ARRAY_FIELDS else code
                if column in COLUMNS["survey"]:
                    result = validate_dataset([survey(**{column: value})])
                else:
                    result = validate_dataset([survey()], [discovery(**{column: value})])
                with self.subTest(column=column, code=code):
                    errors = [i for i in result.errors if i.column == column]
                    self.assertEqual(bool(errors), code == "INVALID_CODE")

    def test_ratings_require_integer_1_to_5(self):
        for column in RATING_FIELDS:
            for value in ("0", "6", "-1", "1.5", "4.0", "NaN", "true", "1", "5", ""):
                result = (validate_dataset([survey(**{column: value})]) if column == "impact_rating"
                          else validate_dataset([survey()], [discovery(**{column: value})]))
                with self.subTest(column=column, value=value):
                    self.assertEqual(any(i.column == column for i in result.errors), value not in {"1", "5", ""})

    def test_malformed_json_and_wrong_array_types(self):
        for column in ARRAY_FIELDS:
            for value in ('[broken', 'manual_data_entry,reporting_analysis', '{}', 'null', '"text"', '[1]', '[null]', '[{}]', '[""]'):
                result = (validate_dataset([survey(**{column: value})]) if column in COLUMNS["survey"]
                          else validate_dataset([survey()], [discovery(**{column: value})]))
                with self.subTest(column=column, value=value):
                    self.assert_issue(result, column)

    def test_more_than_three_distinct_pain_points(self):
        self.assert_issue(validate_dataset([survey(pain_points=json.dumps(ENUMS["pain_points"][:4]))]), "pain_points")

    def test_duplicate_choices_warn_but_distinct_limit_applies(self):
        result = validate_dataset([survey(pain_points='["manual_data_entry", "manual_data_entry"]')])
        self.assertTrue(result.valid)
        self.assert_issue(result, "pain_points", "warning")
        self.assertEqual(pain_point_prevalence(result)["categories"]["manual_data_entry"]["count"], 1)

    def test_s07_mismatch_warns_without_rewriting(self):
        result = validate_dataset([survey(primary_pain_point="sales_followup")])
        self.assertTrue(result.valid)
        self.assert_issue(result, "primary_pain_point", "warning")
        self.assertEqual(result.survey[0]["primary_pain_point"], "sales_followup")

    def test_exclusive_selections_warn(self):
        result = validate_dataset([survey(business_systems='["none_paper", "crm"]', ai_concerns='["none", "cost_roi"]')])
        self.assertTrue(result.valid)
        self.assert_issue(result, "business_systems", "warning")
        self.assert_issue(result, "ai_concerns", "warning")

    def test_other_text_warnings(self):
        for column in ("industry", "pain_points", "primary_pain_point", "business_systems", "ai_concerns", "desired_outcome"):
            value = '["other"]' if column in ARRAY_FIELDS else "other"
            result = validate_dataset([survey(**{column: value})])
            self.assert_issue(result, column + "_other", "warning")
            filled = validate_dataset([survey(**{column: value, column + "_other": "Explanation"})])
            self.assertFalse(any(i.column == column + "_other" for i in filled.issues))

    def test_conditional_followup_warnings(self):
        result = validate_dataset([survey(ai_adoption="not_using", ai_tools_and_uses="Example tool",
                                          subscription_underuse="mostly_utilised", underused_software_names="Example software")])
        self.assertTrue(result.valid)
        self.assert_issue(result, "ai_tools_and_uses", "warning")
        self.assert_issue(result, "underused_software_names", "warning")

    def test_workload_missing_and_unsure_never_become_zero(self):
        for value, expected in (("", None), ("unsure", "unsure"), ("over_20", "over_20")):
            result = validate_dataset([survey(weekly_hours_band=value)])
            self.assertTrue(result.valid)
            self.assertEqual(result.survey[0]["weekly_hours_band"], expected)
            self.assertNotIn("modelled_staff_hours_per_week", result.survey[0])

    def test_filtered_proportions_and_metric_denominators(self):
        result = validate_dataset([
            survey(pain_points='["manual_data_entry", "reporting_analysis", "manual_data_entry"]'),
            survey(response_id="R2", pain_points='["reporting_analysis"]', impact_rating="2"),
            survey(response_id="R3", pain_points="", impact_rating=""),
            survey(response_id="R4", industry="retail_ecommerce", impact_rating="5"),
        ], [discovery(), discovery(assessment_id="D2", workflow_id="W2")])
        selected = lambda row: row["industry"] == "professional_services"
        pain = pain_point_prevalence(result, selected)
        self.assertEqual(pain["denominator"], 2)
        self.assertEqual(pain["categories"]["manual_data_entry"]["percentage"], 50)
        self.assertEqual(pain["categories"]["reporting_analysis"]["percentage"], 100)
        self.assertEqual(high_impact_prevalence(result, predicate=selected), {"count": 1, "denominator": 2, "percentage": 50})
        self.assertEqual(high_impact_prevalence(result, threshold=5, predicate=selected)["count"], 0)

    def test_empty_denominators_are_unknown_not_zero_percent(self):
        result = validate_dataset([survey(pain_points="[]", impact_rating="")])
        self.assertIsNone(high_impact_prevalence(result)["percentage"])
        self.assertEqual(pain_point_prevalence(result)["denominator"], 0)
        self.assertIsNone(pain_point_prevalence(result)["categories"]["manual_data_entry"]["percentage"])

    def test_interest_does_not_imply_permission(self):
        for consent in ("", "false"):
            result = validate_dataset([survey()], contacts=[contact(followup_consent=consent, marketing_consent="true")])
            self.assertEqual(contact_ready_response_ids(result), [])
        self.assertEqual(contact_ready_response_ids(validate_dataset([survey()])), [])

    def test_contact_eligibility_exact_conjunction(self):
        for interest in ("yes", "maybe", "not_now", ""):
            for consent in ("true", "false", ""):
                for email in ("respondent@example.invalid", ""):
                    result = validate_dataset([survey(followup_interest=interest)], contacts=[contact(followup_consent=consent, email=email)])
                    expected = ["R0001"] if interest in {"yes", "maybe"} and consent == "true" and email else []
                    self.assertEqual(contact_ready_response_ids(result), expected)

    def test_contact_must_match_submission_not_just_prospect(self):
        result = validate_dataset([survey(), survey(response_id="R2")], contacts=[contact(followup_consent="false")])
        self.assertEqual(contact_ready_response_ids(result), [])
        self.assert_issue(validate_dataset([survey()], contacts=[contact(response_id="R404")]), "response_id")
        self.assert_issue(validate_dataset([survey()], contacts=[contact(prospect_id="P404")]), "prospect_id")

    def test_consent_boolean_types_and_missing_values(self):
        for column in ("privacy_acknowledged", "followup_consent", "marketing_consent"):
            for value in ("TRUE", "1", "yes"):
                self.assert_issue(validate_dataset([survey()], contacts=[contact(**{column: value})]), column)
            result = validate_dataset([survey()], contacts=[contact(**{column: ""})])
            self.assertIsNone(result.contacts[0][column])

    def test_consent_provenance_warns_when_missing(self):
        result = validate_dataset([survey()], contacts=[contact(privacy_notice_version="", consent_recorded_at="")])
        self.assertTrue(result.valid)
        self.assert_issue(result, "privacy_notice_version", "warning")
        self.assert_issue(result, "consent_recorded_at", "warning")

    def test_email_validation(self):
        for email in ("a@b.invalid", "first.last+tag@example.invalid"):
            self.assertTrue(valid_email(email))
        for email in ("a@b", "@example.invalid", "a b@example.invalid", "a@@example.invalid", "a@-bad.invalid", "a..b@example.invalid", "a@example..invalid"):
            self.assertFalse(valid_email(email))
            self.assert_issue(validate_dataset([survey()], contacts=[contact(email=email)]), "email")

    def test_numeric_measurements_and_headcount(self):
        for column in NUMBER_FIELDS:
            for value in ("-1", "NaN", "Infinity", "1,000", "$10"):
                self.assert_issue(validate_dataset([survey()], [discovery(**{column: value}, currency="AUD")]), column)
            result = validate_dataset([survey()], [discovery(**{column: "2.5"}, currency="AUD")])
            self.assertTrue(result.valid)
            self.assertEqual(result.discovery[0][column], Decimal("2.5"))
        for value in ("1.5", "-1"):
            self.assert_issue(validate_dataset([survey()], [discovery(staff_count=value)]), "staff_count")
        self.assertTrue(validate_dataset([survey()], [discovery(staff_count="0")]).valid)

    def test_zero_minutes_is_flagged_without_inventing_work_flag(self):
        result = validate_dataset([survey()], [discovery(minutes_per_instance="0")])
        self.assertTrue(result.valid)
        self.assert_issue(result, "minutes_per_instance", "warning")

    def test_explicit_currency_required_only_with_amount(self):
        for column in ("labour_cost_per_hour", "indicative_budget"):
            self.assert_issue(validate_dataset([survey()], [discovery(**{column: "0"})]), "currency")
            self.assertTrue(validate_dataset([survey()], [discovery(**{column: "12.50"}, currency="NZD")]).valid)
        self.assertTrue(validate_dataset([survey()], [discovery()]).valid)

    def test_evidence_warnings(self):
        result = validate_dataset([survey()], [discovery(implementation_complexity="3", data_quality_rating="4",
                                  integration_capability="confirmed_api", evidence_status="validated", observed_impact_types='["other"]')])
        self.assertTrue(result.valid)
        for column in ("assessment_evidence", "data_quality_evidence", "integration_evidence", "impact_evidence"):
            self.assert_issue(result, column, "warning")

    def test_iso_dates(self):
        for value in ("2026-10-10", "2026-10-10T09:00", "2026-10-10T09:00:00Z", "2026-10-10T09:00:00.123+11:00", ""):
            self.assertTrue(validate_dataset([survey(submitted_at=value)]).valid)
        for column, kind in (("submitted_at", "survey"), ("assessment_date", "discovery"), ("consent_recorded_at", "contacts")):
            for value in ("10/10/2026", "2026-02-30", "20261010", "2026-10-10T25:00:00", "2026-10-10T09:00+25:00"):
                rows = {"survey": [survey()]}
                rows[kind] = [{"survey": survey, "discovery": discovery, "contacts": contact}[kind](**{column: value})]
                self.assert_issue(validate_dataset(**rows), column)

    def test_versions_warn_without_overwriting(self):
        result = validate_dataset([survey(dataset_version="2.0", questionnaire_version="2.0")])
        self.assertTrue(result.valid)
        self.assert_issue(result, "dataset_version", "warning")
        self.assert_issue(result, "questionnaire_version", "warning")
        self.assertEqual(result.survey[0]["dataset_version"], "2.0")
        self.assertIsNone(validate_dataset([survey(questionnaire_version="")]).survey[0]["questionnaire_version"])

    def test_survey_only_never_invents_discovery_claims_or_copies_contacts(self):
        result = validate_dataset([survey()], contacts=[contact()])
        output = survey_with_discovery(result)[0]
        self.assertEqual(output["assessments"], [])
        for key in ("implementation_complexity", "budget_status", "roi", "technical_feasibility", "email", "contact_name"):
            self.assertNotIn(key, output["survey"])

    def test_issues_are_structured_and_do_not_echo_private_values(self):
        result = validate_dataset([survey(impact_rating="7")], contacts=[contact(email="private invalid email")])
        for issue in result.issues:
            self.assertEqual(set(asdict(issue)), {"severity", "dataset", "row_id", "column", "issue", "suggested_fix"})
            self.assertTrue(issue.suggested_fix)
        self.assertNotIn("private invalid email", json.dumps([asdict(i) for i in result.issues]))

    def test_input_rows_are_not_mutated(self):
        original = survey()
        before = original.copy()
        validate_dataset([original])
        self.assertEqual(original, before)

    def test_extra_columns_fail_including_contacts_in_survey(self):
        self.assert_issue(validate_dataset([survey(email="respondent@example.invalid")]), "email")

    def test_non_csv_cell_types_return_errors_without_crashing(self):
        for column, value in (("pain_points", [{"unexpected": "object"}]),
                              ("impact_rating", 4), ("prospect_id", [])):
            self.assert_issue(validate_dataset([survey(**{column: value})]), column)

    def test_invalid_timezone_minutes_rejected(self):
        self.assert_issue(validate_dataset([survey(submitted_at="2026-10-10T09:00:00+11:99")]), "submitted_at")

    def test_invalid_datasets_cannot_enter_helpers(self):
        result = validate_dataset([survey(impact_rating="9")])
        for helper in (survey_with_discovery, pain_point_prevalence, high_impact_prevalence, contact_ready_response_ids):
            with self.assertRaises(ValueError):
                helper(result)

    def test_threshold_bounds(self):
        for threshold in (0, 6, 4.5, True):
            with self.assertRaises(ValueError):
                high_impact_prevalence(validate_dataset([survey()]), threshold)


class CsvTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "survey.csv"

    def write_rows(self, rows, header=None):
        with self.path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=header or COLUMNS["survey"])
            writer.writeheader()
            writer.writerows(rows)

    def test_csv_load_and_json_quoting_unicode_multiline(self):
        self.write_rows([survey(additional_comments='Example, café\nsecond line', pain_points='["manual_data_entry", "reporting_analysis"]')])
        result = validate_csv_files(self.path)
        self.assertTrue(result.valid)
        self.assertEqual(result.survey[0]["additional_comments"], 'Example, café\nsecond line')
        self.assertEqual(result.survey[0]["pain_points"], ["manual_data_entry", "reporting_analysis"])

    def test_wrong_headers_fail_even_with_no_rows(self):
        for header in (COLUMNS["survey"][:-1], list(reversed(COLUMNS["survey"])), COLUMNS["survey"] + ["email"], COLUMNS["survey"] + ["response_id"]):
            self.write_rows([], header)
            self.assertFalse(validate_csv_files(self.path).valid)

    def test_wrong_row_width_fails(self):
        self.path.write_text(",".join(COLUMNS["survey"]) + "\nR1,P1\n", encoding="utf-8")
        self.assertFalse(validate_csv_files(self.path).valid)

    def test_empty_file_missing_file_bad_encoding_and_malformed_csv(self):
        self.assertFalse(validate_csv_files(self.path).valid)
        for content in (b"", b"\xff", (",".join(COLUMNS["survey"]) + '\n"unterminated').encode()):
            self.path.write_bytes(content)
            self.assertFalse(validate_csv_files(self.path).valid)

    def test_utf8_bom_accepted(self):
        self.write_rows([survey()])
        self.path.write_bytes(b"\xef\xbb\xbf" + self.path.read_bytes())
        self.assertTrue(validate_csv_files(self.path).valid)

    def test_all_header_only_templates_validate(self):
        result = validate_csv_files(ROOT / "templates/survey_responses_template.csv",
                                    ROOT / "templates/discovery_assessments_template.csv",
                                    ROOT / "templates/contacts_and_consent_template.csv")
        self.assertTrue(result.valid)
        self.assertEqual(result.issues, [])
        self.assertEqual(result.survey + result.discovery + result.contacts, [])


if __name__ == "__main__":
    unittest.main()
