import pytest


@pytest.fixture()
def faker_locale_us():
    return ["en_US"]


@pytest.fixture()
def faker_locale_ja():
    return ["ja_JP"]
