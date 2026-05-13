from risk_assessment.classification.identifiers import URI


def test_valid():
    valid_URI = [
        "www.google.com",
        "mail.google.com",
        "http://www.nba.com",
        "http://www.nba.co.uk",
        "https://www.nba.com",
        "http://www.nba.com/index.html",
        "http://www.nba.com/index.html?q=MichaelJordan",
        "http://www.nba.com:8080",
        "http://22.33.44.55",
        "http://22.33.44.55:8080",
        "https://22.33.44.55:8080",
        "http://username@test.com",
        "https://username@test.com",
        "http://username:password@test.com",
        "https://username:password@test.com",
        "http://[2001:db8:1f70::999:de8:7648:6e8]/index.html",
        "http://[2001:db8:1f70::999:de8:7648:6e8]:100/",
        "http://www.w3.org/TR/html4/strict.dtd",
    ]

    identifier = URI()

    for uri in valid_URI:
        assert identifier.is_of_this_type(uri), uri


def test_invalid():
    invalid_URI = [
        "xyzw",
        "https://w3.ibm.com:443/help or download the Help@IBM mobile app for iOS from",
        "http://www.foo.com\r",
    ]

    identifier = URI()

    for uri in invalid_URI:
        assert not identifier.is_of_this_type(uri), uri


def test_cornercases_from_rwe():
    identifier = URI()

    assert identifier.is_of_this_type("https://plus.google.com/11677")
    assert not identifier.is_of_this_type("Diazhttps://plus.google.com/11677")
    assert not identifier.is_of_this_type("www.churchproduction.com/ministry/mirror-manager-or-leader/, Thu")
