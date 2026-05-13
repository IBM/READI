from risk_assessment.classification.identifiers import RRNSouthKorea


def test_positive():
    identifier = RRNSouthKorea()

    assert identifier.is_of_this_type("820701-2409181"), "820701-2409181"


def test_negative():
    identifier = RRNSouthKorea()

    assert not identifier.is_of_this_type("202701-2409183"), "202701-2409184"
    assert not identifier.is_of_this_type("202701-24091831234"), "202701-24091841234"
