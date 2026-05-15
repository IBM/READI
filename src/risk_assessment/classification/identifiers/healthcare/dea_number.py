"""DEA number identifier for detecting Drug Enforcement Administration numbers.

This module provides an identifier for recognizing DEA registration numbers
used by healthcare providers authorized to prescribe controlled substances.
"""

import re

from risk_assessment.classification.identifiers import RegexIdentifier


class DEANumber(RegexIdentifier):
    """Identifier for DEA (Drug Enforcement Administration) registration numbers.

    DEA numbers are issued to healthcare providers and consist of:
    - 2 letters (registrant type and first letter of last name)
    - 6 digits
    - 1 check digit

    Example:
        >>> identifier = DEANumber()
        >>> identifier.is_of_this_type("AB1234563")
        True
    """

    def __init__(self) -> None:
        """Initialize the DEANumber identifier with regex patterns."""
        super().__init__(
            "DEANumber",
            [
                # re.compile(r"^[A-Z]{2}\d{7}$", re.U),
                re.compile(r"^[ABCDEFGHJKLMPRSTUX][A-Z9]\d{6}\d$", re.U),
                re.compile(r"^[ABCDEFGHJKLMPRSTUX][A-Z9]\d{6}\d-\w{3,}$", re.U),
            ],
        )

    def is_of_this_type(self, text: str) -> bool:
        """Check if text is a valid DEA number.

        Args:
            text: The text to check.

        Returns:
            True if text matches DEA format and has valid checksum, False otherwise.
        """
        return super().is_of_this_type(text) and self._checksum(text)

    def _checksum(self, text: str) -> bool:
        """Validate DEA number checksum.

        Args:
            text: The DEA number to validate.

        Returns:
            True if checksum is valid, False otherwise.
        """
        numbers = text.split("-")[0][2:]

        calc_135 = int(numbers[0]) + int(numbers[2]) + int(numbers[4])
        calc_246 = int(numbers[1]) + int(numbers[3]) + int(numbers[5])
        calc_246 *= 2

        check = str(calc_135 + calc_246)[-1]

        return numbers[-1] == check
