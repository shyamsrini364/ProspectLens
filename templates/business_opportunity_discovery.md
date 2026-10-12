# Business Opportunity Discovery

Questionnaire version: 1.0. Consultant-led, suggested session 30–45 minutes. This is optional discovery, not a compulsory second public survey. Use one assessment per specific workflow/opportunity. Record evidence and uncertainty; any uninvestigated answer can remain blank. Do not invent measurements or ratings.

## D01 — Problem

What specific business process or workflow are we investigating?

- `workflow_name`: text.

## D02 — Problem

Describe how this process works today, beginning to end.

- `workflow_steps`: text.

## D03 — Problem

Which people, teams or external parties are involved?

- `stakeholders`: JSON array of text entries.

Describe roles or teams where possible; avoid unnecessary personal identifiers.

## D04 — Problem

What are the biggest delays, errors or frustrations?

- `bottlenecks`: text.

## D05 — Impact

Approximately how many times does the process occur, and per what time period?

- `activity_volume`: nonnegative decimal number.
- `volume_period`: single choice. Choices: `day`, `week`, `month`, `unknown`.

Record occurrence count and period separately. Unknown period does not support a weekly-hours estimate.

## D06 — Impact

How many minutes does one instance typically take?

- `minutes_per_instance`: nonnegative decimal number.

Record total person-minutes for one occurrence. Do not multiply this value by staff_count automatically. Record the time basis in source/evidence notes. Zero is allowed for no work; for actual work record a positive value.

## D07 — Impact

How many people are involved, and how many total staff hours per week are spent on the process?

- `staff_count`: nonnegative integer.
- `reported_staff_hours_per_week`: nonnegative decimal number.

Staff count is a headcount. Reported weekly hours are the total across people, not hours per person.

## D08 — Impact

What is the approximate hourly labour cost (if known and voluntarily shared)?

- `labour_cost_per_hour`: nonnegative decimal number.
- `currency`: text.

Voluntary; leave unknown labour costs blank. Supply explicit currency when providing a monetary value.

## D09 — Impact

What measurable negative outcomes occur?

- `observed_impact_types`: JSON array of text entries. Choices: `delayed_responses`, `errors_rework`, `missed_sales`, `complaints`, `extra_costs`, `overtime`, `other`.
- `impact_evidence`: text.

Select observed impact codes and describe the evidence. For other, explain it in impact_evidence.

## D10 — Impact

What should success look like and how would it be measured?

- `success_metric`: text.
- `current_baseline`: nonnegative decimal number.
- `target_value`: nonnegative decimal number.
- `target_unit`: text.

Use numeric current_baseline and target_value with an explicit target_unit. Describe qualitative success in success_metric; do not force it to zero.

## D11 — Systems

Which applications or tools are involved?

- `systems_involved`: JSON array of text entries.

## D12 — Systems

Where is required information stored?

- `information_storage`: single choice. Choices: `central_system`, `multiple_systems`, `spreadsheets_documents`, `partly_paper`, `unknown`.

## D13 — Systems

How would you assess data quality/consistency (1–5) and why?

- `data_quality_rating`: integer 1–5.
- `data_quality_evidence`: text.

1 = often incomplete/poorly organised; 5 = organised, accurate and consistent. Include supporting evidence.

## D14 — Systems

What integration or export capability is confirmed?

- `integration_capability`: single choice. Choices: `confirmed_api`, `file_export_import`, `manual_only`, `not_investigated`, `unknown`.
- `integration_evidence`: text.

A CRM being present does not confirm API access. Record what integration/export capability has actually been investigated.

## D15 — Systems

How standardised is the workflow (1–5), and what exceptions occur?

- `standardisation_rating`: integer 1–5.
- `exceptions_description`: text.

1 = highly variable/many exceptions; 5 = standardised/few exceptions.

## D16 — Systems

What security, privacy, compliance or human-approval requirements apply?

- `safety_requirements`: JSON array of text entries.
- `safety_notes`: text.

Use a JSON array of requirements and add explanatory notes. Do not include secrets or private records.

## D17 — Commercial

Who approves investment?

- `decision_authority`: single choice. Choices: `interviewee`, `owner_director`, `department_manager`, `multiple_stakeholders`, `unknown`.

## D18 — Commercial

When would the business ideally address the problem?

- `implementation_timeline`: single choice. Choices: `within_1_month`, `within_1_to_3_months`, `within_3_to_6_months`, `longer_term`, `no_defined_timeline`.

## D19 — Commercial

Is budget approved, indicative, conditional, absent or undiscussed? Optional budget amount.

- `budget_status`: single choice. Choices: `approved`, `indicative`, `conditional_value_case`, `none`, `not_discussed`.
- `indicative_budget`: nonnegative decimal number.

Budget amount is optional and uses currency from D08. Do not infer approved budget from interest.

## D20 — Commercial

Would the business consider a scoped pilot?

- `pilot_interest`: single choice. Choices: `yes`, `maybe`, `no`, `not_discussed`.

## D21 — Reuse

Is this workflow similar across teams/branches/other businesses?

- `workflow_reuse_observation`: single choice. Choices: `substantially_similar`, `partially_similar`, `business_specific`, `unknown`.
- `reuse_evidence`: text.

## D22 — Reuse

What solution elements seem standardisable versus custom?

- `reusable_components`: text.
- `customisation_needs`: text.

## D23 — Expansion

Are there other problems in this business worth investigating?

- `additional_opportunities`: JSON array of text entries.

## D24 — Consultant

Structured opportunity judgement with rationale and recommended next step.

- `business_impact_assessment`: single choice. Choices: `low`, `medium`, `high`, `unknown`.
- `commercial_potential`: single choice. Choices: `low`, `medium`, `high`, `unknown`.
- `solution_reusability`: single choice. Choices: `low`, `medium`, `high`, `unknown`.
- `technical_feasibility`: single choice. Choices: `low`, `medium`, `high`, `unknown`.
- `implementation_complexity`: integer 1–5.
- `expansion_potential`: single choice. Choices: `low`, `medium`, `high`, `unknown`.
- `assessment_evidence`: text.
- `evidence_status`: single choice. Choices: `self_reported`, `consultant_assessed`, `validated`, `unknown`.
- `recommended_next_action`: single choice. Choices: `further_discovery`, `process_improvement`, `technical_feasibility_test`, `pilot_proposal`, `defer`, `no_suitable_opportunity`.

The five low/medium/high/unknown dimensions are human assessments. Complexity: 1–2 simple, 3 medium, 4–5 complex; blank means unassessed. Include rationale in assessment_evidence. For validated evidence, describe what was validated in evidence/source notes. These assessments are not predictions of conversion or guaranteed returns.

## Assessment metadata (not extra questions)

Required: `assessment_id`, `prospect_id`, `workflow_id`, `dataset_version` (`1.0`). Optional: `assessment_date`, `assessor_id`, `source_reference`, `questionnaire_version` (new collections default to `1.0`). The prospect must exist in the survey dataset. Use a new assessment ID for each assessment. A workflow ID identifies a distinct workflow within a prospect; reassessments may reuse it.

Use UTF-8 CSV and JSON arrays for list fields. All other unanswered fields remain blank. Modelled weekly hours are a later derived measure, not an extra input column. Calculate them only when period and time basis are known, keep reported and modelled values separate, and flag material differences. Day/month conversions and a material-difference threshold are not specified in this contract; no conversion or ROI calculation is implemented in this pack.
