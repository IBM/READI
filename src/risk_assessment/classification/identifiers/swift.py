"""SWIFT identifier for detecting SWIFT/BIC codes.

This module provides an identifier for recognizing SWIFT/BIC
(Society for Worldwide Interbank Financial Telecommunication) codes.
"""

import re
from pathlib import Path

from risk_assessment.classification.identifiers import Identifier


def _load_codes() -> set[str]:
    """Load known SWIFT codes from data file.

    Returns:
        Set of valid SWIFT codes.
    """
    with (Path(__file__).parent / "data" / "common" / "swiftcodes.csv").open("r") as io_stream:
        return {code.strip().casefold() for code in io_stream}


class SWIFT(Identifier):
    """Identifier for SWIFT/BIC codes.

    Validates SWIFT codes (8 or 11 characters) against a known list.
    Format: 4 letters (bank), 2 letters (country), 2 alphanumeric (location),
    optional 3 alphanumeric (branch).

    Attributes:
        codes: Set of known valid SWIFT codes.
        pattern: Regex pattern for SWIFT code format.

    Example:
        >>> identifier = SWIFT()
        >>> identifier.is_of_this_type("DEUTDEFF")
        True
        >>> identifier.is_of_this_type("CHASUS33XXX")
        True
    """

    codes = _load_codes()
    pattern = re.compile(r"^[a-z]{4}[ -]?[a-z]{2}[ -]?[a-z0-9]{2}[ -]?(?:[a-z0-9]{3})?$", re.I)

    def is_of_this_type(self, text: str) -> bool:
        """Check if text is a valid SWIFT code.

        Args:
            text: The text to check.

        Returns:
            True if text matches SWIFT format and is in known codes list, False otherwise.
        """
        return self.pattern.match(text) is not None and text.casefold() in self.codes
