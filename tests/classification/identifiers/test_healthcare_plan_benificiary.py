import json
from pathlib import Path

from risk_assessment.classification.identifiers.healthcare.healthcare_plan_beneficiary import (
    HealthcareBeneficiaryNumber,
)


def test_from_dataset():
    identifier = HealthcareBeneficiaryNumber()

    file = Path(__file__).parent / "data" / "health_plan_beneficiary_number.json"

    with file.open() as input:
        for number in json.load(input):
            assert identifier.is_of_this_type(number), number


def test_from_benchmark():
    identifier = HealthcareBeneficiaryNumber()

    assert identifier.is_of_this_type("L6303940")
