import csv
import re
from pathlib import Path

from risk_assessment.classification.identifiers import Identifier


class CreditCardType(Identifier):
    def __init__(self) -> None:
        with (Path(__file__).parent / "data" / "french_zipcodes").open("r") as io_stream:
            reader = csv.reader(io_stream)
            self.patterns = [re.compile(f"^{parts[0].strip()}$", re.IGNORECASE) for parts in reader]

    def is_of_this_type(self, text: str) -> bool:
        for pattern in self.patterns:
            if pattern.match(text):
                return True
        return False
