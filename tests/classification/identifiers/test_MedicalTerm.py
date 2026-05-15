import pytest

from risk_assessment.classification.identifiers import MedicalTerm


@pytest.mark.skip("Missing UMLS data files")
def test_positive():
    identifier = MedicalTerm(umls_only=False)

    assert identifier.is_of_this_type("COVID-19"), "COVID-19"
    assert identifier.is_of_this_type("NSAIDS"), "NSAIDS"
    assert identifier.is_of_this_type("BPH"), "BPH"
    assert identifier.is_of_this_type("CPAP"), "CPAP"
    assert identifier.is_of_this_type("Staph Food Poisoning"), "Staph Food Poisoning"
    assert identifier.is_of_this_type("Staph Food Poisoning".lower()), "Staph Food Poisoning".lower()
    assert identifier.is_of_this_type("Staphylococcal Food Poisoning"), "Staphylococcal Food Poisoning"

    assert identifier.is_of_this_type("A01.0"), "A01.0"
    assert identifier.is_of_this_type("Typhoid Fever"), "Typhoid Fever"
    assert identifier.is_of_this_type("Typhoid Fever".lower()), "Typhoid Fever".lower()


@pytest.mark.skip("Missing UMLS data files")
def test_positive_umls_only():
    identifier = MedicalTerm(umls_only=True)

    assert identifier.is_of_this_type("COVID-19"), "COVID-19"
    assert identifier.is_of_this_type("NSAIDS"), "NSAIDS"
    assert identifier.is_of_this_type("BPH"), "BPH"
    assert identifier.is_of_this_type("CPAP"), "CPAP"
    assert identifier.is_of_this_type("Poisoning"), "Poisoning"
    assert identifier.is_of_this_type("Fever"), "Fever"


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

    identifier = MedicalTerm(umls_only=False)

    for entry in data.strip().split():
        assert identifier.is_of_this_type(entry), entry
