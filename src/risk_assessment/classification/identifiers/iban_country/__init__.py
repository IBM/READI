"""IBAN country validator for validating country-specific IBAN formats.

This module provides a validator class for checking IBAN numbers against
country-specific patterns and performing mod-97 checksum validation.
"""

from dataclasses import dataclass
from re import Pattern


@dataclass
class IBANCountryValidator:
    r"""Validator for country-specific IBAN formats.

    Validates IBAN numbers using country-specific regex patterns and
    the ISO 7064 mod-97 checksum algorithm.

    Attributes:
        pattern: Compiled regex pattern for the country's IBAN format.

    Example:
        >>> import re
        >>> validator = IBANCountryValidator(re.compile(r"^GB\d{2}[A-Z]{4}\d{14}$"))
        >>> validator.is_valid("GB82WEST12345698765432")
        True
    """

    pattern: Pattern[str]

    def validate(self, text: str) -> bool:
        """Validate IBAN using mod-97 checksum algorithm.

        An IBAN is validated by converting it into an integer and performing
        a mod-97 operation (ISO 7064). If valid, the remainder equals 1.

        Algorithm:
        1. Check that the total IBAN length is correct as per the country
        2. Move the four initial characters to the end of the string
        3. Replace each letter with two digits (A=10, B=11, ..., Z=35)
        4. Compute the remainder of that number on division by 97
        5. If the remainder is 1, the check digit test passes

        Args:
            text: The IBAN string to validate.

        Returns:
            True if the checksum is valid (remainder is 1), False otherwise.
        """
        text = text[4:] + text[0:4]

        return 1 == self.convert_to_int(text.upper()) % 97

    def convert_to_int(self, iban: str) -> int:
        """Convert IBAN string to integer for mod-97 calculation.

        Replaces letters with numbers (A=10, B=11, ..., Z=35).

        Args:
            iban: The IBAN string to convert.

        Returns:
            Integer representation of the IBAN.
        """
        return int("".join([c if c.isdigit() else str(10 + ord(c) - ord("A")) for c in iban.upper()]))

    def is_valid(self, text: str) -> bool:
        """Check if IBAN is valid for this country.

        Validates both the format (regex pattern) and checksum.

        Args:
            text: The IBAN string to validate.

        Returns:
            True if IBAN matches pattern and has valid checksum, False otherwise.
        """
        if self.get_pattern().fullmatch(text) and self.validate(text):
            return True
        return False

    def get_pattern(self) -> Pattern[str]:
        """Get the regex pattern for this country's IBAN format.

        Returns:
            The compiled regex pattern.
        """
        return self.pattern
