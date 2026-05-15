import pytest

from risk_assessment.classification.identifiers import IsraelID
from risk_assessment.classification.identifiers.national_identifier import (
    CanadaSIN,
    MexicoCURP,
    NationalIdentity,
    USPassport,
)


def test_israel_national_id(faker):
    examples = [
        "137291217",
        "802879585",
        "482165016",
        "338079445",
        "221509805",
        "684510100",
        "804835734",
        "850263880",
        "637242462",
        "175440072",
        "521843060",
        "436051833",
        "163337546",
        "167016526",
        "622337616",
        "853839132",
        "138005392",
        "337039655",
        "416200467",
        "877896209",
    ]

    identifier = IsraelID()

    for example in examples:
        assert identifier.is_of_this_type(example), example


def test_mexican_curb():
    examples = [
        "HEGG560427MVZRRL04",
    ]

    identifier = MexicoCURP()

    for example in examples:
        assert identifier.is_of_this_type(example), example


def test_canada_social_insurance_number():
    examples = [
        "046 454 286",  # <--- A fictitious, but valid, SIN.
        "046454286",  # <--- A fictitious, but valid, SIN.
        "046-454-286",  # <--- A fictitious, but valid, SIN.
    ]

    identifier = CanadaSIN()

    for example in examples:
        assert identifier.is_of_this_type(example), example


def test_fix_misidentified_CanadaSIN():
    examples = [
        "123123456\n",
    ]

    identifier = CanadaSIN()

    for example in examples:
        assert not identifier.is_of_this_type(example), example


def test_national_identity_safe():
    identifier = NationalIdentity(safe=True)

    examples = [
        "046 454 286",  # <--- A fictitious, but valid, SIN.
        "046454286",  # <--- A fictitious, but valid, SIN.
        "046-454-286",  # <--- A fictitious, but valid, SIN.
        "HEGG560427MVZRRL04",
        "137291217",
        "802879585",
        "482165016",
        "338079445",
        "221509805",
        "684510100",
        "804835734",
        "850263880",
        "637242462",
        "175440072",
        "521843060",
        "436051833",
        "163337546",
        "167016526",
        "622337616",
        "853839132",
        "138005392",
        "337039655",
        "416200467",
        "877896209",
    ]

    for example in examples:
        assert identifier.is_of_this_type(example), example


def test_national_identity():
    identifier = NationalIdentity(safe=False)

    examples = [
        "766489967",  # Canada
        "2234 5678 9123",
        "103024 570890 0001",
    ]

    for example in examples:
        assert identifier.is_of_this_type(example), example


def test_national_identity_safe_invalid():
    identifier = NationalIdentity(safe=True)

    examples = [
        "2234",
        "HEGG560427MVZRRL0",
        "1234,5678,9012",
        "103024 570890 0001",  # valid Indonesia ICD, but not safe
    ]

    for example in examples:
        assert not identifier.is_of_this_type(example), example


def test_national_identity_invalid():
    identifier = NationalIdentity(safe=False)

    examples = [
        "2234",
        "HEGG560427MVZRRL0",
    ]

    for example in examples:
        assert not identifier.is_of_this_type(example), example


@pytest.mark.skip("Faker not working properly yet")
def test_us_passport(faker):
    identifier = USPassport()

    for _ in range(100):
        example = faker.passport_number()
        assert identifier.is_of_this_type(example), example


def test_us_passport_from_examples():
    identifier = USPassport()

    examples = [
        "A12345678",
        "E00007734",
        "C12345678",
    ]

    for example in examples:
        assert identifier.is_of_this_type(example)
