from faker import Faker

from risk_assessment.classification.identifiers import DNISpain, NIESpain, NIFSpain


def test_DNI():
    identifier = DNISpain()

    assert identifier.is_of_this_type("12345679S")

    assert not identifier.is_of_this_type("12345679E")
    assert not identifier.is_of_this_type("12345679S1111S")


def test_NIE(faker: Faker) -> None:
    identifier = NIESpain()

    assert identifier.is_of_this_type("X1234567L")
    assert identifier.is_of_this_type("Y1234567X")
    assert identifier.is_of_this_type("Z1234567R")

    assert not identifier.is_of_this_type("12345679S")
    assert not identifier.is_of_this_type("12345679E")
    assert not identifier.is_of_this_type("12345679S1111S")


def test_NIF(faker: Faker) -> None:
    identifier = NIFSpain()

    assert identifier.is_of_this_type("12345679S")  # DNI
    assert identifier.is_of_this_type("X1234567L")  # NIE

    assert identifier.is_of_this_type("L1234567D")  # NIF person
    assert identifier.is_of_this_type("F12345674")  # NIF org w number
    assert identifier.is_of_this_type("P1234567D")  # NIF org w letter
