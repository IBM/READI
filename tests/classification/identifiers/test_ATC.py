from risk_assessment.classification.identifiers import ATC


def test_ATC():
    identifier = ATC()

    assert identifier.is_of_this_type("A04AA02")
    assert identifier.is_of_this_type("a02aa01")
