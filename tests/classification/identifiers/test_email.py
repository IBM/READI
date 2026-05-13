from risk_assessment.classification.identifiers import Email


def test_is_of_this_type():
    identifier = Email()

    assert identifier.is_of_this_type("john@ie.ibm.com")
    assert identifier.is_of_this_type("santonat@ie.ibm.com")
    assert identifier.is_of_this_type("santonat_with_comment@ie.ibm.com")
    assert not identifier.is_of_this_type("somethin else")
    assert not identifier.is_of_this_type("Help@IBM")
