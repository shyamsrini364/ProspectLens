"""Plain-language filter help shared by both dashboard lenses."""

AI_ADOPTION_HELP = (
    "Filter by how a business says it currently uses AI.\n\n"
    "- **Regular use:** AI is used regularly in the business.\n"
    "- **Specific tasks:** AI is used for some tasks, but not widely.\n"
    "- **Experimented:** the business has tried AI but does not use it regularly.\n"
    "- **Not using:** the business reports that it is not currently using AI.\n"
    "- **Not sure:** the respondent is unsure; this is different from not using AI.\n\n"
    "These are self-reported answers, not an assessment of AI skill or readiness. "
    "Select one or more levels to compare that group, or leave empty to include everyone, "
    "including missing answers."
)

ASSESSMENT_STAGE_HELP = (
    "Filter by the type of evidence available for each business.\n\n"
    "- **Survey Only:** survey answers are available, but no discovery assessment is linked. "
    "Commercial potential and the overall opportunity score are not assessed.\n"
    "- **Discovery Enriched:** at least one discovery assessment is linked. "
    "It may contain workflow, commercial and technical evidence, but can still be incomplete. "
    "This label does not mean the business qualifies for an overall score.\n\n"
    "Use this filter to compare businesses at the same evidence stage. "
    "Leave empty to include both stages; open Business details to inspect the evidence."
)


def opportunity_band_help(config):
    """Read band boundaries from the scoring configuration so help stays accurate."""
    bands = config['bands']
    descriptions = [
        f'- **{name}:** {floor}–100.' if index == 0 else
        f'- **{name}:** {floor} to below {bands[index - 1][0]}.'
        for index, (floor, name) in enumerate(bands)
    ]
    return (
        "Filter by the overall Prospect Opportunity Score, which combines business "
        "opportunity value and commercial potential.\n\n"
        + '\n'.join(descriptions)
        + "\n- **Not assessed:** required evidence is missing, so no overall score is calculated; "
        "this does not mean a low score.\n\n"
        "Bands use the score before display rounding. They are provisional investigation "
        "priorities, not predictions of sales or success. Select bands to focus the view, "
        "or leave empty to include all businesses. Open How scores work for the calculation."
    )
