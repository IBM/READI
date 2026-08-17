import csv
import importlib.resources

from risk_assessment.utility.hierarchy import MaterializedHierarchy


class MaritalStatusHierarchy(MaterializedHierarchy):
    def __init__(self) -> None:
        res = importlib.resources.files(__name__).joinpath("data/marital_status.csv")
        with res.open("r") as iostream:
            reader = csv.reader(iostream)
            super().__init__([[record[0], record[1], "*"] for record in reader])
