"""Five pandas examples and a profile calculated from saved synthetic CSV files.

Run: python -m scripts.analyse_synthetic_data
No contact names, business names or email addresses are written to the report.
"""

from __future__ import annotations

import argparse
import hashlib
import inspect
import json
from collections import Counter
from pathlib import Path

import pandas as pd

from scripts.generate_synthetic_data import DISCLAIMER, FILENAMES, ROOT
from src.data_validation import valid_email, validate_csv_files
from src.schema import COLUMNS, ENUMS, SURVEY_LABELS

HIGH_IMPACT_THRESHOLD = 4
MINIMUM_GROUP_WARNING = 5


def load_synthetic_files(data_dir):
    """Validate CSV files and check their recorded provenance before profiling."""
    data_dir = Path(data_dir)
    manifest = json.loads((data_dir / "generation_manifest.json").read_text(encoding="utf-8"))
    if manifest.get("disclaimer") != DISCLAIMER:
        raise ValueError("Expected a labelled synthetic generation manifest")
    for filename in FILENAMES.values():
        actual = hashlib.sha256((data_dir / filename).read_bytes()).hexdigest()
        if manifest.get("sha256", {}).get(filename) != actual:
            raise ValueError(f"{filename} differs from the generation manifest; regenerate before profiling")
    result = validate_csv_files(*(data_dir / FILENAMES[k] for k in ("survey", "discovery", "contacts")))
    result.require_valid()
    # Keep canonical codes, blanks and version strings intact before conversion.
    frames = {kind: pd.read_csv(data_dir / name, dtype=str, keep_default_na=False, encoding="utf-8")
              for kind, name in FILENAMES.items()}
    return frames, result, manifest


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


def complexity_vs_commercial(discovery):
    """Question 5: assessment-level counts, with unassessed/unknown kept explicit."""
    rows = discovery[["assessment_id", "implementation_complexity", "commercial_potential"]].copy()
    rows["implementation_complexity"] = rows["implementation_complexity"].replace("", "unassessed")
    rows["commercial_potential"] = rows["commercial_potential"].replace("", "unassessed")
    counts = pd.crosstab(rows["implementation_complexity"], rows["commercial_potential"])
    return counts.reindex(index=["1", "2", "3", "4", "5", "unassessed"],
                          columns=["low", "medium", "high", "unknown", "unassessed"], fill_value=0).reset_index()


def distribution(frame, column, allowed=None):
    values = frame[column].replace("", "missing")
    order = list(allowed if allowed is not None else sorted(values.unique()))
    if "missing" not in order:
        order.append("missing")
    output = values.value_counts().reindex(order, fill_value=0).rename("records").reset_index()
    output.columns = [column, "records"]
    output["percentage_of_all_rows"] = output["records"] * 100 / len(frame) if len(frame) else float("nan")
    return output


def workload_comparison(discovery):
    """Weekly person-minute baseline only; preserve reported hours independently."""
    rows = discovery[["assessment_id", "prospect_id", "volume_period", "activity_volume",
                      "minutes_per_instance", "reported_staff_hours_per_week"]].copy()
    for column in ("activity_volume", "minutes_per_instance", "reported_staff_hours_per_week"):
        rows[column] = pd.to_numeric(rows[column], errors="coerce")
    known = rows["volume_period"].eq("week") & rows["activity_volume"].notna() & rows["minutes_per_instance"].notna()
    rows["modelled_staff_hours_per_week"] = (rows["activity_volume"] * rows["minutes_per_instance"] / 60).where(known)
    baseline = rows["modelled_staff_hours_per_week"].replace(0, float("nan"))
    rows["difference_percentage"] = (rows["reported_staff_hours_per_week"] - baseline).abs() * 100 / baseline
    # Demonstration review threshold, not an approved business scoring rule.
    rows["review_difference_over_25_percent"] = rows["difference_percentage"].gt(25)
    return rows


def missing_summary(frames):
    rows = []
    for kind, frame in frames.items():
        for column in frame.columns:
            missing = int(frame[column].eq("").sum())
            if missing:
                rows.append({"dataset": kind, "column": column, "blank_cells": missing,
                             "total_rows": len(frame), "percentage": 100 * missing / len(frame)})
    return pd.DataFrame(rows, columns=["dataset", "column", "blank_cells", "total_rows", "percentage"])


def field_profile(frames):
    """Review every column slot; diversity is descriptive, not a quality score."""
    output = []
    for kind, frame in frames.items():
        for column in frame.columns:
            answered = frame.loc[frame[column].ne(""), column]
            output.append({"dataset": kind, "column": column, "answered": len(answered),
                           "blank": len(frame) - len(answered), "distinct_nonblank": answered.nunique()})
    return pd.DataFrame(output)


def markdown_table(frame):
    """Render without pandas.to_markdown's optional tabulate dependency."""
    def cell(value):
        if pd.isna(value):
            return "—"
        if isinstance(value, float):
            return f"{value:.2f}"
        return str(value).replace("|", "\\|").replace("\n", " ")
    lines = ["| " + " | ".join(map(str, frame.columns)) + " |",
             "| " + " | ".join(["---"] * len(frame.columns)) + " |"]
    lines.extend("| " + " | ".join(cell(value) for value in row) + " |" for row in frame.itertuples(index=False, name=None))
    return "\n".join(lines)


def create_report(data_dir):
    frames, validation, manifest = load_synthetic_files(data_dir)
    survey, discovery, contacts = (frames[k] for k in ("survey", "discovery", "contacts"))
    config = manifest["configuration"]
    covered = discovery["prospect_id"].nunique()
    survey_count = survey["response_id"].nunique()
    parts = ["# ProspectLens synthetic data profile", f"**{DISCLAIMER}**",
             "All counts below are calculated from the saved CSV files after validation and checksum verification. "
             "The results describe this generated sample only; they are not market research, predictions or evidence of business outcomes.",
             f"Generator version: {manifest['generator_version']}. Seed: `{config['seed']}`. "
             f"Python used for generation: {manifest['python_version']}. pandas used for profiling: {pd.__version__}. "
             f"Currency: {config['currency']}. No live clock is used in generation or report content.",
             "## Records and validation",
             markdown_table(pd.DataFrame([{"dataset": k, "rows": len(frame), "unique_prospects": frame['prospect_id'].nunique()} for k, frame in frames.items()])),
             f"Validation: **{len(validation.errors)} errors, {len(validation.warnings)} warnings**. "
             "Missing recommended survey answers are intentional; warnings remain visible and are not suppressed."]
    warning_counts = Counter((i.dataset, i.column, i.issue) for i in validation.warnings)
    parts.append(markdown_table(pd.DataFrame([{"dataset": k[0], "column": k[1], "issue": k[2], "count": n}
                                             for k, n in warning_counts.items()], columns=["dataset", "column", "issue", "count"])))
    parts += ["## Survey distributions",
              "These tables use all survey rows as their denominator and include missing answers. "
              "The five analytical examples later use question-specific denominators. Stored codes map to friendly labels in the Template Pack dictionary."]
    for column in ("industry", "employee_band", "primary_pain_point", "ai_adoption", "impact_rating", "weekly_hours_band", "desired_outcome", "current_process"):
        allowed = [str(n) for n in range(1, 6)] if column == "impact_rating" else ENUMS[column]
        parts += [f"### {column}", markdown_table(distribution(survey, column, allowed))]

    ai_examples = survey.loc[survey["ai_tools_and_uses"].ne(""),
                             ["response_id", "ai_adoption", "ai_tools_and_uses"]]
    parts += ["## AI tools tried or used, and their uses",
              'S14 follow-up: "Which AI tools have you tried or used, and what do you use them for?"',
              f"**{len(ai_examples)}** responses name tools and explain their uses; "
              f"**{ai_examples['ai_tools_and_uses'].nunique()}** distinct descriptions are present. "
              "Examples below are drawn from the saved file, with up to two per adoption category. "
              "Regular users describe several activities, limited users describe a specific task, and experimenters describe a trial. "
              "Missing optional answers stay blank; this follow-up is not populated for not_using, unsure or missing adoption. "
              "Tool names occur in fictional respondent accounts, not verified product integrations or recommendations.",
              markdown_table(ai_examples.groupby("ai_adoption", sort=False).head(2))]

    parts += ["## Follow-up interest versus explicit consent",
              "Contacts are joined on both response_id and prospect_id. The tables contain aggregate counts; no names, businesses or email addresses are exported."]
    private = survey[["response_id", "prospect_id", "followup_interest", "impact_rating"]].merge(
        contacts[["response_id", "prospect_id", "followup_consent", "marketing_consent", "email"]],
        on=["response_id", "prospect_id"], validate="one_to_one")
    consent_table = pd.crosstab(private["followup_interest"].replace("", "missing"), private["followup_consent"].replace("", "unknown"))
    consent_table = consent_table.reindex(columns=["true", "false", "unknown"], fill_value=0).reset_index()
    parts.append(markdown_table(consent_table))
    interested = private["followup_interest"].isin(["yes", "maybe"])
    permitted = private["followup_consent"].eq("true")
    valid_address = private["email"].map(valid_email)
    eligibility = interested & permitted & valid_address
    parts += [f"Interested (yes/maybe): **{int(interested.sum())}**. Interested without explicit follow-up consent: "
              f"**{int((interested & ~permitted).sum())}**. Interested and permitted but missing a usable email: "
              f"**{int((interested & permitted & ~valid_address).sum())}**. Contact-eligible under the contract: **{int(eligibility.sum())}**. "
              "Eligibility is a data condition, not an instruction to contact anyone.",
              "Marketing permission is a separate choice:", markdown_table(distribution(contacts, "marketing_consent", ["true", "false"]))]

    assessment_counts = discovery.groupby("prospect_id").size()
    parts += ["## Discovery coverage and evidence",
              f"**{len(discovery)} assessments cover {covered} of {survey_count} survey prospects** "
              f"({100 * covered / survey_count if survey_count else 0:.2f}%). "
              f"**{int(assessment_counts.gt(1).sum())} prospects have multiple assessments**; "
              f"**{survey_count - covered}** prospects have no discovery. "
              "The default generator deliberately selects a subset, not a representative discovery sample. "
              "Each generated assessment concerns a distinct workflow within its prospect; no reassessments are generated in this version.",
              markdown_table(assessment_counts.rename("assessments").value_counts().sort_index().rename("prospects").reset_index())]
    for column in ("implementation_complexity", "technical_feasibility", "commercial_potential", "budget_status", "integration_capability", "workflow_reuse_observation", "evidence_status"):
        allowed = [str(n) for n in range(1, 6)] if column == "implementation_complexity" else ENUMS[column]
        parts += [f"### {column}", markdown_table(distribution(discovery, column, allowed))]
    comparison = workload_comparison(discovery)
    parts += ["### Workload consistency",
              "For this generated dataset, every known activity period is week and source notes define time as total person-minutes. "
              "Modelled hours = activity_volume × minutes_per_instance ÷ 60. Staff count is NOT another multiplier. "
              "Missing inputs or unknown period produce no modelled estimate. Reported hours remain separate. "
              "A difference over 25% is a disclosed demonstration review flag, not a new scoring rule or an approved production threshold.",
              f"Supported weekly baselines: **{int(comparison['modelled_staff_hours_per_week'].notna().sum())}/{len(discovery)}**. "
              f"Differences flagged for review: **{int(comparison['review_difference_over_25_percent'].sum())}**.",
              markdown_table(comparison)]
    primary = discovery.sort_values("assessment_id").drop_duplicates("prospect_id").merge(
        survey[["prospect_id", "weekly_hours_band"]], on="prospect_id", validate="one_to_one")
    comparison_by_id = comparison.set_index("assessment_id")["modelled_staff_hours_per_week"]
    primary["modelled_discovery_hours"] = primary["assessment_id"].map(comparison_by_id)
    parts += ["### Survey band beside first assessed workflow",
              "These are different questions/scopes: a broad challenge band versus one workflow baseline. "
              "Differences are not automatically errors. Bands have not been converted to exact hours.",
              markdown_table(primary[["prospect_id", "assessment_id", "weekly_hours_band", "workflow_name", "modelled_discovery_hours"]])]

    parts += ["## Missing values and explicit uncertainty",
              "Blank means missing, not zero or no. The table lists every column containing blank cells. "
              "Many blanks are intentional conditional fields (Other text, software/AI follow-ups), optional comments, or uninvestigated measurements. "
              "They should not all be treated as defects. Empty JSON arrays mean an explicitly empty list and are not blank cells.",
              markdown_table(missing_summary(frames))]
    uncertainty = []
    for kind, frame in frames.items():
        for column in frame.columns:
            for code in ("unknown", "unsure", "not_investigated", "not_discussed"):
                count = int(frame[column].eq(code).sum())
                if count:
                    uncertainty.append({"dataset": kind, "column": column, "recorded_code": code, "count": count})
    parts += ["Explicit uncertainty is retained separately:", markdown_table(pd.DataFrame(uncertainty, columns=["dataset", "column", "recorded_code", "count"]))]

    parts += ["## Field-by-field realism review",
              "All 94 column positions across the three schemas were reviewed. Stable IDs, versions, currency and policy metadata are deliberately repetitive; "
              "adding variation to those would reduce data quality. Canonical answer codes retain their approved meaning. "
              "The table below measures populated, missing and distinct values directly from the current files; low diversity is not automatically an error.",
              markdown_table(field_profile(frames)),
              "### Business and workflow context",
              "Generator 1.2 adds a separate catalogue of industry-specific business types and process vocabulary. "
              "Survey software categories determine the named software available to discovery and the names of underused subscriptions. "
              "Several underused subscriptions require at least three named paid products; supporting categories are added when needed. "
              "Business labels remain visibly fictional, contacts remain restricted, and no brand's technical capability is asserted as fact.",
              "Workflow volumes are capped by the type of work: a report takes longer and occurs less often than a short enquiry. "
              "Success measures include processing person-minutes, elapsed response hours and percentage requiring rework; each has matching units, baseline and target. "
              "Reported hours remain a separate estimate. The narrower workflow can differ substantially from the broad survey challenge.",
              "Evidence notes describe the recorded rating/status. Uninvestigated or unknown integration leaves feasibility unknown or missing. "
              "Reuse conclusions match the similarity observation; safety notes reflect the sector and task. "
              "A pilot proposal requires positive pilot interest, a plausible budget state and assessed medium/high feasibility. "
              "Budget amounts vary with business size. These are authored synthetic scenarios, not a new scoring model.",
              "A few examples from the saved discovery file:",
              markdown_table(discovery[["assessment_id", "workflow_name", "systems_involved", "success_metric", "recommended_next_action"]].head(5))]

    parts += ["## Five pandas analysis examples",
              "Run `python -m scripts.analyse_synthetic_data` to reproduce this report. "
              "The following functions operate on validated, raw-string pandas DataFrames loaded from the files. "
              "They are defined in `scripts/analyse_synthetic_data.py`; constants and imports are in that file. "
              "All results below are generated by these functions."]
    examples = [
        ("1. Which operational problems are reported most often?", pain_point_frequency, pain_point_frequency(survey),
         "Each respondent counts at most once per category. The denominator excludes unanswered S06. Since one respondent can select several problems, percentages can add to more than 100%. Pass an industry code as the second argument to filter before calculating counts."),
        ("2. Which industries have the highest high-impact proportion?", industry_high_impact, industry_high_impact(survey),
         "High impact uses the approved example threshold of 4. Compare numerator and answered_S09 together: 2 of 3 can look stronger than 20 of 40 while being much less stable. Groups below five valid answers are flagged. This is sample description, not industry-level market evidence."),
        ("3. How does AI adoption vary by business size?", ai_by_business_size, ai_by_business_size(survey),
         "Percentages are within each size group, using nonblank S14 answers. Unsure remains an answered category; blanks have no percentage. An empty size group has no rate, rather than an invented 0%."),
        ("4. Which high-impact prospects meet follow-up eligibility?", high_impact_contact_candidates, high_impact_contact_candidates(survey, contacts),
         "Every listed ID has impact at least 4, interest yes/maybe, explicit true follow-up consent, and a structurally valid email. Names and addresses are excluded. Marketing permission never substitutes for follow-up consent, and missing consent never becomes true."),
        ("5. How does assessed complexity compare with commercial potential?", complexity_vs_commercial, complexity_vs_commercial(discovery),
         "Each cell counts assessments, not survey responses or businesses. Complexity 1–2 is simple, 3 medium, 4–5 complex. High commercial potential can coexist with high complexity. Unknown and unassessed remain explicit; these fictional judgements do not estimate conversion or ROI."),
    ]
    for title, function, table, interpretation in examples:
        parts += [f"### {title}", "```python\n" + inspect.getsource(function).strip() + "\n```", markdown_table(table), interpretation]

    # Measure a few of the deliberately imperfect relationships from actual files.
    association = survey[["current_process", "weekly_hours_band", "response_id"]].copy()
    association = association.loc[association["weekly_hours_band"].isin(ENUMS["weekly_hours_band"][:-1])]
    association["higher_workload_band"] = association["weekly_hours_band"].isin(["11_20", "over_20"])
    association = association.groupby("current_process").agg(known_band_responses=("response_id", "nunique"),
        higher_workload_responses=("higher_workload_band", "sum")).reset_index()
    association["percentage"] = association["higher_workload_responses"] * 100 / association["known_band_responses"]
    parts += ["## Intentional relationships, assumptions and limitations",
              "- Industry affects pain-category selection weights; it does not dictate a business's answer. The first nine records cover all industries; remaining records use uneven weights.\n"
              "- Manual/mixed processes have higher chances of the 11–20 and over-20 bands. Impact is loosely associated with burden, with random exceptions. No numeric workload midpoint is used.\n"
              "- Larger businesses tend to list more systems; small digital and large manual counterexamples are built in. AI use is associated with process maturity but does not remove operational pain.\n"
              "- AI tool descriptions pair a named tool with a concrete task related to the respondent's primary challenge. A separate seeded stream varies this text without reshuffling other fields; the original optional-answer pattern is preserved. These are fictional usage accounts.\n"
              "- The first eight survey cases deliberately exercise exceptions, including high impact without interest, AI use with high impact, unknown consent, and consent with missing email. Remaining scenarios combine weighted draws with explicit consistency rules.\n"
              "- Follow-up interest is drawn separately from consent. Follow-up consent and marketing consent use independent random draws except for the documented teaching cases.\n"
              "- Discovery starts with eight teaching prospects, then a random subset; the default covers 27 businesses. Extra workflows are assigned within that subset. This creates selection bias deliberately, so discovery cannot stand in for the whole sample.\n"
              "- Discovery volume and person-minutes are generated together to give a plausible workload; reported hours normally vary by up to 15%, with occasional 35% scope/recollection differences. Staff capacity is capped at 35 process-hours per person per week as a synthetic plausibility check, not a productivity benchmark.\n"
              "- Budget influences fictional commercial judgements; integration and data quality influence fictional complexity/feasibility with noise. Integration evidence is kept consistent with feasibility uncertainty. Deliberate high-commercial/high-complexity examples prevent equating attractiveness with ease of delivery.\n"
              "- Each broad pain category has two workflow variants. Similar survey pain does not establish the same technical solution or confirmed reuse.\n"
              "- Currency applies to optional labour costs and budget amounts. No ROI, guaranteed savings, exchange rates, or conversion probabilities are generated. Numeric targets are aspirations.\n"
              "- Dates use a fixed September 2026 collection window and subsequent fictional discovery dates. No real people, contacts, company records or external data were read to create the rows. Names are visibly fictional constructions and email addresses use example.invalid.\n"
              "- All assessed, confirmed and validated labels are simulated role-play evidence states. They do not describe an actual vendor verification or real consultant observation.\n"
              "- The seed reproduces CSV bytes with the same code/configuration and Python runtime. The manifest records the runtime and SHA-256 hashes. Changing the algorithm or runtime can change the output. Separate random streams keep survey/contact data stable when only discovery count changes.\n"
              "- Contact data stays in its own ignored local CSV. The report uses aggregate consent counts and pseudonymous candidate IDs. A future public demo must explicitly exclude the contact file and test its export boundary.",
              "### Observed process/workload relationship in these files", markdown_table(association),
              "## Source fingerprints", markdown_table(pd.DataFrame([{"file": name, "sha256": digest} for name, digest in manifest["sha256"].items()])),
              "## Reading the code",
              "A DataFrame is like a spreadsheet with named columns. `groupby` makes piles of rows with the same label; "
              "`explode` temporarily gives each selected pain point its own row; `drop_duplicates` prevents counting a respondent twice for the same category. "
              "A merge is a lookup using matching IDs. We compute survey proportions before joining discovery, because one business with three workflows must not become three survey respondents.",
              "`pd.read_csv(..., dtype=str, keep_default_na=False)` preserves the raw contract values before explicit conversion. "
              "See the [pandas read_csv documentation](https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html). "
              "Only the analysis/report script needs pandas; the generator and existing validator remain standard-library Python."]
    return "\n\n".join(parts) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Profile saved fictional ProspectLens datasets")
    parser.add_argument("--data-dir", type=Path, default=ROOT / "data/synthetic")
    parser.add_argument("--report", type=Path, default=ROOT / "docs/synthetic_data_report.md")
    args = parser.parse_args()
    report = create_report(args.data_dir)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(report, encoding="utf-8")
    print(DISCLAIMER)
    print(f"Report written to {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
