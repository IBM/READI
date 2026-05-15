"""Gene identifier for detecting gene names and identifiers.

This module provides an identifier for recognizing gene names, HGNC IDs,
and UniProt identifiers.
"""

import csv
from pathlib import Path

from risk_assessment.classification.identifiers import Identifier


class Gene(Identifier):
    """Identifier for gene names and identifiers.

    Recognizes gene symbols, HGNC (HUGO Gene Nomenclature Committee) IDs,
    and UniProt protein identifiers.

    Attributes:
        gene_names: Set of valid gene names/symbols.
        HGNC_ID: Set of valid HGNC identifiers.
        uni_prot: Set of valid UniProt identifiers.

    Example:
        >>> identifier = Gene()
        >>> identifier.is_of_this_type("BRCA1")
        True
        >>> identifier.is_of_this_type("HGNC:1100")
        True
    """

    def __init__(self) -> None:
        """Initialize the Gene identifier by loading gene data from file."""
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
        """Check if text is a valid gene identifier.

        Args:
            text: The text to check.

        Returns:
            True if text matches a gene name, HGNC ID, or UniProt ID, False otherwise.
        """
        return (text in self.gene_names) or (text in self.HGNC_ID) or (text in self.uni_prot)
