import pytest

from risk_assessment.classification.identifiers import InternationalZipcode


def test_basic_testing():
    identifier = InternationalZipcode()

    assert identifier.is_of_this_type("21016"), "Luino, IT"
    assert identifier.is_of_this_type("490-1425"), "Higashishijimi, Japan"

    assert not identifier.is_of_this_type("djflaksjfdkla"), "Garbage"


@pytest.mark.skip("Faker is generating nonexisting zipcodes")
def test_us_zipcode(faker, faker_locale_us):
    identifier = InternationalZipcode()

    for _ in range(1_000):
        zipcode = faker.zipcode()
        assert identifier.is_of_this_type(zipcode), zipcode
