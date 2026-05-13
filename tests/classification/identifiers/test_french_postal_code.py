from risk_assessment.classification.identifiers import FrenchPostalCode


def test_french_postal_code() -> None:
    identifier = FrenchPostalCode()

    assert identifier.is_of_this_type("64205"), "Biarritz"
    assert identifier.is_of_this_type("43000"), "Aiguilhe"

    assert not identifier.is_of_this_type("642050"), "6 digits"
    assert not identifier.is_of_this_type("asfas"), "letters"
