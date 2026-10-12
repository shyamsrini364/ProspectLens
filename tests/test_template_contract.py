"""Independent snapshots of specification v1.0: changes must be deliberate."""

import csv
import re
import unittest
from pathlib import Path

from src.schema import COLUMNS

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "headers": {
        "survey": [
            "response_id",
            "prospect_id",
            "submitted_at",
            "dataset_version",
            "questionnaire_version",
            "recruitment_channel",
            "industry",
            "industry_other",
            "employee_band",
            "pain_points",
            "pain_points_other",
            "primary_pain_point",
            "primary_pain_point_other",
            "weekly_hours_band",
            "impact_rating",
            "current_process",
            "sensitive_data_frequency",
            "business_systems",
            "business_systems_other",
            "subscription_underuse",
            "underused_software_names",
            "ai_adoption",
            "ai_tools_and_uses",
            "ai_concerns",
            "ai_concerns_other",
            "main_concern_details",
            "desired_outcome",
            "desired_outcome_other",
            "followup_interest",
            "additional_comments"
        ],
        "contacts": [
            "response_id",
            "prospect_id",
            "contact_name",
            "business_name",
            "email",
            "privacy_acknowledged",
            "privacy_notice_version",
            "followup_consent",
            "marketing_consent",
            "consent_recorded_at"
        ],
        "discovery": [
            "assessment_id",
            "prospect_id",
            "workflow_id",
            "assessment_date",
            "assessor_id",
            "source_reference",
            "dataset_version",
            "questionnaire_version",
            "workflow_name",
            "workflow_steps",
            "stakeholders",
            "bottlenecks",
            "activity_volume",
            "volume_period",
            "minutes_per_instance",
            "staff_count",
            "reported_staff_hours_per_week",
            "labour_cost_per_hour",
            "currency",
            "observed_impact_types",
            "impact_evidence",
            "success_metric",
            "current_baseline",
            "target_value",
            "target_unit",
            "systems_involved",
            "information_storage",
            "data_quality_rating",
            "data_quality_evidence",
            "integration_capability",
            "integration_evidence",
            "standardisation_rating",
            "exceptions_description",
            "safety_requirements",
            "safety_notes",
            "decision_authority",
            "implementation_timeline",
            "budget_status",
            "indicative_budget",
            "pilot_interest",
            "workflow_reuse_observation",
            "reuse_evidence",
            "reusable_components",
            "customisation_needs",
            "additional_opportunities",
            "business_impact_assessment",
            "commercial_potential",
            "solution_reusability",
            "technical_feasibility",
            "implementation_complexity",
            "expansion_potential",
            "assessment_evidence",
            "evidence_status",
            "recommended_next_action"
        ]
    },
    "survey": [
        "What is your name? — short text",
        "What is your business name? — short text",
        "What is your email address? — email",
        "Which industry best describes your business? — single choice",
        "Approximately how many people work in your business, including yourself? — single choice",
        "Which activities currently consume the most time or create the biggest challenges for your business? — multi-select, **maximum three**",
        "Of the challenges listed above, which ONE would you most like to improve? — single choice using S06 categories",
        "Approximately how much staff time does this particular challenge consume each week, across your business? — single choice",
        "How significantly does this challenge affect your business? — 1–5",
        "How is this work currently performed? — single choice",
        "Does the work involved in this challenge require handling sensitive or confidential information? — single choice",
        "Which business systems or software tools do you currently use? — multi-select",
        "Are there any software subscriptions your business pays for but does not fully utilise? — single choice; optional tool-name follow-up",
        "Is your business currently using AI tools? — single choice; conditional tools-and-use follow-up",
        "What concerns, if any, would you have about adopting AI or automation in your business? — multi-select",
        "Could you briefly explain your main concern about adopting AI or automation? — optional text",
        "If you could meaningfully improve your biggest business challenge, which outcome would be most valuable to your business? — single choice",
        "Would you be interested in discussing potential business improvements with `[Organisation Name]`? — single choice",
        "Would you like to share anything else about your business challenges or technology needs? — optional text"
    ],
    "discovery": [
        "What specific business process or workflow are we investigating?",
        "Describe how this process works today, beginning to end.",
        "Which people, teams or external parties are involved?",
        "What are the biggest delays, errors or frustrations?",
        "Approximately how many times does the process occur, and per what time period?",
        "How many minutes does one instance typically take?",
        "How many people are involved, and how many total staff hours per week are spent on the process?",
        "What is the approximate hourly labour cost (if known and voluntarily shared)?",
        "What measurable negative outcomes occur?",
        "What should success look like and how would it be measured?",
        "Which applications or tools are involved?",
        "Where is required information stored?",
        "How would you assess data quality/consistency (1–5) and why?",
        "What integration or export capability is confirmed?",
        "How standardised is the workflow (1–5), and what exceptions occur?",
        "What security, privacy, compliance or human-approval requirements apply?",
        "Who approves investment?",
        "When would the business ideally address the problem?",
        "Is budget approved, indicative, conditional, absent or undiscussed? Optional budget amount.",
        "Would the business consider a scoped pilot?",
        "Is this workflow similar across teams/branches/other businesses?",
        "What solution elements seem standardisable versus custom?",
        "Are there other problems in this business worth investigating?",
        "Structured opportunity judgement with rationale and recommended next step."
    ],
    "labels": {
        "industry": {
            "professional_services": "Professional services (accounting, legal, consulting, etc.)",
            "healthcare_allied": "Healthcare and allied health",
            "retail_ecommerce": "Retail or e-commerce",
            "trades_construction": "Trades and construction",
            "hospitality": "Hospitality",
            "real_estate": "Real estate and property",
            "manufacturing_logistics": "Manufacturing or logistics",
            "education_training": "Education and training",
            "other": "Other (please specify)"
        },
        "employee_band": {
            "solo": "Just me",
            "2_5": "2–5",
            "6_20": "6–20",
            "21_50": "21–50",
            "51_200": "51–200",
            "over_200": "More than 200"
        },
        "pain_points": {
            "customer_enquiries": "Responding to customer enquiries",
            "sales_followup": "Lead generation and sales follow-up",
            "appointment_scheduling": "Appointment scheduling and reminders",
            "manual_data_entry": "Manual data entry and administration",
            "reporting_analysis": "Preparing reports and analysing information",
            "documents_information": "Managing documents and information",
            "finance_invoicing": "Finance, invoicing, and payment follow-up",
            "staff_coordination": "Staff scheduling and coordination",
            "customer_support": "Customer support and complaint handling",
            "marketing_content": "Marketing and content creation",
            "other": "Other (please specify)"
        },
        "primary_pain_point": {
            "customer_enquiries": "Responding to customer enquiries",
            "sales_followup": "Lead generation and sales follow-up",
            "appointment_scheduling": "Appointment scheduling and reminders",
            "manual_data_entry": "Manual data entry and administration",
            "reporting_analysis": "Preparing reports and analysing information",
            "documents_information": "Managing documents and information",
            "finance_invoicing": "Finance, invoicing, and payment follow-up",
            "staff_coordination": "Staff scheduling and coordination",
            "customer_support": "Customer support and complaint handling",
            "marketing_content": "Marketing and content creation",
            "other": "Other (please specify)"
        },
        "weekly_hours_band": {
            "under_2": "Less than 2 hours",
            "2_5": "2–5 hours",
            "6_10": "6–10 hours",
            "11_20": "11–20 hours",
            "over_20": "More than 20 hours",
            "unsure": "Not sure"
        },
        "current_process": {
            "mostly_manual": "Mostly manually",
            "mixed_manual_digital": "A combination of manual work and digital tools",
            "mostly_software": "Mostly through existing software",
            "automated_with_issues": "Already automated, but experiencing frequent issues",
            "unsure": "Not sure"
        },
        "sensitive_data_frequency": {
            "frequent": "Yes, frequently (e.g. customer, health, financial, or employee information)",
            "sometimes": "Sometimes",
            "rare_never": "Rarely or never",
            "unsure": "Not sure"
        },
        "business_systems": {
            "crm": "Customer relationship management (CRM) software",
            "accounting_invoicing": "Accounting or invoicing software",
            "booking_scheduling": "Booking or scheduling software",
            "task_management": "Project or task management software",
            "spreadsheets": "Spreadsheets",
            "email_messaging": "Email and messaging platforms",
            "industry_specific": "Industry-specific business software",
            "none_paper": "None / mostly paper-based",
            "other": "Other (please specify)"
        },
        "subscription_underuse": {
            "several": "Yes, several",
            "one_or_two": "Yes, one or two",
            "mostly_utilised": "No, most of our subscriptions are well utilised",
            "unsure": "Not sure"
        },
        "ai_adoption": {
            "regular_multiple": "Yes, regularly across multiple business activities",
            "limited_tasks": "Yes, for a few specific tasks",
            "experimented": "We have experimented with AI but don't use it consistently",
            "not_using": "No, we are not currently using AI",
            "unsure": "Not sure"
        },
        "ai_concerns": {
            "cost_roi": "Cost and return on investment",
            "privacy_security": "Data privacy and security",
            "accuracy_reliability": "Accuracy and reliability",
            "staff_adoption": "Staff training and adoption",
            "systems_integration": "Integration with existing systems",
            "legal_compliance": "Compliance and legal requirements",
            "technical_knowledge": "Lack of technical knowledge",
            "uncertain_use_cases": "Unsure where AI would be useful",
            "none": "No significant concerns",
            "other": "Other (please specify)"
        },
        "desired_outcome": {
            "save_time": "Save employee time",
            "reduce_costs": "Reduce operating costs",
            "increase_revenue": "Increase sales or revenue",
            "faster_responses": "Improve customer response times",
            "reduce_errors": "Reduce mistakes or rework",
            "improve_satisfaction": "Improve customer satisfaction",
            "scale_without_staff_growth": "Support business growth without proportionately increasing staff",
            "other": "Other (please specify)"
        },
        "followup_interest": {
            "yes": "Yes, I'd be interested in a discussion",
            "maybe": "Maybe, I'd like to learn more first",
            "not_now": "Not at the moment"
        }
    }
}


class TemplateContractTests(unittest.TestCase):
    def test_exact_headers_order_counts_and_no_response_rows(self):
        names = {"survey": "survey_responses", "discovery": "discovery_assessments", "contacts": "contacts_and_consent"}
        for kind, name in names.items():
            with (ROOT / "templates" / (name + "_template.csv")).open(encoding="utf-8", newline="") as handle:
                rows = list(csv.reader(handle))
            self.assertEqual(rows, [EXPECTED["headers"][kind]])
            self.assertEqual(COLUMNS[kind], EXPECTED["headers"][kind])

    def test_all_19_survey_questions_exact_wording_and_labels(self):
        text = (ROOT / "templates/business_opportunity_survey.md").read_text(encoding="utf-8")
        self.assertEqual(re.findall(r"^## (S\d{2})$", text, re.M), [f"S{i:02d}" for i in range(1, 20)])
        for wording in EXPECTED["survey"]:
            self.assertIn(wording, text)
        for choices in EXPECTED["labels"].values():
            for label in choices.values():
                self.assertIn(label, text)

    def test_all_24_discovery_questions_exact_wording(self):
        text = (ROOT / "templates/business_opportunity_discovery.md").read_text(encoding="utf-8")
        self.assertEqual(re.findall(r"^## (D\d{2}) —", text, re.M), [f"D{i:02d}" for i in range(1, 25)])
        for wording in EXPECTED["discovery"]:
            self.assertIn(wording, text)

    def test_dictionary_covers_every_column_and_survey_mapping(self):
        text = (ROOT / "templates/data_dictionary.md").read_text(encoding="utf-8")
        documented = re.findall(r"^\| `([a-z_]+)` \|", text, re.M)
        for column in set(sum(EXPECTED["headers"].values(), [])):
            self.assertIn(column, documented)
        for choices in EXPECTED["labels"].values():
            for code, label in choices.items():
                self.assertIn(f"| `{code}` | {label} |", text)

    def test_examples_and_templates_are_generically_branded(self):
        paths = [ROOT / "README.md", *list((ROOT / "templates").glob("*.md")),
                 ROOT / "templates/example_organisation_config.yaml", ROOT / "scripts/template_pack_example.py"]
        for path in paths:
            text = path.read_text(encoding="utf-8")
            self.assertNotRegex(text.lower(), r"\btaa\b|agentdote|the ai architects|shyam")

    def test_no_actual_contacts_in_csv_templates_or_public_artifacts(self):
        # Current artifact check only; a future public demo needs its own export tests.
        for path in (ROOT / "templates").glob("*.csv"):
            with path.open(encoding="utf-8", newline="") as handle:
                self.assertEqual(len(list(csv.reader(handle))), 1)
        for dirname in ("public", "dist"):
            if (ROOT / dirname).exists():
                self.assertEqual(list((ROOT / dirname).rglob("*contacts*csv")), [])

    def test_fictional_example_contacts_use_reserved_domain(self):
        from scripts.template_pack_example import example_records
        _, _, contacts = example_records()
        self.assertTrue(all(r["email"].endswith(".invalid") for r in contacts))
        self.assertTrue(all("Fictional" in r["contact_name"] for r in contacts))

    def test_configuration_preserves_baseline_thresholds(self):
        text = (ROOT / "templates/example_organisation_config.yaml").read_text(encoding="utf-8")
        for expected in ("high_impact_threshold: 4", "minimum_group_size_warning: 5",
                         "complexity_simple_max: 2", "complexity_medium_max: 3"):
            self.assertIn(expected, text)


if __name__ == "__main__":
    unittest.main()
