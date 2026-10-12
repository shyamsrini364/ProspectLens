# Submission evidence and readiness

Checked 12 October 2026. This records evidence, not a substitute for the owner's
personal account of the project.

## Accessible evidence

- Current source, schemas, templates, configuration, generated-data manifest and tests.
- Actual user messages in this conversation; quotations in the overview are excerpts
  from those messages. Individual historical timestamps and the exact Codex model
  version were not recovered.
- Existing local browser screenshots and executed test results. No prior Git
  development history existed: Git was initialised for this submission snapshot.
- A newly created public repository supplied by the owner:
  https://github.com/shyamsrini364/ProspectLens

## Verified implementation

| Claim | Evidence |
| --- | --- |
| 19 survey and 24 discovery questions; exact schemas | `templates/`, `src/schema.py`, `tests/test_template_contract.py` |
| 150 survey rows, 35 discovery rows, fixed seed 20261010 | `scripts/generate_synthetic_data.py`, locally generated manifest |
| Market charts and shared filters | `src/market_ui.py`, `src/market_metrics.py`, `tests/test_market_app.py` |
| One business per ranking/matrix record | `src/opportunity_metrics.py`, `tests/test_opportunity.py` |
| Explicit score rules and missing-evidence gates | `src/opportunity_config.py`, `src/opportunity_scoring.py`, methodology document |
| Shared uploads and reset across lenses | `src/shared_data.py`, `tests/test_opportunity_app.py` |
| Three decision exports and independent reconciliation | `src/opportunity_reports.py`, `tests/test_export_audit.py` |
| Straight trend segments, period-end markers, unchanged totals | `src/opportunity_charts.py`, `tests/test_opportunity_trend_chart.py` |

## Executed validation

Command: `.\.venv\Scripts\python.exe -m unittest discover -s tests -q`

Result on 12 October 2026: **202 tests passed**, 16.076 seconds in the submission
preparation run, before the project folder was renamed. The earlier export audit
also compared the user's downloaded brief and shortlist with source-backed
regeneration and checked fresh browser downloads of all three outputs.

Browser checks executed during development covered both dashboards at 1440, 1024,
768 and 390px in light and dark themes, including actual filtering, uploads,
downloads, dialogs and menu interactions. These checks do not establish full
accessibility, security or compatibility with every browser.

The export audit found correct numerical outputs and two wording limitations:
the brief includes a deferred record among investigation-priority examples;
survey-only examples are ID-ordered because their overall scores are unassessed.
These issues are disclosed, not silently presented as resolved.

## Repository preparation

- Source, templates, configuration, documentation and tests are included.
- Runtime data, contact CSVs, the virtual environment and local browser captures
  are excluded. The deterministic generator recreates the demo after cloning.
- No licence is selected: do not call this a licensed open-source release.
- README includes first-checkout commands; a public deployment is not claimed.
- Initial Git history is a current snapshot, not reconstructed past milestones.
- A clean temporary copy containing only the 65 staged source files regenerated
  the synthetic datasets with zero errors and 17 warnings, then passed all
  202 tests in 21.472 seconds. This used the installed project interpreter and
  dependencies; it was not a fresh dependency installation.
- The staged-file preflight found no known credential patterns and confirmed
  runtime data and the virtual environment were excluded. This is a targeted
  check, not a guarantee against every possible sensitive string.

## Owner's remaining evidence

- Add your own experiences and conclusions to the Google Doc.
- Capture genuine prompt screenshots; do not create recreated chat screenshots.
- Choose 3–5 screenshots: template/schema, Market filter result, Opportunity
  matrix/detail, one real iteration and test/repository evidence.
- Record and upload the video yourself, then add its URL.
- Check the document and repository using the intended reviewer access.
- Decide on a licence if you intend to grant reuse rights.
- Submit the final links in the course form yourself.

Neither course submission nor document sharing changes are performed as part of
drafting these materials.
