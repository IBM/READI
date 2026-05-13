from risk_assessment.classification.identifiers import SSN


def test_positive():
    identifier = SSN()

    assert identifier.is_of_this_type("123-12-1234"), "123-12-1234"


def test_negative():
    identifier = SSN()

    assert not identifier.is_of_this_type("1234-12-1234"), "1234-12-1234"
    assert not identifier.is_of_this_type("12a-12-1234"), "12a-12-1234"
    assert not identifier.is_of_this_type("123-123-1234"), "123-123-1234"
    assert not identifier.is_of_this_type("123-12-12345"), "123-12-12345"
    assert not identifier.is_of_this_type("123-12-a234"), "123-12-a234"
    assert not identifier.is_of_this_type("123-1b-1234"), "123-1b-1234"


def test_random(faker):
    identifier = SSN()

    for _ in range(100):
        ssn = faker.ssn()

        assert identifier.is_of_this_type(ssn), ssn
