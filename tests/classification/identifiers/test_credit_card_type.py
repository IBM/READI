from risk_assessment.classification.identifiers import CreditCardType


def test_is_of_this_type():
    identifier = CreditCardType()

    assert identifier.is_of_this_type("VISA")
    assert identifier.is_of_this_type("vISa")

    assert not identifier.is_of_this_type("SOMETHING TOTALLY DIFFERENT")
