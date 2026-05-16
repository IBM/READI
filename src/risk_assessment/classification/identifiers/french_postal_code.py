import re
from pathlib import Path

from risk_assessment.classification.identifiers import Identifier


def _load_valid_zipcodes() -> dict[str, set[str]]:
    with (Path(__file__).parent / "data" / "french_zipcodes").open("r") as input_data:
        data = [line.strip() for line in input_data.readlines() if len(line.strip()) == 5]

    departments: dict[str, set[str]] = {zipcode[:2]: set() for zipcode in data if len(zipcode) == 5}

    for zipcode in data:
        if len(zipcode.strip()) != 5:
            continue
        departments[zipcode[:2]].add(zipcode[2:])

    return departments


class FrenchPostalCode(Identifier):
    pattern: re.Pattern[str] = re.compile(r"^(\d{2})(\d{3})$")
    departments: dict[str, set[str]] = _load_valid_zipcodes()

    def is_of_this_type(self, text: str) -> bool:
        match = self.pattern.match(text)

        if not match:
            return False
        if int(text) > 95880:
            return False  # more than current largest int value
        if int(text) < 1000:
            return False  # less than smallest int value

        department = match.group(1)
        prefecture = match.group(2)

        if department not in self.departments:
            return False

        return prefecture in self.departments[department]
