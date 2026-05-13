from risk_assessment.classification.identifiers import CFPBrazil


def test_positive():
    identifier = CFPBrazil()

    assert identifier.is_of_this_type("529.982.247-25"), "529.982.247-25"
    assert identifier.is_of_this_type("470.392.165-07"), "470.392.165-07"
    assert identifier.is_of_this_type("470392165-07"), "470392165-07"
    assert identifier.is_of_this_type("47039216507"), "47039216507"


def test_negative():
    identifier = CFPBrazil()
    assert not identifier.is_of_this_type("470.392.165-01"), "470.392.165-01"
    assert not identifier.is_of_this_type("4703921650"), "4703921650"
    assert not identifier.is_of_this_type("470.39216507"), "470.3921650"
    assert not identifier.is_of_this_type("47039216507777"), "47039216507777"
