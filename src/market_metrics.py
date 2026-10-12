"""Pure pandas calculations: no Streamlit, file access or chart styling.

The unit is a survey submission (response_id), not an exploded selection or an
assessment. Repeated submissions from one prospect remain separate responses.
"""

from dataclasses import dataclass

import pandas as pd

from src.schema import ENUMS

FILTER_FIELDS = ("industry", "employee_band", "primary_pain_point", "ai_adoption")
MULTI_FIELDS = ("pain_points", "ai_concerns")
MISSING = "__missing__"  # UI-only sentinel; never written back into a CSV.
HIGH_IMPACT_THRESHOLD = 4  # Agreed example configuration and requested KPI.
MINIMUM_GROUP_SIZE = 5


def answered(frame, field):
    if field in MULTI_FIELDS:
        return frame[field].map(lambda value: isinstance(value, list) and bool(value)).astype(bool)
    return (frame[field].notna() & frame[field].ne("")).astype(bool)


def filter_options(frame, field):
    present = set(frame.loc[answered(frame, field), field])
    return [code for code in ENUMS[field] if code in present] + ([MISSING] if (~answered(frame, field)).any() else [])


def filter_survey(frame, selections):
    """OR within a filter, AND across filters. Empty selections mean all."""
    mask = pd.Series(True, index=frame.index, dtype=bool)
    for field, choices in selections.items():
        if field not in FILTER_FIELDS:
            raise ValueError(f"Unsupported filter: {field}")
        if choices:
            mask &= frame[field].fillna(MISSING).replace("", MISSING).isin(choices)
    return frame.loc[mask].copy()


@dataclass(frozen=True)
class Rate:
    count: int
    denominator: int
    missing: int

    @property
    def percentage(self):
        return 100 * self.count / self.denominator if self.denominator else None


def market_kpis(frame):
    """Unknown/unsure is an explicit answer; blanks are not answers.

    AI numerator: regular_multiple + limited_tasks (not experimented).
    Follow-up numerator: yes only. Maybe is reported separately, never consent.
    """
    def rate(field, positive):
        known = answered(frame, field)
        return Rate(int((known & positive).sum()), int(known.sum()), int((~known).sum()))

    impact = pd.to_numeric(frame["impact_rating"], errors="coerce")
    return {
        "responses": int(frame["response_id"].nunique()),
        "prospects": int(frame["prospect_id"].nunique()),
        "industries": int(frame.loc[answered(frame, "industry"), "industry"].nunique()),
        "industry_missing": int((~answered(frame, "industry")).sum()),
        "high_impact": rate("impact_rating", impact.ge(HIGH_IMPACT_THRESHOLD)),
        "using_ai": rate("ai_adoption", frame["ai_adoption"].isin(["regular_multiple", "limited_tasks"])),
        "followup": rate("followup_interest", frame["followup_interest"].eq("yes")),
        "followup_maybe": int(frame["followup_interest"].eq("maybe").sum()),
        "ai_unsure": int(frame["ai_adoption"].eq("unsure").sum()),
    }


def frequency(frame, field, group_by=None):
    """Counts and answered-question denominators, optionally within each group.

    explode makes one temporary row per selected option. drop_duplicates then
    ensures each response contributes at most once to each category. The
    denominator is taken BEFORE exploding, so three choices are still one person.
    Zero answers produce NaN percentages, never an invented 0%.
    """
    groups = [(None, frame)]
    if group_by:
        keys = frame[group_by].fillna(MISSING).replace("", MISSING)
        order = [value for value in [*ENUMS[group_by], MISSING] if value in set(keys)]
        groups = [(key, frame.loc[keys.eq(key)]) for key in order]
    output = []
    for key, group in groups:
        eligible = group.loc[answered(group, field), ["response_id", field]]
        denominator = int(eligible["response_id"].nunique())
        entries = eligible.explode(field) if field in MULTI_FIELDS else eligible
        counts = entries.drop_duplicates(["response_id", field])[field].value_counts()
        for code in ENUMS[field]:
            count = int(counts.get(code, 0))
            row = dict(category=code, count=count, denominator=denominator,
                       percentage=100 * count / denominator if denominator else float("nan"),
                       missing=len(group) - denominator, group_total=len(group),
                       small_sample=0 < denominator < MINIMUM_GROUP_SIZE)
            if group_by:
                row[group_by] = key
            output.append(row)
    columns = ["category", "count", "denominator", "percentage", "missing", "group_total", "small_sample"]
    return pd.DataFrame(output, columns=columns + ([group_by] if group_by else []))


def quality_summary(frame):
    fields = {"industry": "S04 · Industry", "employee_band": "S05 · Business size",
              "pain_points": "S06 · Pain points", "primary_pain_point": "S07 · Primary pain point",
              "impact_rating": "S09 · Impact", "ai_adoption": "S14 · AI adoption",
              "ai_concerns": "S15 · Concerns", "desired_outcome": "S17 · Outcome",
              "followup_interest": "S18 · Follow-up"}
    return pd.DataFrame([{"Question": label, "Answered": int(answered(frame, field).sum()),
                          "Missing": int((~answered(frame, field)).sum()), "Filtered responses": len(frame)}
                         for field, label in fields.items()])


def ai_adoption_by_industry(frame):
    """Same S14 denominators, ordered by answered response count (largest first).

    Stable sorting retains contract order for ties and for the five categories.
    Missing S14 is excluded; Not sure remains a separate, valid answer.
    """
    return frequency(frame, "ai_adoption", "industry").sort_values(
        "denominator", ascending=False, kind="stable").reset_index(drop=True)
