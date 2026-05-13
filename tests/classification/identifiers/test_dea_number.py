from risk_assessment.classification.identifiers.healthcare import DEANumber


def test_from_wiki() -> None:
    identifier = DEANumber()

    assert identifier.is_of_this_type("F91234563")
    assert identifier.is_of_this_type("F91234563-001AB")
