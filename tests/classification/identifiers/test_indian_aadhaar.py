from risk_assessment.classification.identifiers import AadhaarNumber


def test_positive():
    identifier = AadhaarNumber()

    assert identifier.is_of_this_type("2234 5678 9123"), "2234 5678 9123"
    assert identifier.is_of_this_type("223456789123"), "223456789123"


def test_negative():
    identifier = AadhaarNumber()

    assert not identifier.is_of_this_type("023456789123"), "023456789123"
    assert not identifier.is_of_this_type("1234 5678 9123"), "1234 5678 9123"
    assert not identifier.is_of_this_type("1234 5678 91239123"), "1234 5678 91239123"
