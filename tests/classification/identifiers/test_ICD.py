from risk_assessment.classification.identifiers import ICDv9, ICDv10, ICDv11


def test_icdv9():
    identifier = ICDv9()

    assert identifier.is_of_this_type("004.8"), "004.8"

    assert not identifier.is_of_this_type("Staph Food Poisoning"), "Staph Food Poisoning"
    assert not identifier.is_of_this_type("Staph Food Poisoning".lower()), "Staph Food Poisoning".lower()
    assert not identifier.is_of_this_type("Staphylococcal Food Poisoning"), "Staphylococcal Food Poisoning"


def test_icdv9_with_terms():
    identifier = ICDv9(with_terms=True)

    assert identifier.is_of_this_type("004.8"), "004.8"

    assert identifier.is_of_this_type("Staph Food Poisoning"), "Staph Food Poisoning"
    assert identifier.is_of_this_type("Staph Food Poisoning".lower()), "Staph Food Poisoning".lower()
    assert identifier.is_of_this_type("Staphylococcal Food Poisoning"), "Staphylococcal Food Poisoning"


def test_icdv10():
    identifier = ICDv10()

    assert identifier.is_of_this_type("A01.0"), "A01.0"

    assert not identifier.is_of_this_type("Typhoid Fever"), "Typhoid Fever"
    assert not identifier.is_of_this_type("Typhoid Fever".lower()), "Typhoid Fever".lower()


def test_icdv10_with_term():
    identifier = ICDv10(with_terms=True)

    assert identifier.is_of_this_type("A01.0"), "A01.0"

    assert identifier.is_of_this_type("Typhoid Fever"), "Typhoid Fever"
    assert identifier.is_of_this_type("Typhoid Fever".lower()), "Typhoid Fever".lower()


def test_from_synthetic():
    data = """
244.9
250.00
272.4
311
401.1
401.9
427.31
530.81
V58.69
V70.0
"""

    identifier = ICDv9()

    for entry in data.strip().split():
        assert identifier.is_of_this_type(entry), entry


def test_valid_icd11():
    identifier = ICDv11()

    data = """GA13
LC0Y
2B02
SF02
SH7Z
LB5Y
EL1Y
EB42
LD27"""

    for entry in data.strip().split():
        assert identifier.is_of_this_type(entry)

    identifier_with_terms = ICDv11(with_terms=True)

    data_terms = """Ischaemic cardiomyopathy
Disorders with hearing impairment, unspecified
Certain current complications following acute myocardial infarction
Other specified strangury disorders (TM1)
Lyme borreliosis
Spontaneous palpitation disorder (TM1)
Cold pattern (TM1)
Hypoparathyroidism
Cutaneous involvement by other specified infection or infestation"""

    for entry in data_terms.strip().split("\n"):
        assert identifier_with_terms.is_of_this_type(entry)
