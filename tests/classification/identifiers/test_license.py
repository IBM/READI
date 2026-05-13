from risk_assessment.classification.identifiers import CaliforniaFinancingLaw, NationwideMultistateLicensingSystem


def test_basic_nmls():
    examples: list[str] = [
        "NMLS #1136148",
        "NMLS License #1136148",
        "#1136148",
        "NMLS #1979518",
    ]

    identifier = NationwideMultistateLicensingSystem()

    for example in examples:
        assert identifier.is_of_this_type(example), example


def test_basic_CFL():
    examples: list[str] = [
        "CFL #6055856",
        "CFL License #60DBO-116115",
    ]

    identifier = CaliforniaFinancingLaw()

    for example in examples:
        assert identifier.is_of_this_type(example), example
