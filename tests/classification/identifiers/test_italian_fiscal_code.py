import pytest

from risk_assessment.classification.identifiers import ItalianFiscalCode


def test_valid():
    identifier = ItalianFiscalCode()

    for valid in [
        "BRGSFN81P10L682K",
        "MRTMTT25D09F205Z",
        "MLLSNT82P65Z404U",
        "BRG SFN 81P10 L682K",
    ]:
        assert identifier.is_of_this_type(valid), valid


def test_invalid():
    identifier = ItalianFiscalCode()

    for invalid in [
        "BRG SFN 81P72 L682K",
        "MLLSNT82P65Z4049",
        "MLLSNT82P65Z404D",
        "MLLSNT82P65Z404J",
        "MLL-NT8-P65Z404U",
        "MLLSNT82P65ZJDS404U",
        "MLLSNT8204U",
    ]:
        assert not identifier.is_of_this_type(invalid), invalid


@pytest.mark.skip("Needs to fix faker_locale for italian")
def test_positive(faker, faker_locale_it):
    identifier = ItalianFiscalCode()

    for _ in range(100):
        cf = faker.ssn()

        assert identifier.is_of_this_type(cf), cf
