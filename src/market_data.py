"""Load only survey data, through the existing contract validator.

No contact/discovery file is opened. Invalid files stop the whole dashboard:
silently dropping invalid rows would change the sample and its denominators.
"""

from dataclasses import dataclass
import csv
import hashlib
import io
import json
from pathlib import Path

import pandas as pd

from src.data_validation import ValidationResult, validate_csv_files
from src.schema import SURVEY_COLUMNS

ROOT = Path(__file__).resolve().parents[1]
DEMO_SURVEY = ROOT / "data/synthetic/survey_responses.csv"
DEMO_MANIFEST = ROOT / "data/synthetic/generation_manifest.json"


def export_survey_csv(frame):
    """Serialize filtered, validated survey rows back into the exact CSV contract.

    Explicitly allowlist survey columns. JSON lists must remain JSON, and pandas
    may hold optional integer ratings as floats when a column contains blanks.
    UTF-8 with BOM lets Excel recognise the questionnaire's Unicode text.
    """
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=SURVEY_COLUMNS, lineterminator="\n")
    writer.writeheader()
    for record in frame[SURVEY_COLUMNS].to_dict(orient="records"):
        cells = {}
        for field, value in record.items():
            if isinstance(value, list):
                cells[field] = json.dumps(value, ensure_ascii=False)
            elif pd.isna(value):
                cells[field] = ""
            elif field == "impact_rating":
                cells[field] = str(int(value))
            else:
                cells[field] = str(value)
        writer.writerow(cells)
    return output.getvalue().encode("utf-8-sig")


class SurveyLoadError(ValueError):
    def __init__(self, message, issues=()):
        super().__init__(message)
        self.issues = list(issues)


@dataclass
class SurveyData:
    frame: pd.DataFrame
    validation: ValidationResult
    synthetic_verified: bool


def load_uploaded_survey(payload):
    """Validate an upload in memory, without overwriting the saved demo files."""
    if len(payload) > 5 * 1024 * 1024:
        raise SurveyLoadError("Choose a survey CSV no larger than 5 MB.")
    try:
        text = payload.decode("utf-8-sig")
    except UnicodeError as exc:
        raise SurveyLoadError("The CSV must use UTF-8 encoding. In Excel, save as CSV UTF-8.") from exc
    result = validate_csv_files(io.StringIO(text, newline=""))
    if not result.valid:
        raise SurveyLoadError("Survey validation failed. The current dataset has not been replaced.", result.errors)
    return SurveyData(pd.DataFrame(result.survey, columns=SURVEY_COLUMNS), result, False)


def load_survey(path=DEMO_SURVEY, manifest_path=DEMO_MANIFEST):
    """Return a DataFrame of validated, typed records; blanks stay missing.

    Pass manifest_path=None for local test fixtures without provenance. The app
    always uses the demo manifest; hashes are checked before AND after validation
    so a file edited during loading cannot silently mix two versions.
    """
    path = Path(path)
    if not path.is_file():
        raise SurveyLoadError("Survey dataset is missing. Complete synthetic dataset generation before opening this view.")
    try:
        before = hashlib.sha256(path.read_bytes()).hexdigest()
        result = validate_csv_files(path)
        if not result.valid:
            raise SurveyLoadError("Survey validation failed. Correct the listed issues before analysis.", result.errors)
        if hashlib.sha256(path.read_bytes()).hexdigest() != before:
            raise SurveyLoadError("The survey changed during loading. Please reload the page.")
        verified = False
        if manifest_path is not None:
            manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
            if not isinstance(manifest, dict) or not isinstance(manifest.get("sha256"), dict):
                raise SurveyLoadError("The generation manifest is malformed. Restore the matching synthetic manifest.")
            if (manifest.get("disclaimer") != "SYNTHETIC DATA - NOT REAL MARKET FINDINGS"
                    or manifest["sha256"].get(path.name) != before):
                raise SurveyLoadError("The survey does not match its synthetic generation manifest. Restore the matching files or rerun the generator deliberately.")
            verified = True
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SurveyLoadError("Cannot read the survey or generation manifest. Check file availability, permissions and UTF-8 encoding.") from exc
    # The validator already decoded JSON arrays and converted ratings to integers.
    # Reusing its parsed rows avoids a second, differently interpreted CSV parser.
    return SurveyData(pd.DataFrame(result.survey, columns=SURVEY_COLUMNS), result, verified)
