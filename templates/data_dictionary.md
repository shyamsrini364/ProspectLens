# ProspectLens data dictionary — version 1.0

The three CSV templates are UTF-8, comma-delimited and contain only their exact ordered header. Each survey row is a submission; each discovery row is an assessment of one workflow; each contact row links to a submission. JSON arrays are serialized inside CSV cells using normal CSV quoting. Use Python `csv.writer`/`csv.DictWriter`, not hand-built comma splitting.

## Shared rules and implementation decisions

- Blank (including whitespace-only cells) becomes Python `None`: unknown/missing, never zero or false. Explicit `unknown`, `unsure`, `not_discussed` and similar codes remain recorded answers. No missing ratings, workload hours or monetary values are fabricated.
- All table fields marked Optional accept blank. A nonblank value must satisfy its type/enum. Entire discovery and contacts datasets may be absent. Recommended survey answers produce warnings when missing, not errors.
- Codes are case-sensitive. Surrounding whitespace on scalar cells is trimmed; JSON entries must match codes exactly. Unknown codes are errors. Repeated list choices warn and remain in parsed data; examples count each respondent once per category. An empty JSON array means no recorded selections; for S06 it is not a valid answered denominator.
- Required contact response/prospect IDs and one contacts row per response are implementation decisions for unambiguous linkage and consent. Repeated survey submissions for one prospect are allowed. Repeated assessment IDs are errors; repeated workflow IDs within a prospect are allowed for reassessments.
- IDs are nonempty text, without an imposed R/P/D/W format. Uniqueness is checked within the supplied files; global uniqueness across separate imports needs a future persistent registry.
- Accepted dates: `YYYY-MM-DD`, or extended ISO timestamps such as `2026-10-10T09:00:00+11:00` (minutes required, seconds/fraction and timezone optional). Impossible calendar dates fail. No timezone is inferred.
- `staff_count` is interpreted as integer headcount. Other numeric measurements, including `current_baseline` and `target_value`, are finite nonnegative decimals. Describe qualitative success in `success_metric`. These are documented choices where the specification does not give exact Python types.
- `minutes_per_instance = 0` is allowed but warns for review: the schema has no actual-work flag. Actual work needs positive person-minutes. No extra CSV column or inferred work flag is introduced.
- Currency is free text (prefer a three-letter currency code); no currency whitelist is invented. A monetary amount requires explicit currency. `target_unit` describes the unit of D10 measurements. No exchange rates, ROI, weekly conversion factors or scoring are implemented.
- New collection templates default questionnaire version to `1.0`; validators preserve missing imported versions and warn for any nonblank version other than `1.0`. `dataset_version` is required.
- Error = invalid key, relationship, format, type, category or bound; resolve before analysis. Warning = missing analytical context, inconsistent selections, incomplete evidence or unknown version; review limitations. Warnings never rewrite answers.
- Evidence warnings are advisory, including missing rationale for complexity/data quality, unsupported confirmed API and validated status, or missing permission provenance. Free-text evidence is not machine verification.

Sensitivity categories: **Analytical-sensitive** includes commercially sensitive or potentially identifying answers even under pseudonymous IDs. **Restricted** is the entire contacts/consent table. Neither pseudonymisation nor validation proves anonymisation. Free text and evidence references require review before any public use.

## Survey responses

| Column | Source | Type / allowed values | Required / null | Unit | Sensitivity | Meaning |
|---|---|---|---|---|---|---|
| `response_id` | Metadata | text | Required; no blank | — | Analytical-sensitive | Globally unique survey submission ID; contacts reference the same submission. |
| `prospect_id` | Metadata | text | Required; no blank | — | Analytical-sensitive | Pseudonymous ID of the underlying business; may occur on repeated survey submissions and multiple assessments. |
| `submitted_at` | Metadata | ISO date or timestamp | Optional; blank = missing | — | Analytical-sensitive | When the survey was submitted. |
| `dataset_version` | Metadata | text | Required; no blank | — | Analytical-sensitive | Schema version. This contract is 1.0; unrecognised values trigger a compatibility warning. |
| `questionnaire_version` | Metadata | text | Optional; blank = missing | — | Analytical-sensitive | Questionnaire wording version. New collections default to 1.0; imports keep blanks missing and warn on unrecognised values. |
| `recruitment_channel` | Metadata | recruitment_channel codes below | Optional; blank = missing | — | Analytical-sensitive | Collection channel; metadata, not an extra survey question or evidence of representativeness. |
| `industry` | S04 | industry codes below | Recommended; blank warns | — | Analytical-sensitive | Business industry category. |
| `industry_other` | S04 | text | Optional; blank = missing | — | Analytical-sensitive | Explanation when industry is other. |
| `employee_band` | S05 | employee_band codes below | Optional; blank = missing | people band | Analytical-sensitive | Business size including respondent, recorded as a band. |
| `pain_points` | S06 | JSON string array; pain_points codes below | Recommended; blank warns | — | Analytical-sensitive | Up to three distinct time-consuming or challenging activity categories. |
| `pain_points_other` | S06 | text | Optional; blank = missing | — | Analytical-sensitive | Explanation of other pain points. |
| `primary_pain_point` | S07 | primary_pain_point codes below | Recommended; blank warns | — | Analytical-sensitive | Single highest-priority challenge; should be among pain_points. |
| `primary_pain_point_other` | S07 | text | Optional; blank = missing | — | Analytical-sensitive | Explanation when the primary challenge is other. |
| `weekly_hours_band` | S08 | weekly_hours_band codes below | Recommended; blank warns | staff-hours/week band | Analytical-sensitive | Total staff time spent on the primary challenge per week, recorded as an ordered band, not a measurement. |
| `impact_rating` | S09 | integer 1–5 | Recommended; blank warns | rating points | Analytical-sensitive | Severity: 1 minor inconvenience; 5 significant impact on productivity, costs, revenue or customer experience. |
| `current_process` | S10 | current_process codes below | Optional; blank = missing | — | Analytical-sensitive | How the primary challenge's work is currently performed. |
| `sensitive_data_frequency` | S11 | sensitive_data_frequency codes below | Optional; blank = missing | — | Analytical-sensitive | Frequency of handling sensitive/confidential information. |
| `business_systems` | S12 | JSON string array; business_systems codes below | Optional; blank = missing | — | Analytical-sensitive | Business software categories; none_paper should appear alone. |
| `business_systems_other` | S12 | text | Optional; blank = missing | — | Analytical-sensitive | Explanation of other systems. |
| `subscription_underuse` | S13 | subscription_underuse codes below | Optional; blank = missing | — | Analytical-sensitive | Whether paid software subscriptions are underused. |
| `underused_software_names` | S13 | text | Optional; blank = missing | — | Analytical-sensitive | Optional names, collected only for several or one_or_two underused subscriptions. |
| `ai_adoption` | S14 | ai_adoption codes below | Optional; blank = missing | — | Analytical-sensitive | Current level of AI use. |
| `ai_tools_and_uses` | S14 | text | Optional; blank = missing | — | Analytical-sensitive | Answers "Which AI tools have you tried or used, and what do you use them for?" Name the tools and describe their tasks, distinguishing trials from current use. Follow-up for regular_multiple, limited_tasks or experimented; optional when unknown. This is free text, not a closed tool-name enum or proof of integration capability. |
| `ai_concerns` | S15 | JSON string array; ai_concerns codes below | Optional; blank = missing | — | Analytical-sensitive | AI/automation concerns; none should appear alone. |
| `ai_concerns_other` | S15 | text | Optional; blank = missing | — | Analytical-sensitive | Explanation of other concerns. |
| `main_concern_details` | S16 | text | Optional; blank = missing | — | Analytical-sensitive | Optional explanation of the main concern. |
| `desired_outcome` | S17 | desired_outcome codes below | Optional; blank = missing | — | Analytical-sensitive | Single most valuable business improvement. |
| `desired_outcome_other` | S17 | text | Optional; blank = missing | — | Analytical-sensitive | Explanation of other desired outcome. |
| `followup_interest` | S18 | followup_interest codes below | Optional; blank = missing | — | Analytical-sensitive | Interest in discussion; never a substitute for permission. |
| `additional_comments` | S19 | text | Optional; blank = missing | — | Analytical-sensitive | Optional additional business challenges or technology needs. |

## Restricted contacts and consent

| Column | Source | Type / allowed values | Required / null | Unit | Sensitivity | Meaning |
|---|---|---|---|---|---|---|
| `response_id` | Metadata | text | Required; no blank | — | Restricted | Globally unique survey submission ID; contacts reference the same submission. |
| `prospect_id` | Metadata | text | Required; no blank | — | Restricted | Pseudonymous ID of the underlying business; may occur on repeated survey submissions and multiple assessments. |
| `contact_name` | S01 | text | Optional; blank = missing | — | Restricted | Respondent's name; restricted contact data. |
| `business_name` | S02 | text | Optional; blank = missing | — | Restricted | Business name; restricted identifying data. |
| `email` | S03 | email text (structural check) | Optional; blank = missing | — | Restricted | Optional email address; structural validation does not prove ownership or deliverability. |
| `privacy_acknowledged` | Consent control (outside S01–S19) | true / false | Optional; blank = missing | — | Restricted | Recorded acknowledgement of reading the privacy notice; distinct from permissions. |
| `privacy_notice_version` | Consent control (outside S01–S19) | text | Optional; blank = missing | — | Restricted | Version of the notice shown at collection. |
| `followup_consent` | Consent control (outside S01–S19) | true / false | Optional; blank = missing | — | Restricted | Independent optional permission to make follow-up contact; never inferred from interest. |
| `marketing_consent` | Consent control (outside S01–S19) | true / false | Optional; blank = missing | — | Restricted | Independent optional marketing permission; never inferred from follow-up consent. |
| `consent_recorded_at` | Consent control (outside S01–S19) | ISO date or timestamp | Optional; blank = missing | — | Restricted | When acknowledgement/permission choices were recorded; record where possible. |

## Discovery assessments

| Column | Source | Type / allowed values | Required / null | Unit | Sensitivity | Meaning |
|---|---|---|---|---|---|---|
| `assessment_id` | Metadata | text | Required; no blank | — | Analytical-sensitive | Unique discovery assessment record ID; use a new ID for reassessments. |
| `prospect_id` | Metadata | text | Required; no blank | — | Analytical-sensitive | Pseudonymous ID of the underlying business; may occur on repeated survey submissions and multiple assessments. |
| `workflow_id` | Metadata | text | Required; no blank | — | Analytical-sensitive | ID of a distinct workflow within a prospect. The pair (prospect_id, workflow_id) identifies the workflow; reassessments may reuse it. |
| `assessment_date` | Metadata | ISO date or timestamp | Optional; blank = missing | — | Analytical-sensitive | Date/time of the discovery assessment. |
| `assessor_id` | Metadata | text | Optional; blank = missing | — | Analytical-sensitive | Identifier of the consultant; may itself be identifying information. |
| `source_reference` | Metadata | text | Optional; blank = missing | — | Analytical-sensitive | Reference to supporting notes/evidence; avoid secrets or unrestricted links to private material. |
| `dataset_version` | Metadata | text | Required; no blank | — | Analytical-sensitive | Schema version. This contract is 1.0; unrecognised values trigger a compatibility warning. |
| `questionnaire_version` | Metadata | text | Optional; blank = missing | — | Analytical-sensitive | Questionnaire wording version. New collections default to 1.0; imports keep blanks missing and warn on unrecognised values. |
| `workflow_name` | D01 | text | Optional; blank = missing | — | Analytical-sensitive | Name of the one workflow/opportunity assessed. |
| `workflow_steps` | D02 | text | Optional; blank = missing | — | Analytical-sensitive | Description of the current process from beginning to end. |
| `stakeholders` | D03 | JSON array of nonempty text/code strings (open vocabulary) | Optional; blank = missing | — | Analytical-sensitive | Roles, teams or external parties involved; prefer role descriptions to personal names. |
| `bottlenecks` | D04 | text | Optional; blank = missing | — | Analytical-sensitive | Biggest delays, errors or frustrations. |
| `activity_volume` | D05 | finite decimal ≥ 0 | Optional; blank = missing | occurrences / volume_period | Analytical-sensitive | Number of occurrences in volume_period; not staff count or person-minutes. |
| `volume_period` | D05 | volume_period codes below | Optional; blank = missing | — | Analytical-sensitive | Period for activity_volume; unknown cannot support weekly modelling. |
| `minutes_per_instance` | D06 | finite decimal ≥ 0 | Optional; blank = missing | person-minutes / occurrence | Analytical-sensitive | Total person-minutes per occurrence; do not automatically multiply by staff_count. |
| `staff_count` | D07 | integer ≥ 0 | Optional; blank = missing | people | Analytical-sensitive | Number of people involved; integer headcount. |
| `reported_staff_hours_per_week` | D07 | finite decimal ≥ 0 | Optional; blank = missing | staff-hours/week | Analytical-sensitive | Total staff hours per week reported by the respondent, across people. |
| `labour_cost_per_hour` | D08 | finite decimal ≥ 0 | Optional; blank = missing | currency/hour | Analytical-sensitive | Optional voluntarily shared hourly labour cost; requires explicit currency. |
| `currency` | D08 | text | Optional; blank = missing | — | Analytical-sensitive | Currency for labour_cost_per_hour and indicative_budget; explicit when either amount is supplied, configurable by organisation. |
| `observed_impact_types` | D09 | JSON string array; observed_impact_types codes below | Optional; blank = missing | — | Analytical-sensitive | Observed negative outcome categories; explain other in impact_evidence. |
| `impact_evidence` | D09 | text | Optional; blank = missing | — | Analytical-sensitive | Evidence for observed negative outcomes. |
| `success_metric` | D10 | text | Optional; blank = missing | — | Analytical-sensitive | Description of how success will be measured, including qualitative context. |
| `current_baseline` | D10 | finite decimal ≥ 0 | Optional; blank = missing | target_unit | Analytical-sensitive | Current numeric value of success_metric, expressed in target_unit. |
| `target_value` | D10 | finite decimal ≥ 0 | Optional; blank = missing | target_unit | Analytical-sensitive | Desired numeric value of success_metric, expressed in target_unit. |
| `target_unit` | D10 | text | Optional; blank = missing | — | Analytical-sensitive | Unit shared by current_baseline and target_value; e.g. minutes, percentage or count. |
| `systems_involved` | D11 | JSON array of nonempty text/code strings (open vocabulary) | Optional; blank = missing | — | Analytical-sensitive | Actual applications/tools involved; free text entries, not the survey's closed category set. |
| `information_storage` | D12 | information_storage codes below | Optional; blank = missing | — | Analytical-sensitive | Where the required information is stored. |
| `data_quality_rating` | D13 | integer 1–5 | Optional; blank = missing | rating points | Analytical-sensitive | 1 often incomplete/poorly organised; 5 organised, accurate and consistent. |
| `data_quality_evidence` | D13 | text | Optional; blank = missing | — | Analytical-sensitive | Reasons and evidence for the data quality rating. |
| `integration_capability` | D14 | integration_capability codes below | Optional; blank = missing | — | Analytical-sensitive | Confirmed integration/export status. Presence of a CRM does not confirm an API. |
| `integration_evidence` | D14 | text | Optional; blank = missing | — | Analytical-sensitive | Evidence for the integration capability. |
| `standardisation_rating` | D15 | integer 1–5 | Optional; blank = missing | rating points | Analytical-sensitive | 1 highly variable/many exceptions; 5 standardised/few exceptions. |
| `exceptions_description` | D15 | text | Optional; blank = missing | — | Analytical-sensitive | Description of workflow exceptions. |
| `safety_requirements` | D16 | JSON array of nonempty text/code strings (open vocabulary) | Optional; blank = missing | — | Analytical-sensitive | Security, privacy, compliance or human-approval requirements; open text/code vocabulary. |
| `safety_notes` | D16 | text | Optional; blank = missing | — | Analytical-sensitive | Explanatory safety notes; do not include credentials or private records. |
| `decision_authority` | D17 | decision_authority codes below | Optional; blank = missing | — | Analytical-sensitive | Who approves investment. |
| `implementation_timeline` | D18 | implementation_timeline codes below | Optional; blank = missing | — | Analytical-sensitive | When the business would ideally address the problem. |
| `budget_status` | D19 | budget_status codes below | Optional; blank = missing | — | Analytical-sensitive | State of budget evidence, independent of interest. |
| `indicative_budget` | D19 | finite decimal ≥ 0 | Optional; blank = missing | currency | Analytical-sensitive | Optional budget amount in currency; do not invent when absent or undiscussed. |
| `pilot_interest` | D20 | pilot_interest codes below | Optional; blank = missing | — | Analytical-sensitive | Whether the business would consider a scoped pilot. |
| `workflow_reuse_observation` | D21 | workflow_reuse_observation codes below | Optional; blank = missing | — | Analytical-sensitive | Observed similarity across teams, branches or businesses. |
| `reuse_evidence` | D21 | text | Optional; blank = missing | — | Analytical-sensitive | Evidence for the reuse observation. |
| `reusable_components` | D22 | text | Optional; blank = missing | — | Analytical-sensitive | Text describing potentially standardisable solution elements; not a JSON-list field. |
| `customisation_needs` | D22 | text | Optional; blank = missing | — | Analytical-sensitive | Text describing elements requiring customisation. |
| `additional_opportunities` | D23 | JSON array of nonempty text/code strings (open vocabulary) | Optional; blank = missing | — | Analytical-sensitive | Other business problems worth investigating; no assessed claims implied. |
| `business_impact_assessment` | D24 | business_impact_assessment codes below | Optional; blank = missing | — | Analytical-sensitive | Consultant's business-impact judgement, supported by evidence. |
| `commercial_potential` | D24 | commercial_potential codes below | Optional; blank = missing | — | Analytical-sensitive | Consultant's commercial judgement; not a conversion probability. |
| `solution_reusability` | D24 | solution_reusability codes below | Optional; blank = missing | — | Analytical-sensitive | Consultant's assessment of reusable solution potential. |
| `technical_feasibility` | D24 | technical_feasibility codes below | Optional; blank = missing | — | Analytical-sensitive | Consultant's feasibility assessment; never inferred from survey answers. |
| `implementation_complexity` | D24 | integer 1–5 | Optional; blank = missing | rating points | Analytical-sensitive | Human-assessed complexity: 1–2 simple, 3 medium, 4–5 complex. Include rationale in assessment_evidence. |
| `expansion_potential` | D24 | expansion_potential codes below | Optional; blank = missing | — | Analytical-sensitive | Consultant's assessment of expansion potential. |
| `assessment_evidence` | D24 | text | Optional; blank = missing | — | Analytical-sensitive | Rationale, evidence and uncertainty supporting consultant judgements. |
| `evidence_status` | D24 | evidence_status codes below | Optional; blank = missing | — | Analytical-sensitive | Evidence status; validated requires a description of what was validated in evidence/source notes. |
| `recommended_next_action` | D24 | recommended_next_action codes below | Optional; blank = missing | — | Analytical-sensitive | Consultant's recommended next step for human review; no task integration. |

## Canonical codes and display labels

Survey labels below are verbatim from the agreed questionnaire. Discovery choices are stored codes from the specification; readable labels below are mechanical presentations of those codes, without adding choices. Recruitment labels describe metadata.

### industry

| Stored code | Display label |
|---|---|
| `professional_services` | Professional services (accounting, legal, consulting, etc.) |
| `healthcare_allied` | Healthcare and allied health |
| `retail_ecommerce` | Retail or e-commerce |
| `trades_construction` | Trades and construction |
| `hospitality` | Hospitality |
| `real_estate` | Real estate and property |
| `manufacturing_logistics` | Manufacturing or logistics |
| `education_training` | Education and training |
| `other` | Other (please specify) |

### employee_band

| Stored code | Display label |
|---|---|
| `solo` | Just me |
| `2_5` | 2–5 |
| `6_20` | 6–20 |
| `21_50` | 21–50 |
| `51_200` | 51–200 |
| `over_200` | More than 200 |

### pain_points

| Stored code | Display label |
|---|---|
| `customer_enquiries` | Responding to customer enquiries |
| `sales_followup` | Lead generation and sales follow-up |
| `appointment_scheduling` | Appointment scheduling and reminders |
| `manual_data_entry` | Manual data entry and administration |
| `reporting_analysis` | Preparing reports and analysing information |
| `documents_information` | Managing documents and information |
| `finance_invoicing` | Finance, invoicing, and payment follow-up |
| `staff_coordination` | Staff scheduling and coordination |
| `customer_support` | Customer support and complaint handling |
| `marketing_content` | Marketing and content creation |
| `other` | Other (please specify) |

### primary_pain_point

| Stored code | Display label |
|---|---|
| `customer_enquiries` | Responding to customer enquiries |
| `sales_followup` | Lead generation and sales follow-up |
| `appointment_scheduling` | Appointment scheduling and reminders |
| `manual_data_entry` | Manual data entry and administration |
| `reporting_analysis` | Preparing reports and analysing information |
| `documents_information` | Managing documents and information |
| `finance_invoicing` | Finance, invoicing, and payment follow-up |
| `staff_coordination` | Staff scheduling and coordination |
| `customer_support` | Customer support and complaint handling |
| `marketing_content` | Marketing and content creation |
| `other` | Other (please specify) |

### weekly_hours_band

| Stored code | Display label |
|---|---|
| `under_2` | Less than 2 hours |
| `2_5` | 2–5 hours |
| `6_10` | 6–10 hours |
| `11_20` | 11–20 hours |
| `over_20` | More than 20 hours |
| `unsure` | Not sure |

### current_process

| Stored code | Display label |
|---|---|
| `mostly_manual` | Mostly manually |
| `mixed_manual_digital` | A combination of manual work and digital tools |
| `mostly_software` | Mostly through existing software |
| `automated_with_issues` | Already automated, but experiencing frequent issues |
| `unsure` | Not sure |

### sensitive_data_frequency

| Stored code | Display label |
|---|---|
| `frequent` | Yes, frequently (e.g. customer, health, financial, or employee information) |
| `sometimes` | Sometimes |
| `rare_never` | Rarely or never |
| `unsure` | Not sure |

### business_systems

| Stored code | Display label |
|---|---|
| `crm` | Customer relationship management (CRM) software |
| `accounting_invoicing` | Accounting or invoicing software |
| `booking_scheduling` | Booking or scheduling software |
| `task_management` | Project or task management software |
| `spreadsheets` | Spreadsheets |
| `email_messaging` | Email and messaging platforms |
| `industry_specific` | Industry-specific business software |
| `none_paper` | None / mostly paper-based |
| `other` | Other (please specify) |

### subscription_underuse

| Stored code | Display label |
|---|---|
| `several` | Yes, several |
| `one_or_two` | Yes, one or two |
| `mostly_utilised` | No, most of our subscriptions are well utilised |
| `unsure` | Not sure |

### ai_adoption

| Stored code | Display label |
|---|---|
| `regular_multiple` | Yes, regularly across multiple business activities |
| `limited_tasks` | Yes, for a few specific tasks |
| `experimented` | We have experimented with AI but don't use it consistently |
| `not_using` | No, we are not currently using AI |
| `unsure` | Not sure |

### ai_concerns

| Stored code | Display label |
|---|---|
| `cost_roi` | Cost and return on investment |
| `privacy_security` | Data privacy and security |
| `accuracy_reliability` | Accuracy and reliability |
| `staff_adoption` | Staff training and adoption |
| `systems_integration` | Integration with existing systems |
| `legal_compliance` | Compliance and legal requirements |
| `technical_knowledge` | Lack of technical knowledge |
| `uncertain_use_cases` | Unsure where AI would be useful |
| `none` | No significant concerns |
| `other` | Other (please specify) |

### desired_outcome

| Stored code | Display label |
|---|---|
| `save_time` | Save employee time |
| `reduce_costs` | Reduce operating costs |
| `increase_revenue` | Increase sales or revenue |
| `faster_responses` | Improve customer response times |
| `reduce_errors` | Reduce mistakes or rework |
| `improve_satisfaction` | Improve customer satisfaction |
| `scale_without_staff_growth` | Support business growth without proportionately increasing staff |
| `other` | Other (please specify) |

### followup_interest

| Stored code | Display label |
|---|---|
| `yes` | Yes, I'd be interested in a discussion |
| `maybe` | Maybe, I'd like to learn more first |
| `not_now` | Not at the moment |

### recruitment_channel

| Stored code | Display label |
|---|---|
| `in_person` | in person |
| `direct_invitation` | direct invitation |
| `referral` | referral |
| `website` | website |
| `other` | other |
| `unknown` | unknown |

### volume_period

| Stored code | Display label |
|---|---|
| `day` | day |
| `week` | week |
| `month` | month |
| `unknown` | unknown |

### information_storage

| Stored code | Display label |
|---|---|
| `central_system` | central system |
| `multiple_systems` | multiple systems |
| `spreadsheets_documents` | spreadsheets documents |
| `partly_paper` | partly paper |
| `unknown` | unknown |

### integration_capability

| Stored code | Display label |
|---|---|
| `confirmed_api` | confirmed api |
| `file_export_import` | file export import |
| `manual_only` | manual only |
| `not_investigated` | not investigated |
| `unknown` | unknown |

### decision_authority

| Stored code | Display label |
|---|---|
| `interviewee` | interviewee |
| `owner_director` | owner director |
| `department_manager` | department manager |
| `multiple_stakeholders` | multiple stakeholders |
| `unknown` | unknown |

### implementation_timeline

| Stored code | Display label |
|---|---|
| `within_1_month` | within 1 month |
| `within_1_to_3_months` | within 1 to 3 months |
| `within_3_to_6_months` | within 3 to 6 months |
| `longer_term` | longer term |
| `no_defined_timeline` | no defined timeline |

### budget_status

| Stored code | Display label |
|---|---|
| `approved` | approved |
| `indicative` | indicative |
| `conditional_value_case` | conditional value case |
| `none` | none |
| `not_discussed` | not discussed |

### pilot_interest

| Stored code | Display label |
|---|---|
| `yes` | yes |
| `maybe` | maybe |
| `no` | no |
| `not_discussed` | not discussed |

### workflow_reuse_observation

| Stored code | Display label |
|---|---|
| `substantially_similar` | substantially similar |
| `partially_similar` | partially similar |
| `business_specific` | business specific |
| `unknown` | unknown |

### evidence_status

| Stored code | Display label |
|---|---|
| `self_reported` | self reported |
| `consultant_assessed` | consultant assessed |
| `validated` | validated |
| `unknown` | unknown |

### recommended_next_action

| Stored code | Display label |
|---|---|
| `further_discovery` | further discovery |
| `process_improvement` | process improvement |
| `technical_feasibility_test` | technical feasibility test |
| `pilot_proposal` | pilot proposal |
| `defer` | defer |
| `no_suitable_opportunity` | no suitable opportunity |

### observed_impact_types

| Stored code | Display label |
|---|---|
| `delayed_responses` | delayed responses |
| `errors_rework` | errors rework |
| `missed_sales` | missed sales |
| `complaints` | complaints |
| `extra_costs` | extra costs |
| `overtime` | overtime |
| `other` | other |

### business_impact_assessment

| Stored code | Display label |
|---|---|
| `low` | low |
| `medium` | medium |
| `high` | high |
| `unknown` | unknown |

### commercial_potential

| Stored code | Display label |
|---|---|
| `low` | low |
| `medium` | medium |
| `high` | high |
| `unknown` | unknown |

### solution_reusability

| Stored code | Display label |
|---|---|
| `low` | low |
| `medium` | medium |
| `high` | high |
| `unknown` | unknown |

### technical_feasibility

| Stored code | Display label |
|---|---|
| `low` | low |
| `medium` | medium |
| `high` | high |
| `unknown` | unknown |

### expansion_potential

| Stored code | Display label |
|---|---|
| `low` | low |
| `medium` | medium |
| `high` | high |
| `unknown` | unknown |

## Cross-field checks and analytical boundaries

S06 permits at most three distinct choices (error). S07 outside S06 warns. S12 `none_paper` mixed with another selection warns. S15 `none` mixed with concerns warns. An `other` selection without its corresponding explanation warns, including discovery observed impacts. Recruitment `other` has no explanation column in this schema and does not require one. S14 tool details under `not_using` warn. S13 names outside the underuse branch warn.

Discovery prospect IDs must exist in survey data. Contacts must match both the response ID and its prospect ID. Survey/discovery keys must be unique; contacts also use one row per response. A workflow ID is scoped to a prospect and can recur for reassessment. Validation cannot infer whether two descriptions actually concern distinct real workflows.

A private contact-ready candidate requires survey interest `yes` or `maybe`, explicit `followup_consent = true`, and a structurally valid email. Marketing permission and privacy acknowledgement do not replace follow-up permission. Without contacts, only an interest-based investigation list can be made. The helper returns eligible IDs only; it is not a public export or contact-sending function.

For pain-point prevalence, filter survey respondents first, then count distinct response IDs selecting a category divided by respondents with a nonempty valid S06 answer. Totals across categories can exceed 100%. High-impact prevalence uses only valid S09 answers and defaults to the configured example threshold of 4. Do not join to a flat discovery table before computing survey denominators: several assessments could multiply respondents.

Workload codes remain ordered bands; `unsure` and missing values are never zero hours. Keep precise discovery measurements separate. All consultant dimensions, complexity, budget and feasibility remain unassessed when missing. No conversion probabilities, commercial predictions or ROI are computed. The example YAML preserves the specified thresholds and affects labels, units and transparent thresholds only; the pack does not yet parse YAML or run an analytics application.
