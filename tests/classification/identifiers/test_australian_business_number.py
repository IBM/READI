from risk_assessment.classification.identifiers import AustralianBusinessNumber


def test_valid_number():
    identifier = AustralianBusinessNumber()

    for valid in [
        "51 824 753 556",
        "51824753556",
    ]:
        assert identifier.is_of_this_type(valid), valid

    for invalid in [
        "alksdfjalksf",
        "51824753557",
    ]:
        assert not identifier.is_of_this_type(invalid), invalid
