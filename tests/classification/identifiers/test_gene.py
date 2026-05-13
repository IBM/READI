from risk_assessment.classification.identifiers import Gene


def test_Gene():
    identifier = Gene()

    assert identifier.is_of_this_type("A1BG")
    assert identifier.is_of_this_type("P04217")
    assert identifier.is_of_this_type("HGNC:5")
    assert not identifier.is_of_this_type("BBBAASDH")
