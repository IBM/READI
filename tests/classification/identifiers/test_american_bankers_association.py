from faker import Faker

from risk_assessment.classification.identifiers import AmericanBankersAssociationNumber


def test_with_faker(faker: Faker) -> None:
    identifier = AmericanBankersAssociationNumber()

    missed: set[str] = set()
    count: int = 0

    for _ in range(10_000):
        aba = faker.aba()

        if aba in missed:
            continue

        if not identifier.is_of_this_type(aba):
            missed.add(aba)

        count += 1

    assert len(missed) / count < 0.005, missed


def test_basic_validation():
    identifier = AmericanBankersAssociationNumber()

    for valid in [
        "031101266",
        "256075025",
        "111000025",
    ]:
        assert identifier.is_of_this_type(valid), valid

    for invalid in [
        "123u1382904q25",
        "adsfaklf",
        "12345678997654",
    ]:
        assert not identifier.is_of_this_type(invalid), invalid
