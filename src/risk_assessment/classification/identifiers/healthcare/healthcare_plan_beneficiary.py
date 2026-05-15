"""Healthcare plan beneficiary identifier for detecting beneficiary numbers.

This module provides an identifier for recognizing healthcare plan
beneficiary identification numbers.
"""

import re

from risk_assessment.classification.identifiers import RegexIdentifier


class HealthcareBeneficiaryNumber(RegexIdentifier):
    """Identifier for healthcare plan beneficiary numbers.

    Recognizes various formats of healthcare beneficiary identification numbers
    including alphanumeric patterns and HPBN-prefixed formats.

    Example:
        >>> identifier = HealthcareBeneficiaryNumber()
        >>> identifier.is_of_this_type("A1234567")
        True
        >>> identifier.is_of_this_type("HPBN-123456")
        True
    """

    def __init__(self) -> None:
        """Initialize the HealthcareBeneficiaryNumber identifier with regex patterns."""
        super().__init__(
            "HealthcareBeneficiaryNumber",
            [
                re.compile(r"^[a-z]\d{7,9}$", re.I | re.U),
                re.compile(r"^HPBN-\d{6,8}$", re.I | re.U),
            ],
        )
