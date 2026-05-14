from functools import reduce
from pathlib import Path

from risk_assessment.classification.identifiers import Identifier


def _map_to_dict(key_value: tuple[str, ...]) -> dict[str, set[str]]:
    return {
        key_value[0]: {key_value[1]},
    }


def _reduce_dicts(left: dict[str, set[str]], right: dict[str, set[str]]) -> dict[str, set[str]]:
    for key, item in right.items():
        if key in left:
            left[key].update(item)
        else:
            left[key] = item
    return left


def _extract_zipcode_by_country() -> dict[str, set[str]]:
    with (Path(__file__).parent / "data" / "allCountries-short.txt").open("r") as input_data:
        country_zipcode: dict[str, set[str]] = reduce(
            _reduce_dicts,
            map(
                _map_to_dict,
                [tuple(line.split()[:2]) for line in input_data.readlines() if line.strip()],
            ),
        )

    return country_zipcode


_zipcodes_by_country: dict[str, set[str]] = _extract_zipcode_by_country()


class InternationalZipcode(Identifier):
    def is_of_this_type(self, text: str) -> bool:
        return any(self.is_of_this_type_by_country(text, country) for country in _zipcodes_by_country.keys())

    def is_of_this_type_by_country(self, text: str, country: str) -> bool:
        return text in _zipcodes_by_country[country]
