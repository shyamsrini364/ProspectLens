"""Reproducible fictional v1.0 data. Run: python -m scripts.generate_synthetic_data.

Generation, validation and writing are separate steps. All probabilities here
are demonstration design choices, not estimates of any real business population.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import platform
import random
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

from src.data_validation import validate_csv_files, validate_dataset
from src.schema import COLUMNS, ENUMS
from scripts.synthetic_profiles import enrich_contacts, enrich_discoveries, enrich_surveys

ROOT = Path(__file__).resolve().parents[1]
GENERATOR_VERSION = "1.2"
DISCLAIMER = "SYNTHETIC DATA - NOT REAL MARKET FINDINGS"
FILENAMES = {"survey": "survey_responses.csv", "discovery": "discovery_assessments.csv",
             "contacts": "contacts_and_consent.csv"}


@dataclass(frozen=True)
class GenerationConfig:
    seed: int = 20261010
    survey_count: int = 150
    discovery_count: int = 35
    currency: str = "AUD"

    def check(self):
        for name in ("seed", "survey_count", "discovery_count"):
            if type(getattr(self, name)) is not int:
                raise ValueError(f"{name} must be an integer")
        if self.survey_count < 0 or self.discovery_count < 0:
            raise ValueError("Record counts must be nonnegative")
        if self.discovery_count and not self.survey_count:
            raise ValueError("Discovery requires at least one survey prospect")
        if not self.currency.strip():
            raise ValueError("Currency must be explicit")


# Ordered weights align with existing canonical enums, not new response codes.
INDUSTRY_WEIGHTS = [29, 17, 14, 16, 8, 7, 5, 3, 1]
SIZE_WEIGHTS = [22, 31, 25, 13, 7, 2]
INDUSTRY_PAINS = {
    "professional_services": ["documents_information", "reporting_analysis", "manual_data_entry"],
    "healthcare_allied": ["appointment_scheduling", "documents_information", "manual_data_entry"],
    "retail_ecommerce": ["customer_support", "customer_enquiries", "marketing_content"],
    "trades_construction": ["finance_invoicing", "staff_coordination", "sales_followup"],
    "hospitality": ["staff_coordination", "appointment_scheduling", "customer_support"],
    "real_estate": ["sales_followup", "documents_information", "customer_enquiries"],
    "manufacturing_logistics": ["manual_data_entry", "reporting_analysis", "staff_coordination"],
    "education_training": ["appointment_scheduling", "customer_enquiries", "documents_information"],
    "other": ["manual_data_entry", "finance_invoicing", "other"],
}

# A pain category is deliberately broader than any one workflow design.
WORKFLOWS = {
    "customer_enquiries": ("Shared inbox enquiry routing", "Website quote-request triage"),
    "sales_followup": ("Proposal reminder follow-up", "New lead qualification handoff"),
    "appointment_scheduling": ("Appointment confirmation reminders", "Cancellation slot backfilling"),
    "manual_data_entry": ("Supplier invoice entry", "New customer record transcription"),
    "reporting_analysis": ("Weekly service performance reporting", "Monthly operational exception review"),
    "documents_information": ("Document intake and filing", "Policy version retrieval"),
    "finance_invoicing": ("Overdue invoice reminders", "Invoice approval routing"),
    "staff_coordination": ("Roster change approvals", "Shift availability collection"),
    "customer_support": ("Complaint escalation handoff", "Order status response handling"),
    "marketing_content": ("Content draft review and scheduling", "Campaign enquiry attribution"),
    "other": ("Equipment handover checks", "Supplier compliance renewal checks"),
}

# Fictional respondent descriptions, not verified integrations or vendor claims.
# These general assistants can be paired with text/formula drafting tasks below.
AI_ASSISTANTS = ("ChatGPT", "Claude", "Google Gemini", "Microsoft Copilot")
AI_TASKS_BY_PAIN = {
    "customer_enquiries": ("draft replies to common customer questions", "turn sample enquiries into a draft FAQ", "rewrite enquiry replies in plain language"),
    "sales_followup": ("draft follow-up emails after sales calls", "turn de-identified sales notes into proposal outlines", "prepare first drafts of outreach messages"),
    "appointment_scheduling": ("draft appointment reminder messages", "write cancellation and rescheduling message templates", "draft answers to booking questions"),
    "manual_data_entry": ("suggest spreadsheet formulas for cleaning copied records", "turn sample form entries into a draft table", "draft checklists for checking manually entered records"),
    "reporting_analysis": ("draft a narrative from non-confidential weekly figures", "suggest spreadsheet formulas for a monthly report", "summarise anonymised survey comments into themes"),
    "documents_information": ("summarise non-confidential procedure documents", "turn internal process notes into draft checklists", "rewrite draft instructions into a consistent format"),
    "finance_invoicing": ("draft overdue-invoice reminder emails", "suggest spreadsheet formulas for invoice reconciliation", "write a draft invoice-approval checklist"),
    "staff_coordination": ("draft staff handover checklists", "rewrite roster-change announcements", "turn team meeting notes into draft action lists"),
    "customer_support": ("draft complaint acknowledgement messages", "rewrite support replies in a calmer tone", "summarise de-identified support tickets into recurring issues"),
    "marketing_content": ("draft social media captions", "brainstorm newsletter topics", "write first drafts of product descriptions"),
    "other": ("draft equipment handover checklists", "write supplier renewal reminder templates", "turn process notes into staff instructions"),
}
AI_SECONDARY_USES = (
    ("Canva Magic Write", "draft captions for promotional posts"),
    ("Grammarly", "rewrite customer emails for clarity and tone"),
    ("Perplexity", "research background information for articles and review the cited sources"),
    ("ChatGPT", "brainstorm topics for staff training sessions"),
    ("Claude", "summarise non-confidential meeting notes into draft actions"),
    ("Google Gemini", "draft outlines for customer information sheets"),
    ("Microsoft Copilot", "draft agendas and staff update emails"),
)


def describe_ai_use(rng, row):
    """Answer the S14 follow-up with a named tool, task and adoption context."""
    adoption = row["ai_adoption"]
    if adoption not in {"regular_multiple", "limited_tasks", "experimented"}:
        return ""
    tool = rng.choice(AI_ASSISTANTS)
    task = rng.choice(AI_TASKS_BY_PAIN[row["primary_pain_point"] or "other"])
    uses = [(tool, task)]
    if adoption == "regular_multiple":
        secondary = [pair for pair in AI_SECONDARY_USES if pair[0] != tool]
        uses += rng.sample(secondary, rng.randint(1, 2))
        descriptions = "; ".join(f"{name} to {purpose}" for name, purpose in uses)
        return f"We regularly use {descriptions}. Staff check the outputs before using them."
    if adoption == "limited_tasks":
        return f"We use {tool} to {task}. This is an occasional, specific task; a staff member checks the result."
    return f"We tried {tool} to {task} using sample material. We have not made this part of our regular work."

# Teaching cases guarantee important exceptions when at least eight rows exist.
# They are intentionally designed cases, not independent statistical samples.
SURVEY_CASES = [
    {"current_process": "mostly_manual", "weekly_hours_band": "over_20", "impact_rating": "5",
     "followup_interest": "not_now", "primary_pain_point": "manual_data_entry", "employee_band": "6_20"},
    {"current_process": "mostly_software", "ai_adoption": "regular_multiple", "impact_rating": "5",
     "weekly_hours_band": "11_20", "followup_interest": "yes", "primary_pain_point": "manual_data_entry"},
    {"employee_band": "solo", "current_process": "mostly_software", "ai_adoption": "regular_multiple",
     "impact_rating": "4", "weekly_hours_band": "6_10", "followup_interest": "yes"},
    {"employee_band": "51_200", "current_process": "mostly_manual", "impact_rating": "4",
     "weekly_hours_band": "11_20", "followup_interest": "maybe"},
    {"impact_rating": "5", "followup_interest": "yes"},
    {"impact_rating": "5", "followup_interest": "yes"},
    {"impact_rating": "5", "followup_interest": "not_now"},
    {"current_process": "mostly_manual", "weekly_hours_band": "under_2", "impact_rating": "2"},
]


def choose(rng, column, weights=None):
    return rng.choices(ENUMS[column], weights=weights, k=1)[0]


def json_array(values):
    return json.dumps(values, ensure_ascii=False)


def blank_row(kind):
    return dict.fromkeys(COLUMNS[kind], "")


def sample_choices(rng, values, count, favourites=()):
    """Weighted sampling without replacement, preserving selection order."""
    available = list(values)
    selected = []
    for _ in range(min(count, len(available))):
        item = rng.choices(available, weights=[4 if v in favourites else 1 for v in available], k=1)[0]
        selected.append(item)
        available.remove(item)
    return selected


def make_surveys(rng, count, tools_rng):
    rows = []
    start = datetime(2026, 9, 1, 9, tzinfo=timezone(timedelta(hours=10)))
    for index in range(count):
        row = blank_row("survey")
        # One early case per industry, followed by uneven weighted sampling.
        industry = ENUMS["industry"][index] if index < len(ENUMS["industry"]) else choose(rng, "industry", INDUSTRY_WEIGHTS)
        size = choose(rng, "employee_band", SIZE_WEIGHTS)
        process = choose(rng, "current_process", [31, 42, 18, 6, 3])
        row.update(response_id=f"R{index + 1:04d}", prospect_id=f"P{index + 1:04d}",
                   submitted_at=(start + timedelta(days=rng.randrange(28), minutes=rng.randrange(480))).isoformat(),
                   dataset_version="1.0", questionnaire_version="1.0", industry=industry,
                   employee_band=size, current_process=process,
                   recruitment_channel=choose(rng, "recruitment_channel", [20, 35, 20, 15, 5, 5]))
        if index < len(SURVEY_CASES):
            row.update(SURVEY_CASES[index])
        size, process = row["employee_band"], row["current_process"]
        manual = process in {"mostly_manual", "mixed_manual_digital"}
        high_work_weights = [6, 16, 28, 28, 17, 5] if manual else [17, 28, 25, 16, 9, 5]
        row["weekly_hours_band"] = row["weekly_hours_band"] or choose(rng, "weekly_hours_band", high_work_weights)
        busy = row["weekly_hours_band"] in {"11_20", "over_20"}
        row["impact_rating"] = row["impact_rating"] or str(rng.choices([1, 2, 3, 4, 5], [3, 9, 22, 36, 30] if busy else [9, 22, 32, 25, 12])[0])
        pain = sample_choices(rng, ENUMS["pain_points"], rng.choices([1, 2, 3], [15, 45, 40])[0], INDUSTRY_PAINS[industry])
        if row["primary_pain_point"]:
            pain = [row["primary_pain_point"]] + [p for p in pain if p != row["primary_pain_point"]][:2]
        else:
            row["primary_pain_point"] = rng.choice(pain)
        row["pain_points"] = json_array(pain)
        row["industry_other"] = "Fictional community equipment services" if industry == "other" else ""
        row["pain_points_other"] = "Equipment handover and supplier checks" if "other" in pain else ""
        row["primary_pain_point_other"] = row["pain_points_other"] if row["primary_pain_point"] == "other" else ""
        row["sensitive_data_frequency"] = choose(rng, "sensitive_data_frequency", [65, 25, 5, 5] if industry in {"healthcare_allied", "professional_services"} else [22, 42, 30, 6])

        # Software count depends loosely on size, with intentional exceptions.
        large = size in {"21_50", "51_200", "over_200"}
        system_count = rng.randint(3, 6) if large else rng.randint(1, 4)
        if index == 2:
            system_count = 6  # a highly digital solo business
        systems = sample_choices(rng, [c for c in ENUMS["business_systems"] if c != "none_paper"], system_count,
                                 ["email_messaging", "spreadsheets", "accounting_invoicing"])
        if (process == "mostly_manual" and rng.random() < 0.13) or index == 3:
            systems = ["none_paper"]
        row["business_systems"] = json_array(systems)
        row["business_systems_other"] = "Fictional equipment register" if "other" in systems else ""
        row["subscription_underuse"] = "mostly_utilised" if systems == ["none_paper"] else choose(rng, "subscription_underuse", [25, 40, 25, 10])
        if row["subscription_underuse"] in {"several", "one_or_two"} and rng.random() < 0.7:
            row["underused_software_names"] = "Example task manager; Example document workspace"
        row["ai_adoption"] = row["ai_adoption"] or choose(rng, "ai_adoption", [7, 20, 26, 41, 6] if manual else [28, 35, 22, 10, 5])
        if row["ai_adoption"] in {"regular_multiple", "limited_tasks", "experimented"} and rng.random() < 0.85:
            row["ai_tools_and_uses"] = describe_ai_use(tools_rng, row)
        concerns = sample_choices(rng, [v for v in ENUMS["ai_concerns"] if v != "none"], rng.randint(1, 4),
                                  ["privacy_security", "accuracy_reliability"] if row["sensitive_data_frequency"] == "frequent" else ["cost_roi", "staff_adoption"])
        if rng.random() < 0.1:
            concerns = ["none"]
        row["ai_concerns"] = json_array(concerns)
        row["ai_concerns_other"] = "Dependence on one supplier" if "other" in concerns else ""
        if concerns != ["none"] and rng.random() < 0.5:
            row["main_concern_details"] = "We need evidence of value and a clear staff review process before changing the workflow."
        outcomes = [25, 14, 15, 12, 13, 10, 9, 2]
        if row["primary_pain_point"] in {"customer_enquiries", "customer_support"}:
            outcomes = [12, 8, 12, 30, 8, 23, 5, 2]
        row["desired_outcome"] = choose(rng, "desired_outcome", outcomes)
        row["desired_outcome_other"] = "Improve supplier coordination" if row["desired_outcome"] == "other" else ""
        row["followup_interest"] = row["followup_interest"] or choose(rng, "followup_interest", [40, 35, 25])
        if rng.random() < 0.25:
            row["additional_comments"] = "Fictional case: seasonal demand and staff availability affect our answers."

        # Controlled missing answers, after the eight teaching cases.
        if index >= 8:
            for column, rate in (("employee_band", .03), ("recruitment_channel", .04),
                                 ("ai_adoption", .03), ("impact_rating", .025), ("weekly_hours_band", .035)):
                if rng.random() < rate:
                    row[column] = ""
                    if column == "ai_adoption":
                        row["ai_tools_and_uses"] = ""
            if index % 37 == 0:
                row.update(pain_points="", pain_points_other="", primary_pain_point="", primary_pain_point_other="")
        rows.append(row)
    return rows


def make_contacts(rng, survey):
    rows = []
    for index, answer in enumerate(survey):
        row = blank_row("contacts")
        # Permission probabilities are independent of survey interest and each other.
        row.update(response_id=answer["response_id"], prospect_id=answer["prospect_id"],
                   contact_name=f"Fictional {rng.choice(['Nerali', 'Ovelin', 'Taviri', 'Meravo', 'Luneri', 'Soravi', 'Kelora', 'Amveli', 'Noriva', 'Teleri', 'Vesali', 'Omrien', 'Raleni', 'Delavo', 'Yavina', 'Elvari'])} {rng.choice(['Velnor', 'Talven', 'Roveli', 'Senvar', 'Morilan', 'Kelvane', 'Daviren', 'Solven', 'Neralis', 'Orevane', 'Trenali', 'Veloran', 'Sarneli', 'Lomvare', 'Arvendi', 'Nolvari'])} {index + 1:04d}",
                   business_name=f"Fictional {rng.choice(['Amber', 'Cedar', 'Cloud', 'Pebble'])} {rng.choice(['Lantern', 'Orbit', 'Meadow', 'Harbour'])} Works {index + 1:04d}",
                   email=f"person{index + 1:04d}@example.invalid",
                   privacy_acknowledged="true", privacy_notice_version="SYNTHETIC-EXAMPLE-1.0",
                   followup_consent=rng.choices(["true", "false", ""], [52, 42, 6])[0],
                   marketing_consent=rng.choices(["true", "false", ""], [24, 70, 6])[0],
                   consent_recorded_at=answer["submitted_at"])
        if rng.random() < .06:
            row["email"] = ""
        # Deliberate mismatches that any future shortlist must handle correctly.
        if index == 0:
            row.update(followup_consent="false", marketing_consent="true")
        elif index == 1:
            row.update(followup_consent="false", marketing_consent="true")
        elif index in {2, 3}:
            row.update(followup_consent="true", email=f"person{index + 1:04d}@example.invalid")
        elif index == 4:
            row["followup_consent"] = ""
        elif index == 5:
            row.update(followup_consent="true", email="")
        elif index == 6:
            row["followup_consent"] = "true"
        rows.append(row)
    return rows


def make_discoveries(rng, survey, count, currency):
    if not count:
        return []
    # Default: 27 of 150 prospects, with 8 additional workflows among that subset.
    covered = min(len(survey), max(1, round(count * .77)))
    anchors = list(range(min(8, covered)))
    selected = anchors + rng.sample(list(range(len(anchors), len(survey))), covered - len(anchors))
    assignments = selected + [rng.choice(selected) for _ in range(count - covered)]
    occurrences = Counter()
    rows = []
    band_hours = {"under_2": (0.5, 1.9), "2_5": (2, 5), "6_10": (6, 10),
                  "11_20": (11, 20), "over_20": (22, 36), "unsure": (2, 16), "": (2, 16)}
    for index, survey_index in enumerate(assignments):
        answer = survey[survey_index]
        prospect = answer["prospect_id"]
        occurrences[prospect] += 1
        workflow_number = occurrences[prospect]
        pain = answer["primary_pain_point"] or "manual_data_entry"
        variant = (workflow_number - 1 + survey_index) % 2
        workflow = WORKFLOWS[pain][variant]
        # Suffix keeps later custom-count workflows distinct without implying reassessment.
        if workflow_number > 2:
            workflow += f" - team {workflow_number}"
        row = blank_row("discovery")
        staff = 1 if answer["employee_band"] == "solo" else rng.randint(1, 4)
        target_hours = rng.uniform(*band_hours[answer["weekly_hours_band"]])
        # Discovery can have a narrower scope or reveal omitted work.
        target_hours *= rng.uniform(.65, 1.35) if workflow_number == 1 else rng.uniform(.25, .75)
        target_hours = min(target_hours, staff * 25)
        minutes = rng.choice([4, 8, 12, 18, 25, 35])
        volume = max(1, round(target_hours * 60 / minutes))
        modelled = volume * minutes / 60
        reported = round(modelled * rng.uniform(.85, 1.15), 2)
        if index % 12 == 7:
            reported = round(modelled * 1.35, 2)  # explicit recollection/scope discrepancy
        staff = max(staff, math.ceil(reported / 35))
        quality = rng.choices([1, 2, 3, 4, 5], [8, 17, 35, 28, 12])[0]
        standard = rng.randint(1, 5)
        integration = choose(rng, "integration_capability", [22, 33, 18, 20, 7])
        complexity = min(5, max(1, 3 + (quality <= 2) + (integration == "manual_only") - (standard >= 4) + rng.choice([-1, 0, 1])))
        budget = choose(rng, "budget_status", [15, 24, 26, 18, 17])
        commercial = choose(rng, "commercial_potential", [12, 32, 48, 8] if budget in {"approved", "indicative"} else [36, 34, 15, 15])
        feasibility = choose(rng, "technical_feasibility", [12, 30, 52, 6] if integration == "confirmed_api" else [24, 36, 15, 25])
        # Explicit contrasting cases: commercial promise does not equal easy delivery.
        if index == 0:
            complexity, commercial, integration, budget, feasibility = 5, "high", "manual_only", "conditional_value_case", "medium"
        elif index == 1:
            complexity, commercial, integration, budget, feasibility = 2, "high", "confirmed_api", "approved", "high"
        elif index == 2:
            complexity, integration, feasibility = 4, "not_investigated", "unknown"
        systems = ["Example document workspace", "Example operations system"]
        if answer["business_systems"] == '["none_paper"]':
            systems = ["Paper register", "Example shared spreadsheet"]
        discovery_date = datetime.fromisoformat(answer["submitted_at"]) + timedelta(days=rng.randint(2, 10))
        row.update(assessment_id=f"D{index + 1:04d}", prospect_id=prospect, workflow_id=f"W{workflow_number:04d}",
                   assessment_date=discovery_date.date().isoformat(), assessor_id=f"SYNTHETIC-ASSESSOR-{index % 3 + 1}",
                   source_reference=f"Synthetic interview {index + 1:04d}; fabricated inputs; time basis is total person-minutes per occurrence.",
                   dataset_version="1.0", questionnaire_version="1.0", workflow_name=workflow,
                   workflow_steps=f"Receive input for {workflow.lower()}; check completeness; enter or route the record; obtain staff approval; record completion.",
                   stakeholders=json_array(["Process owner", "Operations coordinator"] if staff > 1 else ["Owner-operator"]),
                   bottlenecks=rng.choice(["Duplicate entry and missing information delay completion.", "Approval queues require repeated manual reminders.", "Exceptions interrupt otherwise standard processing."]),
                   activity_volume=str(volume), volume_period="week", minutes_per_instance=str(minutes), staff_count=str(staff),
                   reported_staff_hours_per_week=str(reported), currency=currency,
                   observed_impact_types=json_array(sample_choices(rng, ENUMS["observed_impact_types"], rng.randint(1, 3), ["errors_rework", "delayed_responses"])),
                   impact_evidence="Fictional interview describes repeated handoffs, rework and delay; no real business observation.",
                   success_metric="Staff processing minutes per occurrence; proposed target is an aspiration, not a savings promise.",
                   current_baseline=str(minutes), target_value=str(round(minutes * rng.uniform(.65, .9), 2)), target_unit="person-minutes per occurrence",
                   systems_involved=json_array(systems), information_storage=choose(rng, "information_storage", [20, 30, 35, 10, 5]),
                   data_quality_rating=str(quality), data_quality_evidence=f"Synthetic assessment: quality {quality}/5 reflects completeness and consistency in the fictional case.",
                   integration_capability=integration,
                   integration_evidence="Synthetic scenario assumes a documented API and test access were checked; no real vendor capability was verified." if integration == "confirmed_api" else "Synthetic scenario: export/manual-access constraints remain subject to investigation.",
                   standardisation_rating=str(standard), exceptions_description="Missing references, unusual requests and approval exceptions require human review.",
                   safety_requirements=json_array(["role_based_access", "human_approval", "audit_trail"] + (["sensitive_record_review"] if answer["sensitive_data_frequency"] == "frequent" else [])),
                   safety_notes="Fictional scenario: use minimum necessary data and obtain staff approval before external actions.",
                   decision_authority=choose(rng, "decision_authority"), implementation_timeline=choose(rng, "implementation_timeline"),
                   budget_status=budget, pilot_interest=choose(rng, "pilot_interest", [42, 33, 15, 10]),
                   workflow_reuse_observation=choose(rng, "workflow_reuse_observation", [32, 38, 20, 10]),
                   reuse_evidence="Synthetic comparison: intake and review steps recur, but permissions and exception handling differ.",
                   reusable_components="Input checklist, routing rules and review queue.", customisation_needs="Local approval roles, field mappings and exception rules.",
                   additional_opportunities=json_array(rng.sample(["Related reconciliation workflow", "Staff handover quality review", "Supplier renewal reminders", "Management reporting handoff"], rng.randint(0, 3))),
                   business_impact_assessment="high" if answer["impact_rating"] in {"4", "5"} else choose(rng, "business_impact_assessment"),
                   commercial_potential=commercial, solution_reusability=choose(rng, "solution_reusability", [15, 40, 35, 10]),
                   technical_feasibility=feasibility, implementation_complexity=str(complexity),
                   expansion_potential=choose(rng, "expansion_potential", [20, 35, 30, 15]),
                   assessment_evidence=f"Fictional consultant judgement: complexity {complexity}/5 considers data quality, exceptions and {integration}; commercial judgement considers {budget}. Not a sales or ROI prediction.",
                   evidence_status=choose(rng, "evidence_status", [30, 50, 15, 5]),
                   recommended_next_action="technical_feasibility_test" if integration in {"not_investigated", "unknown"} else choose(rng, "recommended_next_action"))
        if rng.random() < .65:
            row["labour_cost_per_hour"] = str(rng.choice([35, 45, 60, 80, 100, 120]))
        if budget in {"approved", "indicative", "conditional_value_case"} and rng.random() < .8:
            row["indicative_budget"] = str(rng.choice([1500, 3000, 6000, 12000, 25000]))
        if row["evidence_status"] == "validated":
            row["assessment_evidence"] += " Synthetic role-play only: occurrence count and total person-minute basis are assumed checked against a fictional process log."
        if index % 12 == 7:
            row["impact_evidence"] += " Reported hours include extra handoff time; modelled and reported baselines deliberately differ by about 35%."

        # Preserve distinct missing, unknown and not-investigated states.
        if index % 9 == 8:
            row["implementation_complexity"] = ""
            row["assessment_evidence"] = "Fictional assessment incomplete: complexity not yet assessed; budget and system constraints still need review."
            row["evidence_status"] = "consultant_assessed"
        if index % 7 == 6:
            row["technical_feasibility"] = "unknown"
        if index % 11 == 10:
            row.update(technical_feasibility="", reported_staff_hours_per_week="", target_value="")
        if index % 13 == 12:
            row.update(minutes_per_instance="", current_baseline="", target_value="")
        if index % 17 == 16:
            row["activity_volume"] = ""
        if index % 19 == 18:
            row["volume_period"] = "unknown"
        rows.append(row)
    return rows


def generate_datasets(config=GenerationConfig()):
    """Pure generation: no file writes, validator calls, clock or network access."""
    config.check()
    # Separate streams prevent discovery count changes from altering survey/contact data.
    survey = make_surveys(random.Random(config.seed), config.survey_count, random.Random(config.seed + 3))
    enrich_surveys(survey, config.seed + 4)
    contacts = make_contacts(random.Random(config.seed + 1), survey)
    enrich_contacts(contacts, survey)
    discovery = make_discoveries(random.Random(config.seed + 2), survey, config.discovery_count, config.currency)
    enrich_discoveries(discovery, survey, config.seed + 5)
    return {"survey": survey, "discovery": discovery, "contacts": contacts}


def write_datasets(datasets, output_dir, config):
    """Write exact schema headers and deterministic UTF-8/LF bytes plus provenance."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    hashes = {}
    for kind, rows in datasets.items():
        path = output_dir / FILENAMES[kind]
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=COLUMNS[kind], lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
        hashes[FILENAMES[kind]] = hashlib.sha256(path.read_bytes()).hexdigest()
    manifest = {"disclaimer": DISCLAIMER, "generator_version": GENERATOR_VERSION,
                "dataset_version": "1.0", "configuration": asdict(config),
                "python_version": platform.python_version(), "sha256": hashes,
                "restricted_file": FILENAMES["contacts"]}
    (output_dir / "generation_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def main():
    parser = argparse.ArgumentParser(description=DISCLAIMER)
    parser.add_argument("--seed", type=int, default=20261010)
    parser.add_argument("--survey-count", type=int, default=150)
    parser.add_argument("--discovery-count", type=int, default=35)
    parser.add_argument("--currency", default="AUD")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "data/synthetic")
    args = parser.parse_args()
    config = GenerationConfig(args.seed, args.survey_count, args.discovery_count, args.currency)
    try:
        datasets = generate_datasets(config)
    except ValueError as exc:
        parser.error(str(exc))
    result = validate_dataset(**datasets)
    result.require_valid()  # Never weaken validation to make generated rows pass.
    write_datasets(datasets, args.output_dir, config)
    result = validate_csv_files(*(args.output_dir / FILENAMES[k] for k in ("survey", "discovery", "contacts")))
    result.require_valid()  # Check the actual serialized files as well.
    print(DISCLAIMER)
    print(json.dumps({"seed": config.seed, "rows": {k: len(v) for k, v in datasets.items()},
                      "errors": len(result.errors), "warnings": len(result.warnings),
                      "warning_counts": dict(Counter(f"{i.dataset}.{i.column}: {i.issue}" for i in result.warnings))}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
