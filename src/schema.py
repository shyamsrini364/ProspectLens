"""Version 1.0 data contract. Standard library only; codes are case-sensitive."""

SURVEY_COLUMNS = [
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
]
DISCOVERY_COLUMNS = [
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
CONTACT_COLUMNS = [
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
]
COLUMNS = {"survey": SURVEY_COLUMNS, "discovery": DISCOVERY_COLUMNS, "contacts": CONTACT_COLUMNS}
REQUIRED = {
    "survey": [
        "response_id",
        "prospect_id",
        "dataset_version"
    ],
    "discovery": [
        "assessment_id",
        "prospect_id",
        "workflow_id",
        "dataset_version"
    ],
    "contacts": [
        "response_id",
        "prospect_id"
    ]
}
ENUMS = {
    "industry": [
        "professional_services",
        "healthcare_allied",
        "retail_ecommerce",
        "trades_construction",
        "hospitality",
        "real_estate",
        "manufacturing_logistics",
        "education_training",
        "other"
    ],
    "employee_band": [
        "solo",
        "2_5",
        "6_20",
        "21_50",
        "51_200",
        "over_200"
    ],
    "pain_points": [
        "customer_enquiries",
        "sales_followup",
        "appointment_scheduling",
        "manual_data_entry",
        "reporting_analysis",
        "documents_information",
        "finance_invoicing",
        "staff_coordination",
        "customer_support",
        "marketing_content",
        "other"
    ],
    "primary_pain_point": [
        "customer_enquiries",
        "sales_followup",
        "appointment_scheduling",
        "manual_data_entry",
        "reporting_analysis",
        "documents_information",
        "finance_invoicing",
        "staff_coordination",
        "customer_support",
        "marketing_content",
        "other"
    ],
    "weekly_hours_band": [
        "under_2",
        "2_5",
        "6_10",
        "11_20",
        "over_20",
        "unsure"
    ],
    "current_process": [
        "mostly_manual",
        "mixed_manual_digital",
        "mostly_software",
        "automated_with_issues",
        "unsure"
    ],
    "sensitive_data_frequency": [
        "frequent",
        "sometimes",
        "rare_never",
        "unsure"
    ],
    "business_systems": [
        "crm",
        "accounting_invoicing",
        "booking_scheduling",
        "task_management",
        "spreadsheets",
        "email_messaging",
        "industry_specific",
        "none_paper",
        "other"
    ],
    "subscription_underuse": [
        "several",
        "one_or_two",
        "mostly_utilised",
        "unsure"
    ],
    "ai_adoption": [
        "regular_multiple",
        "limited_tasks",
        "experimented",
        "not_using",
        "unsure"
    ],
    "ai_concerns": [
        "cost_roi",
        "privacy_security",
        "accuracy_reliability",
        "staff_adoption",
        "systems_integration",
        "legal_compliance",
        "technical_knowledge",
        "uncertain_use_cases",
        "none",
        "other"
    ],
    "desired_outcome": [
        "save_time",
        "reduce_costs",
        "increase_revenue",
        "faster_responses",
        "reduce_errors",
        "improve_satisfaction",
        "scale_without_staff_growth",
        "other"
    ],
    "followup_interest": [
        "yes",
        "maybe",
        "not_now"
    ],
    "recruitment_channel": [
        "in_person",
        "direct_invitation",
        "referral",
        "website",
        "other",
        "unknown"
    ],
    "volume_period": [
        "day",
        "week",
        "month",
        "unknown"
    ],
    "information_storage": [
        "central_system",
        "multiple_systems",
        "spreadsheets_documents",
        "partly_paper",
        "unknown"
    ],
    "integration_capability": [
        "confirmed_api",
        "file_export_import",
        "manual_only",
        "not_investigated",
        "unknown"
    ],
    "decision_authority": [
        "interviewee",
        "owner_director",
        "department_manager",
        "multiple_stakeholders",
        "unknown"
    ],
    "implementation_timeline": [
        "within_1_month",
        "within_1_to_3_months",
        "within_3_to_6_months",
        "longer_term",
        "no_defined_timeline"
    ],
    "budget_status": [
        "approved",
        "indicative",
        "conditional_value_case",
        "none",
        "not_discussed"
    ],
    "pilot_interest": [
        "yes",
        "maybe",
        "no",
        "not_discussed"
    ],
    "workflow_reuse_observation": [
        "substantially_similar",
        "partially_similar",
        "business_specific",
        "unknown"
    ],
    "evidence_status": [
        "self_reported",
        "consultant_assessed",
        "validated",
        "unknown"
    ],
    "recommended_next_action": [
        "further_discovery",
        "process_improvement",
        "technical_feasibility_test",
        "pilot_proposal",
        "defer",
        "no_suitable_opportunity"
    ],
    "observed_impact_types": [
        "delayed_responses",
        "errors_rework",
        "missed_sales",
        "complaints",
        "extra_costs",
        "overtime",
        "other"
    ],
    "business_impact_assessment": [
        "low",
        "medium",
        "high",
        "unknown"
    ],
    "commercial_potential": [
        "low",
        "medium",
        "high",
        "unknown"
    ],
    "solution_reusability": [
        "low",
        "medium",
        "high",
        "unknown"
    ],
    "technical_feasibility": [
        "low",
        "medium",
        "high",
        "unknown"
    ],
    "expansion_potential": [
        "low",
        "medium",
        "high",
        "unknown"
    ]
}
SURVEY_LABELS = {
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
ARRAY_FIELDS = [
    "pain_points",
    "business_systems",
    "ai_concerns",
    "observed_impact_types",
    "systems_involved",
    "stakeholders",
    "safety_requirements",
    "additional_opportunities"
]
RATING_FIELDS = [
    "impact_rating",
    "data_quality_rating",
    "standardisation_rating",
    "implementation_complexity"
]
NUMBER_FIELDS = [
    "activity_volume",
    "minutes_per_instance",
    "reported_staff_hours_per_week",
    "labour_cost_per_hour",
    "current_baseline",
    "target_value",
    "indicative_budget"
]
BOOLEAN_FIELDS = [
    "privacy_acknowledged",
    "followup_consent",
    "marketing_consent"
]
DATE_FIELDS = [
    "submitted_at",
    "assessment_date",
    "consent_recorded_at"
]
RECOMMENDED_SURVEY_FIELDS = ["industry", "pain_points", "primary_pain_point", "weekly_hours_band", "impact_rating"]
