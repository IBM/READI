"""IMEI identifier for detecting International Mobile Equipment Identity numbers.

This module provides an identifier for recognizing IMEI numbers used to
identify mobile devices.
"""

import re

from risk_assessment.classification.identifiers import LuhnIdentifier


class IMEI(LuhnIdentifier):
    """Identifier for IMEI (International Mobile Equipment Identity) numbers.

    Validates 15-digit IMEI numbers with Luhn checksum verification.

    Attributes:
        pattern: Regex pattern for 15-digit format.

    Example:
        >>> identifier = IMEI()
        >>> identifier.is_of_this_type("490154203237518")
        True
    """

    pattern = re.compile(r"^\d{15}$")

    def is_of_this_type(self, text: str) -> bool:
        """Check if text is a valid IMEI number.

        Args:
            text: The text to check.

        Returns:
            True if text is a 15-digit number with valid Luhn checksum, False otherwise.
        """
        if text.isnumeric():
            if self.pattern.match(text) and self.check_luhn(text):
                return True
        return False
