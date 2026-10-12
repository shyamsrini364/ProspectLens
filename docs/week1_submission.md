# ProspectLens: from business surveys to useful consulting insights

Editable project overview · prepared 12 October 2026

## How to use this draft

This draft separates verified implementation details from your personal experience.
Keep or shorten the factual paragraphs, replace each **[YOUR EXPERIENCE]** prompt
with your own words, and add screenshots where indicated. Do not present the
reflection prompts as experiences you have already had. Video ideas are in
`docs/week1_demo_talking_points.md`; they are prompts, not a script to memorise.

Repository: https://github.com/shyamsrini364/ProspectLens

Local demonstration: http://localhost:8501 — this address works on the computer
running the app; it is not a public deployment. No public app deployment has been
verified for this submission. Repository publication status is recorded separately
in `docs/submission_evidence.md`.

## 1. What the project does

ProspectLens is a business-survey and opportunity-analysis application for
consultants and business advisors. It turns structured survey answers and optional
discovery assessments into two connected dashboards. Market Intelligence shows
patterns across respondents. Opportunity Intelligence helps examine individual
businesses and the evidence behind potential consulting opportunities.

The goal is to make a spreadsheet easier to explore and question. A consultant can
see which problems recur, compare different groups of businesses and inspect why a
particular business receives a provisional score. The application supports human
judgement; it does not automatically sell, contact prospects or make decisions.

**[YOUR EXPERIENCE]** What made this problem interesting to you? Add a real example
of a spreadsheet, consulting conversation or repeated administrative task that
inspired the idea. Do not invent a customer or claim the app has real users.

## 2. The problem and intended users

A spreadsheet can store many answers but does not automatically explain them.
For example, a consultant might want to know whether manual data entry is common
among several industries, or whether a business with a serious problem has enough
commercial evidence to justify further discovery. Reviewing each row manually
makes these comparisons slow and inconsistent.

ProspectLens gives consultants and business advisors a repeatable way to explore
those questions. It is organisation-neutral: users can load compatible CSVs
without replacing the app's branding or rewriting its calculations. Findings still
depend on who answered the survey; they are not automatically representative of
the wider market.

## 3. Data: three linked spreadsheets with different jobs

The project began with a data contract: an agreed set of questions, column names,
allowed answers and validation rules. Think of it as a standard form that every
dataset must follow. This keeps the charts from guessing what an unfamiliar
column or answer means.

- The Business Opportunity Survey contains 19 questions and a 30-column CSV
  schema, including identifiers and metadata. Its demo has 150 responses from
  150 unique businesses.
- The Discovery Assessment contains 24 questions and a 54-column CSV schema.
  Its demo has 35 assessments across 27 businesses. Discovery adds evidence about
  individual workflows, commercial qualification and technical delivery.
- Contacts and consent use a separate 10-column CSV schema. The generator creates
  150 fictional contact records, but the default dashboards do not load that file.
  An optional upload checks eligibility; analytical exports omit contact fields.

All demonstration records are synthetic. They were generated in Python with the
default seed 20261010. A seed is like a repeatable recipe number: using the same
generator, configuration and environment produces the same sample. A manifest
records file fingerprints, so the demo loader can detect files that no longer
match the generated dataset.

The identifiers work like a filing system. `prospect_id` identifies the business's
folder; `response_id` identifies a survey submission; `workflow_id` identifies a
workflow within that business; and `assessment_id` identifies one assessment of
that workflow. Several documents can belong to one folder without creating
several businesses in the ranking.

Missing answers remain missing. For example, if only 146 businesses answer a
question, its percentage uses 146 as the denominator and reports the four missing
answers. A respondent choosing three problems counts once in each category, but
does not become three separate businesses.

**[SCREENSHOT]** Show the blank survey CSV header or data dictionary, not a contact
file. Caption idea: “The contract defines how every dataset is interpreted.”

## 4. What users can do

### Market Intelligence: understand the sample

The first lens summarises response counts, industries, high-impact problems,
current AI use and follow-up interest. Shared filters let users focus on an
industry, business size, primary problem or AI adoption level. The charts update
together, so the KPIs and visualisations describe the same selected respondents.

Charts cover operational pain points, pain points across industries, AI adoption
by industry, business sizes, desired outcomes and AI/automation concerns. Users
can inspect counts and denominators, switch the AI-adoption heatmap to donut
charts and read filter explanations. Small groups and missing answers are flagged.

### Opportunity Intelligence: inspect individual businesses

The second lens creates one analytical row per business. It provides a matrix,
sortable ranking, recurring-problem analysis, discovery activity over time and a
commercial/technical evidence table. Additional filters distinguish assessment
stage and score band. Clicking a matrix point or opening Business details shows
survey evidence, linked workflow assessments, score breakdowns and evidence gaps.

The matrix places Commercial Potential horizontally and Business Opportunity
Value vertically. This helps distinguish a significant problem from evidence of
a possible engagement. The shaded quadrants and score bands are provisional
investigation guides, not probabilities of success.

### One dataset, two views, three decision outputs

Manage data opens the same upload dialog from either lens or the three-dot menu.
A survey upload powers both lenses. Optional discovery enriches Opportunity
Intelligence; it is never silently borrowed from the synthetic demo. Restoring the
demo resets both lenses. Uploads are held for the current session rather than
overwriting the saved files.

Market exports use `market_intelligence_export.csv`. Opportunity exports include
`opportunity_intelligence_export.csv`, a Markdown Consultant Decision Brief and
`opportunity_intelligence_followup_shortlist.csv`. They reflect the active filters.
The brief uses fixed reporting templates and calculated results, not an AI model.
Without contact evidence, the shortlist is explicitly analytical, not a list of
people authorised for contact. An opportunity ranking CSV is an output, not a
replacement for the original survey input schema.

**[SCREENSHOTS]** Add one Market view before/after a filter, and one Opportunity
matrix with a business evidence pop-up. Describe what changed, not just how it looks.

## 5. The technical design in everyday language

Python is the language connecting the parts. Streamlit builds the interactive
page and reruns the display when controls change. pandas works with tables in
memory, like a programmable spreadsheet. Plotly turns prepared tables into
interactive charts with hover details and selection events.

The verified environment uses Python 3.13.14, pandas 3.0.6, Streamlit 1.65.0 and
Plotly 7.1.0. Optional browser checks use Playwright 1.63.0 with Microsoft Edge.
These are the project versions, not a claim that they are the latest releases.

Data moves through the application in this order:

1. Read the CSVs and validate headers, values, dates and relationships.
2. Turn validated records into pandas tables.
3. Build the business snapshot and calculate explainable scores where evidence permits.
4. Apply the user's filters to select the relevant records.
5. Use those records for charts, tables, KPIs and downloads.

The code keeps these responsibilities separate. For example, changing a chart's
colour does not require changing the scoring formula. Pure scoring functions can
be tested without starting the dashboard. Session state is the app's short-term
memory: it retains the active dataset and controls during a user's session.

The repository contains separate modules for validation, loading, metrics,
scoring, charts, UI and reports. There is no database, CRM integration or external
LLM call required for the current application.

## 6. How scoring works, and what it does not establish

The provisional Business Opportunity Value score combines impact (45%), workload
(35%), category recurrence (10%) and additional reported problems (at most 10%).
The additional-problem cap prevents a long list of selections from dominating
the score. Recurrence uses the full loaded business sample, so a score does not
change simply because someone narrows a dashboard filter.

Commercial Potential combines budget (35%), pilot interest (25%), timeline (20%)
and the consultant's commercial assessment (20%). It also requires minimum
evidence such as a named, dated workflow, rationale, known authority and a
qualifying evidence status. Interest in a conversation does not prove purchasing
readiness, so survey-only commercial and overall scores remain unassessed.

Overall score = 60% Business Opportunity Value + 40% Commercial Potential.
For example, value 80 and commercial 60 produce an overall score of 72. This is
a configured priority score, not a 72% chance of winning a client.

The current demo has 11 businesses eligible for an overall score. Other businesses
stay visible in the ranking with missing evidence identified. For multiple
workflows, the app selects the latest assessment for each workflow, then uses the
highest recorded business impact to choose a primary workflow; ties use date and
ID. It does not add every workflow score together.

Full rules are available in the How scores work pop-up and
`docs/opportunity_methodology.md`. Weights live in one configuration file so they
can be reviewed and revised explicitly.

## 7. How AI-assisted development was used

The recorded conversation shows a staged workflow with Codex: establish the data
contract, generate synthetic data, build Market Intelligence, build Opportunity
Intelligence, refine the visuals and audit the outputs. The user supplied goals,
constraints and screenshot feedback; Codex implemented changes and ran checks.
The app itself is rules-based analytics, not an autonomous AI agent.

Exact excerpts available in the conversation include:

- “Do not silently change the survey questions, scoring assumptions or CSV specification.”
- “Do not combine \"Not sure\" with \"Not using AI\".”
- “Do not apply curved smoothing or interpolate additional data points.”
- “are you able to test the Consultant Decision Brief, follow up short list and ranking csv is all accurate?”

These excerpts show how constraints made the work reviewable: preserve the
contract, keep categories meaningful, change presentation without inventing
observations, and verify the exported results. Original message timestamps and
the exact Codex model/version have not been independently recovered; add your
own screenshots if your assignment requires them. The new repository starts with
an initial snapshot, not a fabricated history of earlier development commits.

**[YOUR EXPERIENCE]** Which request took the most refinement? What did you notice
in a screenshot that the original prompt missed? Explain one choice you made
yourself, and one area where you still relied heavily on the assistant.

## 8. Iterations worth discussing

AI adoption moved from stacked bars to a heatmap, with optional donuts, to make
industry comparisons easier to read. The five original answer categories were
kept distinct. Chart leaders now share theme-specific accents rather than using
inconsistent highlight colours.

Opportunity trends changed from steps to straight segments with visible markers.
The totals stayed the same; the points now sit at reporting-period ends. The
chart communicates research activity, not increasing market demand.

Data management was unified after a review showed that lens-specific uploads
could leave the two pages using different datasets. Manage data now supplies one
survey to both lenses. Export names also identify the relevant dashboard.

A browser check caught a decision-brief download that could be cancelled when a
page rerun regenerated the report timestamp. Download buttons now use
`on_click='ignore'`, letting the prepared file download without triggering that
rerun. This illustrates why a passing formula test does not replace trying the
real interface.

**[YOUR EXPERIENCE]** Choose two of these examples. Describe what you expected,
what you observed, what you asked to change and what you learned. Add genuine
before/after or prompt screenshots where available.

## 9. Verification and current limitations

On 12 October 2026, the full command `python -m unittest discover -s tests -q`
passed 202 tests in the project virtual environment. Tests cover schemas, exact
questionnaire wording, validation, multi-select counts, scores, business
deduplication, filters, trends, permissions, exports and Streamlit behaviour.
Earlier executed browser checks covered both themes at 1440, 1024, 768 and 390px,
including uploads, downloads, pop-ups and switching between lenses. This is not
an exhaustive security, accessibility or cross-browser certification.

The export audit independently recalculated results from the raw CSVs rather
than only calling the same scoring helpers again. It verified 150 ranking rows,
122 analytical shortlist entries (67 Yes and 55 Maybe after exclusions), and the
brief's numerical summaries. The audit also found two remaining wording issues:
a deferred business appears under investigation priorities, and survey-only
examples are ID-ordered rather than proven top opportunities. Numerical accuracy
does not make those descriptions ideal; they should be clarified before treating
the brief as a polished client deliverable.

Other limits are deliberate. Data is synthetic, weights are provisional, and no
real-world predictive accuracy or ROI has been established. The schema has no
explicit assessment-completed flag, so the app documents a completion proxy.
It also has no direct mapping from a discovery workflow to a survey problem code;
the app does not invent that relationship. Production access controls, retention
policies and hosting require further work before using sensitive real data.

## 10. My learning and next steps

**[YOUR EXPERIENCE — replace these prompts with two or three short paragraphs]**
What can you now explain about Python, pandas or Streamlit that you could not
explain before? Which part of the code would you be comfortable changing yourself?
What evidence helped you decide whether an AI-generated change was correct?
What would you do differently in your first prompt if you started again?

Practical next steps are to clarify the decision brief's wording, review the
provisional scoring with intended users, test a permitted real-data pilot, and
prepare appropriate access and data-handling safeguards before public deployment.
Trello, autonomous agents and CRM integration remain future ideas.

**[YOUR CONCLUSION]** In your own words, explain the project's most useful result,
one limitation you understand better now, and the next improvement you would make.

## Evidence to add before submitting

Add a genuine prompt screenshot, a before/after iteration if available, one screen
from each lens, and the latest test output. Check the GitHub link as a reviewer,
add your video link, and replace all personal-reflection prompts. Keep the document
editable while drafting; choose its sharing settings deliberately when ready.
