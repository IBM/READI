from risk_assessment.masking.actions import (
    format_preserving_redact,
    redact_factory,
    redact_size_preserving,
    tagging_factory,
    tagging_with_hash,
)


def test_tagging():
    assert tagging_with_hash("person", "FOO") != "FOO"


def test_format_preserving_redact():
    assert format_preserving_redact("FOO", "BAR") != "BAR"

    assert len(format_preserving_redact("FOO", "BAR")) == len("BAR")
    assert format_preserving_redact("WHATEVER", "192.168.1.1") == "XXX.XXX.X.X"


def test_redact_size_preserving():
    assert redact_size_preserving("FOO", "THIS IS LONG") == "X" * len("THIS IS LONG")


def test_tagging_sequential():
    tagging = tagging_factory()

    assert tagging("foo", "BAR") == tagging("foo", "BAR")
    assert tagging("fooooo", "BAR") == tagging("fooooo", "BAR")
    assert tagging("foo", "BAR") != tagging("fooooo", "BAR")


def test_redaction():
    assert redact_factory()("", "VALUE") == "XXX"
    assert redact_factory(size=1)("", "VALUE") == "X"
    assert redact_factory(symbol="Y", size=5)("", "VALUE") == "YYYYY"
