from risk_assessment.classification.identifiers import AustralianMedicareNumber


def test_AustralianMedicareNumber():
    identifier = AustralianMedicareNumber()

    assert not identifier.is_of_this_type("2123 45671 1"), "2123 45670 1"
    assert identifier.is_of_this_type("2123 45670 1"), "2123 45670 1"
