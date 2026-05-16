import pytest

from risk_assessment.classification.identifiers import CreditCard


@pytest.mark.skip("needs to verify all types")
def test_random_faker(faker):
    identifer = CreditCard()

    for _ in range(100):
        credit_card = faker.credit_card_number()

        assert identifer.is_of_this_type(credit_card)


@pytest.mark.skip("needs to verify all types")
def test_random_by_type(faker):
    identifier = CreditCard()

    for cc_type in [
        "amex",
        "diners",
        "discover",
        "jcb",
        "jcb15",
        "jcb16",
        "maestro",
        "mastercard",
        "visa",
        "visa13",
        "visa16",
        "visa19",
    ]:
        for _ in range(100):
            credit_card_number = faker.credit_card_number(cc_type)

            assert identifier.is_of_this_type(credit_card_number), f"{cc_type}: {credit_card_number}"


def test_AMEX(faker):
    identifier = CreditCard()
    assert identifier.is_of_this_type("370000992821860")

    for _ in range(100):
        ccn = faker.credit_card_number("amex")
        assert identifier.is_of_this_type(ccn), ccn


def test_DC(faker):
    identifier = CreditCard()

    assert identifier.is_of_this_type("30000099611752")
    for _ in range(100):
        ccn = faker.credit_card_number("diners")
        assert identifier.is_of_this_type(ccn), ccn


def test_DISC(faker):
    identifier = CreditCard()

    assert identifier.is_of_this_type("6011009285752817")
    assert identifier.is_of_this_type("6560487647593829")

    for _ in range(100):
        ccn = faker.credit_card_number("discover")
        assert identifier.is_of_this_type(ccn), ccn


def test_JBC(faker):
    identifier = CreditCard()

    for _ in range(100):
        ccn = faker.credit_card_number("jcb")
        assert identifier.is_of_this_type(ccn), ccn


def test_MasterCard(faker):
    identifier = CreditCard()

    assert identifier.is_of_this_type("5500009337062017")

    for _ in range(100):
        ccn = faker.credit_card_number("mastercard")
        assert identifier.is_of_this_type(ccn), ccn


def test_VISA(faker):
    identifier = CreditCard()

    assert identifier.is_of_this_type("4111 1197 6237 8756")
    assert identifier.is_of_this_type("4111-1197-6237-8756")

    for _ in range(100):
        ccn = faker.credit_card_number("visa")
        assert identifier.is_of_this_type(ccn), ccn


def test_negatives():
    identifier = CreditCard()

    assert not identifier.is_of_this_type("fjadlsjfal;sf")
    assert not identifier.is_of_this_type("1234567890")
