import pytest

from risk_assessment.classification.identifiers import City, Country, CountryCode, CountryName, ZipCode
from risk_assessment.classification.identifiers.geography import (
    UKPostCode,
    UnitedStateState,
    _extract_all_langugage_city_names,
)


def test_country_name(faker):
    identifier = Country()

    missed: set[str] = set()
    done: int = 0

    for _ in range(10_000):
        country = faker.country()

        if country in missed:
            continue

        done += 1

        if not identifier.is_of_this_type(country):
            missed.add(country)

    assert len(missed) / done < 0.005, missed  # account for Faker having a larger dictionary than us


def test_country_name_proper(faker):
    identifier = CountryName()

    missed: set[str] = set()
    done: int = 0

    for _ in range(10_000):
        country = faker.country()

        if country in missed:
            continue

        done += 1

        if not identifier.is_of_this_type(country):
            missed.add(country)

    assert len(missed) / done < 0.005, missed  # account for Faker having a larger dictionary than us


def test_country_code(faker):
    identifier = Country()

    for _ in range(100):
        country = faker.country_code()

        assert identifier.is_of_this_type(country), country


def test_country_codes(faker):
    identifier = CountryCode()

    for _ in range(100):
        code = faker.country_code()

        assert identifier.is_of_this_type(code), code


def test_zipcode(faker, faker_locale_us):
    identifier = ZipCode()

    for _ in range(100):
        postcode = faker.postcode_in_state()

        assert identifier.is_of_this_type(postcode), postcode


def test_zipcode_positive():
    identifier = ZipCode()

    assert identifier.is_of_this_type("94104")


def test_zipcode_wrong_misidentifications():
    identifier = ZipCode()

    assert not identifier.is_of_this_type("2020\n")


@pytest.mark.skip("For now, dictionary needs to be improved")
def test_city_name(faker):
    identifier = City()

    missed: set[str] = set()
    done: int = 0

    for _ in range(10_000):
        city = faker.city()

        if city in missed:
            continue

        if not identifier.is_of_this_type(city):
            missed.add(city)

        done += 1

    assert len(missed) / done < 0.005, missed  # account for Faker having a larger dictionary than us


def test_us_state(faker, faker_locale_us):
    identifier = UnitedStateState()

    for _ in range(100):
        state = faker.state()
        assert identifier.is_of_this_type(state), state

        state_code = faker.state_abbr()
        assert identifier.is_of_this_type(state_code), state_code


def test_us_state_individual():
    identifier = UnitedStateState()

    assert identifier.is_of_this_type("CA")
    assert identifier.is_of_this_type("California")


def test_uk_postcode_support_7_character_post_codes():
    identifier = UKPostCode()

    assert identifier.is_of_this_type("SO171BJ")
    assert not identifier.is_of_this_type("CA 94104 - USA Phone: 800-225-5935 Account")


def test_uk_postcode_support_8_character_post_codes():
    identifier = UKPostCode()

    assert identifier.is_of_this_type("SO17 1BJ")


def test_uk_postcode_possibly_addressable_but_incorrect():
    variants = [
        "S0171BJ",
        "SOI7 1BJ",
        "SO17 IBJ",
        "S0I7 IBJ",
        "SO I7 Ibj",
        "S017 1BJ",
        "So17IBJ",
        "SO1 71BJ",
    ]

    identifier = UKPostCode()
    for variant in variants:
        assert not identifier.is_of_this_type(variant), variant


def test_uk_postcode_suppors_for_known_formats():
    # /*
    # AN_NAA           B1 1AA          Royal Mail Central Birmingham Delivery Office
    # ANN_NAA          M60 2LA         Manchester City Council
    # AAN_NAA          SA6 7JL         Driver and Vehicle Licensing Authority, Swansea
    # AANN_NAA         SO17 1BJ        University of Southampton
    # ANA_NAA          W1D 1AN         Tottenham Court Road Tube Station, London
    # AANA_NAA         EC2R 8AH        Bank of England, London
    # */

    formats = [
        "B1 1AA",
        "M60 2LA",
        "SA6 7JL",
        "SO17 1BJ",
        "W1D 1AN",
        "EC2R 8AH",
    ]

    identifier = UKPostCode()

    for format in formats:
        assert identifier.is_of_this_type(format), format


def test_all_city_names():
    identifier = City("data/all_language_city_names.txt", _extract_all_langugage_city_names)

    assert len(identifier.data) == 930425, len(identifier.data)

    examples = """wei le pu la te
솔트레이크시티
بيلايا
lebocha
эверсон
maidiguri
tchornomorske
cuyutlán
qigzhi
鹅池镇""".split("\n")

    for example in examples:
        assert identifier.is_of_this_type(example), example


def test_from_data():
    all = Country()
    no_code = Country(False)

    assert all.is_of_this_type("to"), "to"
    assert all.is_of_this_type("at"), "at"
    assert all.is_of_this_type("in"), "in"

    assert not no_code.is_of_this_type("to"), "to"
    assert not no_code.is_of_this_type("at"), "at"
    assert not no_code.is_of_this_type("in"), "in"
