from pathlib import Path

from risk_assessment.classification.identifiers.phone import Phone, PhoneNumber


def test_us_phone():
    examples = [
        "(123)-456-7890",
    ]

    identifier = Phone()

    for example in examples:
        assert identifier.is_of_this_type(example), example


def test_phone_examples_from_ITU_T_E_123():
    valid_numbers = [
        "(607) 123 4567",
        "+22 607 123 4567",
    ]

    identifier = PhoneNumber()

    for number in valid_numbers:
        assert identifier.is_of_this_type(number), number


def test_general_phone():
    examples = [
        # "(123)-456-7890",
        "+353-0876653255",
        "00353-0876653255",
        "+353-(087)6653255",
        "0044-(087)6653255",
        "0044 (087)6653255",
        "0044 0876653255",
        "Pgr: 123-45678",
        "Ph: 123-45678",
        "Ph: (781) 555-1234",
        "(781) 555-1234",
        "(781)555-1234",
        "Phone: (781) 555-1234",
        "phone: (781) 555-1234",
        "Fax: (781) 555-1234",
        "Phone (781) 555-1234",
        "Fax (781) 555-1234",
        "Phone #(781) 555-1234",
        "phone #(781) 555-1234",
        "phone #617-333-5555",
        "617-333-5555",
        "3471234567",  # New York
        "2601234555",  # Indiana
        "Contact: (781) 555-1234",
    ]

    identifier = PhoneNumber()

    for example in examples:
        assert identifier.is_of_this_type(example), example


def test_invalid_phone():
    examples = [
        "873320071105095646",
        "140 39-150",
        "+44",
        "+44-123444a122",
        "33917",
        "260123455a",
    ]

    identifier = PhoneNumber()

    for example in examples:
        assert not identifier.is_of_this_type(example), example


def test_if_the_incorrect_detections_are_fixed():
    invalid_phones = [
        "105-150",
        "400-500",
        "2001 1126302",
    ]

    identifier = PhoneNumber()

    for number in invalid_phones:
        assert not identifier.is_of_this_type(number), number


def test_extract_data_correctly():
    identifier = PhoneNumber()

    valid_numbers = [
        "+353-0876653255",
        "00353-0876653255",
        "+353-(087)6653255",
        "0044-(087)6653255",
        "0044 (087)6653255",
        "0044 0876653255",
        "Pgr: 123-45678",
        "Ph: 123-45678",
        "Ph: (781) 555-1234",
        "(781) 555-1234",
        "(781)555-1234",
        "Phone: (781) 555-1234",
        "phone: (781) 555-1234",
        "Fax: (781) 555-1234",
        "Phone (781) 555-1234",
        "Fax (781) 555-1234",
        "Phone #(781) 555-1234",
        "phone #(781) 555-1234",
        "phone #617-333-5555",
        "617-333-5555",
        "3471234567",  # New York
        "2601234555",  # Indiana
        "Contact: (781) 555-1234",
    ]

    validation_data = [
        "+353-0876653255",
        "00353-0876653255",
        "+353-(087)6653255",
        "0044-(087)6653255",
        "0044 (087)6653255",
        "0044 0876653255",
        "123-45678",
        "123-45678",
        "(781) 555-1234",
        "(781) 555-1234",
        "(781)555-1234",
        "(781) 555-1234",
        "(781) 555-1234",
        "(781) 555-1234",
        "(781) 555-1234",
        "(781) 555-1234",
        "(781) 555-1234",
        "(781) 555-1234",
        "617-333-5555",
        "617-333-5555",
        "3471234567",  # New York
        "2601234555",  # Indiana
        "(781) 555-1234",
    ]

    for number, validation in zip(valid_numbers, validation_data):
        is_match, span = identifier.is_of_this_type_with_span(number)

        assert is_match, number

        assert span is not None, number

        assert number[span[0] : span[0] + span[1]] == validation


def test_it_does_not_detect_wrong_formatted_numbers() -> None:
    identifier = PhoneNumber()

    invalid_numbers = [
        "873320071105095646",
        "140 39-150",
        "+44",
        "+44-123444a122",
        "33917",
        "260123455a",  # it contains letters
    ]

    for number in invalid_numbers:
        assert not identifier.is_of_this_type(number), number


def test_is_of_this_type():
    identifier = PhoneNumber()

    valid_numbers = [
        "+353-0876653255",
        "00353-0876653255",
        "+353-(087)6653255",
        "0044-(087)6653255",
        "0044 (087)6653255",
        "0044 0876653255",
        "Pgr: 123-45678",
        "Ph: 123-45678",
        "Ph: (781) 555-1234",
        "(781) 555-1234",
        "(781)555-1234",
        "Phone: (781) 555-1234",
        "phone: (781) 555-1234",
        "Fax: (781) 555-1234",
        "Phone (781) 555-1234",
        "Fax (781) 555-1234",
        "Phone #(781) 555-1234",
        "phone #(781) 555-1234",
        "phone #617-333-5555",
        "617-333-5555",
        "3471234567",  # New York
        "2601234555",  # Indiana
    ]

    for number in valid_numbers:
        assert identifier.is_of_this_type(number), number


def test_wrongly_identified_phone():
    incorrect_phones = [
        "1993.04.30",
        "12345678901234567890",
    ]

    identifier = PhoneNumber()

    for number in incorrect_phones:
        assert not identifier.is_of_this_type(number), number


def test_support_UK_numbers():
    valid_phones = [
        "020 76001818",
        "02076001818",
        "(+44)02076001818",
        "+442076001818",
    ]

    identifier = PhoneNumber()

    for number in valid_phones:
        assert identifier.is_of_this_type(number), number


def test_support_US_numbers():
    valid_phones = [
        "754-3010",  # Local
        "(541) 754-3010",  # Domestic
        "541-754-3010",  # International
        "+1-541-754-3010",  # International
        "1-541-754-3010",  # Dialed in the US
        "001-541-754-3010",  # Dialed from Germany
        "191 541 754 3010",  # Dialed from France
    ]

    identifier = PhoneNumber()

    for number in valid_phones:
        assert identifier.is_of_this_type(number), number


def test_support_weird_formats():
    supported_formats = [
        "+99(099)9999-9999",
        "0099(099)9999-9999",
        "+1.458.202.0462",
    ]

    identifier = PhoneNumber()

    for number in supported_formats:
        assert identifier.is_of_this_type(number), number


def test_common_patterns():
    numbers = [
        "Phone: 800-123-4567",
        "800-123-4567",
        "+34 123 12 34 56",
    ]

    identifier = PhoneNumber()

    for number in numbers:
        assert identifier.is_of_this_type(number), number


def test_from_dataset():
    number = PhoneNumber()

    numbers = [
        "+913115741270",
        "368-217-1505",
        "702-565-9662",
        "368-217-1505x3262",
        "702-565-9662 x421",
        "+44(0)909 879 0897",
        "305.271.3630",
    ]

    for n in numbers:
        assert number.is_of_this_type(n)


def test_from_dataset_ugly():
    identifier = Phone()

    file = Path(__file__).parent / "data" / "phone_numbers.txt"

    with file.open() as input:
        for id, number in enumerate(input.readlines()):
            assert identifier.is_of_this_type(number.strip()), f"{id} {number=}"
