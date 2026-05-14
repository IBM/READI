from risk_assessment.classification.unstructured import Entity, merge_overlapping


def test_only_one_type() -> None:
    before = [
        Entity(0, 10, "FOO", frozenset(["BAR"])),
        Entity(0, 20, "FOO", frozenset(["BAR"])),
        Entity(0, 30, "FOO", frozenset(["BAR"])),
        Entity(0, 40, "FOO", frozenset(["BAR"])),
    ]

    after = merge_overlapping(before)

    assert len(after) == 1
    assert after[0].start == 0
    assert after[0].end == 40


def test_more_than_one_type() -> None:
    before = [
        Entity(0, 10, "FOO", frozenset(["BAR"])),
        Entity(0, 20, "FOO", frozenset(["BAR"])),
        Entity(0, 30, "FOO", frozenset(["BAR"])),
        Entity(0, 40, "BAR", frozenset(["BAR"])),
        Entity(0, 10, "BAR", frozenset(["BAR"])),
        Entity(0, 20, "BAR", frozenset(["BAR"])),
        Entity(0, 30, "BAR", frozenset(["BAR"])),
        Entity(0, 40, "BAR", frozenset(["BAR"])),
    ]

    after = merge_overlapping(before)

    assert len(after) == 2
    bar = [e for e in after if e.entity_type == "BAR"][0]

    assert bar.start == 0
    assert bar.end == 40

    foo = [e for e in after if e.entity_type == "FOO"][0]

    assert foo.start == 0
    assert foo.end == 30


def test_not_overlapping() -> None:
    before = [
        Entity(0, 10, "BAR", frozenset(["BAR"])),
        Entity(20, 40, "BAR", frozenset(["BAR"])),
    ]

    after = merge_overlapping(before)

    assert len(after) == 2


def test_included() -> None:
    # Monday 5 Jan 2024 3:00PM vs 5 Jan 2024
    before = [
        Entity(0, 10, "BAR", frozenset(["BAR"])),
        Entity(5, 8, "BAR", frozenset(["BAR"])),
    ]

    after = merge_overlapping(before)

    assert len(after) == 1


def test_two_overlapping_groups() -> None:
    before = [
        Entity(0, 10, "BAR", frozenset(["BAR"])),
        Entity(0, 4, "BAR", frozenset(["BAR"])),
        Entity(20, 40, "BAR", frozenset(["BAR"])),
        Entity(20, 30, "BAR", frozenset(["BAR"])),
    ]

    after = merge_overlapping(before)

    assert len(after) == 2


def test_partial_overlapping_with_bleed() -> None:
    # Monday 5 Jan 2024 3:00PM
    # detected as:
    # Monday 5 Jan
    #        5 Jan 2024 3:PM
    before = [
        Entity(0, 10, "BAR", frozenset(["BAR"])),
        Entity(5, 20, "BAR", frozenset(["BAR"])),
    ]

    after = merge_overlapping(before)

    assert len(after) == 1
    assert after[0].start == 0
    assert after[0].end == 20
