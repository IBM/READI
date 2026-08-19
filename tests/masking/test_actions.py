import re

import pandas as pd
import pytest

from risk_assessment.masking.actions import (
    InMemoryMappingStorage,
    format_preserving_redact,
    no_action,
    random_from_series_factory,
    redact_factory,
    redact_size_preserving,
    tagging_factory,
    tagging_with_hash,
)

# ---------------------------------------------------------------------------
# tagging_with_hash
# ---------------------------------------------------------------------------


def test_tagging_with_hash_differs_from_input():
    assert tagging_with_hash("Person", "John Doe") != "John Doe"


def test_tagging_with_hash_format():
    result = tagging_with_hash("Email", "user@example.com")
    # Format: TYPE-<5 hex chars>
    assert re.fullmatch(r"EMAIL-[0-9a-f]{5}", result)


def test_tagging_with_hash_is_deterministic():
    assert tagging_with_hash("SSN", "123-45-6789") == tagging_with_hash("SSN", "123-45-6789")


def test_tagging_with_hash_differs_for_different_inputs():
    assert tagging_with_hash("SSN", "123-45-6789") != tagging_with_hash("SSN", "999-00-0001")


def test_tagging_with_hash_uppercases_type():
    result = tagging_with_hash("email", "a@b.com")
    assert result.startswith("EMAIL-")


# ---------------------------------------------------------------------------
# format_preserving_redact
# ---------------------------------------------------------------------------


def test_format_preserving_redact_differs_from_input():
    assert format_preserving_redact("FOO", "BAR") != "BAR"


def test_format_preserving_redact_preserves_length():
    assert len(format_preserving_redact("FOO", "BAR")) == len("BAR")


def test_format_preserving_redact_ip_address():
    assert format_preserving_redact("IP", "192.168.1.1") == "XXX.XXX.X.X"


def test_format_preserving_redact_phone():
    assert format_preserving_redact("Phone", "+1 (800) 555-0100") == "+X (XXX) XXX-XXXX"


def test_format_preserving_redact_empty_string():
    assert format_preserving_redact("Any", "") == ""


def test_format_preserving_redact_only_punctuation():
    assert format_preserving_redact("Any", "---") == "---"


# ---------------------------------------------------------------------------
# redact_size_preserving
# ---------------------------------------------------------------------------


def test_redact_size_preserving_all_x():
    assert redact_size_preserving("FOO", "THIS IS LONG") == "X" * len("THIS IS LONG")


def test_redact_size_preserving_preserves_length():
    text = "hello world"
    result = redact_size_preserving("Any", text)
    assert len(result) == len(text)
    assert result == "X" * len(text)


def test_redact_size_preserving_empty():
    assert redact_size_preserving("Any", "") == ""


# ---------------------------------------------------------------------------
# redact_factory
# ---------------------------------------------------------------------------


def test_redact_factory_default():
    assert redact_factory()("", "VALUE") == "XXX"


def test_redact_factory_custom_size():
    assert redact_factory(size=1)("", "VALUE") == "X"
    assert redact_factory(size=10)("", "long text here") == "X" * 10


def test_redact_factory_custom_symbol():
    assert redact_factory(symbol="Y", size=5)("", "VALUE") == "YYYYY"


def test_redact_factory_ignores_input():
    redact = redact_factory(size=3)
    assert redact("Email", "short") == redact("Person", "a much longer string")


# ---------------------------------------------------------------------------
# tagging_factory / InMemoryMappingStorage
# ---------------------------------------------------------------------------


def test_tagging_factory_same_value_same_label():
    tagging = tagging_factory(InMemoryMappingStorage())
    assert tagging("Person", "John") == tagging("Person", "John")


def test_tagging_factory_different_values_different_labels():
    tagging = tagging_factory(InMemoryMappingStorage())
    assert tagging("Person", "John") != tagging("Person", "Jane")


def test_tagging_factory_same_value_different_types_different_labels():
    tagging = tagging_factory(InMemoryMappingStorage())
    assert tagging("Person", "Smith") != tagging("Organization", "Smith")


def test_tagging_factory_sequential_labels():
    storage = InMemoryMappingStorage()
    tagging = tagging_factory(storage)
    first = tagging("Email", "a@example.com")
    second = tagging("Email", "b@example.com")
    assert first == "EMAIL-1"
    assert second == "EMAIL-2"


def test_tagging_factory_label_uppercases_type():
    tagging = tagging_factory(InMemoryMappingStorage())
    label = tagging("email", "x@y.com")
    assert label.startswith("EMAIL-")


# ---------------------------------------------------------------------------
# no_action
# ---------------------------------------------------------------------------


def test_no_action_returns_first_argument():
    assert no_action("Person", "ignored") == "Person"


def test_no_action_empty_string():
    assert no_action("", "anything") == ""


# ---------------------------------------------------------------------------
# random_from_series_factory
# ---------------------------------------------------------------------------


def test_random_from_series_returns_value_from_pool():
    pool = pd.Series(["Alice", "Bob", "Carol"])
    action = random_from_series_factory(pool)
    for _ in range(50):
        assert action("Person", "John Doe") in {"Alice", "Bob", "Carol"}


def test_random_from_series_single_value_always_returns_it():
    action = random_from_series_factory(pd.Series(["Only"]))
    assert action("Person", "anyone") == "Only"
    assert action("Email", "test@test.com") == "Only"


def test_random_from_series_returns_string():
    action = random_from_series_factory(pd.Series([1, 2, 3]))
    result = action("Age", "25")
    assert isinstance(result, str)


def test_random_from_series_ignores_entity_type_and_text():
    pool = pd.Series(["X", "Y"])
    action = random_from_series_factory(pool)
    # Both type and text are ignored; only pool contents matter
    r1 = action("TypeA", "foo")
    r2 = action("TypeB", "bar")
    assert r1 in {"X", "Y"}
    assert r2 in {"X", "Y"}


def test_random_from_series_uses_full_pool():
    pool = pd.Series(["A", "B", "C", "D", "E"])
    action = random_from_series_factory(pool)
    seen = {action("T", "v") for _ in range(500)}
    assert seen == {"A", "B", "C", "D", "E"}


def test_random_from_series_raises_on_empty_pool():
    action = random_from_series_factory(pd.Series([], dtype=str))
    with pytest.raises(IndexError):
        action("Person", "John")
