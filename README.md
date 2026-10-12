# ProspectLens: Market & Opportunity Intelligence

## First checkout

This repository contains the generator rather than runtime datasets or contact
files. From a new checkout in PowerShell, use Python 3.13 (the tested version),
then run:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dashboard.txt
.\.venv\Scripts\python.exe -m scripts.generate_synthetic_data
.\.venv\Scripts\python.exe -m unittest discover -s tests -q
.\.venv\Scripts\python.exe -m streamlit run app.py
```

On macOS/Linux use `.venv/bin/python` in place of `.\.venv\Scripts\python.exe`.
The generator creates fictional survey, discovery and restricted contact CSVs
locally; all stay ignored by Git. Default dashboard loading does not open contacts.
See the [editable project overview](docs/week1_submission.md),
[video talking points](docs/week1_demo_talking_points.md) and
[submission evidence](docs/submission_evidence.md). No public deployment or
open-source licence is claimed.

Version 1.0, based on the agreed Template Pack Specification dated 10 October 2026.
Steps 2 and 3 implement the data contract and reproducible fictional datasets:
questionnaires, empty CSV templates, dictionary, privacy/configuration examples,
validation, synthetic generation, a profiling report and automated tests.
Step 4 adds the first working Streamlit dashboard: **View 1 — Market Intelligence**.
Step 5 adds **Opportunity Intelligence** with business-level scoring, evidence
pop-ups, shared filters, a matrix, rankings, research trends and decision exports.
Read the [Opportunity Intelligence guide](docs/opportunity_intelligence_guide.md)
for a walkthrough and the [scoring methodology](docs/opportunity_methodology.md)
for the provisional rules and evidence requirements.
The Template Pack and generator use standard-library Python (3.10+). The five
analysis examples and report use pandas 3.0.6 (Python 3.11+). The tested project
environment is Python 3.13.14; pandas is installed in the local `.venv`.

Start with the [synthetic data report](docs/synthetic_data_report.md) for the actual
distributions, missing-value counts, five pandas examples and their results.
**SYNTHETIC DATA — NOT REAL MARKET FINDINGS.**

## Run the Market Intelligence dashboard

From this project folder in PowerShell:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dashboard.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Open <http://127.0.0.1:8501>. Stop the server with Ctrl+C. Dependencies are pinned
to the tested pandas 3.0.6, Streamlit 1.65.0 and Plotly 7.1.0. The existing survey
CSV and generation manifest are required; the dashboard never generates replacement
data. It stops with an actionable error if a file is missing, invalid or does not
match the synthetic manifest. It does not open the contacts or discovery CSVs.

The existing **top-right three-dot menu** contains a lens-specific export action,
then **Manage data**, immediately below the appearance controls. Manage data also
appears below the introduction on both dashboards and opens the same dialog.
Market exports use `market_intelligence_export.csv`, preserving the exact
30-column survey contract, JSON arrays and blank answers. Opportunity ranking
exports use `opportunity_intelligence_export.csv`; these analytical columns are
not a survey upload template. Empty selections produce headers; contact fields
are excluded from analytical exports.

Upload accepts a UTF-8 survey CSV plus optional discovery and contacts/consent
CSVs, up to 5 MB per file. The existing validator checks the
exact headers, CSV quoting, row widths, IDs, JSON arrays and category values.
Invalid files leave the current view untouched. A valid preview reports response
and warning counts; **Use data in both dashboards** applies the shared bundle
and clears both lenses' filters. Both lenses use the same survey; optional
discovery enriches Opportunity Intelligence. Uploaded data never inherits demo
discovery records.
Data stays in this browser session's server memory, with no overwrite of the saved
demo files. Uploads are labelled as uploaded, not as verified synthetic data.
Open Manage data again and choose **Restore synthetic demo for both dashboards**
to return both lenses to the original sample. Manage data also works when the
saved demo is unavailable.

Streamlit's [supported menu configuration](https://docs.streamlit.io/develop/api-reference/configuration/st.set_page_config)
does not accept custom action widgets. `assets/native_menu.js` is a small,
version-specific adapter for pinned Streamlit 1.65.0: it inserts two menu buttons
that invoke native Python download/upload widgets. It preserves the native menu
and theme controls, sends no data to third-party services, and never interpolates
CSV contents into JavaScript. Re-run the browser checks when upgrading Streamlit,
since this adapter depends on the frontend menu structure. `src/market_menu.py`
owns the upload dialog and actions. The CSV validator additionally accepts decoded
in-memory text streams, using the same validation rules as filesystem inputs.
The title now contains the heading and description only, and the Filters section
blends into the page background. Synthetic provenance remains in the source and
data-quality notes.

Choose **Light** or **Dark** in the top-right menu to switch between Celestial
Pearl and Pearl Nocturne. The initial theme follows Streamlit/browser preference,
with the configured light theme as the fallback. Filters remain selected across
theme changes. No data is uploaded or published by launching this local app.

## Dashboard files and data flow

| File | Responsibility |
|---|---|
| `app.py` | Small Streamlit entry point |
| `src/market_data.py` | Survey-only loading, existing validation, synthetic fingerprint verification |
| `src/market_metrics.py` | Pure pandas filters, KPIs, frequency tables and missing-answer summaries |
| `src/market_charts.py` | Plotly bars, heatmaps and optional AI-adoption donuts from aggregate tables |
| `src/market_ui.py` | Navigation, controls, KPI cards, chart panels, warnings and empty states |
| `src/market_style.py` | Read the supplied semantic CSS tokens for both themes |
| `assets/market.css` | Responsive dashboard layout and component styling |
| `.streamlit/config.toml` | Native light/dark controls, fonts and local server settings |
| `requirements-dashboard.txt` | Runtime dependencies; includes existing analytics requirements |
| `requirements-dev.txt` | Optional Playwright dependency for browser checks |
| `tests/test_market_intelligence.py` | Hand-counted calculation, filtering, chart and loader tests |
| `tests/test_ai_adoption.py` | AI heatmap/donut edge cases and independent checks against the local survey CSV |
| `tests/test_market_app.py` | Streamlit AppTest widget, empty-state and error-state tests |
| `scripts/smoke_test_market_dashboard.py` | Optional real-browser theme, responsive and interaction checks |

The existing schemas, questionnaires, validation rules, datasets, scoring assumptions
and design reference files are unchanged. README is extended with these run and
learning notes. The dashboard does not calculate opportunity scores or ROI.

Data moves through a short chain:

```text
survey_responses.csv + matching generation_manifest.json
    -> existing validate_csv_files (exact headers and record checks)
    -> pandas DataFrame from the validator's typed survey rows
    -> one shared filtered DataFrame
    -> KPI values + respondent frequency tables
    -> Streamlit metric cards + Plotly charts + inspectable tables
```

A DataFrame is like a spreadsheet in memory. The validator already turns JSON
array cells into Python lists, impact ratings into integers, and blanks into
missing values. Building the DataFrame from those parsed rows avoids interpreting
the CSV a second way. Any validation error blocks the entire file instead of
quietly removing records and changing the sample. Warnings remain visible.

For this small dataset, the loader runs on each full Streamlit rerun; there is no
cache that could hide a CSV edit. It checks the file fingerprint before and after
validation. Streamlit reruns the page when a filter changes. `st.session_state`
remembers selections, while the reset callback clears all four together. A small
one-second `st.fragment` checks native theme changes, which do not otherwise rerun
Python immediately in this Streamlit version. Only a changed theme triggers a
full rerun; the fragment does not repeatedly reload data or calculate charts.

## Filters and denominators

Industry, business size, primary pain point and AI adoption all filter the same
DataFrame. Multiple selections within one control mean **OR**; different controls
combine with **AND**. For example, Retail or Hospitality plus Just me includes
solo respondents from either industry. An empty control means all answers.
Missing answers are a separate selectable option when present. Options are drawn
from the full loaded sample, so combinations with zero results are possible and
display a clear empty state with a reset button.

`Series.isin` checks whether each row belongs to the selected categories. Combining
these Boolean masks with `&` is like keeping only spreadsheet rows that satisfy
every filter. All KPI and chart functions receive the resulting rows, so none
uses an unfiltered denominator by accident. The source validation line is explicitly
file-wide; the selection count, chart tables and quality panel describe filtered rows.

| KPI | Calculation | Default synthetic sample |
|---|---|---|
| Total survey responses | Distinct `response_id` in the selection | 150 |
| Industries represented | Distinct nonmissing `industry` categories; Other is one category | 9 |
| High-impact problems | S09 ratings 4–5 / responses with a recorded S09 rating | 83 / 146 = 56.8%; 4 missing |
| Currently using AI | S14 `regular_multiple` or `limited_tasks` / answered S14 | 60 / 146 = 41.1%; 4 missing |
| Interested in follow-up | S18 `yes` / answered S18 | 69 / 150 = 46.0%; 0 missing |

Experimentation is shown separately from current AI use. S14 Not sure remains in
the answered denominator and is separately counted. S18 Maybe remains in its
denominator but is not counted as Yes; 56 respondents answered Maybe in this
sample. Follow-up interest never establishes permission to contact someone.

The counting unit is a **survey submission**. Repeated submissions from one
prospect remain separate responses, and the total card also shows distinct
prospects so the distinction is visible. There are no joins that could multiply
survey rows by the number of discovery assessments.

Multi-select S06 and S15 need an extra step. `explode` temporarily gives each
choice its own row; `drop_duplicates(["response_id", field])` ensures one response
counts only once in a category. The denominator is counted **before** exploding.
If Alice selects three challenges and Ben selects one, there are still two
respondents, not four businesses. Each category is a share of those two answers,
so multi-select percentages can add to more than 100%.

## Charts and data quality

| Visualisation | Type | Denominator |
|---|---|---|
| Operational pain points | Horizontal bars | Selected responses answering S06 |
| Pain points across industries | Heatmap | Responses answering S06 within each selected industry |
| AI adoption by industry | Heatmap; optional small multiple donut charts | Responses answering S14 within each selected industry |
| Business size | Ordered horizontal bars | Selected responses answering S05 |
| Most desired outcomes | Rounded vertical columns | Selected responses answering S17; single-select |
| Concerns about AI and automation | Ranked rounded horizontal bars with 100% tracks | Selected responses answering S15 |

Counts and denominators appear on bars or in hover details and are available in
each panel's expandable table. Blank answers and empty multi-select lists are
missing. Not sure and No significant concerns remain explicit answered categories.
An industry with no answers has no percentage; a zero-denominator KPI displays
an em dash. Missing industry answers remain a labelled group in grouped charts.
Fewer than five answered responses triggers a small-sample caution, matching the
existing example configuration. This is not a test of statistical significance.

The AI heatmap keeps all five S14 categories separate, including Not sure and
Not using AI. Industries are sorted by **answered S14 count**, descending; ties
retain the existing industry order. Each row label shows that denominator as
`n`, with an explicit small-sample flag below five answers. Cells show one decimal
place when needed: `0%` means nobody selected that category, while `N/A` means
the industry has no answered S14 responses. A fixed 0–100% single-blue scale makes
the intensity comparable after filtering. Hover shows the industry, full answer
label, count, denominator, percentage and missing count. Display rounding can
make a row total slightly different from 100%; calculations use unrounded values.

The optional **Donut charts** selector uses exactly the same aggregate table,
one donut per industry, with three columns on desktop and one on mobile. The
heatmap expands with available width and scrolls horizontally below 640 pixels
to preserve readable labels and values. Both views retain the expandable table.

To verify the AI chart manually, reset filters and open **AI adoption by industry**.
In the current demo CSV, Professional services has 44 answered S14 responses:
7 regular users / 44 = **15.9%**. Its Not sure cell shows **0%**, and Other is
flagged with **n=2 · small sample**. Hover those cells and compare with **View
counts and denominators**. Apply an industry or AI-adoption filter: the table,
denominators, cells and donuts all recalculate from that same filtered selection.
Switching the visualisation alone changes neither the filters nor the KPIs.

The display uses the supplied palette, Lexend/Inter font pairing, pearl gradients,
rounded cards and navigation. Fonts use the reference's Google Fonts import with
local fallbacks when unavailable. Native Streamlit controls replace the static
preview controls. Five requested KPIs replace its four illustrative cards; the
six requested survey analyses replace its opportunity/trend/AI-insight examples.
No illustrative numbers or invented insights from the preview are copied.
The dense heatmap scrolls inside its card on narrow screens, with a data-table
alternative. The native menu controls both themes; there is no extra theme library.

## Dashboard verification and Step 5

Operational pain points and Business size share a rounded-bar component with
100% tracks, right-aligned percentages and theme-specific highlights for all
joint maximum values. Pain points retain descending frequency order; business
sizes retain questionnaire order. The descriptive Sample insight is calculated
from the filtered aggregate table, including ties and missing-answer handling;
it does not call an AI service or infer broader market conclusions. Labels use
the primary foreground colour for readable small text in both themes.

Outcomes and concerns highlight joint leaders with the shared survey iris token
(Electric Iris in dark mode, the existing Celestial Pearl chart accent in light
mode). Concerns retain a 0–100% scale. The outcome axis starts at zero and follows
the filtered maximum with 25% headroom, rounded up to five percentage points and
capped at 100%. For example, a 20% maximum produces a 25% axis; the displayed
survey percentages are never normalised to the maximum. Outcomes use shortened, wrapped column labels
with full questionnaire labels in hover details; the chart scrolls horizontally
on small screens. Concerns retain ranked horizontal bars, wrapped labels above
their tracks and right-aligned percentages. Hover details and data tables retain
counts, denominators and unrounded calculations, including zero-count categories.

Executed on 10 October 2026: **153 unittest tests passed** (104 existing tests,
26 metric/loader/chart/export/upload tests, 6 AI-adoption tests, 7 survey-bar tests and 10 Streamlit
AppTest tests). The AI tests independently count raw CSV records and compare
every heatmap cell before filtering and across four filtered selections; they
also check sorting, zero versus N/A, separate Not sure answers, the small-sample
boundary, hover payloads and donut values. Tests cover
hand-calculated percentages, combined filters, duplicates in multi-select lists,
missing/unsure answers, zero matches, all-missing responses, header-only files,
schema errors, malformed JSON, duplicate response IDs, manifest mismatches and
navigation. Export tests check round-trip validation, quoted text,
Unicode, missing answers, JSON lists, filtered IDs, exact headers and contact-column
exclusion. AppTest actually runs the Streamlit script and reruns
it after widget changes; it does not merely check the helper functions.

Run the full suite:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

For optional real-browser checks, keep the dashboard server running in another
terminal, then run:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m scripts.smoke_test_market_dashboard
```

The script uses installed Microsoft Edge headlessly and checks both palettes at
1440, 1024, 768 and 390 pixels, chart presence/colours, page overflow, combined
filters, reset, keyboard focus and reduced-motion mode. Screenshots are saved to
ignored `data/dashboard_checks/`. This is a browser smoke check, not a complete
accessibility certification or cross-browser compatibility audit.

The browser smoke check was executed successfully in both themes at all four
widths, including combined filtering, reset, visible keyboard focus and reduced
motion. It also checks corner-menu order, actual CSV downloads, rejection of an
invalid upload, applying a valid upload, exporting that upload, and restoring the
demo. The running page produced no JavaScript page errors. The local Streamlit
server returned HTTP 200 and rendered six charts from the existing survey CSV.
AI-specific browser checks also passed: heatmap default and row sorting, readable
minimum plot width on mobile, switching to donuts and back, mobile donut stacking,
and real mouse hovers for both answered cells and zero-denominator N/A cells.

Step 5 is now implemented: select **Opportunity Intelligence** in the same app.
Its scores are provisional and explicitly gated by evidence; the decision brief
and permission-aware shortlist reflect the current filters. Trello, CRM,
external AI services and production deployment remain outside this milestone.
This is a local synthetic demonstration, not a production access-control system.

## How the pieces fit together

Think of each CSV as a table. A row is one record, and a named column is one fact.
The survey describes a business's challenges. Optional discovery records describe
specific workflows in more detail. Contact details and permissions live in their
own restricted table. Survey-only data works without either optional table.

The questionnaires tell people what to answer. The dictionary tells a developer
what each answer means and how to store it. Validation checks that incoming data
honours those rules. It reports errors and warnings without inventing answers.

| Identifier | What it identifies | Relationship |
|---|---|---|
| `response_id` | One survey submission | Unique survey key; contacts link to this submission |
| `prospect_id` | One underlying business | Joins survey and discovery; repeated submissions are allowed |
| `assessment_id` | One discovery assessment | Unique even for a reassessment of the same workflow |
| `workflow_id` | One workflow within a business | `(prospect_id, workflow_id)` identifies the workflow; reassessments reuse it |

A prospect can have zero, one or many assessments. A contact row must match the
survey's response ID **and** its prospect ID. There is one contacts row per response
in this implementation to avoid conflicting consent records. IDs such as R0001
are examples, not mandatory formatting. The validator checks uniqueness within
the supplied files; it cannot check every submission ever collected elsewhere.

## Created files

```text
templates/
  business_opportunity_survey.md           19 questions, exact wording and labels
  business_opportunity_discovery.md        24 consultant-led questions
  survey_responses_template.csv           30 columns, zero response rows
  discovery_assessments_template.csv      54 columns, zero assessment rows
  contacts_and_consent_template.csv       10 columns, zero contact rows
  data_dictionary.md                      every field, code, unit and sensitivity
  privacy_notice_template.md              configurable, unverified example
  example_organisation_config.yaml        agreed labels, currency and thresholds
src/
  __init__.py
  schema.py                               column names, enums and type groups
  data_validation.py                      parsing, validation and small contract helpers
scripts/
  template_pack_example.py                one in-memory fictional linked example
  generate_synthetic_data.py              seeded survey, discovery and contact generation
  synthetic_profiles.py                  industry, software and workflow context
  analyse_synthetic_data.py               saved-file profile and five pandas examples
data/synthetic/                           generated local files (ignored by Git)
  survey_responses.csv                    150 fictional responses
  discovery_assessments.csv               35 assessments across 27 prospects
  contacts_and_consent.csv                150 restricted fictional contact/consent rows
  generation_manifest.json                configuration, runtime and SHA-256 fingerprints
docs/
  synthetic_data_report.md                file-derived results, code and explanations
tests/
  test_data_validation.py                 validation and relationship tests
  test_template_contract.py               exact wording/header regression checks
  test_synthetic_data.py                  generation, IDs, reproducibility and consistency
  test_synthetic_analysis.py              pandas denominators, consent and report boundaries
  test_synthetic_realism.py               cross-field realism and evidence consistency
requirements-analytics.txt                pinned pandas dependency for analysis/reporting
.gitignore                               excludes local data and Python caches
README.md
```

The profiling report describes generated data. Step 5 adds a separate provisional
opportunity scoring module and deterministic decision-brief exporter; Trello and
YAML loading remain future work. The original prevalence and eligibility helpers
exercise the contract. Approved questions, columns, categories and validation
rules remain unchanged.

## Run it

From the project folder in PowerShell, install the analysis dependency into a
local virtual environment if setting up a new checkout:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-analytics.txt
```

Generate the default data, build the report, and run the full test suite:

```powershell
python -m scripts.generate_synthetic_data
.\.venv\Scripts\python.exe -m scripts.analyse_synthetic_data
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

The existing Template Pack commands continue to work without pandas:

```powershell
python -m src.data_validation templates/survey_responses_template.csv --discovery templates/discovery_assessments_template.csv --contacts templates/contacts_and_consent_template.csv
python -m scripts.template_pack_example
```

Validate the saved synthetic CSVs directly:

```powershell
python -m src.data_validation data/synthetic/survey_responses.csv --discovery data/synthetic/discovery_assessments.csv --contacts data/synthetic/contacts_and_consent.csv
```

Counts and seed are configurable. One contact record is generated per survey
submission. Use a different output folder for experiments to preserve the default
sample/report pair:

```powershell
python -m scripts.generate_synthetic_data --seed 42 --survey-count 60 --discovery-count 12 --currency NZD --output-dir data/synthetic_experiment
.\.venv\Scripts\python.exe -m scripts.analyse_synthetic_data --data-dir data/synthetic_experiment --report docs/synthetic_experiment_report.md
```

The generator writes/replaces the three known CSVs and manifest in its output
folder. The report command reads those files and refuses mismatched fingerprints;
regenerate the report after regenerating data. It does not silently generate a
different dataset for the report. No files are published or sent externally.

To validate your own local survey CSV (discovery/contacts are optional):

```powershell
python -m src.data_validation path/to/survey.csv
python -m src.data_validation path/to/survey.csv --discovery path/to/discovery.csv --contacts path/to/contacts.csv
```

The command prints JSON with `valid`, row counts, `errors` and `warnings`. Its exit
code is 0 for no errors, 1 for validation errors. Each issue includes severity,
dataset, row ID, column, issue and suggested fix. File/header problems use a file
or header marker instead of a record ID. Header-only templates are valid empty
structures; passing them does not mean any response data has been collected.

## One linked example

**SYNTHETIC DATA — NOT REAL MARKET FINDINGS**

The example script contains these raw row dictionaries; all omitted optional
fields become missing values. This is one educational fixture, not the later
150-response synthetic dataset.

```python
survey_row = {
    "response_id": "R0001",
    "prospect_id": "P0001",
    "dataset_version": "1.0",
    "industry": "professional_services",
    "pain_points": '["manual_data_entry", "reporting_analysis"]',
    "primary_pain_point": "manual_data_entry",
    "weekly_hours_band": "6_10",
    "impact_rating": "4",
    "followup_interest": "yes",
}

discovery_row = {
    "assessment_id": "D0001",
    "prospect_id": "P0001",
    "workflow_id": "W0001",
    "dataset_version": "1.0",
    "workflow_name": "Fictional invoice entry",
    "activity_volume": "40",
    "volume_period": "week",
    "minutes_per_instance": "10",
}
```

Both rows carry `P0001`, so they belong to the same business. A second workflow
could have assessment `D0002` and workflow `W0002`. A later reassessment of `W0001`
would get another assessment ID, such as `D0003`. Another business may also use
`W0001`; the prospect/workflow pair distinguishes it.

```python
from src.data_validation import validate_dataset, survey_with_discovery

result = validate_dataset([survey_row], [discovery_row])
result.require_valid()  # raises ValueError if any error needs resolving
joined = survey_with_discovery(result)
# joined[0]["survey"] is R0001; joined[0]["assessments"] contains D0001.
```

The nested list preserves multiple assessments without multiplying survey rows.
The contacts fixture links through `(R0001, P0001)` and uses an address ending in
`.invalid`. It has follow-up permission `false`, so the example returns an empty
contact-ready ID list despite the survey's `yes` interest. The example output
does not print contact details. Eligibility is only a data rule; sending contact
or publishing private details requires a separate authorised workflow.

## Python concepts used here

- A **dictionary** maps column names to values: `row["prospect_id"]` retrieves the
  business ID. A **list of dictionaries** represents the rows of a table.
- CSV cells initially contain strings. `csv` understands commas, quotes and
  embedded newlines; `json.loads` turns a multi-select cell into a Python list.
  For example, the JSON above becomes two strings in `pain_points`.
- `None` means missing. It is different from numeric `0`, boolean `False`, and
  explicit codes such as `unknown`. An unassessed complexity value stays `None`;
  there is no evidence to assign a score. `unsure` workload stays a category.
- Integers represent ratings/headcount; `Decimal` represents numeric measurements
  without introducing binary floating-point rounding during parsing. Parsed date
  values are checked but retained as ISO strings.
- A **set** counts distinct selections. One respondent selecting two pain points
  contributes once to each category, never twice to the same category. After
  filtering, the denominator includes only respondents with an answered S06.
  In this one-row example both selected categories have 1/1 = 100%; summed
  multi-select percentages can exceed 100%.
- A **dataclass** gives issues/results named fields. Small functions keep parsing,
  cross-table checks and examples separate. `unittest` checks both valid inputs
  and deliberately invalid cases using fictional data in memory/temporary files.

The row API accepts dictionaries of raw CSV strings or `None`. It returns parsed
copies without changing the input. Check `result.valid` before using parsed data;
failed cells are not safe to analyse. All included analytical helpers refuse a
result with errors. Warnings preserve answers for review.

## Contract choices and current limitations

The [data dictionary](templates/data_dictionary.md) documents every implemented
interpretation, including accepted ISO date forms, integer headcount, numeric
baseline/target fields, empty arrays, version handling and advisory evidence checks.
Actual work requires positive person-minutes, but there is no work-occurs flag in
the schema; zero minutes therefore warns for review. Monetary values require
explicit currency. New forms default questionnaire version to 1.0; missing
imported values remain missing.

The YAML example preserves high-impact threshold 4, small-group warning size 5,
simple complexity maximum 2 and medium maximum 3. The pandas examples explicitly
use the first two baseline values; they do not yet load YAML. Complexity counts
retain the original ratings, without creating a composite score. No workload
midpoints, day/month conversions, ROI or conversion estimates are used.

Generated discovery records with complete measurements use a known weekly period
and total person-minutes per occurrence. The report calculates volume × minutes ÷
60 without multiplying by staff count. It displays reported hours alongside the
modelled value. Differences above 25% get a **demonstration review flag**. That
threshold is an explicitly documented report assumption, not a change to approved
scoring or validation. Production conversion/review policies remain later work.

The privacy notice has placeholders for actual collector, hosting, processors,
overseas processing, retention, security and request-handling details. The collector
must verify and fill these before real collection. Validation does not establish
legal compliance, accuracy of evidence, permission to publish, or anonymity.

All three templates remain header-only. Generated contacts are visibly fictional
and use the reserved `.invalid` domain. Their local CSV remains separate and
ignored by Git. The report includes aggregate consent figures and pseudonymous
eligible IDs, never contact names, business names or email addresses. There is no
public demo in this stage; public-export safeguards must be tested when built.
Real uploaded data belongs outside version-controlled/public artifacts. `.gitignore`
is a convenience, not access control.

## Validation coverage and next step

Step 3 verification on 10 October 2026 with Python 3.13.14 and pandas 3.0.6:
**104 tests passed**, including all 55 original Template Pack tests. The default generated files
validate with **0 errors and 17 intentional warnings**: 5 missing workload bands,
4 missing impact ratings, 4 missing pain-point lists and 4 missing primary pain
points. The warnings are reported, not suppressed. All templates and the original
one-row example still validate with 0 errors and 0 warnings. No blocking issues
remain; privacy configuration and future public-export controls are still pending
for their respective stages.

Tests cover all stage-relevant requirements from specification section 11:
survey-only input, matched/orphan discovery, duplicate IDs, multiple workflows,
invalid types/enums/JSON, selection limits and warnings, missing-value preservation,
filtered distinct-response denominators, permission gating, absence of invented
discovery claims, neutral branding and fictional/private-data boundaries. Snapshot
tests also protect all 43 question texts and the exact 94 CSV header positions.
Step 3 tests also check exact counts, byte-for-byte reproducibility, changed seeds,
custom counts, reserved fictional contacts, numerical consistency, saved-file
profiling, pandas denominators and exclusion of private details from the report.
Public-demo behaviour remains deferred until that application exists.

## Understanding the generator

Think of a seed as a repeatable shuffle of a deck. `random.Random(20261010)` starts
the same sequence of draws each time, so the same code, settings and runtime
produce the same records. Separate random streams for surveys, contacts and
discovery mean changing the discovery count does not reshuffle the survey answers.
Generator version 1.1 introduced a separate stream for `ai_tools_and_uses`: answers
name tools and their tasks, distinguishing regular use, occasional tasks and past
experimentation. For example, a respondent might describe using ChatGPT to draft
invoice reminders or trying Claude to summarise procedures. These are fictional
usage accounts, not verified integrations. That earlier correction preserved every
other generated field and the existing pattern of missing optional answers. The S14
follow-up wording now explicitly asks: "Which AI tools have you tried or used,
and what do you use them for?" The dataset schema remains version 1.0.

Generator version **1.2** extends the review to all other fields. Its separate
`synthetic_profiles.py` catalogue gives businesses industry-specific vocabulary,
software identities, roles and workflow context. Underused software names come
from the business's software list; discovery uses the same list. Where "several"
subscriptions were reported with too few software categories, supporting categories
are added. This revision intentionally changes related data values while keeping
the approved column names, categories, IDs, record counts and missing-answer rules.

The survey's concerns, comments and Other explanations now describe concrete
circumstances. Fictional business names reflect their industries. Discovery steps,
bottlenecks, observed impacts, exception handling, safety requirements, reuse and
customisation notes describe the workflow instead of repeating one generic paragraph.
Budget, authority, timeline, feasibility and next-action fields are checked for
agreement. A declined pilot does not lead to a pilot proposal, and an uninvestigated
integration does not become confirmed feasibility.

Workload assumptions now distinguish frequent short tasks from longer, less frequent
work such as reporting. Success measures include elapsed response hours and rework
percentages as well as staff processing time, with explicit matching units. Labour
costs and budget amounts remain illustrative, optional scenario inputs; they do not
claim market rates or guaranteed returns. The generated report includes a complete
94-column profile and examples for inspecting these relationships.
The manifest records the settings and file fingerprints so the exact sample can
be identified later. It uses no current-time values or external personal data.

Weighted choices are like putting more tickets for some answers into a draw.
For example, manual work makes heavier workload bands more likely, without making
them inevitable. Industry influences likely problems, and size influences the
number of software systems. First-case examples deliberately break simplistic
assumptions: a small firm can be highly digital, an AI user can still have severe
problems, and an interested respondent can refuse contact permission. These are
demonstration assumptions, not statistics learned from real businesses.

The generator fills raw-string dictionaries using the schema's exact columns.
`json.dumps` encodes list answers, and `csv.DictWriter` handles their quoting.
Generation is separate from validation: think of the generator as assembling
practice records and the validator as checking them against a checklist. Records
must pass before writing and are checked again after being read from disk.

Missing values deliberately remain empty. An empty impact rating is like an
unanswered exam question, not a mark of zero. When calculating high-impact share,
we count only people who supplied a rating. In the default sample, 146 answered
S09 and 4 did not; those 4 should not dilute the percentage.

Discovery is a closer inspection of a particular workflow. The 150 surveys are
the broad view; 35 inspections cover 27 of those businesses, with eight receiving
two workflow assessments. Similar broad survey problems can lead to different
processes, integration constraints and judgements. Unassessed feasibility or
complexity stays visibly unknown rather than receiving an invented neutral score.

Read the report's five code-and-result examples for recurring problems, industry
impact rates, AI adoption by size, permission-aware high-impact follow-up, and
complexity versus commercial potential. It also explains `groupby`, `explode`,
distinct counting and joins using spreadsheet analogies.

Market Intelligence uses the validated survey file as described above.
Opportunity Intelligence also loads discovery records and offers human-review
exports with explicit evidence gaps. Its default demo never loads contact details;
optional contact uploads are reduced to eligibility flags. Before production
deployment, review access control, upload retention and consent requirements.
