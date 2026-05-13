from risk_assessment.classification.identifiers import IMEI


def test_positive():
    identifier = IMEI()

    assert identifier.is_of_this_type("012837001234567"), "012837001234567"


def test_negative():
    identifier = IMEI()

    assert not identifier.is_of_this_type("012837001234561"), "012837001234561"  # invalid check digit
    assert not identifier.is_of_this_type("12312313"), "12312313"  # short
    assert not identifier.is_of_this_type("001013001a34567"), "001013001a34567"  # contains letters
    assert not identifier.is_of_this_type("12345678901234567")  # too long
