"""Bank account identifier for detecting bank account numbers.

This module provides identifiers for recognizing bank account numbers
from various countries.
"""

import re

from risk_assessment.classification.identifiers import RegexIdentifierWithSpan


class JapanBankAccountNumber(RegexIdentifierWithSpan):
    """Identifier for Japanese bank account numbers.

    Recognizes Japanese bank account numbers in the format of 7-8 digits
    followed by 4 digits and optionally 3 more digits with separators.

    Example:
        >>> identifier = JapanBankAccountNumber()
        >>> identifier.is_of_this_type("12345678-1234-123")
        True
    """

    def __init__(self) -> None:
        """Initialize the JapanBankAccountNumber identifier with regex pattern."""
        return super().__init__(
            "JapanBankAccountNumber",
            [
                re.compile(r"^(\d{7,8}\d{4}[ -]?\d{3})$", re.UNICODE),
            ],
        )
