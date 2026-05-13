from risk_assessment.classification.identifiers import MyNumberJapan


def test_positive():
    identifier = MyNumberJapan()

    assert identifier.is_of_this_type("3234,5678,9012"), "3234,5678,9012"
    assert identifier.is_of_this_type("3234 5678 9012"), "3234 5678 9012"


def test_negative():
    identifier = MyNumberJapan()

    assert not identifier.is_of_this_type("1234,5678,9012"), "1234,5678,9012"
    assert not identifier.is_of_this_type("1234,5678,901"), "1234,5678,901"
    assert not identifier.is_of_this_type("1234,5678,901234"), "1234,5678,901234"
