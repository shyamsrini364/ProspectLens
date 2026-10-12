"""Provisional decision-support rules, not fitted coefficients or probabilities.

Change this single configuration to adjust the model; bump MODEL_VERSION when
changing its meaning. Questionnaire fields and their validation stay untouched.
"""

MODEL_VERSION = 'opportunity-v1.0-provisional'
CONFIG = {
    'value_weights': {'impact': .45, 'workload': .35, 'recurrence': .10, 'additional': .10},
    'impact_points': {1: 0, 2: 25, 3: 50, 4: 75, 5: 100},
    'workload_points': {'under_2': 0, '2_5': 25, '6_10': 50, '11_20': 75, 'over_20': 100},
    'additional_cap': 2,
    'commercial_weights': {'budget_status': .35, 'pilot_interest': .25,
                           'implementation_timeline': .20, 'commercial_potential': .20},
    'commercial_points': {
        'budget_status': {'approved': 100, 'indicative': 65, 'conditional_value_case': 40, 'none': 0},
        'pilot_interest': {'yes': 100, 'maybe': 50, 'no': 0},
        'implementation_timeline': {'within_1_month': 100, 'within_1_to_3_months': 75,
                                    'within_3_to_6_months': 50, 'longer_term': 25, 'no_defined_timeline': 0},
        'commercial_potential': {'high': 100, 'medium': 50, 'low': 0},
    },
    'qualified_evidence': ['consultant_assessed', 'validated'],
    'known_authority': ['interviewee', 'owner_director', 'department_manager', 'multiple_stakeholders'],
    'overall_weights': {'value_score': .60, 'commercial_score': .40},
    'bands': [(80, 'High'), (60, 'Promising'), (40, 'Moderate'), (0, 'Low')],
    'quadrant_threshold': 50,
    'minimum_group': 5,
    'high_impact': 4,
    'impact_priority': {'high': 3, 'medium': 2, 'low': 1},
}

# Broad problem-to-family hypotheses only; never links a discovery workflow by guesswork.
SOLUTION_HYPOTHESES = {
    'customer_enquiries': 'Enquiry intake and routing',
    'sales_followup': 'Lead follow-up coordination',
    'appointment_scheduling': 'Booking and reminder workflows',
    'manual_data_entry': 'Data capture and validation',
    'reporting_analysis': 'Reporting preparation',
    'documents_information': 'Document organisation and retrieval',
    'finance_invoicing': 'Invoice and payment administration',
    'staff_coordination': 'Staff coordination workflows',
    'customer_support': 'Support triage and case handling',
    'marketing_content': 'Content preparation and review',
    'other': 'Clarify the problem before proposing a family',
}
