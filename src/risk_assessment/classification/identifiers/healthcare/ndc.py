"""NDC identifier for detecting National Drug Codes.

This module provides an identifier for recognizing NDC (National Drug Code)
numbers used to identify medications in the United States.
"""

import csv
from pathlib import Path

from risk_assessment.classification.identifiers import Identifier


class NDC(Identifier):
    """Identifier for NDC (National Drug Code) numbers.

    NDC is a unique identifier for medications in the US, assigned by the FDA.

    Attributes:
        values: Set of valid NDC codes.

    Example:
        >>> identifier = NDC()
        >>> identifier.is_of_this_type("0069-2587-01")
        True
    """

    def __init__(self) -> None:
        """Initialize the NDC identifier by loading codes from data file."""
        with (Path(__file__).parent / "data" / "en" / "medicines.csv").open("r") as io_stream:
            reader = csv.reader(io_stream, delimiter=";")

            self.values = {record[0].strip().upper() for record in reader}

    def is_of_this_type(self, text: str) -> bool:
        """Check if text is a valid NDC code.

        Args:
            text: The text to check.

        Returns:
            True if text matches a known NDC code, False otherwise.
        """
        return text.upper() in self.values
