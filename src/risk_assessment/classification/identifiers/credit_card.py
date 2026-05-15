"""Credit card identifier for detecting credit card numbers.

This module provides an identifier for recognizing credit card numbers from
various card networks including Visa, MasterCard, American Express, Discover,
JCB, Diners Club, and Maestro. Uses Luhn algorithm for validation.
"""

import re

from risk_assessment.classification.identifiers import LuhnIdentifier


class CreditCard(LuhnIdentifier):
    """Identifier for credit card numbers with Luhn validation.

    Recognizes credit card numbers from major card networks and validates
    them using the Luhn checksum algorithm.

    Supported card types:
    - Visa (16 digits, starts with 4)
    - MasterCard (16 digits, starts with 51-55 or 2221-2720)
    - American Express (15 digits, starts with 34 or 37)
    - Diners Club (14 digits, starts with 300-305 or 36 or 38)
    - Discover (16 digits, starts with 6011 or 65)
    - JCB (16 digits, starts with 2131, 1800, or 35)
    - Maestro (12-19 digits, various prefixes)

    Attributes:
        patterns: List of compiled regex patterns for different card formats.

    Example:
        >>> identifier = CreditCard()
        >>> identifier.is_of_this_type("4532015112830366")  # Valid Visa
        True
        >>> identifier.is_of_this_type("1234567890123456")  # Invalid
        False
    """

    patterns = [
        re.compile(r"^4\d{15}$"),  # visa
        re.compile(r"^4\d{3}(?:[- ]?\d{4}){3}$"),  # visa with formatting
        re.compile(r"^4\d{3}(?:[- ]?\d{4}){2}[- ]\d{3}$"),  # visa with formatting
        re.compile(r"^(?:5[1-5]\d{2}|222[1-9]|22[3-9]\d|2[3-6]\d{2}|27[01]\d|2720)\d{12}$"),  # MasterCard
        re.compile(r"^(?:5[1-5]\d{2}|222[1-9]|22[3-9]\d|2[3-6]\d{2}|27[01]\d|2720)\d{12}$"),  # MasterCard v2
        re.compile(r"^3[47]\d{13}$"),  # AMEX
        re.compile(r"^3[47]\d{2}-\d{4}-\d{4}-\d{3}$"),  # AMEX v2
        re.compile(r"^3[47]\d{2} \d{4} \d{4} \d{3}$"),  # AMEX v3
        re.compile(r"^3(?:0[0-5]|[68]\d)\d{11}$"),  # Diners Club
        re.compile(r"^6(?:011|5\d{2})\d{12}$"),  # Discover
        re.compile(r"^(?:2131|1800|35\d{3})\d{11}$"),  # JCB
        re.compile(r"^(?:5018|5020|5038|5893|6304|6759|6761|6762|6763)\d{8,15}$"),  # MAESTRO
        re.compile(r"^6759\d{8,15}$"),  # MAESTRO UK 1
        re.compile(r"^67677[04]\d{6,13}$"),  # MAESTRO UK
    ]

    def is_of_this_type(self, text: str) -> bool:
        """Check if text is a valid credit card number.

        Args:
            text: The text to check.

        Returns:
            True if text matches a card pattern and passes Luhn validation, False otherwise.
        """
        for pattern in self.patterns:
            if pattern.match(text) and self.check_luhn(text):
                return True
        return False

    def debug_values(self, text: str) -> int:
        """Debug method to check validation status.

        Args:
            text: The text to check.

        Returns:
            0 if valid (pattern match and Luhn pass),
            1 if pattern matches but Luhn fails,
            2 if pattern doesn't match.
        """
        for pattern in self.patterns:
            if pattern.match(text):
                if self.check_luhn(text):
                    return 0
                else:
                    return 1
        return 2
