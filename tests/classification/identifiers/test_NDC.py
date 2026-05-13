from risk_assessment.classification.identifiers import NDC


def test_NDC():
    identifier = NDC()

    assert identifier.is_of_this_type("Drotrecogin alfa")
    assert identifier.is_of_this_type("Drotrecogin ALFA")
