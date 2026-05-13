import csv
from pathlib import Path

from risk_assessment.classification.identifiers import Identifier


class Gene(Identifier):
    def __init__(self) -> None:
        self.gene_names: set[str] = set()
        self.HGNC_ID: set[str] = set()
        self.uni_prot: set[str] = set()

        with (Path(__file__).parent / "data" / "genes_list.csv").open("r") as io_stream:
            reader = csv.reader(io_stream, delimiter=",")

            for record in reader:
                self.gene_names.add(record[1].strip())
                self.HGNC_ID.add(record[2].strip())
                self.uni_prot.add(record[3].strip())

    def is_of_this_type(self, text: str) -> bool:
        return (text in self.gene_names) or (text in self.HGNC_ID) or (text in self.uni_prot)
