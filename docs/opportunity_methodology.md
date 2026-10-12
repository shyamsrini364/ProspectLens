# Opportunity Intelligence — how to read the evidence

Model: **opportunity-v1.0-provisional**. Scores support investigation; they are
not validated statistical coefficients, conversion probabilities or ROI forecasts.
All weights, mappings, bands and thresholds live in `src/opportunity_config.py`.

## One business, one row

Survey submissions join to discovery through `prospect_id`. A `response_id`
identifies a submission, `assessment_id` an assessment, and the pair
`prospect_id` + `workflow_id` a workflow that may be reassessed.

For the business snapshot, select the latest survey by recorded calendar date;
dated records sort after undated ones. Ties use the lexicographically greatest
response ID as a deterministic tie-break, not proof of event order. Do not mix
answers from different submissions or fill missing current answers from older ones.
All original submissions remain in the business details and activity trend.

For discovery, keep the latest assessment date (then assessment ID) for each
workflow. Choose the workflow with the highest recorded D24 business impact
(high > medium > low > unknown), breaking ties by assessment date then ID.
This is an explicit investigation-priority rule, not a sum or maximum of
commercial scores. Never fall back to an older favourable assessment when a
newer one lacks evidence. Every assessment remains accessible in the pop-up.

The schema has no completion flag. For the **Discovery-Assessed Businesses**
KPI, a completed assessment means a named workflow, assessment date, assessment
rationale and a recorded self-reported, consultant-assessed or validated status.
This operational check is not independent evidence verification. A business with
any discovery record is marked Discovery Enriched, even if qualification remains
incomplete; the pop-up and coverage counts make that distinction visible.

## A — Business Opportunity Value (0–100)

The same survey-based model is used in both stages; it contains no commercial inputs.

| Component | Weight | Rule |
|---|---:|---|
| S09 primary-problem impact | 45% | Ratings 1, 2, 3, 4, 5 map to 0, 25, 50, 75, 100 points |
| S08 workload band | 35% | Under 2, 2–5, 6–10, 11–20, over 20 map to 0, 25, 50, 75, 100 ordinal points |
| S06 recurrence of the S07 primary category | 10% | Distinct businesses selecting the category / businesses answering S06 × 100 |
| S06 additional reported problems | 10% maximum | 0, 1, 2+ additional distinct categories map to 0, 50, 100 points |

Add the weighted contributions. All four components are required; missing impact,
unknown workload, absent primary problem, unanswered S06 or a primary problem
outside S06 prevents an overall value score. Do not renormalise weights when
evidence is absent. An explicit lowest rating is a real zero contribution; missing
data is not. Additional reported problems are unvalidated expansion possibilities.
They cannot add more than ten points, and free-text additional opportunities in
discovery are retained as evidence rather than used to inflate this score.

Workload points are an ordinal preference mapping, **not measured hours**. Recurrence
uses the full loaded latest-survey business sample and stays fixed when filters
change, so filtering does not alter a business's score. It is only a broad signal
of possible reuse, not proof of compatible systems or a reusable implementation.

## B — Commercial Potential (0–100)

**Survey Only: Preliminary Commercial Potential — insufficient evidence.** S18
interest alone cannot establish budget, authority or likelihood of purchase. Show
it as a separate answer; do not assign a numeric commercial score.

For the selected discovery workflow, all four components below are required:

| Component | Weight | Answer-to-points mapping |
|---|---:|---|
| Budget status, D19 | 35% | Approved 100; indicative 65; conditional on value case 40; none 0 |
| Paid/scoped pilot interest, D20 | 25% | Yes 100; maybe 50; no 0 |
| Implementation timeline, D18 | 20% | Within 1 month 100; 1–3 months 75; 3–6 months 50; longer term 25; no defined timeline 0 |
| Consultant commercial judgement, D24 | 20% | High 100; medium 50; low 0 |

Also require a named, dated workflow; nonblank assessment rationale; consultant-assessed
or validated evidence status; and an identified investment approver (D17).
The approver's role is a qualification check, not a numeric purchasing signal or
proof that this person attended. The pilot question does not establish agreement
to pay: confirm scope and price in further discovery. The recorded budget amount
is shown as evidence but does not earn additional points.

Unknown, not discussed or missing answers prevent scoring. Recorded “none”, “no”
and “no defined timeline” are genuine negative/weak signals and contribute zero.
These mappings are provisional judgements, not experimentally established buying
behaviour. D24 may overlap the structured commercial signals; its 20% weight must
be reviewed with real evidence before treating rankings as operational policy.

## C — Overall Prospect Opportunity Score

**Overall = 0.60 × Opportunity Value + 0.40 × Commercial Potential.**

Calculate only when both inputs meet their evidence checks. Scores retain full
precision for sorting, averaging and bands; displays round to one decimal.
Bands are High ≥80, Promising ≥60, Moderate ≥40, Low ≥0. These are priorities,
not probabilities. Matrix reference lines at 50 are provisional visual guides.

The matrix has one point per eligible business. Missing scores are omitted and
counted explicitly, never plotted at zero. The average KPI identifies its eligible
stage and denominator. Survey-only businesses have no composite rank; they remain
in the table and can be sorted by value or reported impact for further investigation.
Sorting remains separated by assessment stage; unknown values appear last.

## Filters, recurring problems and technical evidence

Filters combine with AND; multiple choices within one filter combine with OR.
Empty choices include every answer, including missing ones. Search matches the
pseudonymous prospect ID. The same selection feeds KPIs, tables, charts and exports.

Recurring problems count each latest-survey business once per selected S06 category.
Their denominator is businesses answering S06, not the number of selections;
percentages can total above 100%. Impact averages and workload distributions refer
only to businesses choosing that problem as primary, with an answered-impact count.

The schema has no closed discovery pain-category field. **Assessments at reporting
businesses** counts related business records, not category-matched workflows;
workflow-matched counts remain unassessed. Candidate solution families use the
explicit category mapping in configuration and are labelled hypotheses.

Technical feasibility, reuse and complexity are recorded discovery assessments,
not inferences from industry, AI adoption or business size. Complexity uses the
single existing rating: 1–2 Simple, 3 Medium, 4–5 Complex; missing is Not assessed.
The compact table shows all assessments, including historic reassessments. No
component-complexity aggregation or financial ROI estimation is performed.

## Research activity over time

Use submitted_at and assessment_date calendar dates as recorded (no inferred
timezone). Weekly periods run Monday–Sunday; monthly periods use calendar months.
The trend includes all unique response IDs and assessment IDs for selected
businesses; high-impact responses have S09 ≥4. Fill intermediate periods with zero
new activity and use a cumulative sum when selected. Count dates missing from the
trend explicitly; invalid dates are blocked by the existing CSV validator.
Cumulative increases measure research activity, not growing market demand.

## Contact permission and exports

The synthetic demo never opens contacts_and_consent.csv. Uploads can optionally
include consent data, validated against the supplied survey. A contact-ready flag
requires the existing validator's rule (yes/maybe interest, explicit follow-up
permission and valid email) **plus** acknowledgement, notice version and recorded
consent date for documented provenance. This stricter shortlist check does not
change raw schema validation. Email format does not verify ownership or delivery.

Only the latest representative survey's linked permission is considered; never
reuse older consent for a newer submission. Missing provenance is flagged for
review; no consent file means an analytical-only shortlist. Defer/no-opportunity
recommendations are excluded. No messages are sent. Personal names, business
names and emails are discarded after checking permissions and excluded from
rankings, downloads and the public demo. Identifiers and free-text survey/discovery
evidence may still be sensitive; uploads remain local session evidence.

Exports use allowlisted analytical columns. CSV text is protected against common
spreadsheet-formula prefixes. The Markdown decision brief uses the actual filtered
metrics, provenance, configuration version, filters and Australia/Sydney generation
timestamp. It is deterministic and needs no external AI API. All recommendations
require human review; synthetic results do not describe the real market.
