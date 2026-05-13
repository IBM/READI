from risk_assessment.classification.identifiers import LuhnIdentifier


class DummyLuhn(LuhnIdentifier):
    def is_of_this_type(self, text: str) -> bool:
        return False


def test_valid_luhn():
    dummy = DummyLuhn()

    assert dummy.check_luhn(str(79927398713))


def test_invalid_luhn():
    dummy = DummyLuhn()

    assert not dummy.check_luhn("123123456\n")


def test_random_cc(faker):
    dummy = DummyLuhn()

    for _ in range(100):
        ccn = faker.credit_card_number()

        assert dummy.check_luhn(ccn), ccn
