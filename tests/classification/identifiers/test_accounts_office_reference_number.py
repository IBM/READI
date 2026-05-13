from risk_assessment.classification.identifiers import AccountsOfficeReferenceNumber


def test_basic_validation():
    identifier = AccountsOfficeReferenceNumber()

    for valid in [
        "123PA12345678",
        "123PA1234567X",
        "123PA123456781511",
    ]:
        assert identifier.is_of_this_type(valid), valid

    for invalid in [
        "12312313120938091",
        "dfalksjflkajslkfjal123PA123456781522",
    ]:
        assert not identifier.is_of_this_type(invalid), invalid
