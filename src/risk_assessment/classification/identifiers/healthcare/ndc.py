import csv
import importlib.resources

from risk_assessment.classification.identifiers import Identifier


class NDC(Identifier):
    def __init__(self) -> None:
        res = importlib.resources.files(__package__).joinpath("data/en/medicines.csv")
        with res.open("r") as io_stream:
            reader = csv.reader(io_stream, delimiter=";")

            self.values = {record[0].strip().upper() for record in reader}

    def is_of_this_type(self, text: str) -> bool:
        return text.upper() in self.values
