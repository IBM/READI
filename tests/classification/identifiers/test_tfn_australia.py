from risk_assessment.classification.identifiers import TFNAustralia


def test_positive():
    identifier = TFNAustralia()

    assert identifier.is_of_this_type("123456782"), "123456782"
    assert identifier.is_of_this_type("876543210"), "876543210"


def test_negative():
    identifier = TFNAustralia()

    assert not identifier.is_of_this_type("123456783"), "123456783"
    assert not identifier.is_of_this_type("12345678s"), "12345678s"
    assert not identifier.is_of_this_type("8765432100"), "8765432100"
    # assert not identifier.is_of_this_type("500676400"), "500676400"
