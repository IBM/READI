import pytest

from risk_assessment.classification.identifiers import SSNUK


def test_positive_known():
    identifier = SSNUK()

    assert identifier.is_of_this_type("AB123456C"), "AB123456C"
    assert identifier.is_of_this_type("OA123456C"), "OA123456C"


def test_ignore_spaces():
    identifier = SSNUK()

    assert identifier.is_of_this_type("AB 12 34 56 C"), "AB 12 34 56 C"


def test_negative_known():
    identifier = SSNUK()

    assert not identifier.is_of_this_type("DB123456C"), "DB123456C"
    assert not identifier.is_of_this_type("AD123456C"), "AD123456C"
    assert not identifier.is_of_this_type("AO123456C"), "AO123456C"
    assert not identifier.is_of_this_type("BA12A456C"), "BA12A456C"
    assert not identifier.is_of_this_type("BA1234567"), "BA1234567"
    assert not identifier.is_of_this_type("BA123456Z"), "BA123456Z"

    assert not identifier.is_of_this_type("木製 230214C"), "木製 230214C"


@pytest.fixture()
def faker_locale():
    return ["en_UK"]


@pytest.mark.skip("Apparently Faker is generating invalid UK SSN")
def test_random(faker, faker_locale):
    identifier = SSNUK()

    for _ in range(100):
        ssn = faker.ssn()

        assert identifier.is_of_this_type(ssn), ssn
