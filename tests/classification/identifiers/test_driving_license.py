from risk_assessment.classification.identifiers import DrivingLicense, JapanDrivingLicense


def test_driving_licenses():
    identifier = DrivingLicense()

    examples: list[tuple[str, str]] = [
        ("567894345123", "Japan"),
    ]

    for example, country in examples:
        assert identifier.is_of_this_type(example), country


def test_japanese_driving_license():
    examples = [
        "345623456789",
        "678456789345",
        "456789321456",
        "567894345123",
        "678904567345",
        "345678234908",
        "567893456789",
        "321456789345",
        "456789123456",
        "908765345678",
        "987654123456",
    ]

    identifer = JapanDrivingLicense()

    for example in examples:
        assert identifer.is_of_this_type(example), example

        for prefix in JapanDrivingLicense._prefixes:
            assert identifer.is_of_this_type(prefix + example), (prefix, example)
            assert identifer.is_of_this_type(prefix + " " + example), (prefix, example)
