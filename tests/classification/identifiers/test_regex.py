import re

from risk_assessment.classification.identifiers import RegexIdentifier, RegexIdentifierWithSpan


def test_regex():
    identifier = RegexIdentifier(
        "FOO",
        [
            re.compile(r"12345"),
        ],
    )

    assert identifier.is_of_this_type("12345")
    assert not identifier.is_of_this_type("FOO BAR")

    identifier = RegexIdentifier("FOO", [re.compile(r"1234[5]+67")])

    assert identifier.is_of_this_type("1234567")
    assert identifier.is_of_this_type("12345567")
    assert identifier.is_of_this_type("12345555555567")

    assert not identifier.is_of_this_type("123467")


def test_regex_with_span():
    identifier = RegexIdentifierWithSpan(
        "FOO",
        [
            re.compile(r"FOO (12345)"),
        ],
    )

    assert identifier.is_of_this_type("FOO 12345")
    assert not identifier.is_of_this_type("FOO BAR")

    match = identifier.is_of_this_type_with_span("FOO 12345")

    assert match[0]
    assert match[1] is not None
    assert not identifier.is_of_this_type_with_span("FOO BAR")[0]
    assert identifier.is_of_this_type_with_span("FOO BAR")[1] is None


def test_from_rwd():
    identifier = RegexIdentifierWithSpan(
        "VoterID",
        [
            re.compile(r"voter\s+ID\s+number\s+(?:is\s+)?(\d{9,})", re.IGNORECASE),
        ],
    )

    text = "voter ID number 123456789"

    is_match, span = identifier.is_of_this_type_with_span(text)

    assert is_match
    assert span is not None
    assert text[span[0] : span[1]] == "123456789"

    text2 = "voter ID number is 123456789"

    is_match, span = identifier.is_of_this_type_with_span(text2)

    assert is_match
    assert span is not None
    assert text2[span[0] : span[1]] == "123456789"
