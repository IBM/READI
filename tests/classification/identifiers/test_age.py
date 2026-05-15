from random import randrange

from risk_assessment.classification.identifiers import Age, AgeImproved


def test_valid_age():
    identifier = Age()

    for _ in range(100):
        age_in_number = randrange(18, 90)
        assert identifier.is_of_this_type(str(age_in_number))


def test_invalid(faker):
    identifier = Age()

    for _ in range(50):
        assert not identifier.is_of_this_type(faker.email())
        assert not identifier.is_of_this_type(faker.iban())
        assert not identifier.is_of_this_type(faker.credit_card_number())


def test_is_of_this_type_valid() -> None:
    patterns: list[str] = [
        "9 years old",
        "9 YEARS OLD",
        "19 years old",
        "19-years-old",
        "19-year-old",
        "6 months old",
        "6-months old",
        "6-months-old",
        "22-weeks-old",
        "at age 6",
        "at age 6 and 1/2",
        "nine years old",
        "ninety five years old",
        "ninety-five years old",
        "twenty two yrs old",
        "37 yr old",
        "37 yr. old",
        "63 yrs. old",
        "66 yo",
        "66 y/o",
        "DOB: 1945",
        "DOB: 01-12-1945",
        "DOB 01-12-1945",
        "42 yrs. male",
        "42yrs. male",
        "42yrs.  male",
        "42 yrs. female",
        "DOB:  12/11/1925",
        "54 yrs. old",
        "16 y/o female",
        "16y/o female",
        "4 YRS 10/12 MO",
        "Date of Birth: 1981",
        "Date of Birth: 01/05/1981",
        "at the age of 93",
        "on his ninety third birthday",
        "on his fifty three birthday",
        "on her ninety third birthday",
        "on his ninety-third birthday",
        "AGE: 36",
        "26 Yrs man",
        "67yo female",
        "nine-years-old",
        "4 1/2 yo",
        "died age 88",
        "died of leukemia at age of 7",
        # "passed away from leukemia at age 7",
        "age 7",
        # "passed away at age 7",
        "died of Alzheimer's at 90",
        "died 91-old age",
    ]

    identifier = AgeImproved()

    for pattern in patterns:
        assert identifier.is_of_this_type(pattern), pattern


def test_is_of_this_type_invalid() -> None:
    patterns = ["9 years", "9 years ago"]

    identifier = AgeImproved()

    for pattern in patterns:
        assert not identifier.is_of_this_type(pattern), pattern


def test_negative_examples() -> None:
    identifier = AgeImproved()

    assert not identifier.is_of_this_type("DOB 1919-12-29, first name Alison.")
