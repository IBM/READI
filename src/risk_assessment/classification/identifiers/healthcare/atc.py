"""ATC identifier for detecting Anatomical Therapeutic Chemical codes.

This module provides an identifier for recognizing ATC codes used for
classifying medications.
"""

import csv
from pathlib import Path

from risk_assessment.classification.identifiers import Identifier


class ATC(Identifier):
    """Identifier for ATC (Anatomical Therapeutic Chemical) codes.

    ATC is a classification system for medications based on their therapeutic,
    pharmacological, and chemical properties.

    Attributes:
        values: Set of valid ATC codes.

    Example:
        >>> identifier = ATC()
        >>> identifier.is_of_this_type("A02BC01")
        True
    """

    def __init__(self) -> None:
        """Initialize the ATC identifier by loading codes from data file."""
        with (Path(__file__).parent / "data" / "atc.csv").open("r") as io_stream:
            reader = csv.reader(io_stream, delimiter=";")

            self.values = {record[0].strip().casefold() for record in reader}

    def is_of_this_type(self, text: str) -> bool:
        """Check if text is a valid ATC code.

        Args:
            text: The text to check.

        Returns:
            True if text matches a known ATC code, False otherwise.
        """
        return text.casefold() in self.values
