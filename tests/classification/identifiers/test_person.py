import pytest

from risk_assessment.classification.identifiers import Job, Name, Person, Surname


def test_name(faker):
    identifier = Name()

    for _ in range(100):
        name = faker.first_name()

        assert identifier.is_of_this_type(name), name


@pytest.mark.xfail(reason="Should be fixed after POS check")
def test_surname_specific():
    identifier = Surname()
    assert not identifier.is_of_this_type("voter"), "voter"
    assert not identifier.is_of_this_type("number"), "number"


def test_surname(faker):
    identifier = Surname()

    for _ in range(100):
        name = faker.last_name()

        assert identifier.is_of_this_type(name), name


def test_person_name(faker):
    identifier = Person()

    for _ in range(100):
        name = faker.name()

        assert identifier.is_of_this_type(name), name


def test_person_job(faker):
    identifier = Job()

    for _ in range(100):
        job = faker.job()

        assert identifier.is_of_this_type(job), job


def test_names_japanese():
    identifier = Name(
        female="data/ja/female_firstname.csv",
        male="data/ja/male_firstname.csv",
    )

    examples = """優菜
真緒
Manami
匠
ゆうこ
ゆうこ
たつや
Kaori
明子
Mika""".split()

    for example in examples:
        assert identifier.is_of_this_type(example), example


def test_japanese_surname():
    identifier = Surname(
        data_file="data/ja/surnames.csv",
    )

    examples = """たかぎ
まつもと
Murata
おかもと
ふじい
三浦
川島
まつだ
Watanabe
Ōnishi""".split()

    for example in examples:
        assert identifier.is_of_this_type(example), example


def test_personr_name_japanese():
    identifier = Person(
        name=Name(
            female="data/ja/female_firstname.csv",
            male="data/ja/male_firstname.csv",
        ),
        surname=Surname(
            data_file="data/ja/surnames.csv",
        ),
    )

    assert identifier.is_of_this_type("Watanabe 匠")
