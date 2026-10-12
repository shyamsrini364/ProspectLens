# Opportunity Intelligence: a practical guide

Opportunity Intelligence compares individual businesses and lets you inspect the
evidence behind each score. Market Intelligence describes the survey sample as a
whole; this second lens helps decide what to investigate next. Scores are
provisional priorities, not sales predictions or verified financial returns.

## Open and explore

From the project folder in PowerShell:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py --server.port 8501
```

Open <http://localhost:8501/> and select **Opportunity Intelligence**. Both lenses
share navigation, typography, cards and the Celestial Pearl / Pearl Nocturne theme
tokens. Change appearance in the existing top-right menu.

1. Read the introduction, then select **How scores work**. This opens a pop-up
   containing the formulas, evidence gates, missing-data rules and active settings.
2. Use the six filters and ID search to select businesses. Empty filters include
   all answers. Every KPI, chart, table and download follows this selection.
3. Hover over a matrix bubble for a summary; click it for the business evidence
   pop-up. You can also select any business beneath the ranking and press
   **Business details**, including businesses that cannot yet be plotted.
4. Explore recurring problems, actual survey/discovery dates and the supporting
   technical evidence table. Download the filtered ranking, decision brief or
   follow-up shortlist at the bottom.

**Manage data** appears on both dashboards and in the three-dot menu. It opens
one shared dialog accepting the survey CSV plus optional discovery and
contacts/consent CSVs. Validation runs before replacing the shared session bundle;
both dashboards then use that same survey. Survey-only uploads do not inherit
synthetic discovery records. Restoring the demo resets both dashboards and their
filters. Existing CSV schemas and saved demo files are unchanged.

The current filtered survey downloads as `market_intelligence_export.csv`; the
filtered business ranking downloads as `opportunity_intelligence_export.csv`.
The latter is an analytical output, not a survey upload template. The follow-up
shortlist is `opportunity_intelligence_followup_shortlist.csv`, and the brief is
`opportunity_intelligence_decision_brief.md`. `src/shared_data.py` owns the common
upload dialog and session state.

## How records connect

Think of `prospect_id` as the label on a business's folder. Several survey forms
and several workflow assessments can go in that folder:

```text
prospect_id P0001
  response_id R0001: one survey submission
  response_id R0002: a later survey submission
  workflow_id W01
    assessment_id D0001: first assessment
    assessment_id D0002: reassessment
  workflow_id W02
    assessment_id D0003: another workflow
```

This illustrative folder still creates **one business row and at most one bubble**.
The latest survey supplies its current answers; older submissions remain available
in the evidence pop-up and activity trend. We take the latest assessment per
workflow, then select the workflow with the highest recorded business impact;
dates and IDs resolve ties. We preserve every assessment rather than adding
workflow scores together. Full tie-breaking rules are in the methodology.

The schema has no completion checkbox. The discovery-assessed KPI therefore uses
a documented operational definition: a workflow name, assessment date, rationale
and a recorded evidence status other than unknown. This does not mean all the
commercial evidence needed for scoring is present.

## Scores and rankings

All score settings live in `src/opportunity_config.py` and are provisional.

| Score | Default calculation |
| --- | --- |
| Business Opportunity Value | 45% impact + 35% workload + 10% recurrence + 10% additional problems |
| Commercial Potential | 35% budget + 25% pilot interest + 20% timeline + 20% consultant commercial assessment |
| Overall Prospect Opportunity | 60% Business Opportunity Value + 40% Commercial Potential |

Each component is mapped to a 0–100 scale before weighting. Impact ratings 1–5
map to 0, 25, 50, 75 and 100. The five known workload bands use the same ordinal
points; these are not estimated exact hours. Recurrence is the percentage of
businesses in the full loaded sample reporting the business's primary problem.
Additional problems contribute at most 10 points, reaching that cap with two
additional distinct selections. They are reported problems, not validated projects.

Commercial qualification requires the selected assessment's mapped inputs,
known decision authority, dated and named workflow, rationale and qualifying
consultant-assessed or validated evidence status. Authority is an evidence gate,
not a made-up numerical score. Survey interest alone does not establish budget
or purchasing readiness, so survey-only commercial and overall scores remain
unassessed. Missing required evidence never becomes zero.

For a simple arithmetic example, Value 80 and Commercial 60 give
`0.60 × 80 + 0.40 × 60 = 72`, which is **Promising**. Value measures the significance
of the problem; Commercial measures engagement evidence. Keeping them separate
lets a severe problem coexist with weak buying evidence instead of hiding that
difference inside one number.

The ranking retains all selected businesses, groups them by assessment stage and
sorts within each stage by your chosen metric. Unassessed values remain blank;
they receive no composite rank. The matrix only includes businesses with both
scores: commercial on the horizontal axis, value on the vertical axis, colour for
the overall band. The 50-point reference lines are configurable investigation
guides, not statistically established boundaries. Changing filters does not
recalculate recurrence weights, so a business's score does not move simply
because you changed the segment being viewed.

## KPIs and supporting analysis

- **Businesses analysed:** distinct prospect IDs after filters.
- **High-impact businesses:** latest survey impact 4 or 5; answered coverage is shown.
- **Discovery-assessed businesses:** businesses meeting the completion proxy above.
- **Interested prospects:** latest survey follow-up interest of Yes, not Maybe.
- **Average prospect score:** mean of eligible Discovery Enriched scores only,
  with eligible/total stage coverage shown.

Recurring problems count each business once per selected category. A business
choosing three categories contributes to each category but remains one business
in the denominator. The table also provides primary-problem impact, workload
distribution and explicitly labelled reusable-solution hypotheses. The schema
does not map discovery workflows to survey problem codes; assessment counts at
reporting businesses are not presented as category-matched workflow evidence.

The trend uses actual `submitted_at` and `assessment_date` values. It counts unique
response and assessment IDs, fills empty periods with zero activity, and supports
weekly/monthly and cumulative/new-per-period views. A cumulative sum is like a
running total in a spreadsheet. It shows research activity, not increasing market
demand; missing dates are reported and excluded.

## Exports and permissions

The Markdown decision brief is assembled from calculated results with fixed prose
templates: dataset, timestamp, filters, coverage, recurring problems, investigation
priorities, evidence gaps and next questions. No external AI service is involved.

Without contact data, the shortlist is explicitly **analytical only**. When an
optional contact file is supplied, the shortlist requires documented permission,
eligible interest, a valid email and privacy-notice provenance. The original
validator is reused; the stricter shortlist provenance checks are documented.
Deferred/no-suitable-opportunity records are excluded. Permission attaches to the
representative survey response, not automatically to every response from a business.
Exports never include personal contact fields. Default demonstration loading does
not open the restricted contacts file.

## Code map and Python concepts

| File | Responsibility |
| --- | --- |
| `src/opportunity_data.py` | Load CSVs, reuse validation, project permission flags |
| `src/opportunity_config.py` | Shared model weights, maps, bands and hypotheses |
| `src/opportunity_scoring.py` | Pure scoring functions and workflow selection |
| `src/opportunity_metrics.py` | One row per business, filters, KPIs and trends |
| `src/opportunity_charts.py` | Plotly matrix and trend figures |
| `src/opportunity_reports.py` | Ranking CSV, decision brief and shortlist |
| `src/opportunity_ui.py` | Streamlit controls, sections and pop-ups |
| `docs/opportunity_methodology.md` | Detailed methodology displayed in the app |
| `tests/test_opportunity.py` | Deterministic scoring/data/export tests |
| `tests/test_opportunity_app.py` | Streamlit interaction and error-state tests |
| `scripts/smoke_test_opportunity_dashboard.py` | Real-browser checks and screenshots |

Shared changes are in `market_ui.py` (navigation), `market_menu.py` (reuse the same
CSV menu for either lens), `assets/market.css` (matching cards and responsive rules),
README and existing navigation/browser checks. Existing schemas and validators
are unchanged. No new application dependencies are required.

A pandas **DataFrame** is an in-memory table, much like an Excel sheet. Sorting and
deduplication build a business snapshot; Boolean masks select rows for filters;
grouping and period sums build chart tables. Dictionaries hold configurable
category-to-point mappings. Pure Python functions calculate scores without
Streamlit, making them easy to test using small examples with known answers.
Plotly turns those tables into interactive figures; Streamlit reruns the page when
controls change and uses session state to retain selections and uploaded bundles.
`st.dialog` opens the methodology and business evidence without leaving the lens.

## Verification and remaining limits

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
# With Streamlit running on port 8501:
.\.venv\Scripts\python.exe -m scripts.smoke_test_opportunity_dashboard
.\.venv\Scripts\python.exe -m scripts.smoke_test_market_dashboard
```

On 12 October 2026, the full unittest suite passed **193 tests**, including 40 new
Opportunity Intelligence tests. Tests cover score arithmetic, caps, missing values,
deduplication, workflow selection, stage separation, scatter inputs, ranks, dates,
filters, multi-select counts, permissions, uploads, exports and Streamlit dialogs.
Browser artifacts are saved under ignored `data/opportunity_checks/` and
`data/dashboard_checks/`.

Both real-browser scripts also passed on 12 October 2026. Opportunity checks
covered light/dark themes at 1440, 1024, 768 and 390 pixels, all six filters, search,
bubble-click and methodology dialogs, filtered CSV/Markdown downloads, the native
corner menu, weekly/monthly controls, empty selections, invalid/valid uploads and
returning to Market Intelligence. Both dialogs were additionally checked at
390px. Market Intelligence's browser regression checks also passed. These checks
use installed Microsoft Edge, not an exhaustive cross-browser accessibility audit.

The current demo has 150 businesses, 35 discovery records across 27 businesses,
and 11 businesses eligible for an overall score. The other businesses stay in the
ranking with their evidence gaps visible. The inputs validate with zero errors
and 17 warnings; warnings are shown in the dashboard, not silently discarded.
Scoring weights need consultant review and calibration against real outcomes.
Completion is a documented proxy, and no automatic workflow/category mapping is
invented. Production authentication, hosting, CRM/Trello and external AI remain
outside this milestone.
