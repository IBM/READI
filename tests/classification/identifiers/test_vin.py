import json
from pathlib import Path

from risk_assessment.classification.identifiers import VehicleIdentificationNumber


def test_check_digit() -> None:
    identifier = VehicleIdentificationNumber()

    assert identifier.is_of_this_type("1M8GDM9AXKP042788")


def test_from_dpt() -> None:
    identifier = VehicleIdentificationNumber()

    assert not identifier.is_of_this_type("ABV3231333"), "too short"
    assert not identifier.is_of_this_type("ABQ12345678901234"), "invalid characters"
    assert not identifier.is_of_this_type("AIB12345678901234"), "invalid characters, I"
    assert not identifier.is_of_this_type("AOB12345678901234"), "invalid characters,"
    assert not identifier.is_of_this_type("1B312-45678901234"), "invalid characters, non digits or letters"
    assert not identifier.is_of_this_type("1B312.45678901234"), "invalid characters, non digits or letters"
    assert not identifier.is_of_this_type("11112345678901234"), "not known WMI 111"
    assert not identifier.is_of_this_type("1B312345678901234"), "char 0 is invalid"

    assert identifier.is_of_this_type("5GZCZ43D13S812715")
    assert not identifier.is_of_this_type("SGZCZ43D13S812715"), "incorrect leading S"
    assert identifier.is_of_this_type("WP0ZZZ99ZTS392124"), "valid for Porche, not for US"
    assert identifier.is_of_this_type("KLATF08Y1VB363636"), "valid for GM-T, not for US"


def test_from_datasets():
    identifier = VehicleIdentificationNumber()

    detected: list[str] = []
    missed: list[str] = []

    with (Path(__file__).parent / "data" / "vin_list.json").open() as input:
        for vin in json.load(input):
            if identifier.is_of_this_type(vin):
                detected.append(vin)
            else:
                missed.append(vin)

    assert len(detected)
