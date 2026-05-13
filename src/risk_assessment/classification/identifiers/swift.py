import re
from pathlib import Path

from risk_assessment.classification.identifiers import Identifier


def _load_codes() -> set[str]:
    with (Path(__file__).parent / "data" / "common" / "swiftcodes.csv").open("r") as io_stream:
        return {code.strip().casefold() for code in io_stream}


class SWIFT(Identifier):
    codes = _load_codes()
    pattern = re.compile(r"^[a-z]{4}[ -]?[a-z]{2}[ -]?[a-z0-9]{2}[ -]?(?:[a-z0-9]{3})?$", re.I)

    def is_of_this_type(self, text: str) -> bool:
        return self.pattern.match(text) is not None and text.casefold() in self.codes
