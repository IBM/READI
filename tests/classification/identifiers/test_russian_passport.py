from risk_assessment.classification.identifiers import RussianInternalPassport, RussianInternationalPassport


def test_positive_internal():
    identifier = RussianInternalPassport()

    assert identifier.is_of_this_type("5341456789"), "5341456789"
    assert identifier.is_of_this_type("5341 456789"), "5341 456789"
    assert identifier.is_of_this_type("53 41 456789"), "53 41 456789"


def test_positive_international():
    identifier = RussianInternationalPassport()

    assert identifier.is_of_this_type("72 1234567"), "72 1234567"
    assert identifier.is_of_this_type("721234567"), "721234567"


def test_negative_internal():
    identifier = RussianInternalPassport()

    assert not identifier.is_of_this_type("02 41 456789"), "02 41 456789"
    assert not identifier.is_of_this_type("0241 456789"), "0241 456789"

    assert not identifier.is_of_this_type("2 41 456789"), "2 41 456789"
    assert not identifier.is_of_this_type("2 41 456789222"), "2 41 456789222"


def test_negative_internaitional():
    identifier = RussianInternationalPassport()

    assert not identifier.is_of_this_type("21234567"), "21234567"
    assert not identifier.is_of_this_type("21234567234567"), "21234567234567"
