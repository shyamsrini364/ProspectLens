# Business Opportunity Survey

Questionnaire version: 1.0. Prepared for [Organisation Name].

Please answer using your current business experience. Choose one answer unless instructed otherwise. Optional text can be left blank; do not include confidential customer or employee details in free text. Contact details (S01–S03) are stored separately from analytical answers. Read the [privacy notice](privacy_notice_template.md) before submitting.

Collector setup: preserve these stable IDs and choice labels. Store the corresponding canonical codes from the [data dictionary](data_dictionary.md), not the display labels. The contract permits incomplete responses; it does not make every question compulsory. “Other” selections should include a short explanation. Blank answers remain missing.

## S01

What is your name? — short text

Stored field(s): `contact_name`.

Restricted contact field. Optional for descriptive analytics.

## S02

What is your business name? — short text

Stored field(s): `business_name`.

Restricted contact field. Optional for descriptive analytics.

## S03

What is your email address? — email

Stored field(s): `email`.

Restricted contact field. Optional for descriptive analytics.

## S04

Which industry best describes your business? — single choice

Stored field(s): `industry`, `industry_other`.

- Professional services (accounting, legal, consulting, etc.)
- Healthcare and allied health
- Retail or e-commerce
- Trades and construction
- Hospitality
- Real estate and property
- Manufacturing or logistics
- Education and training
- Other (please specify)

If Other is selected, please specify in `industry_other`.

## S05

Approximately how many people work in your business, including yourself? — single choice

Stored field(s): `employee_band`.

- Just me
- 2–5
- 6–20
- 21–50
- 51–200
- More than 200

## S06

Which activities currently consume the most time or create the biggest challenges for your business? — multi-select, **maximum three**

Stored field(s): `pain_points`, `pain_points_other`.

- Responding to customer enquiries
- Lead generation and sales follow-up
- Appointment scheduling and reminders
- Manual data entry and administration
- Preparing reports and analysing information
- Managing documents and information
- Finance, invoicing, and payment follow-up
- Staff scheduling and coordination
- Customer support and complaint handling
- Marketing and content creation
- Other (please specify)

Select at most three distinct choices. If Other is selected, please specify in `pain_points_other`.

## S07

Of the challenges listed above, which ONE would you most like to improve? — single choice using S06 categories

Stored field(s): `primary_pain_point`, `primary_pain_point_other`.

- Responding to customer enquiries
- Lead generation and sales follow-up
- Appointment scheduling and reminders
- Manual data entry and administration
- Preparing reports and analysing information
- Managing documents and information
- Finance, invoicing, and payment follow-up
- Staff scheduling and coordination
- Customer support and complaint handling
- Marketing and content creation
- Other (please specify)

Choose ONE of your S06 selections where the form supports this. If Other is selected, please specify in `primary_pain_point_other`. A mismatch is flagged for review, not rewritten.

## S08

Approximately how much staff time does this particular challenge consume each week, across your business? — single choice

Stored field(s): `weekly_hours_band`.

- Less than 2 hours
- 2–5 hours
- 6–10 hours
- 11–20 hours
- More than 20 hours
- Not sure

## S09

How significantly does this challenge affect your business? — 1–5

Stored field(s): `impact_rating`.

Choose an integer from 1 to 5: 1 = minor inconvenience; 5 = significant impact on productivity, costs, revenue or customer experience.

## S10

How is this work currently performed? — single choice

Stored field(s): `current_process`.

- Mostly manually
- A combination of manual work and digital tools
- Mostly through existing software
- Already automated, but experiencing frequent issues
- Not sure

## S11

Does the work involved in this challenge require handling sensitive or confidential information? — single choice

Stored field(s): `sensitive_data_frequency`.

- Yes, frequently (e.g. customer, health, financial, or employee information)
- Sometimes
- Rarely or never
- Not sure

## S12

Which business systems or software tools do you currently use? — multi-select

Stored field(s): `business_systems`, `business_systems_other`.

- Customer relationship management (CRM) software
- Accounting or invoicing software
- Booking or scheduling software
- Project or task management software
- Spreadsheets
- Email and messaging platforms
- Industry-specific business software
- None / mostly paper-based
- Other (please specify)

If None / mostly paper-based is selected, do not select other systems.

If Other is selected, please specify in `business_systems_other`.

## S13

Are there any software subscriptions your business pays for but does not fully utilise? — single choice; optional tool-name follow-up

Stored field(s): `subscription_underuse`, `underused_software_names`.

- Yes, several
- Yes, one or two
- No, most of our subscriptions are well utilised
- Not sure

Optional follow-up: name the underused software in `underused_software_names`. Show this text field only for Yes, several or Yes, one or two.

## S14

Is your business currently using AI tools? — single choice; conditional tools-and-use follow-up

Stored field(s): `ai_adoption`, `ai_tools_and_uses`.

- Yes, regularly across multiple business activities
- Yes, for a few specific tasks
- We have experimented with AI but don't use it consistently
- No, we are not currently using AI
- Not sure

Conditional follow-up — optional text: **Which AI tools have you tried or used, and what do you use them for?** Store the answer in `ai_tools_and_uses`. Name each tool and briefly describe its use. Show this text field only for regular use, specific tasks or experimented responses. The contract permits this field to remain blank.

## S15

What concerns, if any, would you have about adopting AI or automation in your business? — multi-select

Stored field(s): `ai_concerns`, `ai_concerns_other`.

- Cost and return on investment
- Data privacy and security
- Accuracy and reliability
- Staff training and adoption
- Integration with existing systems
- Compliance and legal requirements
- Lack of technical knowledge
- Unsure where AI would be useful
- No significant concerns
- Other (please specify)

Select No significant concerns on its own.

If Other is selected, please specify in `ai_concerns_other`.

## S16

Could you briefly explain your main concern about adopting AI or automation? — optional text

Stored field(s): `main_concern_details`.

Optional; show to all respondents.

## S17

If you could meaningfully improve your biggest business challenge, which outcome would be most valuable to your business? — single choice

Stored field(s): `desired_outcome`, `desired_outcome_other`.

- Save employee time
- Reduce operating costs
- Increase sales or revenue
- Improve customer response times
- Reduce mistakes or rework
- Improve customer satisfaction
- Support business growth without proportionately increasing staff
- Other (please specify)

If Other is selected, please specify in `desired_outcome_other`.

## S18

Would you be interested in discussing potential business improvements with `[Organisation Name]`? — single choice

Stored field(s): `followup_interest`.

- Yes, I'd be interested in a discussion
- Maybe, I'd like to learn more first
- Not at the moment

## S19

Would you like to share anything else about your business challenges or technology needs? — optional text

Stored field(s): `additional_comments`.

Optional; show to all respondents.

## Privacy and permissions (outside S01–S19)

Use separate controls, initially unchecked. Follow-up and marketing permissions are optional and independent of each other and of S18 interest.

- [ ] I acknowledge that I have read the [privacy notice](privacy_notice_template.md). (`privacy_acknowledged`)
- [ ] I give [Organisation Name] permission to contact me about discussing my business improvements. (`followup_consent`, optional)
- [ ] I give [Organisation Name] permission to send me marketing communications described in the privacy notice. (`marketing_consent`, optional)

Record `privacy_notice_version` and `consent_recorded_at` where possible. Store explicit choices as `true` or `false`; an unrecorded choice is blank (unknown), never assumed true. Store these controls with S01–S03 and the matching response/prospect IDs in the restricted contacts CSV. Collection metadata (`submitted_at`, versions and optional `recruitment_channel`) is not an extra survey question. New collection forms default `questionnaire_version` to `1.0`.
