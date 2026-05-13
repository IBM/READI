from risk_assessment.classification.identifiers.healthcare.medicare_beneficiary_identifier import (
    MedicareBeneficiaryIdentifier,
)


def test_examples() -> None:
    identifier = MedicareBeneficiaryIdentifier()

    assert identifier.is_of_this_type("1EG4-TE5-MK73")
