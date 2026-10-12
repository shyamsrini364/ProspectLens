# ProspectLens synthetic data profile

**SYNTHETIC DATA - NOT REAL MARKET FINDINGS**

All counts below are calculated from the saved CSV files after validation and checksum verification. The results describe this generated sample only; they are not market research, predictions or evidence of business outcomes.

Generator version: 1.2. Seed: `20261010`. Python used for generation: 3.13.14. pandas used for profiling: 3.0.6. Currency: AUD. No live clock is used in generation or report content.

## Records and validation

| dataset | rows | unique_prospects |
| --- | --- | --- |
| survey | 150 | 150 |
| discovery | 35 | 27 |
| contacts | 150 | 150 |

Validation: **0 errors, 17 warnings**. Missing recommended survey answers are intentional; warnings remain visible and are not suppressed.

| dataset | column | issue | count |
| --- | --- | --- | --- |
| survey | weekly_hours_band | Recommended analytical answer is missing. | 5 |
| survey | impact_rating | Recommended analytical answer is missing. | 4 |
| survey | pain_points | Recommended analytical answer is missing. | 4 |
| survey | primary_pain_point | Recommended analytical answer is missing. | 4 |

## Survey distributions

These tables use all survey rows as their denominator and include missing answers. The five analytical examples later use question-specific denominators. Stored codes map to friendly labels in the Template Pack dictionary.

### industry

| industry | records | percentage_of_all_rows |
| --- | --- | --- |
| professional_services | 47 | 31.33 |
| healthcare_allied | 21 | 14.00 |
| retail_ecommerce | 21 | 14.00 |
| trades_construction | 25 | 16.67 |
| hospitality | 7 | 4.67 |
| real_estate | 10 | 6.67 |
| manufacturing_logistics | 10 | 6.67 |
| education_training | 7 | 4.67 |
| other | 2 | 1.33 |
| missing | 0 | 0.00 |

### employee_band

| employee_band | records | percentage_of_all_rows |
| --- | --- | --- |
| solo | 29 | 19.33 |
| 2_5 | 47 | 31.33 |
| 6_20 | 46 | 30.67 |
| 21_50 | 11 | 7.33 |
| 51_200 | 12 | 8.00 |
| over_200 | 1 | 0.67 |
| missing | 4 | 2.67 |

### primary_pain_point

| primary_pain_point | records | percentage_of_all_rows |
| --- | --- | --- |
| customer_enquiries | 10 | 6.67 |
| sales_followup | 12 | 8.00 |
| appointment_scheduling | 14 | 9.33 |
| manual_data_entry | 24 | 16.00 |
| reporting_analysis | 13 | 8.67 |
| documents_information | 15 | 10.00 |
| finance_invoicing | 15 | 10.00 |
| staff_coordination | 11 | 7.33 |
| customer_support | 11 | 7.33 |
| marketing_content | 17 | 11.33 |
| other | 4 | 2.67 |
| missing | 4 | 2.67 |

### ai_adoption

| ai_adoption | records | percentage_of_all_rows |
| --- | --- | --- |
| regular_multiple | 23 | 15.33 |
| limited_tasks | 37 | 24.67 |
| experimented | 35 | 23.33 |
| not_using | 46 | 30.67 |
| unsure | 5 | 3.33 |
| missing | 4 | 2.67 |

### impact_rating

| impact_rating | records | percentage_of_all_rows |
| --- | --- | --- |
| 1 | 12 | 8.00 |
| 2 | 14 | 9.33 |
| 3 | 37 | 24.67 |
| 4 | 52 | 34.67 |
| 5 | 31 | 20.67 |
| missing | 4 | 2.67 |

### weekly_hours_band

| weekly_hours_band | records | percentage_of_all_rows |
| --- | --- | --- |
| under_2 | 16 | 10.67 |
| 2_5 | 24 | 16.00 |
| 6_10 | 34 | 22.67 |
| 11_20 | 42 | 28.00 |
| over_20 | 19 | 12.67 |
| unsure | 10 | 6.67 |
| missing | 5 | 3.33 |

### desired_outcome

| desired_outcome | records | percentage_of_all_rows |
| --- | --- | --- |
| save_time | 28 | 18.67 |
| reduce_costs | 20 | 13.33 |
| increase_revenue | 15 | 10.00 |
| faster_responses | 24 | 16.00 |
| reduce_errors | 30 | 20.00 |
| improve_satisfaction | 15 | 10.00 |
| scale_without_staff_growth | 14 | 9.33 |
| other | 4 | 2.67 |
| missing | 0 | 0.00 |

### current_process

| current_process | records | percentage_of_all_rows |
| --- | --- | --- |
| mostly_manual | 43 | 28.67 |
| mixed_manual_digital | 60 | 40.00 |
| mostly_software | 28 | 18.67 |
| automated_with_issues | 11 | 7.33 |
| unsure | 8 | 5.33 |
| missing | 0 | 0.00 |

## AI tools tried or used, and their uses

S14 follow-up: "Which AI tools have you tried or used, and what do you use them for?"

**79** responses name tools and explain their uses; **71** distinct descriptions are present. Examples below are drawn from the saved file, with up to two per adoption category. Regular users describe several activities, limited users describe a specific task, and experimenters describe a trial. Missing optional answers stay blank; this follow-up is not populated for not_using, unsure or missing adoption. Tool names occur in fictional respondent accounts, not verified product integrations or recommendations.

| response_id | ai_adoption | ai_tools_and_uses |
| --- | --- | --- |
| R0002 | regular_multiple | We regularly use Microsoft Copilot to suggest spreadsheet formulas for cleaning copied records; ChatGPT to brainstorm topics for staff training sessions; Canva Magic Write to draft captions for promotional posts. Staff check the outputs before using them. |
| R0003 | regular_multiple | We regularly use Microsoft Copilot to write first drafts of product descriptions; Google Gemini to draft outlines for customer information sheets. Staff check the outputs before using them. |
| R0004 | experimented | We tried Claude to turn team meeting notes into draft action lists using sample material. We have not made this part of our regular work. |
| R0005 | experimented | We tried ChatGPT to draft a narrative from non-confidential weekly figures using sample material. We have not made this part of our regular work. |
| R0009 | limited_tasks | We use Claude to draft checklists for checking manually entered records. This is an occasional, specific task; a staff member checks the result. |
| R0011 | limited_tasks | We use Claude to draft social media captions. This is an occasional, specific task; a staff member checks the result. |

## Follow-up interest versus explicit consent

Contacts are joined on both response_id and prospect_id. The tables contain aggregate counts; no names, businesses or email addresses are exported.

| followup_interest | true | false | unknown |
| --- | --- | --- | --- |
| maybe | 28 | 24 | 4 |
| not_now | 14 | 10 | 1 |
| yes | 36 | 28 | 5 |

Interested (yes/maybe): **125**. Interested without explicit follow-up consent: **61**. Interested and permitted but missing a usable email: **8**. Contact-eligible under the contract: **56**. Eligibility is a data condition, not an instruction to contact anyone.

Marketing permission is a separate choice:

| marketing_consent | records | percentage_of_all_rows |
| --- | --- | --- |
| true | 37 | 24.67 |
| false | 105 | 70.00 |
| missing | 8 | 5.33 |

## Discovery coverage and evidence

**35 assessments cover 27 of 150 survey prospects** (18.00%). **8 prospects have multiple assessments**; **123** prospects have no discovery. The default generator deliberately selects a subset, not a representative discovery sample. Each generated assessment concerns a distinct workflow within its prospect; no reassessments are generated in this version.

| assessments | prospects |
| --- | --- |
| 1 | 19 |
| 2 | 8 |

### implementation_complexity

| implementation_complexity | records | percentage_of_all_rows |
| --- | --- | --- |
| 1 | 3 | 8.57 |
| 2 | 6 | 17.14 |
| 3 | 12 | 34.29 |
| 4 | 7 | 20.00 |
| 5 | 4 | 11.43 |
| missing | 3 | 8.57 |

### technical_feasibility

| technical_feasibility | records | percentage_of_all_rows |
| --- | --- | --- |
| low | 7 | 20.00 |
| medium | 5 | 14.29 |
| high | 5 | 14.29 |
| unknown | 15 | 42.86 |
| missing | 3 | 8.57 |

### commercial_potential

| commercial_potential | records | percentage_of_all_rows |
| --- | --- | --- |
| low | 12 | 34.29 |
| medium | 12 | 34.29 |
| high | 8 | 22.86 |
| unknown | 3 | 8.57 |
| missing | 0 | 0.00 |

### budget_status

| budget_status | records | percentage_of_all_rows |
| --- | --- | --- |
| approved | 5 | 14.29 |
| indicative | 11 | 31.43 |
| conditional_value_case | 9 | 25.71 |
| none | 6 | 17.14 |
| not_discussed | 4 | 11.43 |
| missing | 0 | 0.00 |

### integration_capability

| integration_capability | records | percentage_of_all_rows |
| --- | --- | --- |
| confirmed_api | 7 | 20.00 |
| file_export_import | 6 | 17.14 |
| manual_only | 12 | 34.29 |
| not_investigated | 8 | 22.86 |
| unknown | 2 | 5.71 |
| missing | 0 | 0.00 |

### workflow_reuse_observation

| workflow_reuse_observation | records | percentage_of_all_rows |
| --- | --- | --- |
| substantially_similar | 14 | 40.00 |
| partially_similar | 13 | 37.14 |
| business_specific | 6 | 17.14 |
| unknown | 2 | 5.71 |
| missing | 0 | 0.00 |

### evidence_status

| evidence_status | records | percentage_of_all_rows |
| --- | --- | --- |
| self_reported | 10 | 28.57 |
| consultant_assessed | 18 | 51.43 |
| validated | 5 | 14.29 |
| unknown | 2 | 5.71 |
| missing | 0 | 0.00 |

### Workload consistency

For this generated dataset, every known activity period is week and source notes define time as total person-minutes. Modelled hours = activity_volume × minutes_per_instance ÷ 60. Staff count is NOT another multiplier. Missing inputs or unknown period produce no modelled estimate. Reported hours remain separate. A difference over 25% is a disclosed demonstration review flag, not a new scoring rule or an approved production threshold.

Supported weekly baselines: **30/35**. Differences flagged for review: **3**.

| assessment_id | prospect_id | volume_period | activity_volume | minutes_per_instance | reported_staff_hours_per_week | modelled_staff_hours_per_week | difference_percentage | review_difference_over_25_percent |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| D0001 | P0001 | week | 188.00 | 8.00 | 24.24 | 25.07 | 3.30 | False |
| D0002 | P0002 | week | 93.00 | 8.00 | 12.79 | 12.40 | 3.15 | False |
| D0003 | P0003 | week | 15.00 | 20.00 | 5.07 | 5.00 | 1.40 | False |
| D0004 | P0004 | week | 40.00 | 10.00 | 7.16 | 6.67 | 7.40 | False |
| D0005 | P0005 | week | 5.00 | 120.00 | 8.87 | 10.00 | 11.30 | False |
| D0006 | P0006 | week | 86.00 | 12.00 | 19.15 | 17.20 | 11.34 | False |
| D0007 | P0007 | week | 40.00 | 15.00 | 10.48 | 10.00 | 4.80 | False |
| D0008 | P0008 | week | 1.00 | 35.00 | 0.79 | 0.58 | 35.43 | True |
| D0009 | P0113 | week | 132.00 | 4.00 | 7.74 | 8.80 | 12.05 | False |
| D0010 | P0011 | week | 15.00 | 20.00 | 4.37 | 5.00 | 12.60 | False |
| D0011 | P0021 | week | 78.00 | 15.00 | — | 19.50 | — | False |
| D0012 | P0009 | week | 130.00 | 8.00 | 16.58 | 17.33 | 4.35 | False |
| D0013 | P0020 | week | 12.00 | — | 3.27 | — | — | False |
| D0014 | P0144 | week | 7.00 | 10.00 | 1.32 | 1.17 | 13.14 | False |
| D0015 | P0026 | week | 36.00 | 35.00 | 22.44 | 21.00 | 6.86 | False |
| D0016 | P0065 | week | 1.00 | 30.00 | 0.45 | 0.50 | 10.00 | False |
| D0017 | P0109 | week | — | 8.00 | 6.08 | — | — | False |
| D0018 | P0052 | week | 10.00 | 15.00 | 2.64 | 2.50 | 5.60 | False |
| D0019 | P0067 | unknown | 160.00 | 5.00 | 11.87 | — | — | False |
| D0020 | P0068 | week | 11.00 | 50.00 | 12.38 | 9.17 | 35.05 | True |
| D0021 | P0028 | week | 120.00 | 5.00 | 8.95 | 10.00 | 10.50 | False |
| D0022 | P0148 | week | 99.00 | 4.00 | — | 6.60 | — | False |
| D0023 | P0089 | week | 330.00 | 4.00 | 25.29 | 22.00 | 14.95 | False |
| D0024 | P0120 | week | 40.00 | 15.00 | 8.57 | 10.00 | 14.30 | False |
| D0025 | P0038 | week | 21.00 | 12.00 | 4.25 | 4.20 | 1.19 | False |
| D0026 | P0147 | week | 16.00 | — | 4.95 | — | — | False |
| D0027 | P0041 | week | 94.00 | 15.00 | 24.15 | 23.50 | 2.77 | False |
| D0028 | P0003 | week | 15.00 | 20.00 | 5.26 | 5.00 | 5.20 | False |
| D0029 | P0021 | week | 58.00 | 10.00 | 10.64 | 9.67 | 10.07 | False |
| D0030 | P0113 | week | 14.00 | 18.00 | 4.82 | 4.20 | 14.76 | False |
| D0031 | P0068 | week | 9.00 | 20.00 | 2.67 | 3.00 | 11.00 | False |
| D0032 | P0067 | week | 61.00 | 5.00 | 6.86 | 5.08 | 34.95 | True |
| D0033 | P0089 | week | 26.00 | 12.00 | — | 5.20 | — | False |
| D0034 | P0028 | week | — | 15.00 | 7.93 | — | — | False |
| D0035 | P0026 | week | 36.00 | 25.00 | 13.79 | 15.00 | 8.07 | False |

### Survey band beside first assessed workflow

These are different questions/scopes: a broad challenge band versus one workflow baseline. Differences are not automatically errors. Bands have not been converted to exact hours.

| prospect_id | assessment_id | weekly_hours_band | workflow_name | modelled_discovery_hours |
| --- | --- | --- | --- | --- |
| P0001 | D0001 | over_20 | Supplier invoice entry - design consultancy | 25.07 |
| P0002 | D0002 | 11_20 | New customer record transcription - physiotherapy clinic | 12.40 |
| P0003 | D0003 | 6_10 | Content draft review and scheduling - specialty retail store | 5.00 |
| P0004 | D0004 | 11_20 | Shift availability collection - electrical contractor | 6.67 |
| P0005 | D0005 | over_20 | Weekly service performance reporting - small catering company | 10.00 |
| P0006 | D0006 | 11_20 | Cancellation slot backfilling - property management agency | 17.20 |
| P0007 | D0007 | 11_20 | Roster change approvals - regional freight operator | 10.00 |
| P0008 | D0008 | under_2 | Order status response handling - vocational training provider | 0.58 |
| P0113 | D0009 | 6_10 | Supplier invoice entry - design consultancy | 8.80 |
| P0011 | D0010 | 11_20 | Content draft review and scheduling - specialty retail store | 5.00 |
| P0021 | D0011 | 11_20 | Overdue invoice reminders - tutoring centre | 19.50 |
| P0009 | D0012 |  | Supplier invoice entry - pet grooming studio | 17.33 |
| P0020 | D0013 | over_20 | Shift availability collection - online homewares shop | — |
| P0144 | D0014 | under_2 | Supplier compliance renewal checks - online homewares shop | 1.17 |
| P0026 | D0015 | over_20 | Order status response handling - vocational training provider | 21.00 |
| P0065 | D0016 | under_2 | Proposal reminder follow-up - residential sales agency | 0.50 |
| P0109 | D0017 | 2_5 | Appointment confirmation reminders - small catering company | — |
| P0052 | D0018 | 2_5 | Invoice approval routing - electrical contractor | 2.50 |
| P0067 | D0019 | 11_20 | Appointment confirmation reminders - building maintenance firm | — |
| P0068 | D0020 | 6_10 | Campaign enquiry attribution - accounting practice | 9.17 |
| P0028 | D0021 | 6_10 | Policy version retrieval - physiotherapy clinic | 10.00 |
| P0148 | D0022 | unsure | New customer record transcription - accounting practice | 6.60 |
| P0089 | D0023 | 11_20 | Supplier invoice entry - speech therapy practice | 22.00 |
| P0120 | D0024 | over_20 | Shift availability collection - electrical contractor | 10.00 |
| P0038 | D0025 | 2_5 | New customer record transcription - online homewares shop | 4.20 |
| P0147 | D0026 | 11_20 | Supplier invoice entry - speech therapy practice | — |
| P0041 | D0027 | over_20 | Shared inbox enquiry routing - design consultancy | 23.50 |

## Missing values and explicit uncertainty

Blank means missing, not zero or no. The table lists every column containing blank cells. Many blanks are intentional conditional fields (Other text, software/AI follow-ups), optional comments, or uninvestigated measurements. They should not all be treated as defects. Empty JSON arrays mean an explicitly empty list and are not blank cells.

| dataset | column | blank_cells | total_rows | percentage |
| --- | --- | --- | --- | --- |
| survey | recruitment_channel | 7 | 150 | 4.67 |
| survey | industry_other | 148 | 150 | 98.67 |
| survey | employee_band | 4 | 150 | 2.67 |
| survey | pain_points | 4 | 150 | 2.67 |
| survey | pain_points_other | 140 | 150 | 93.33 |
| survey | primary_pain_point | 4 | 150 | 2.67 |
| survey | primary_pain_point_other | 146 | 150 | 97.33 |
| survey | weekly_hours_band | 5 | 150 | 3.33 |
| survey | impact_rating | 4 | 150 | 2.67 |
| survey | business_systems_other | 116 | 150 | 77.33 |
| survey | underused_software_names | 80 | 150 | 53.33 |
| survey | ai_adoption | 4 | 150 | 2.67 |
| survey | ai_tools_and_uses | 71 | 150 | 47.33 |
| survey | ai_concerns_other | 113 | 150 | 75.33 |
| survey | main_concern_details | 85 | 150 | 56.67 |
| survey | desired_outcome_other | 146 | 150 | 97.33 |
| survey | additional_comments | 116 | 150 | 77.33 |
| discovery | activity_volume | 2 | 35 | 5.71 |
| discovery | minutes_per_instance | 2 | 35 | 5.71 |
| discovery | reported_staff_hours_per_week | 3 | 35 | 8.57 |
| discovery | labour_cost_per_hour | 16 | 35 | 45.71 |
| discovery | current_baseline | 2 | 35 | 5.71 |
| discovery | target_value | 5 | 35 | 14.29 |
| discovery | indicative_budget | 17 | 35 | 48.57 |
| discovery | technical_feasibility | 3 | 35 | 8.57 |
| discovery | implementation_complexity | 3 | 35 | 8.57 |
| contacts | email | 13 | 150 | 8.67 |
| contacts | followup_consent | 10 | 150 | 6.67 |
| contacts | marketing_consent | 8 | 150 | 5.33 |

Explicit uncertainty is retained separately:

| dataset | column | recorded_code | count |
| --- | --- | --- | --- |
| survey | recruitment_channel | unknown | 7 |
| survey | weekly_hours_band | unsure | 10 |
| survey | current_process | unsure | 8 |
| survey | sensitive_data_frequency | unsure | 8 |
| survey | subscription_underuse | unsure | 13 |
| survey | ai_adoption | unsure | 5 |
| discovery | volume_period | unknown | 1 |
| discovery | integration_capability | unknown | 2 |
| discovery | integration_capability | not_investigated | 8 |
| discovery | decision_authority | unknown | 6 |
| discovery | budget_status | not_discussed | 4 |
| discovery | pilot_interest | not_discussed | 2 |
| discovery | workflow_reuse_observation | unknown | 2 |
| discovery | business_impact_assessment | unknown | 2 |
| discovery | commercial_potential | unknown | 3 |
| discovery | solution_reusability | unknown | 2 |
| discovery | technical_feasibility | unknown | 15 |
| discovery | expansion_potential | unknown | 13 |
| discovery | evidence_status | unknown | 2 |

## Field-by-field realism review

All 94 column positions across the three schemas were reviewed. Stable IDs, versions, currency and policy metadata are deliberately repetitive; adding variation to those would reduce data quality. Canonical answer codes retain their approved meaning. The table below measures populated, missing and distinct values directly from the current files; low diversity is not automatically an error.

| dataset | column | answered | blank | distinct_nonblank |
| --- | --- | --- | --- | --- |
| survey | response_id | 150 | 0 | 150 |
| survey | prospect_id | 150 | 0 | 150 |
| survey | submitted_at | 150 | 0 | 149 |
| survey | dataset_version | 150 | 0 | 1 |
| survey | questionnaire_version | 150 | 0 | 1 |
| survey | recruitment_channel | 143 | 7 | 6 |
| survey | industry | 150 | 0 | 9 |
| survey | industry_other | 2 | 148 | 2 |
| survey | employee_band | 146 | 4 | 6 |
| survey | pain_points | 146 | 4 | 111 |
| survey | pain_points_other | 10 | 140 | 4 |
| survey | primary_pain_point | 146 | 4 | 11 |
| survey | primary_pain_point_other | 4 | 146 | 4 |
| survey | weekly_hours_band | 145 | 5 | 6 |
| survey | impact_rating | 146 | 4 | 5 |
| survey | current_process | 150 | 0 | 5 |
| survey | sensitive_data_frequency | 150 | 0 | 4 |
| survey | business_systems | 150 | 0 | 110 |
| survey | business_systems_other | 34 | 116 | 3 |
| survey | subscription_underuse | 150 | 0 | 4 |
| survey | underused_software_names | 70 | 80 | 44 |
| survey | ai_adoption | 146 | 4 | 5 |
| survey | ai_tools_and_uses | 79 | 71 | 71 |
| survey | ai_concerns | 150 | 0 | 107 |
| survey | ai_concerns_other | 37 | 113 | 2 |
| survey | main_concern_details | 65 | 85 | 55 |
| survey | desired_outcome | 150 | 0 | 8 |
| survey | desired_outcome_other | 4 | 146 | 3 |
| survey | followup_interest | 150 | 0 | 3 |
| survey | additional_comments | 34 | 116 | 33 |
| discovery | assessment_id | 35 | 0 | 35 |
| discovery | prospect_id | 35 | 0 | 27 |
| discovery | workflow_id | 35 | 0 | 2 |
| discovery | assessment_date | 35 | 0 | 25 |
| discovery | assessor_id | 35 | 0 | 3 |
| discovery | source_reference | 35 | 0 | 35 |
| discovery | dataset_version | 35 | 0 | 1 |
| discovery | questionnaire_version | 35 | 0 | 1 |
| discovery | workflow_name | 35 | 0 | 30 |
| discovery | workflow_steps | 35 | 0 | 32 |
| discovery | stakeholders | 35 | 0 | 23 |
| discovery | bottlenecks | 35 | 0 | 11 |
| discovery | activity_volume | 33 | 2 | 27 |
| discovery | volume_period | 35 | 0 | 2 |
| discovery | minutes_per_instance | 33 | 2 | 13 |
| discovery | staff_count | 35 | 0 | 4 |
| discovery | reported_staff_hours_per_week | 32 | 3 | 32 |
| discovery | labour_cost_per_hour | 19 | 16 | 7 |
| discovery | currency | 35 | 0 | 1 |
| discovery | observed_impact_types | 35 | 0 | 4 |
| discovery | impact_evidence | 35 | 0 | 35 |
| discovery | success_metric | 35 | 0 | 18 |
| discovery | current_baseline | 33 | 2 | 18 |
| discovery | target_value | 30 | 5 | 29 |
| discovery | target_unit | 35 | 0 | 3 |
| discovery | systems_involved | 35 | 0 | 24 |
| discovery | information_storage | 35 | 0 | 2 |
| discovery | data_quality_rating | 35 | 0 | 5 |
| discovery | data_quality_evidence | 35 | 0 | 22 |
| discovery | integration_capability | 35 | 0 | 5 |
| discovery | integration_evidence | 35 | 0 | 22 |
| discovery | standardisation_rating | 35 | 0 | 5 |
| discovery | exceptions_description | 35 | 0 | 20 |
| discovery | safety_requirements | 35 | 0 | 4 |
| discovery | safety_notes | 35 | 0 | 30 |
| discovery | decision_authority | 35 | 0 | 5 |
| discovery | implementation_timeline | 35 | 0 | 5 |
| discovery | budget_status | 35 | 0 | 5 |
| discovery | indicative_budget | 18 | 17 | 6 |
| discovery | pilot_interest | 35 | 0 | 4 |
| discovery | workflow_reuse_observation | 35 | 0 | 4 |
| discovery | reuse_evidence | 35 | 0 | 21 |
| discovery | reusable_components | 35 | 0 | 12 |
| discovery | customisation_needs | 35 | 0 | 29 |
| discovery | additional_opportunities | 35 | 0 | 19 |
| discovery | business_impact_assessment | 35 | 0 | 4 |
| discovery | commercial_potential | 35 | 0 | 4 |
| discovery | solution_reusability | 35 | 0 | 4 |
| discovery | technical_feasibility | 32 | 3 | 4 |
| discovery | implementation_complexity | 32 | 3 | 5 |
| discovery | expansion_potential | 35 | 0 | 4 |
| discovery | assessment_evidence | 35 | 0 | 35 |
| discovery | evidence_status | 35 | 0 | 4 |
| discovery | recommended_next_action | 35 | 0 | 5 |
| contacts | response_id | 150 | 0 | 150 |
| contacts | prospect_id | 150 | 0 | 150 |
| contacts | contact_name | 150 | 0 | 150 |
| contacts | business_name | 150 | 0 | 150 |
| contacts | email | 137 | 13 | 137 |
| contacts | privacy_acknowledged | 150 | 0 | 1 |
| contacts | privacy_notice_version | 150 | 0 | 1 |
| contacts | followup_consent | 140 | 10 | 2 |
| contacts | marketing_consent | 142 | 8 | 2 |
| contacts | consent_recorded_at | 150 | 0 | 149 |

### Business and workflow context

Generator 1.2 adds a separate catalogue of industry-specific business types and process vocabulary. Survey software categories determine the named software available to discovery and the names of underused subscriptions. Several underused subscriptions require at least three named paid products; supporting categories are added when needed. Business labels remain visibly fictional, contacts remain restricted, and no brand's technical capability is asserted as fact.

Workflow volumes are capped by the type of work: a report takes longer and occurs less often than a short enquiry. Success measures include processing person-minutes, elapsed response hours and percentage requiring rework; each has matching units, baseline and target. Reported hours remain a separate estimate. The narrower workflow can differ substantially from the broad survey challenge.

Evidence notes describe the recorded rating/status. Uninvestigated or unknown integration leaves feasibility unknown or missing. Reuse conclusions match the similarity observation; safety notes reflect the sector and task. A pilot proposal requires positive pilot interest, a plausible budget state and assessed medium/high feasibility. Budget amounts vary with business size. These are authored synthetic scenarios, not a new scoring model.

A few examples from the saved discovery file:

| assessment_id | workflow_name | systems_involved | success_metric | recommended_next_action |
| --- | --- | --- | --- | --- |
| D0001 | Supplier invoice entry - design consultancy | ["Paper register and printed forms"] | Share of invoice records returned for correction; lower is better, and the proposed target requires a pilot. | further_discovery |
| D0002 | New customer record transcription - physiotherapy clinic | ["Microsoft Excel", "MYOB", "ClickUp", "Zoho CRM"] | Share of referral forms returned for correction; lower is better, and the proposed target requires a pilot. | pilot_proposal |
| D0003 | Content draft review and scheduling - specialty retail store | ["Microsoft Outlook", "Google Sheets", "QuickBooks", "Asana", "Calendly", "HubSpot"] | Total staff processing time per content item; lower is better, and the proposed target requires a pilot. | technical_feasibility_test |
| D0004 | Shift availability collection - electrical contractor | ["Paper register and printed forms"] | Total staff processing time per roster change; lower is better, and the proposed target requires a pilot. | pilot_proposal |
| D0005 | Weekly service performance reporting - small catering company | ["Google Sheets", "MYOB"] | Total staff processing time per report; lower is better, and the proposed target requires a pilot. | defer |

## Five pandas analysis examples

Run `python -m scripts.analyse_synthetic_data` to reproduce this report. The following functions operate on validated, raw-string pandas DataFrames loaded from the files. They are defined in `scripts/analyse_synthetic_data.py`; constants and imports are in that file. All results below are generated by these functions.

### 1. Which operational problems are reported most often?

```python
def pain_point_frequency(survey, industry=None):
    """Question 1: which problems recur? Filter BEFORE choosing the denominator."""
    selected = survey if industry is None else survey.loc[survey["industry"].eq(industry)]
    answered = selected.loc[selected["pain_points"].ne(""), ["response_id", "pain_points"]].copy()
    answered["pain_points"] = answered["pain_points"].map(json.loads)
    answered = answered.loc[answered["pain_points"].map(bool)]
    denominator = answered["response_id"].nunique()
    expanded = answered.explode("pain_points").drop_duplicates(["response_id", "pain_points"])
    counts = expanded.groupby("pain_points")["response_id"].nunique()
    output = counts.reindex(ENUMS["pain_points"], fill_value=0).rename("respondents").reset_index()
    output.columns = ["pain_point", "respondents"]
    output["answered_S06"] = denominator
    output["percentage"] = output["respondents"] * 100 / denominator if denominator else float("nan")
    return output.sort_values(["respondents", "pain_point"], ascending=[False, True]).reset_index(drop=True)
```

| pain_point | respondents | answered_S06 | percentage |
| --- | --- | --- | --- |
| manual_data_entry | 47 | 146 | 32.19 |
| reporting_analysis | 35 | 146 | 23.97 |
| sales_followup | 35 | 146 | 23.97 |
| finance_invoicing | 32 | 146 | 21.92 |
| appointment_scheduling | 30 | 146 | 20.55 |
| customer_enquiries | 28 | 146 | 19.18 |
| documents_information | 28 | 146 | 19.18 |
| marketing_content | 28 | 146 | 19.18 |
| customer_support | 25 | 146 | 17.12 |
| staff_coordination | 21 | 146 | 14.38 |
| other | 10 | 146 | 6.85 |

Each respondent counts at most once per category. The denominator excludes unanswered S06. Since one respondent can select several problems, percentages can add to more than 100%. Pass an industry code as the second argument to filter before calculating counts.

### 2. Which industries have the highest high-impact proportion?

```python
def industry_high_impact(survey, threshold=HIGH_IMPACT_THRESHOLD, minimum_group=MINIMUM_GROUP_WARNING):
    """Question 2: compare high-impact shares using answered S09 within industry."""
    rows = survey[["industry", "impact_rating"]].copy()
    rows["industry"] = rows["industry"].replace("", "missing")
    rows["rating"] = pd.to_numeric(rows["impact_rating"], errors="coerce")
    rows["high"] = rows["rating"].ge(threshold)
    output = rows.groupby("industry").agg(responses=("rating", "size"),
        answered_S09=("rating", "count"), high_impact=("high", "sum")).reset_index()
    output["missing_S09"] = output["responses"] - output["answered_S09"]
    output["percentage"] = output["high_impact"] * 100 / output["answered_S09"].replace(0, float("nan"))
    output["small_group_warning"] = output["answered_S09"].lt(minimum_group)
    return output.sort_values(["percentage", "industry"], ascending=[False, True]).reset_index(drop=True)
```

| industry | responses | answered_S09 | high_impact | missing_S09 | percentage | small_group_warning |
| --- | --- | --- | --- | --- | --- | --- |
| other | 2 | 2 | 2 | 0 | 100.00 | True |
| healthcare_allied | 21 | 21 | 15 | 0 | 71.43 | False |
| hospitality | 7 | 7 | 5 | 0 | 71.43 | False |
| manufacturing_logistics | 10 | 10 | 7 | 0 | 70.00 | False |
| professional_services | 47 | 46 | 26 | 1 | 56.52 | False |
| education_training | 7 | 6 | 3 | 1 | 50.00 | False |
| real_estate | 10 | 10 | 5 | 0 | 50.00 | False |
| trades_construction | 25 | 24 | 12 | 1 | 50.00 | False |
| retail_ecommerce | 21 | 20 | 8 | 1 | 40.00 | False |

High impact uses the approved example threshold of 4. Compare numerator and answered_S09 together: 2 of 3 can look stronger than 20 of 40 while being much less stable. Groups below five valid answers are flagged. This is sample description, not industry-level market evidence.

### 3. How does AI adoption vary by business size?

```python
def ai_by_business_size(survey):
    """Question 3: AI adoption within each size; blank answers stay visible."""
    rows = survey[["employee_band", "ai_adoption", "response_id"]].copy()
    rows["employee_band"] = rows["employee_band"].replace("", "missing")
    denominator = rows.loc[rows["ai_adoption"].ne("")].groupby("employee_band")["response_id"].nunique()
    rows["ai_adoption"] = rows["ai_adoption"].replace("", "missing")
    counts = rows.groupby(["employee_band", "ai_adoption"])["response_id"].nunique()
    index = pd.MultiIndex.from_product([ENUMS["employee_band"] + ["missing"], ENUMS["ai_adoption"] + ["missing"]],
                                      names=["employee_band", "ai_adoption"])
    output = counts.reindex(index, fill_value=0).rename("respondents").reset_index()
    output["answered_S14_in_size"] = output["employee_band"].map(denominator).fillna(0).astype(int)
    output["percentage"] = output["respondents"] * 100 / output["answered_S14_in_size"].replace(0, float("nan"))
    output.loc[output["ai_adoption"].eq("missing"), "percentage"] = float("nan")
    return output
```

| employee_band | ai_adoption | respondents | answered_S14_in_size | percentage |
| --- | --- | --- | --- | --- |
| solo | regular_multiple | 6 | 28 | 21.43 |
| solo | limited_tasks | 9 | 28 | 32.14 |
| solo | experimented | 4 | 28 | 14.29 |
| solo | not_using | 7 | 28 | 25.00 |
| solo | unsure | 2 | 28 | 7.14 |
| solo | missing | 1 | 28 | — |
| 2_5 | regular_multiple | 8 | 47 | 17.02 |
| 2_5 | limited_tasks | 11 | 47 | 23.40 |
| 2_5 | experimented | 14 | 47 | 29.79 |
| 2_5 | not_using | 13 | 47 | 27.66 |
| 2_5 | unsure | 1 | 47 | 2.13 |
| 2_5 | missing | 0 | 47 | — |
| 6_20 | regular_multiple | 6 | 44 | 13.64 |
| 6_20 | limited_tasks | 11 | 44 | 25.00 |
| 6_20 | experimented | 11 | 44 | 25.00 |
| 6_20 | not_using | 14 | 44 | 31.82 |
| 6_20 | unsure | 2 | 44 | 4.55 |
| 6_20 | missing | 2 | 44 | — |
| 21_50 | regular_multiple | 1 | 10 | 10.00 |
| 21_50 | limited_tasks | 2 | 10 | 20.00 |
| 21_50 | experimented | 3 | 10 | 30.00 |
| 21_50 | not_using | 4 | 10 | 40.00 |
| 21_50 | unsure | 0 | 10 | 0.00 |
| 21_50 | missing | 1 | 10 | — |
| 51_200 | regular_multiple | 2 | 12 | 16.67 |
| 51_200 | limited_tasks | 3 | 12 | 25.00 |
| 51_200 | experimented | 2 | 12 | 16.67 |
| 51_200 | not_using | 5 | 12 | 41.67 |
| 51_200 | unsure | 0 | 12 | 0.00 |
| 51_200 | missing | 0 | 12 | — |
| over_200 | regular_multiple | 0 | 1 | 0.00 |
| over_200 | limited_tasks | 0 | 1 | 0.00 |
| over_200 | experimented | 0 | 1 | 0.00 |
| over_200 | not_using | 1 | 1 | 100.00 |
| over_200 | unsure | 0 | 1 | 0.00 |
| over_200 | missing | 0 | 1 | — |
| missing | regular_multiple | 0 | 4 | 0.00 |
| missing | limited_tasks | 1 | 4 | 25.00 |
| missing | experimented | 1 | 4 | 25.00 |
| missing | not_using | 2 | 4 | 50.00 |
| missing | unsure | 0 | 4 | 0.00 |
| missing | missing | 0 | 4 | — |

Percentages are within each size group, using nonblank S14 answers. Unsure remains an answered category; blanks have no percentage. An empty size group has no rate, rather than an invented 0%.

### 4. Which high-impact prospects meet follow-up eligibility?

```python
def high_impact_contact_candidates(survey, contacts, threshold=HIGH_IMPACT_THRESHOLD):
    """Question 4: high impact AND interest AND explicit consent AND valid email."""
    private = survey.merge(contacts[["response_id", "prospect_id", "followup_consent", "email"]],
                           on=["response_id", "prospect_id"], how="left", validate="one_to_one")
    eligible = (pd.to_numeric(private["impact_rating"], errors="coerce").ge(threshold)
                & private["followup_interest"].isin(["yes", "maybe"])
                & private["followup_consent"].eq("true")
                & private["email"].map(valid_email))
    # Return an allowlist of pseudonymous analytical fields, never private details.
    return private.loc[eligible, ["response_id", "prospect_id", "primary_pain_point", "impact_rating",
                                 "weekly_hours_band", "followup_interest"]].reset_index(drop=True)
```

| response_id | prospect_id | primary_pain_point | impact_rating | weekly_hours_band | followup_interest |
| --- | --- | --- | --- | --- | --- |
| R0003 | P0003 | marketing_content | 4 | 6_10 | yes |
| R0004 | P0004 | staff_coordination | 4 | 11_20 | maybe |
| R0009 | P0009 | manual_data_entry | 4 |  | maybe |
| R0011 | P0011 | marketing_content | 5 | 11_20 | maybe |
| R0019 | P0019 | appointment_scheduling | 4 | under_2 | maybe |
| R0020 | P0020 | staff_coordination | 4 | over_20 | yes |
| R0021 | P0021 | finance_invoicing | 5 | 11_20 | yes |
| R0026 | P0026 | customer_support | 4 | over_20 | maybe |
| R0031 | P0031 | marketing_content | 5 | over_20 | maybe |
| R0032 | P0032 | customer_enquiries | 5 | over_20 | yes |
| R0039 | P0039 | finance_invoicing | 5 | 6_10 | maybe |
| R0044 | P0044 | staff_coordination | 4 | 6_10 | yes |
| R0057 | P0057 | customer_support | 5 | over_20 | maybe |
| R0066 | P0066 | reporting_analysis | 4 | 6_10 | yes |
| R0067 | P0067 | appointment_scheduling | 4 | 11_20 | maybe |
| R0072 | P0072 | documents_information | 4 | over_20 | maybe |
| R0074 | P0074 | customer_enquiries | 4 | 11_20 | yes |
| R0083 | P0083 | finance_invoicing | 4 | 11_20 | maybe |
| R0104 | P0104 | reporting_analysis | 5 | 6_10 | maybe |
| R0105 | P0105 | documents_information | 4 |  | maybe |
| R0107 | P0107 | manual_data_entry | 5 | 6_10 | yes |
| R0109 | P0109 | appointment_scheduling | 4 | 2_5 | maybe |
| R0111 | P0111 | manual_data_entry | 5 | 6_10 | yes |
| R0115 | P0115 | marketing_content | 4 | 11_20 | yes |
| R0120 | P0120 | staff_coordination | 5 | over_20 | yes |
| R0123 | P0123 | manual_data_entry | 4 |  | yes |
| R0131 | P0131 | manual_data_entry | 4 | over_20 | maybe |
| R0138 | P0138 | reporting_analysis | 5 | 11_20 | yes |
| R0141 | P0141 | sales_followup | 4 | unsure | yes |
| R0150 | P0150 | manual_data_entry | 5 | 6_10 | maybe |

Every listed ID has impact at least 4, interest yes/maybe, explicit true follow-up consent, and a structurally valid email. Names and addresses are excluded. Marketing permission never substitutes for follow-up consent, and missing consent never becomes true.

### 5. How does assessed complexity compare with commercial potential?

```python
def complexity_vs_commercial(discovery):
    """Question 5: assessment-level counts, with unassessed/unknown kept explicit."""
    rows = discovery[["assessment_id", "implementation_complexity", "commercial_potential"]].copy()
    rows["implementation_complexity"] = rows["implementation_complexity"].replace("", "unassessed")
    rows["commercial_potential"] = rows["commercial_potential"].replace("", "unassessed")
    counts = pd.crosstab(rows["implementation_complexity"], rows["commercial_potential"])
    return counts.reindex(index=["1", "2", "3", "4", "5", "unassessed"],
                          columns=["low", "medium", "high", "unknown", "unassessed"], fill_value=0).reset_index()
```

| implementation_complexity | low | medium | high | unknown | unassessed |
| --- | --- | --- | --- | --- | --- |
| 1 | 1 | 1 | 1 | 0 | 0 |
| 2 | 3 | 0 | 1 | 2 | 0 |
| 3 | 4 | 4 | 4 | 0 | 0 |
| 4 | 1 | 4 | 1 | 1 | 0 |
| 5 | 2 | 1 | 1 | 0 | 0 |
| unassessed | 1 | 2 | 0 | 0 | 0 |

Each cell counts assessments, not survey responses or businesses. Complexity 1–2 is simple, 3 medium, 4–5 complex. High commercial potential can coexist with high complexity. Unknown and unassessed remain explicit; these fictional judgements do not estimate conversion or ROI.

## Intentional relationships, assumptions and limitations

- Industry affects pain-category selection weights; it does not dictate a business's answer. The first nine records cover all industries; remaining records use uneven weights.
- Manual/mixed processes have higher chances of the 11–20 and over-20 bands. Impact is loosely associated with burden, with random exceptions. No numeric workload midpoint is used.
- Larger businesses tend to list more systems; small digital and large manual counterexamples are built in. AI use is associated with process maturity but does not remove operational pain.
- AI tool descriptions pair a named tool with a concrete task related to the respondent's primary challenge. A separate seeded stream varies this text without reshuffling other fields; the original optional-answer pattern is preserved. These are fictional usage accounts.
- The first eight survey cases deliberately exercise exceptions, including high impact without interest, AI use with high impact, unknown consent, and consent with missing email. Remaining scenarios combine weighted draws with explicit consistency rules.
- Follow-up interest is drawn separately from consent. Follow-up consent and marketing consent use independent random draws except for the documented teaching cases.
- Discovery starts with eight teaching prospects, then a random subset; the default covers 27 businesses. Extra workflows are assigned within that subset. This creates selection bias deliberately, so discovery cannot stand in for the whole sample.
- Discovery volume and person-minutes are generated together to give a plausible workload; reported hours normally vary by up to 15%, with occasional 35% scope/recollection differences. Staff capacity is capped at 35 process-hours per person per week as a synthetic plausibility check, not a productivity benchmark.
- Budget influences fictional commercial judgements; integration and data quality influence fictional complexity/feasibility with noise. Integration evidence is kept consistent with feasibility uncertainty. Deliberate high-commercial/high-complexity examples prevent equating attractiveness with ease of delivery.
- Each broad pain category has two workflow variants. Similar survey pain does not establish the same technical solution or confirmed reuse.
- Currency applies to optional labour costs and budget amounts. No ROI, guaranteed savings, exchange rates, or conversion probabilities are generated. Numeric targets are aspirations.
- Dates use a fixed September 2026 collection window and subsequent fictional discovery dates. No real people, contacts, company records or external data were read to create the rows. Names are visibly fictional constructions and email addresses use example.invalid.
- All assessed, confirmed and validated labels are simulated role-play evidence states. They do not describe an actual vendor verification or real consultant observation.
- The seed reproduces CSV bytes with the same code/configuration and Python runtime. The manifest records the runtime and SHA-256 hashes. Changing the algorithm or runtime can change the output. Separate random streams keep survey/contact data stable when only discovery count changes.
- Contact data stays in its own ignored local CSV. The report uses aggregate consent counts and pseudonymous candidate IDs. A future public demo must explicitly exclude the contact file and test its export boundary.

### Observed process/workload relationship in these files

| current_process | known_band_responses | higher_workload_responses | percentage |
| --- | --- | --- | --- |
| automated_with_issues | 11 | 4 | 36.36 |
| mixed_manual_digital | 54 | 29 | 53.70 |
| mostly_manual | 37 | 17 | 45.95 |
| mostly_software | 26 | 8 | 30.77 |
| unsure | 7 | 3 | 42.86 |

## Source fingerprints

| file | sha256 |
| --- | --- |
| survey_responses.csv | 40d3141ca2f8f47e0e37e7f356ef1432e7ec70f975ed2d3e9670d34896428271 |
| discovery_assessments.csv | dcbc5b3b246333e65fdb86df28329dc524a6049b9953eafe8c206c219d8aae90 |
| contacts_and_consent.csv | e3871c042c2c0d7bb336425cfc7f5cf4cefab4eefdd23c6e8ee5a2319926220e |

## Reading the code

A DataFrame is like a spreadsheet with named columns. `groupby` makes piles of rows with the same label; `explode` temporarily gives each selected pain point its own row; `drop_duplicates` prevents counting a respondent twice for the same category. A merge is a lookup using matching IDs. We compute survey proportions before joining discovery, because one business with three workflows must not become three survey respondents.

`pd.read_csv(..., dtype=str, keep_default_na=False)` preserves the raw contract values before explicit conversion. See the [pandas read_csv documentation](https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html). Only the analysis/report script needs pandas; the generator and existing validator remain standard-library Python.
