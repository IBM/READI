import json
from pathlib import Path

from risk_assessment.classification.identifiers.healthcare import MedicalRecordNumber


def test_mrn_from_other_sources():
    identifier = MedicalRecordNumber()

    assert identifier.is_of_this_type("T325608")
    assert identifier.is_of_this_type("MED21644304")


def test_mrn_from_dataset():
    identifier = MedicalRecordNumber()

    file = Path(__file__).parent / "data" / "mrn.json"

    with file.open() as input:
        for record_id in json.load(input):
            assert identifier.is_of_this_type(record_id), record_id
