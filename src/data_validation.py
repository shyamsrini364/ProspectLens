"""Validate the v1.0 contract without pandas, schema libraries or data inference.

Public row inputs are dictionaries of CSV strings (or None). Parsed rows are
returned separately; callers must check ``result.valid`` before analysis.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from contextlib import nullcontext
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Callable

from .schema import (
    ARRAY_FIELDS, BOOLEAN_FIELDS, COLUMNS, DATE_FIELDS, ENUMS,
    NUMBER_FIELDS, RATING_FIELDS, RECOMMENDED_SURVEY_FIELDS, REQUIRED,
)


@dataclass(frozen=True)
class Issue:
    severity: str
    dataset: str
    row_id: str
    column: str
    issue: str
    suggested_fix: str


@dataclass
class ValidationResult:
    survey: list[dict] = field(default_factory=list)
    discovery: list[dict] = field(default_factory=list)
    contacts: list[dict] = field(default_factory=list)
    issues: list[Issue] = field(default_factory=list)

    @property
    def errors(self) -> list[Issue]:
        return [item for item in self.issues if item.severity == "error"]

    @property
    def warnings(self) -> list[Issue]:
        return [item for item in self.issues if item.severity == "warning"]

    @property
    def valid(self) -> bool:
        return not self.errors

    def require_valid(self) -> None:
        if not self.valid:
            raise ValueError("Resolve validation errors before using these records.")


def _issue(result, kind, row_id, column, message, fix, severity="error"):
    result.issues.append(Issue(severity, kind, row_id, column, message, fix))


def valid_email(value: object) -> bool:
    """Conservative structural check only; does not verify delivery/ownership."""
    if not isinstance(value, str) or len(value) > 254 or value.count("@") != 1:
        return False
    local, domain = value.split("@")
    if not re.fullmatch(r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]{1,64}", local):
        return False
    if local.startswith(".") or local.endswith(".") or ".." in local:
        return False
    labels = domain.split(".")
    return len(labels) >= 2 and all(
        re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?", part)
        for part in labels
    )


def _iso_date(value: str) -> bool:
    # Accept calendar dates or extended ISO timestamps, optionally with zone.
    if not re.fullmatch(
        r"\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2}(?::\d{2}(?:\.\d+)?)?(?:Z|[+-](?:[01]\d|2[0-3]):[0-5]\d)?)?",
        value,
    ):
        return False
    try:
        if "T" in value:
            datetime.fromisoformat(value.replace("Z", "+00:00"))
        else:
            date.fromisoformat(value)
    except ValueError:
        return False
    return True


def _parse_rows(rows, kind, result):
    parsed = []
    key = "assessment_id" if kind == "discovery" else "response_id"
    seen = set()
    for row_number, raw in enumerate(rows, start=2):
        row_id = str(raw.get(key) or f"CSV row {row_number}").strip()
        row = {}

        def report(column, message, fix, severity="error"):
            _issue(result, kind, row_id, column, message, fix, severity)

        for extra in raw.keys() - set(COLUMNS[kind]):
            report(str(extra), "Unexpected column.", "Use the exact template columns; keep contacts separate.")
        for column in COLUMNS[kind]:
            raw_value = raw.get(column)
            if raw_value is not None and not isinstance(raw_value, str):
                report(column, "Expected a CSV string or None.", "Supply raw CSV cell strings to validate_dataset.")
                row[column] = None
                continue
            value = raw_value.strip() if raw_value is not None else None
            value = value if value else None
            row[column] = value
            if value is None:
                if column in REQUIRED[kind]:
                    report(column, "Required value is missing.", "Supply this record's identifier or dataset version.")
                continue
            if column in ARRAY_FIELDS:
                try:
                    entries = json.loads(value)
                except (ValueError, RecursionError):
                    report(column, "Malformed JSON array.", 'Use a JSON array such as ["manual_data_entry"].')
                    continue
                if not isinstance(entries, list) or any(not isinstance(x, str) or not x.strip() for x in entries):
                    report(column, "Expected a JSON array of nonempty strings.", "Use text entries, not objects, numbers or nulls.")
                    continue
                row[column] = entries
                if column in ENUMS and any(x not in ENUMS[column] for x in entries):
                    report(column, "Unknown category in array.", "Use only the canonical codes in the dictionary.")
                if len(entries) != len(set(entries)):
                    report(column, "Repeated array entries.", "Review duplicate selections; each respondent counts once per category.", "warning")
                if column == "pain_points" and len(set(entries)) > 3:
                    report(column, "More than three distinct pain points.", "Select at most three distinct categories.")
            elif column in ENUMS:
                if value not in ENUMS[column]:
                    report(column, "Unknown category.", "Use a canonical code from the dictionary; do not silently map values.")
            elif column in RATING_FIELDS or column == "staff_count":
                if not re.fullmatch(r"[0-9]+", value):
                    report(column, "Expected a whole integer.", "Use 1–5 for ratings or a nonnegative integer for staff_count.")
                else:
                    try:
                        number = int(value)
                    except ValueError:
                        report(column, "Integer is too long to parse.", "Check the input value.")
                        continue
                    row[column] = number
                    if column in RATING_FIELDS and not 1 <= number <= 5:
                        report(column, "Rating is outside 1–5.", "Use an integer from 1 to 5 or leave unassessed values blank.")
            elif column in NUMBER_FIELDS:
                try:
                    if not re.fullmatch(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?", value):
                        raise InvalidOperation
                    number = Decimal(value)
                    if not number.is_finite() or number < 0:
                        raise InvalidOperation
                    row[column] = number
                except InvalidOperation:
                    report(column, "Expected a finite nonnegative number.", "Use a number without currency symbols or separators; leave unknown values blank.")
            elif column in BOOLEAN_FIELDS:
                if value not in {"true", "false"}:
                    report(column, "Invalid consent boolean.", "Use lowercase true or false, or blank for unknown.")
                else:
                    row[column] = value == "true"
            elif column in DATE_FIELDS:
                if not _iso_date(value):
                    report(column, "Invalid ISO date or timestamp.", "Use YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS with optional Z/offset.")
            elif column == "email" and not valid_email(value):
                report(column, "Invalid email structure.", "Correct the email address or leave it blank.")
            if column in {"dataset_version", "questionnaire_version"} and value != "1.0":
                report(column, "Unrecognised schema/questionnaire version.", "Confirm compatibility with version 1.0 before analysis.", "warning")

        identifier = row.get(key)
        if isinstance(identifier, str):
            if identifier in seen:
                report(key, "Duplicate identifier.", "Use a unique identifier for each record; keep reassessments under new assessment IDs.")
            seen.add(identifier)
        if kind == "survey":
            _survey_checks(row, report)
        elif kind == "discovery":
            _discovery_checks(row, report)
        elif kind == "contacts":
            if any(row.get(f) is True for f in BOOLEAN_FIELDS):
                for column in ("privacy_notice_version", "consent_recorded_at"):
                    if row.get(column) is None:
                        report(column, "Permission/acknowledgement provenance is incomplete.", "Record the notice version and timestamp where possible.", "warning")
        parsed.append(row)
    return parsed


def _survey_checks(row, report):
    for column in RECOMMENDED_SURVEY_FIELDS:
        if row[column] is None or row[column] == []:
            report(column, "Recommended analytical answer is missing.", "Collect if possible; exclude missing answers from this metric's denominator.", "warning")
    pain = row["pain_points"]
    if isinstance(pain, list) and row["primary_pain_point"] and row["primary_pain_point"] not in pain:
        report("primary_pain_point", "S07 is not among S06 selections.", "Review with the respondent; preserve the original answers.", "warning")
    for column, exclusive in (("business_systems", "none_paper"), ("ai_concerns", "none")):
        choices = row[column]
        if isinstance(choices, list) and exclusive in choices and len(set(choices)) > 1:
            report(column, "Exclusive selection is mixed with other choices.", "Review whether the exclusive choice or the other choices apply.", "warning")
    for column in ("industry", "pain_points", "primary_pain_point", "business_systems", "ai_concerns", "desired_outcome"):
        value = row[column]
        if (value == "other" or isinstance(value, list) and "other" in value) and not row[column + "_other"]:
            report(column + "_other", "Other selection lacks explanatory text.", "Provide a short explanation for Other.", "warning")
    if row["ai_adoption"] == "not_using" and row["ai_tools_and_uses"]:
        report("ai_tools_and_uses", "AI tools supplied despite not_using.", "Review the conditional answer; do not rewrite it automatically.", "warning")
    if row["underused_software_names"] and row["subscription_underuse"] not in ("several", "one_or_two"):
        report("underused_software_names", "Software names supplied outside the underuse branch.", "Review S13 and its optional follow-up.", "warning")


def _discovery_checks(row, report):
    # The CSV has no actual-work flag, so zero minutes triggers review, not inference.
    if row["minutes_per_instance"] == Decimal(0):
        report("minutes_per_instance", "Zero minutes needs confirmation that no actual work occurs.", "Record positive person-minutes for actual work, or leave unknown time blank.", "warning")
    if any(row[c] is not None for c in ("labour_cost_per_hour", "indicative_budget")) and not row["currency"]:
        report("currency", "A monetary value has no explicit currency.", "Supply the currency for the amount; do not assume AUD.")
    for value_column, evidence_column in (("data_quality_rating", "data_quality_evidence"),
                                          ("implementation_complexity", "assessment_evidence")):
        if row[value_column] is not None and not row[evidence_column]:
            report(evidence_column, "Assessment lacks supporting reasoning.", "Record the rationale and uncertainty.", "warning")
    if row["integration_capability"] == "confirmed_api" and not row["integration_evidence"]:
        report("integration_evidence", "Confirmed API lacks evidence.", "Describe what was confirmed; tool usage alone is insufficient.", "warning")
    if row["evidence_status"] == "validated" and not (row["assessment_evidence"] or row["source_reference"]):
        report("assessment_evidence", "Validated status lacks evidence/source notes.", "Describe what was validated and its source.", "warning")
    if isinstance(row["observed_impact_types"], list) and "other" in row["observed_impact_types"] and not row["impact_evidence"]:
        report("impact_evidence", "Other impact lacks explanation.", "Describe the observed impact.", "warning")


def validate_dataset(survey, discovery=None, contacts=None) -> ValidationResult:
    """Validate raw CSV-like rows. Discovery and contacts are independently optional."""
    result = ValidationResult()
    result.survey = _parse_rows(survey, "survey", result)
    result.discovery = _parse_rows(discovery if discovery is not None else [], "discovery", result)
    result.contacts = _parse_rows(contacts if contacts is not None else [], "contacts", result)
    prospects = {r["prospect_id"] for r in result.survey if isinstance(r["prospect_id"], str)}
    responses = {r["response_id"]: r for r in result.survey if isinstance(r["response_id"], str)}
    for row in result.discovery:
        if not isinstance(row["prospect_id"], str) or row["prospect_id"] not in prospects:
            _issue(result, "discovery", str(row["assessment_id"]), "prospect_id", "Orphan discovery assessment.", "Supply a survey record for this prospect or correct the ID.")
    for row in result.contacts:
        survey_row = responses.get(row["response_id"]) if isinstance(row["response_id"], str) else None
        if survey_row is None:
            _issue(result, "contacts", str(row["response_id"]), "response_id", "Orphan contacts record.", "Link to an existing survey response.")
        elif row["prospect_id"] != survey_row["prospect_id"]:
            _issue(result, "contacts", str(row["response_id"]), "prospect_id", "Contact and survey prospect IDs do not match.", "Use the prospect ID belonging to this survey response.")
    return result


def _read_csv(path, kind):
    issues = []
    rows = []
    try:
        # A decoded text stream lets uploads use the same CSV checks in memory.
        source = nullcontext(path) if hasattr(path, "read") else Path(path).open(encoding="utf-8-sig", newline="")
        with source as handle:
            reader = csv.reader(handle, strict=True)
            header = next(reader, None)
            if header != COLUMNS[kind]:
                issues.append(Issue("error", kind, "header", "*", "CSV header does not match the contract in name/order.", "Use the exact header-only template, with no extra or duplicate columns."))
                return rows, issues
            for cells in reader:
                if len(cells) != len(header):
                    issues.append(Issue("error", kind, f"CSV line {reader.line_num}", "*", "CSV row width differs from header.", "Use csv.writer to quote embedded JSON, commas and newlines correctly."))
                else:
                    rows.append(dict(zip(header, cells)))
    except (OSError, UnicodeError, csv.Error):
        issues.append(Issue("error", kind, "file", "*", "Unable to read valid UTF-8 comma-delimited CSV.", "Check the file path, encoding, permissions and CSV quoting."))
    return rows, issues


def validate_csv_files(survey_path, discovery_path=None, contacts_path=None) -> ValidationResult:
    """Load paths or decoded text streams, then validate the exact CSV contract."""
    loaded = {}
    file_issues = []
    for kind, path in (("survey", survey_path), ("discovery", discovery_path), ("contacts", contacts_path)):
        loaded[kind], issues = _read_csv(path, kind) if path is not None else ([], [])
        file_issues.extend(issues)
    result = validate_dataset(**loaded)
    result.issues[:0] = file_issues
    return result


def survey_with_discovery(result: ValidationResult) -> list[dict]:
    """Nested join preserves survey counts and every assessment for each prospect."""
    result.require_valid()
    by_prospect = defaultdict(list)
    for assessment in result.discovery:
        by_prospect[assessment["prospect_id"]].append(dict(assessment))
    return [{"survey": dict(row), "assessments": list(by_prospect[row["prospect_id"]])} for row in result.survey]


def contact_ready_response_ids(result: ValidationResult) -> list[str]:
    """Eligibility only; returning IDs is not an authorisation to publish/contact."""
    result.require_valid()
    contacts = {row["response_id"]: row for row in result.contacts}
    return [row["response_id"] for row in result.survey
            if row["followup_interest"] in {"yes", "maybe"}
            and (contact := contacts.get(row["response_id"])) is not None
            and contact["followup_consent"] is True
            and valid_email(contact["email"])]


def _selected_rows(result, predicate):
    result.require_valid()
    return [r for r in result.survey if predicate is None or predicate(r)]


def pain_point_prevalence(result: ValidationResult, predicate: Callable | None = None) -> dict:
    """Small contract example: filter first, count distinct respondents per choice."""
    rows = [r for r in _selected_rows(result, predicate) if r["pain_points"]]
    denominator = len({r["response_id"] for r in rows})
    counts = Counter(choice for row in rows for choice in set(row["pain_points"]))
    return {"denominator": denominator, "categories": {
        choice: {"count": counts[choice], "percentage": 100 * counts[choice] / denominator if denominator else None}
        for choice in ENUMS["pain_points"]}}


def high_impact_prevalence(result: ValidationResult, threshold=4, predicate: Callable | None = None) -> dict:
    if type(threshold) is not int or not 1 <= threshold <= 5:
        raise ValueError("threshold must be an integer from 1 to 5")
    rows = [r for r in _selected_rows(result, predicate) if r["impact_rating"] is not None]
    denominator = len(rows)
    numerator = sum(r["impact_rating"] >= threshold for r in rows)
    return {"count": numerator, "denominator": denominator,
            "percentage": 100 * numerator / denominator if denominator else None}


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate ProspectLens v1.0 CSV files.")
    parser.add_argument("survey")
    parser.add_argument("--discovery")
    parser.add_argument("--contacts")
    args = parser.parse_args()
    result = validate_csv_files(args.survey, args.discovery, args.contacts)
    print(json.dumps({"valid": result.valid,
                      "rows": {kind: len(getattr(result, kind)) for kind in COLUMNS},
                      "errors": [asdict(i) for i in result.errors],
                      "warnings": [asdict(i) for i in result.warnings]}, indent=2))
    return 0 if result.valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
