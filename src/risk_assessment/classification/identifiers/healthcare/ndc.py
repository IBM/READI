import csv
from pathlib import Path

from risk_assessment.classification.identifiers import Identifier


class NDC(Identifier):
    def __init__(self) -> None:
        with (Path(__file__).parent / "data" / "en" / "medicines.csv").open("r") as io_stream:
            reader = csv.reader(io_stream, delimiter=";")

            self.values = {record[0].strip().upper() for record in reader}

    def is_of_this_type(self, text: str) -> bool:
        return text.upper() in self.values
