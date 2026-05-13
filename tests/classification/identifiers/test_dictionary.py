from random import choice

from risk_assessment.classification.identifiers import DictionaryIdentifier


def test_caseless(faker):
    data = [faker.job() for _ in range(50)]

    job_identifier = DictionaryIdentifier("JOB", data, False)

    for _ in range(100):
        assert job_identifier.is_of_this_type(choice(data))


def test_casefull(faker):
    data = [faker.job() for _ in range(50)]

    job_identifier = DictionaryIdentifier("JOB", data, True)

    for _ in range(100):
        value: str = choice(data)
        assert job_identifier.is_of_this_type(value)
        assert not job_identifier.is_of_this_type(value.upper())


def test_negative(faker):
    data = [faker.job() for _ in range(50)]

    job_identifier = DictionaryIdentifier("JOB", data, True)

    for _ in range(100):
        assert not job_identifier.is_of_this_type(faker.email())
