from risk_assessment.classification.identifiers import CODEN, ISBN, ISSN


def test_isbn_10(faker):
    identifier = ISBN()

    for _ in range(100):
        isbn = faker.isbn10()
        assert identifier.is_of_this_type(isbn), isbn


def test_isbn_13(faker):
    identifier = ISBN()

    for _ in range(100):
        isbn = faker.isbn13()
        assert identifier.is_of_this_type(isbn), isbn


def test_isbn_wiki():
    identifier = ISBN()

    assert identifier.is_of_this_type("978-0-306-40615-7")
    assert identifier.is_of_this_type("0-306-40615-2")


def test_isbn_debug():
    identifier = ISBN()

    assert identifier.is_of_this_type("0-15-781565-X")


def test_CODEN():
    identifier = CODEN()

    assert identifier.is_of_this_type("NATUAS")
    assert identifier.is_of_this_type("  NATUAS   ")
    assert identifier.is_of_this_type("TEREAU")
    assert identifier.is_of_this_type("66HYAL")
    assert identifier.is_of_this_type("69ACLK")
    assert identifier.is_of_this_type("USXXDP")
    assert identifier.is_of_this_type("GWXXBX")


def test_ISSN():
    identifier = ISSN()

    assert identifier.is_of_this_type("2049-3630")
