from risk_assessment.classification.identifiers import JapanBankAccountNumber


def test_japanese_bank_account_number():
    identifier = JapanBankAccountNumber()

    examples: list[str] = [
        "12345671234-123",
        "123456781234-123",
        "123456781234 123",
        "123456781234123",
    ]

    for example in examples:
        assert identifier.is_of_this_type(example), example

    negative_examples: list[str] = [
        "garbage not valid",
        "12345678901234567890",
    ]

    for negative in negative_examples:
        assert not identifier.is_of_this_type(negative), negative
