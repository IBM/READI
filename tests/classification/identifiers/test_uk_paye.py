from risk_assessment.classification.identifiers import HMRC_PAYE


def test_basic_validation():
    identifier = HMRC_PAYE()

    for valid in [
        "123/AB456",
        "123/A56789",
        "123/AB56789",
    ]:
        assert identifier.is_of_this_type(valid), valid

    for invalid in [
        "1234567890",
        "ddfalksjdfkla",
        "320/Tree",
        "000/MONTH",
        "600/MONTH",
        "206/2005",
        "861/original",
        "235/original",
        "320/jennifersbday20 ",
        "320/ladiesmeetingbekahcamera",
        "143/medium ",
    ]:
        assert not identifier.is_of_this_type(invalid), invalid
