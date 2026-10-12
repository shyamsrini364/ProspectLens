"""Context for fictional businesses; no real customer data or verified integrations.

Catalogues supply vocabulary, while seeded draws vary the actual records. Hidden
context is used only during generation and never adds columns to the v1.0 CSVs.
"""

import json
import random


# Industry-specific business types, records and staff roles.
SECTORS = {
    "professional_services": [("accounting practice", "client files", "Practice manager", "PracticeDesk", "Advisory"),
                              ("design consultancy", "project briefs", "Project coordinator", "BriefLedger", "Design")],
    "healthcare_allied": [("physiotherapy clinic", "referral forms", "Clinic administrator", "CareRoster", "Allied Health"),
                          ("speech therapy practice", "intake forms", "Practice coordinator", "ReferralDesk", "Therapy")],
    "retail_ecommerce": [("online homewares shop", "customer orders", "Store manager", "OrderHarbour", "Homewares"),
                         ("specialty retail store", "return requests", "Retail supervisor", "StockNest", "Retail")],
    "trades_construction": [("electrical contractor", "job sheets", "Office coordinator", "TradeLedger", "Electrical"),
                            ("building maintenance firm", "work orders", "Service dispatcher", "SiteRoster", "Maintenance")],
    "hospitality": [("neighbourhood cafe", "booking requests", "Venue manager", "TableLedger", "Cafe"),
                    ("small catering company", "event briefs", "Events coordinator", "CateringDesk", "Catering")],
    "real_estate": [("property management agency", "maintenance requests", "Property manager", "TenancyDesk", "Property"),
                    ("residential sales agency", "buyer enquiries", "Sales administrator", "ListingLedger", "Real Estate")],
    "manufacturing_logistics": [("small component manufacturer", "production orders", "Production planner", "BatchLedger", "Manufacturing"),
                                ("regional freight operator", "delivery records", "Dispatch coordinator", "FreightRoster", "Logistics")],
    "education_training": [("vocational training provider", "enrolment forms", "Training coordinator", "CourseLedger", "Training"),
                           ("tutoring centre", "lesson bookings", "Centre administrator", "LessonDesk", "Tutoring")],
    "other": [("community equipment hire service", "equipment returns", "Hire coordinator", "AssetRoster", "Equipment Hire"),
              ("pet grooming studio", "service bookings", "Studio manager", "GroomingDesk", "Grooming")],
}

SOFTWARE = {
    "crm": ("HubSpot", "Pipedrive", "Zoho CRM"),
    "accounting_invoicing": ("Xero", "MYOB", "QuickBooks"),
    "booking_scheduling": ("Calendly", "Microsoft Bookings", "Acuity Scheduling"),
    "task_management": ("Asana", "Monday.com", "ClickUp"),
    "spreadsheets": ("Microsoft Excel", "Google Sheets"),
    "email_messaging": ("Microsoft Outlook", "Gmail", "Microsoft Teams"),
}
PAID_CATEGORIES = {"crm", "accounting_invoicing", "booking_scheduling", "task_management", "industry_specific", "other"}

# Each entry describes the object, work, delays and measurable success of a workflow.
# The two base workflow names remain in the generator; this context makes them concrete.
PROCESS = {
    "customer_enquiries": ("enquiry", "read the message, identify its topic and draft a reply", "messages wait in a shared inbox", "duplicate questions need the same answer", [3, 6, 10, 15], 400),
    "sales_followup": ("lead", "check the last conversation, prepare a follow-up and update the lead record", "next actions are missing from notes", "follow-up dates are kept in separate lists", [8, 12, 20, 30], 120),
    "appointment_scheduling": ("booking", "check availability, confirm the appointment and prepare a reminder", "changes arrive through several channels", "cancellations are not reflected in every diary", [3, 5, 8, 12], 300),
    "manual_data_entry": ("record", "read the source, copy the fields and check the entry against the original", "the same details are entered twice", "handwritten fields need clarification", [4, 8, 12, 18], 400),
    "reporting_analysis": ("report", "collect figures, reconcile totals, investigate exceptions and prepare the commentary", "source files arrive with different cut-off dates", "totals need manual reconciliation", [45, 60, 90, 120], 5),
    "documents_information": ("document", "check its version, tag it, file it and notify the person responsible", "file names do not identify the latest version", "attachments are stored in individual inboxes", [5, 10, 15, 25], 150),
    "finance_invoicing": ("invoice", "match the reference, check the balance and prepare the approval or reminder", "purchase references are missing", "disputed balances need a separate review", [5, 10, 15, 20], 150),
    "staff_coordination": ("roster change", "check availability, obtain agreement and update the roster", "availability changes arrive after the roster is drafted", "staff reply to different message threads", [10, 15, 25, 40], 40),
    "customer_support": ("support case", "review the history, draft a response and route exceptions to a supervisor", "the customer repeats information already supplied", "case ownership is unclear after handover", [8, 15, 25, 35], 150),
    "marketing_content": ("content item", "prepare a brief, draft the content, obtain approval and schedule publication", "feedback arrives in several versions", "approval holds up scheduled posts", [20, 35, 50, 75], 15),
    "other": ("operational check", "inspect the record, identify missing items and request sign-off", "exceptions are recorded only in a notebook", "supporting records are hard to find", [10, 20, 30, 45], 40),
}
CONCERNS = {
    "cost_roi": ("We cannot justify another subscription until we know who will use it each week.", "The setup cost matters more than the monthly fee; we need a small trial first."),
    "privacy_security": ("We do not want customer details copied into an unapproved tool.", "We need to know which staff can access prompts and uploaded files."),
    "accuracy_reliability": ("A plausible but wrong answer could create extra checking work.", "Staff must be able to spot incorrect dates, amounts and commitments before sending a reply."),
    "staff_adoption": ("Our busiest staff have little time to learn a new process.", "We need a named owner and simple instructions so the tool does not get abandoned."),
    "systems_integration": ("We want to avoid maintaining another disconnected list of records.", "Our existing system exports limited fields, so duplicate entry may remain."),
    "legal_compliance": ("We need an agreed approval process before changing customer-facing work.", "We want the retention and review responsibilities documented before a pilot."),
    "technical_knowledge": ("We have no internal specialist to troubleshoot failures.", "We need clear support arrangements once the initial setup is finished."),
    "uncertain_use_cases": ("We can see many possible uses but cannot identify the best first problem.", "We need to compare a small number of tasks before choosing a trial."),
    "other": ("We worry about becoming dependent on a single supplier.", "We need the service to remain usable when internet access is unreliable."),
}
OUTCOME_OTHER = ("Make handovers less dependent on one experienced employee", "Improve visibility of supplier commitments", "Keep service quality consistent during seasonal peaks", "Make ownership of follow-up work clearer")


def context_for(row):
    """Stable per-business vocabulary, independent of changing AI descriptions."""
    number = int(row["prospect_id"][1:])
    sector = SECTORS[row["industry"]][number % 2]
    return dict(zip(("business_type", "records", "role", "sector_system", "suffix"), sector))


def installed_tools(row, context):
    """Reuse the same software identities everywhere for a given business."""
    number = int(row["prospect_id"][1:])
    tools = {}
    for category in json.loads(row["business_systems"]):
        if category in SOFTWARE:
            choices = SOFTWARE[category]
            tools[category] = choices[(number + len(category)) % len(choices)]
        elif category == "industry_specific":
            tools[category] = context["sector_system"] + " (fictional)"
        elif category == "other":
            tools[category] = ("FormLedger", "AssetNotebook", "QuoteBoard")[number % 3] + " (fictional)"
        elif category == "none_paper":
            tools[category] = "Paper register and printed forms"
    return tools


def enrich_surveys(rows, seed):
    """Replace placeholder text and repair only related categorical contradictions."""
    rng = random.Random(seed)
    for row in rows:
        context = context_for(row)
        pain = row["primary_pain_point"] or "other"
        process = PROCESS[pain]
        if row["industry_other"]:
            row["industry_other"] = context["business_type"].capitalize()
        if row["pain_points_other"]:
            row["pain_points_other"] = rng.choice(("Tracking supplier renewals", "Checking equipment handovers", "Managing stock discrepancies", "Coordinating contractor access"))
        if row["primary_pain_point"] == "other":
            row["primary_pain_point_other"] = row["pain_points_other"]
        categories = json.loads(row["business_systems"])
        if row["subscription_underuse"] in {"several", "one_or_two"}:
            minimum = 3 if row["subscription_underuse"] == "several" else 1
            # Several paid subscriptions cannot be supported by paper-only records.
            if categories == ["none_paper"]:
                row["subscription_underuse"] = "mostly_utilised"
                row["underused_software_names"] = ""
            else:
                for category in ("accounting_invoicing", "task_management", "crm"):
                    if len(PAID_CATEGORIES.intersection(categories)) >= minimum:
                        break
                    if category not in categories:
                        categories.append(category)
                row["business_systems"] = json.dumps(categories)
        tools = installed_tools(row, context)
        if row["business_systems_other"]:
            row["business_systems_other"] = tools["other"] + " for tracking local operational requests"
        if row["underused_software_names"]:
            paid = [name for category, name in tools.items() if category in PAID_CATEGORIES]
            count = 3 if row["subscription_underuse"] == "several" else min(len(paid), rng.randint(1, 2))
            row["underused_software_names"] = "; ".join(rng.sample(paid, count))
        concerns = json.loads(row["ai_concerns"])
        if row["ai_concerns_other"]:
            row["ai_concerns_other"] = rng.choice(CONCERNS["other"])
        if row["main_concern_details"]:
            concern = rng.choice([c for c in concerns if c != "none"])
            statement = row["ai_concerns_other"] if concern == "other" else rng.choice(CONCERNS[concern])
            row["main_concern_details"] = f"{statement} This matters when handling {context['records']}."
        if row["desired_outcome_other"]:
            row["desired_outcome_other"] = rng.choice(OUTCOME_OTHER)
        if row["additional_comments"]:
            circumstance = rng.choice(("Demand increases before month-end", "One experienced employee handles most exceptions", "We have recently added a new service", "Staff absences expose gaps in our handover notes"))
            interest_note = {"yes": "We could share a sample process in a discovery discussion.", "maybe": "We would like to see a practical example before deciding on a discussion.", "not_now": "We are not ready for a discussion this quarter."}[row["followup_interest"]]
            row["additional_comments"] = f"{circumstance} at our {context['business_type']}; {process[2]}. {interest_note}"


def enrich_contacts(rows, survey):
    """Keep permissions unchanged; business names describe their fictional sector."""
    by_prospect = {row["prospect_id"]: row for row in survey}
    for row in rows:
        context = context_for(by_prospect[row["prospect_id"]])
        row["business_name"] = row["business_name"].replace(" Works ", f" {context['suffix']} ")


def enrich_discoveries(rows, survey, seed):
    rng = random.Random(seed)
    by_prospect = {row["prospect_id"]: row for row in survey}
    for row in rows:
        answer = by_prospect[row["prospect_id"]]
        context = context_for(answer)
        pain = answer["primary_pain_point"] or "manual_data_entry"
        # Business vocabulary is not always the record type of this particular workflow.
        record_types = {"customer_enquiries": "customer enquiry messages", "sales_followup": "lead and proposal notes",
                        "appointment_scheduling": "booking requests", "reporting_analysis": "operational report inputs",
                        "staff_coordination": "staff availability records", "customer_support": "support case notes",
                        "marketing_content": "content briefs", "finance_invoicing": "invoice records", "other": "operational check records"}
        context["records"] = record_types.get(pain, context["records"])
        if "invoice" in row["workflow_name"].lower():
            context["records"] = "invoice records"
        elif "policy" in row["workflow_name"].lower():
            context["records"] = "policy documents"
        item, steps, delay, exception, minute_options, max_volume = PROCESS[pain]
        tools = installed_tools(answer, context)
        paper = "none_paper" in tools
        system_names = list(tools.values())
        # Numeric baselines describe this specific workflow, not the entire pain band.
        old_model = None
        if row["activity_volume"] and row["minutes_per_instance"]:
            old_model = float(row["activity_volume"]) * float(row["minutes_per_instance"]) / 60
        ratio = float(row["reported_staff_hours_per_week"]) / old_model if old_model and row["reported_staff_hours_per_week"] else rng.uniform(.85, 1.15)
        minutes = rng.choice(minute_options)
        volume = min(max_volume, max(1, round((old_model or rng.uniform(2, 8)) * 60 / minutes)))
        # Allow rounding, while keeping total person-hours within the stated staffing.
        volume = min(volume, max(1, int(int(row["staff_count"]) * 35 * 60 / (minutes * max(1, ratio)))))
        modelled = volume * minutes / 60
        if row["activity_volume"]:
            row["activity_volume"] = str(volume)
        if row["minutes_per_instance"]:
            row["minutes_per_instance"] = str(minutes)
        if row["reported_staff_hours_per_week"]:
            row["reported_staff_hours_per_week"] = str(round(modelled * ratio, 2))
        row["workflow_name"] = row["workflow_name"].replace("Monthly operational exception review", "Operational exception reporting") + f" - {context['business_type']}"
        operator = "owner-operator" if answer["employee_band"] == "solo" else context["role"].lower()
        review = "review exceptions before finalising" if int(row["staff_count"]) == 1 else "resolve exceptions with the business owner"
        row["workflow_steps"] = f"The {operator} follows these steps: receive {context['records']}; {steps}; {review}; record completion in {system_names[0]}."
        row["bottlenecks"] = f"For this {item} workflow, {delay}; {exception}."
        staff = int(row["staff_count"])
        roles = ["Owner-operator"] if answer["employee_band"] == "solo" else [context["role"], "Business owner", "Administration assistant", "Team supervisor"][:staff]
        row["stakeholders"] = json.dumps(roles)
        row["systems_involved"] = json.dumps(system_names)
        if row["information_storage"] != "unknown":
            row["information_storage"] = ("partly_paper" if paper else "central_system" if len(tools) == 1 and "spreadsheets" not in tools else "spreadsheets_documents" if set(tools).issubset({"spreadsheets", "email_messaging"}) else "multiple_systems")
        quality = int(row["data_quality_rating"])
        quality_notes = {1: "several required fields are absent and there is no consistent identifier", 2: "identifiers exist, but dates and names use mixed formats", 3: "most required fields are present; duplicate entries need review", 4: "required fields are consistently captured with occasional duplicate records", 5: "required fields and identifiers are consistently maintained with routine checks"}
        row["data_quality_evidence"] = f"Synthetic review of {context['records']}: {quality_notes[quality]}. Rating {quality}/5."
        standard = int(row["standardisation_rating"])
        row["exceptions_description"] = f"{exception.capitalize()}. " + ("Each case can follow a different approval route." if standard <= 2 else "The usual sequence is documented, but unusual cases still need a named reviewer." if standard == 3 else "Most cases follow the same documented sequence; exceptions are escalated separately.")
        if paper:
            row["integration_capability"] = "manual_only"
        integration = row["integration_capability"]
        evidence = {
            "confirmed_api": f"a sample record was retrieved from the fictional test interface for {system_names[0]}; production permissions still need checking",
            "file_export_import": f"a sample CSV from {system_names[0]} was reviewed; field mapping and the return import still need a pilot",
            "manual_only": f"records are currently transferred by a person from {system_names[0]}; no automated connection is confirmed",
            "not_investigated": f"access to {system_names[0]} has not been reviewed and no interface test has been performed",
            "unknown": f"the interviewee could not confirm export or API access for {system_names[0]}",
        }
        row["integration_evidence"] = f"Synthetic scenario only: {evidence[integration]}. This is not a verified vendor capability."
        requirements = ["human_approval", "role_based_access"]
        if answer["industry"] == "healthcare_allied":
            requirements += ["deidentified_test_data", "restricted_health_record_access"]
            safety = "Use de-identified referral/intake examples; clinical decisions remain with the treating professional."
        elif pain == "finance_invoicing":
            requirements += ["payment_change_verification", "audit_trail"]
            safety = "Bank-detail changes and disputed balances require separate staff verification; reminders are approved before sending."
        elif answer["sensitive_data_frequency"] == "frequent":
            requirements += ["redact_personal_details", "audit_trail"]
            safety = "Use redacted examples and restrict access to customer and employee details."
        else:
            requirements += ["output_review"]
            safety = "Keep drafts internal until a staff member checks the content and recipient."
        row["safety_requirements"] = json.dumps(requirements)
        row["safety_notes"] = f"For {row['workflow_name']}: {safety} Requirements are fictional discovery notes, not a compliance assessment."

        impact_types = ["delayed_responses", "errors_rework"]
        if pain == "sales_followup":
            impact_types = ["missed_sales", "delayed_responses"]
        elif pain == "customer_support":
            impact_types = ["complaints", "delayed_responses"]
        elif pain in {"reporting_analysis", "staff_coordination"}:
            impact_types = ["overtime", "errors_rework"]
        row["observed_impact_types"] = json.dumps(impact_types)
        row["business_impact_assessment"] = rng.choices(["low", "medium", "high", "unknown"],
            weights=[8, 30, 57, 5] if answer["impact_rating"] in {"4", "5"} else [30, 45, 15, 10])[0]
        sample = rng.choice([15, 20, 30])
        evidence_fragments = []
        observed_counts = {}
        for impact in impact_types:
            affected = rng.randint(2, 8)
            observed_counts[impact] = affected
            fragment = {
                "delayed_responses": f"{affected} of {sample} sampled {item} cases waited more than one working day for a response",
                "errors_rework": f"{affected} of {sample} sampled {item} cases needed correction or a second review",
                "missed_sales": f"{affected} of {sample} sampled leads had no recorded follow-up before their quote expired; lost revenue is not quantified",
                "complaints": f"{affected} of {sample} sampled support cases included a complaint about repeated explanations",
                "overtime": f"staff recalled {affected} additional hours during the last month to finish overdue {item} work; this is not a typical weekly baseline",
            }[impact]
            evidence_fragments.append(fragment)
        row["impact_evidence"] = "Fictional interview: " + "; ".join(evidence_fragments) + f". Reported cause: {delay}. These are illustrative observations, not real measurements."
        if ratio > 1.25:
            row["impact_evidence"] += " The reported hours also include handoffs omitted from the per-instance model; the difference is approximately 35%."
        # Vary the success measure while keeping units and direction explicit.
        if row["current_baseline"]:
            if pain in {"customer_enquiries", "customer_support", "sales_followup"}:
                baseline, unit, metric = rng.choice([4, 8, 12, 24, 48]), "elapsed hours", f"Elapsed time to the first reviewed response for each {item}"
            elif pain in {"manual_data_entry", "documents_information"}:
                baseline, unit, metric = round(100 * observed_counts["errors_rework"] / sample, 2), "percent requiring rework", f"Share of {context['records']} returned for correction"
            else:
                baseline, unit, metric = minutes, "person-minutes per occurrence", f"Total staff processing time per {item}"
            row.update(success_metric=metric + "; lower is better, and the proposed target requires a pilot.", current_baseline=str(baseline), target_unit=unit)
            if row["target_value"]:
                row["target_value"] = str(round(baseline * rng.uniform(.65, .9), 2))
        else:
            row.update(success_metric=f"Establish a reliable baseline for {item} processing time before choosing a target.", target_unit="person-minutes per occurrence")

        solo = answer["employee_band"] == "solo"
        large = answer["employee_band"] in {"21_50", "51_200", "over_200"}
        row["decision_authority"] = "interviewee" if solo else rng.choice(["department_manager", "multiple_stakeholders", "owner_director"] if large else ["owner_director", "interviewee", "unknown"])
        budget = row["budget_status"]
        if row["indicative_budget"]:
            row["indicative_budget"] = str(rng.choice([1000, 2000, 3500, 5000] if solo else [5000, 10000, 15000, 25000] if large else [2000, 3500, 6000, 10000]))
        if row["labour_cost_per_hour"]:
            row["labour_cost_per_hour"] = str(rng.choice([45, 60, 75, 90] if answer["industry"] == "professional_services" else [30, 38, 45, 55, 65]))
        row["implementation_timeline"] = rng.choice(["within_1_month", "within_1_to_3_months"] if budget == "approved" else ["within_1_to_3_months", "within_3_to_6_months"] if budget in {"indicative", "conditional_value_case"} else ["longer_term", "no_defined_timeline"])
        if integration in {"unknown", "not_investigated"} and row["technical_feasibility"]:
            row["technical_feasibility"] = "unknown"
        reuse = row["workflow_reuse_observation"]
        similarity = {"substantially_similar": "the same steps recur across comparable work queues", "partially_similar": "the intake steps recur, but approval routes vary", "business_specific": "local rules dominate the sequence and need a bespoke design", "unknown": "no comparable workflow has yet been reviewed"}[reuse]
        row["reuse_evidence"] = f"Synthetic comparison for {item} handling: {similarity}."
        row["solution_reusability"] = rng.choice(["medium", "high"] if reuse == "substantially_similar" else ["low", "medium"] if reuse == "partially_similar" else ["low"] if reuse == "business_specific" else ["unknown"])
        row["reusable_components"] = f"A {item} intake checklist, completeness checks and a staff review queue." if reuse != "unknown" else "No reusable components confirmed; compare another workflow first."
        row["customisation_needs"] = f"Map {context['records']} fields from {system_names[0]}; configure the {context['role'].lower()}'s approval rules and exceptions."
        row["additional_opportunities"] = json.dumps(rng.sample([f"Improve handover of {context['records']}", f"Review duplicate {item} records", f"Clarify ownership of overdue {item} work", "Consolidate subscription usage reports"], rng.randint(0, 3)))
        row["expansion_potential"] = "unknown" if not json.loads(row["additional_opportunities"]) else rng.choice(["low", "medium"] if solo else ["medium", "high"])
        if budget in {"none", "not_discussed"} and row["commercial_potential"] == "high":
            row["commercial_potential"] = "unknown" if budget == "not_discussed" else "medium"
        # Mixed evidence can support some measures while leaving feasibility unassessed.
        if row["pilot_interest"] == "no":
            action = "defer"
        elif row["technical_feasibility"] == "low":
            action = "process_improvement"
        elif integration in {"not_investigated", "unknown"}:
            action = "technical_feasibility_test"
        elif row["pilot_interest"] == "yes" and budget in {"approved", "indicative"} and row["technical_feasibility"] in {"medium", "high"}:
            action = "pilot_proposal"
        elif budget == "none":
            action = "process_improvement"
        else:
            action = "further_discovery"
        row["recommended_next_action"] = action
        complexity = row["implementation_complexity"] or "unassessed"
        feasibility = row["technical_feasibility"] or "unassessed"
        row["assessment_evidence"] = (f"Synthetic judgement for {row['workflow_name']}: complexity {complexity}, data quality {quality}/5, "
            f"standardisation {standard}/5 and integration {integration}. Feasibility is {feasibility}; commercial potential {row['commercial_potential']} "
            f"reflects budget {budget}, authority {row['decision_authority']} and pilot interest {row['pilot_interest']}. "
            f"Next step: {action}. {similarity.capitalize()}. No conversion or savings estimate is implied.")
        if row["evidence_status"] == "validated":
            row["assessment_evidence"] += " Synthetic role-play: document completeness and approval steps are assumed checked against a fictional walkthrough; missing measurements remain unverified."
        elif row["evidence_status"] == "unknown":
            row["assessment_evidence"] += " Evidence provenance is incomplete; treat these ratings as tentative."
        row["source_reference"] = f"Synthetic case {row['assessment_id']}, {row['assessment_date']}: {context['business_type']} interview and workflow notes; total person-minutes per occurrence. No real customer record."
