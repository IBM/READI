from risk_assessment.classification.identifiers import TINGermany


def test_positive():
    identifier = TINGermany()

    assert identifier.is_of_this_type("12 235 678 905"), "12 345 678 905"
    assert identifier.is_of_this_type("12235678905"), "12235678905"
    assert identifier.is_of_this_type("96480255173"), "96480255173"


def test_negative():
    identifier = TINGermany()

    assert not identifier.is_of_this_type("12 345 678 901"), "12 345 678 9011"
    assert not identifier.is_of_this_type("06480255173"), "06480255173"
    assert not identifier.is_of_this_type("12 345 678 903"), "12 345 678 903"
    assert not identifier.is_of_this_type("12 345 678 903903"), "12 345 678 903903"
