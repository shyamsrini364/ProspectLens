"""One fictional linked example; prints results and writes no dataset files."""

import json

from src.data_validation import (
    contact_ready_response_ids, pain_point_prevalence,
    survey_with_discovery, validate_dataset,
)


def example_records():
    survey = [{
        "response_id": "R0001", "prospect_id": "P0001", "dataset_version": "1.0",
        "questionnaire_version": "1.0", "submitted_at": "2026-10-10T09:00:00+11:00",
        "industry": "professional_services", "employee_band": "2_5",
        "pain_points": '["manual_data_entry", "reporting_analysis"]',
        "primary_pain_point": "manual_data_entry", "weekly_hours_band": "6_10",
        "impact_rating": "4", "current_process": "mostly_manual",
        "followup_interest": "yes",
    }]
    discovery = [{
        "assessment_id": "D0001", "prospect_id": "P0001", "workflow_id": "W0001",
        "dataset_version": "1.0", "questionnaire_version": "1.0",
        "assessment_date": "2026-10-10", "workflow_name": "Fictional invoice entry",
        "activity_volume": "40", "volume_period": "week", "minutes_per_instance": "10",
        "staff_count": "2", "reported_staff_hours_per_week": "7",
        "source_reference": "Fictional interview: minutes are total person-minutes per occurrence.",
        "systems_involved": '["Example spreadsheet"]', "evidence_status": "self_reported",
        "integration_capability": "not_investigated", "recommended_next_action": "further_discovery",
    }]
    contacts = [{
        "response_id": "R0001", "prospect_id": "P0001",
        "contact_name": "Fictional Respondent", "business_name": "Fictional Example Business",
        "email": "respondent@example.invalid", "privacy_acknowledged": "true",
        "privacy_notice_version": "EXAMPLE-1.0", "followup_consent": "false",
        "marketing_consent": "false", "consent_recorded_at": "2026-10-10T09:00:00+11:00",
    }]
    return survey, discovery, contacts


def main():
    survey, discovery, contacts = example_records()
    result = validate_dataset(survey, discovery, contacts)
    result.require_valid()
    joined = survey_with_discovery(result)
    print("SYNTHETIC DATA — NOT REAL MARKET FINDINGS")
    print(json.dumps({
        "validation": {"errors": len(result.errors), "warnings": len(result.warnings)},
        "survey_input": survey[0],
        "discovery_input": discovery[0],
        "joined_assessment_ids": [r["assessment_id"] for r in joined[0]["assessments"]],
        "unassessed_complexity": result.discovery[0]["implementation_complexity"],
        "pain_point_prevalence": pain_point_prevalence(result),
        "contact_ready_response_ids": contact_ready_response_ids(result),
        "contact_eligibility_note": "Interest is yes, but follow-up permission is false.",
    }, indent=2))


if __name__ == "__main__":
    main()
