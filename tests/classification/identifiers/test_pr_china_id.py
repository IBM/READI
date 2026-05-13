from risk_assessment.classification.identifiers import PRChinaID


def test_positive():
    identifier = PRChinaID()

    assert identifier.is_of_this_type("34262219840209049X"), "34262219840209049X"
    assert identifier.is_of_this_type("34262219840209049x"), "34262219840209049x"


def test_negative():
    identifier = PRChinaID()

    assert not identifier.is_of_this_type("63280119790817003"), "63280119790817003"
    assert not identifier.is_of_this_type("63280119790817003x"), "63280119790817003x"
    assert not identifier.is_of_this_type("63280119790817003c"), "63280119790817003c"
