import csv
import re
from pathlib import Path

from risk_assessment.classification.identifiers import Identifier


class CreditCardType(Identifier):
    def __init__(self) -> None:
        with (Path(__file__).parent / "data" / "en" / "credit_card_types.csv").open("r") as io_stream:
            reader = csv.reader(io_stream)
            self.patterns = [re.compile(f"^{parts[0].strip()}$", re.IGNORECASE) for parts in reader]

    def is_of_this_type(self, text: str) -> bool:
        return any(pattern.match(text) for pattern in self.patterns)
