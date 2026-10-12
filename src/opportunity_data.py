"""Validated dataset bundles. The demo never opens the restricted contacts CSV."""

from dataclasses import dataclass
import hashlib
import io
import json
from pathlib import Path

import pandas as pd

from src.data_validation import validate_csv_files, contact_ready_response_ids
from src.market_data import ROOT, DEMO_SURVEY, DEMO_MANIFEST, SurveyLoadError, export_survey_csv
from src.schema import SURVEY_COLUMNS, DISCOVERY_COLUMNS


@dataclass
class OpportunityData:
    survey: pd.DataFrame
    discovery: pd.DataFrame
    validation: object
    permission: dict
    name: str
    synthetic: bool = False
    contacts_supplied: bool = False


def _bundle(result, name, synthetic=False, contacts_supplied=False):
    if not result.valid:
        raise SurveyLoadError('Opportunity dataset validation failed. Resolve errors before analysis.',result.errors)
    eligible = set(contact_ready_response_ids(result))
    permission = {}
    for c in result.contacts:
        provenance = c['privacy_acknowledged'] is True and c['privacy_notice_version'] and c['consent_recorded_at']
        permission[c['response_id']] = ('Permission documented' if c['response_id'] in eligible and provenance
            else 'Review permission provenance' if c['response_id'] in eligible else 'Not contact-ready')
    # Keep only eligibility flags, never names, emails or contact records in app state.
    result.contacts = []
    return OpportunityData(pd.DataFrame(result.survey,columns=SURVEY_COLUMNS),
        pd.DataFrame(result.discovery,columns=DISCOVERY_COLUMNS),result,permission,name,synthetic,contacts_supplied)


def _stream(payload):
    if payload is None:
        return None
    if len(payload)>5*1024*1024:
        raise SurveyLoadError('Each CSV must be no larger than 5 MB.')
    try:
        return io.StringIO(payload.decode('utf-8-sig'),newline='')
    except UnicodeError as exc:
        raise SurveyLoadError('Choose UTF-8 encoded CSV files.') from exc


def load_uploaded_opportunities(survey, discovery=None, contacts=None):
    return _bundle(validate_csv_files(_stream(survey),_stream(discovery),_stream(contacts)),
                   'Uploaded dataset',contacts_supplied=contacts is not None)


def from_market_upload(data):
    # Never join a real uploaded survey to coincidentally matching synthetic IDs.
    return load_uploaded_opportunities(export_survey_csv(data.frame))


def load_opportunities(survey_path=DEMO_SURVEY, discovery_path=ROOT/'data/synthetic/discovery_assessments.csv',
                       manifest_path=DEMO_MANIFEST):
    paths=[Path(survey_path)]
    if not paths[0].is_file():
        raise SurveyLoadError('Survey dataset is missing; restore it or upload compatible CSV files.')
    discovery_path=Path(discovery_path) if discovery_path is not None else None
    if discovery_path is not None and discovery_path.is_file():
        paths.append(discovery_path)
    else:
        discovery_path=None
    try:
        hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
        result=validate_csv_files(paths[0],discovery_path)
        if any(hashlib.sha256(p.read_bytes()).hexdigest()!=hashes[p.name] for p in paths):
            raise SurveyLoadError('Dataset changed during loading; reload the page.')
        if manifest_path is not None:
            manifest=json.loads(Path(manifest_path).read_text(encoding='utf-8'))
            if (not isinstance(manifest,dict) or manifest.get('disclaimer')!='SYNTHETIC DATA - NOT REAL MARKET FINDINGS'
                    or not isinstance(manifest.get('sha256'),dict)
                    or any(manifest['sha256'].get(k)!=v for k,v in hashes.items())):
                raise SurveyLoadError('The files do not match the synthetic generation manifest.')
        return _bundle(result,'Synthetic demo' if manifest_path is not None else 'Local dataset',manifest_path is not None)
    except (OSError,UnicodeError,json.JSONDecodeError) as exc:
        raise SurveyLoadError('Cannot read the opportunity files or manifest; check paths and encoding.') from exc
