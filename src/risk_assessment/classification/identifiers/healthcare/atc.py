import csv
from pathlib import Path

from risk_assessment.classification.identifiers import Identifier


class ATC(Identifier):
    def __init__(self) -> None:
        with (Path(__file__).parent / "data" / "atc.csv").open("r") as io_stream:
            reader = csv.reader(io_stream, delimiter=";")

            self.values = {record[0].strip().casefold() for record in reader}

    def is_of_this_type(self, text: str) -> bool:
        return text.casefold() in self.values
