from risk_assessment.classification.identifiers import NIRFrance


def test_positive():
    identifier = NIRFrance()

    assert identifier.is_of_this_type("279058496820192"), "279058496820192"
    assert identifier.is_of_this_type("2 79 05 84 968 201 92"), "2 79 05 84 968 201 92"
    assert identifier.is_of_this_type("279052A96820156"), "279052A96820156"


def test_negative():
    identifier = NIRFrance()

    assert not identifier.is_of_this_type("2 79 05 84 968 201 91"), "2 79 05 84 968 201 91"
    assert not identifier.is_of_this_type("379058496820192"), "379058496820192"
    assert not identifier.is_of_this_type("279053A96820192"), "279053A96820192"
    assert not identifier.is_of_this_type("279053D96820192"), "279053A96820192"
    assert not identifier.is_of_this_type("279053D9682019292"), "279053A9682019292"
