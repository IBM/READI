from risk_assessment.classification.identifiers import ICDIndonesia


def test_positive():
    identifier = ICDIndonesia()

    # d{2}[01237]\d{3}[01234567]\d[01]\d{7}
    assert identifier.is_of_this_type("1030241708900001"), "1030241708900001"
    assert identifier.is_of_this_type("103024 570890 0001"), "103024 570890 0001"
    assert identifier.is_of_this_type("161004 040383 0016"), "161004 040383 0016"


def test_negative():
    identifier = ICDIndonesia()

    assert not identifier.is_of_this_type("103024 870890 0001"), "103024 870890 0001"
    assert not identifier.is_of_this_type("105024 870890 0001"), "105024 870890 0001"
    assert not identifier.is_of_this_type("105024870890000"), "105024870890000"
    assert not identifier.is_of_this_type("1050248708900000000"), "1050248708900000000"
