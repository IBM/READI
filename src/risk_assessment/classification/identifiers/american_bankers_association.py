import re

from risk_assessment.classification.identifiers import Identifier


def _validate_checksum(federal_reserve_routing: str, aba_institution: str, checksum: str) -> bool:
    first_frr = federal_reserve_routing[:2]

    if first_frr in {
        "00",  # United States Government
        # normal, thrift (+20), electornic (+60)
        "01",
        "21",
        "61",  # Boston
        "02",
        "22",
        "62",  # New York
        "03",
        "23",
        "63",  # Philadelphia
        "04",
        "24",
        "64",  # Cleveland
        "05",
        "25",
        "65",  # Richmond
        "06",
        "26",
        "66",  # Atlanta
        "07",
        "27",
        "67",  # Chicago
        "08",
        "28",
        "68",  # St. Louis
        "09",
        "29",
        "69",  # Minneapolis
        "10",
        "30",
        "70",  # Kansas City
        "11",
        "31",
        "71",  # Dallas
        "12",
        "32",
        "72",  # San Francisco
        "80",  # traveler's checks
    }:
        [d1, d2, d3, d4] = [int(d) for d in federal_reserve_routing]
        [d5, d6, d7, d8] = [int(d) for d in aba_institution]

        return (3 * (d1 + d4 + d7) + 7 * (d2 + d5 + d8) + (d3 + d6 + int(checksum))) % 10 == 0

    return False


class AmericanBankersAssociationNumber(Identifier):
    pattern: re.Pattern[str] = re.compile(r"^(\d{4})(\d{4})(\d)$")

    def is_of_this_type(self, text: str) -> bool:
        match = self.pattern.match(text)

        return match is not None and _validate_checksum(match.group(1), match.group(2), match.group(3))
