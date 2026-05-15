"""License identifier for detecting various license numbers.

This module provides identifiers for recognizing license numbers from
various licensing systems.
"""

import re

from risk_assessment.classification.identifiers import RegexIdentifierWithSpan


class NationwideMultistateLicensingSystem(RegexIdentifierWithSpan):
    """Identifier for NMLS (Nationwide Multistate Licensing System) license numbers.

    NMLS is used for licensing mortgage loan originators and other financial services.
    Format: Optional "NMLS" prefix followed by # and 7-12 digits.

    Example:
        >>> identifier = NationwideMultistateLicensingSystem()
        >>> identifier.is_of_this_type("NMLS #1234567")
        True
        >>> identifier.is_of_this_type("#12345678")
        True
    """

    def __init__(self) -> None:
        """Initialize the NMLS identifier with regex pattern."""
        super().__init__(
            "NMLS",
            [
                re.compile(r"^(?:NMLS(?:\s+license)?\s+)?(#\d{7,12})$", re.I | re.U),
            ],
        )


class CaliforniaFinancingLaw(RegexIdentifierWithSpan):
    """Identifier for CFL (California Financing Law) license numbers.

    Format: Optional "CFL" prefix followed by # and 7-12 digits,
    or transitional format with "60DBO-" prefix.

    Example:
        >>> identifier = CaliforniaFinancingLaw()
        >>> identifier.is_of_this_type("CFL #1234567")
        True
        >>> identifier.is_of_this_type("#60DBO-12345")
        True
    """

    def __init__(self) -> None:
        """Initialize the CFL identifier with regex patterns."""
        super().__init__(
            "CFL",
            [
                re.compile(r"^(?:CFL(?:\s+license)?\s+)?(#\d{7,12})$", re.I | re.U),
                re.compile(
                    r"^(?:CFL(?:\s+license)?\s+)?(#60DBO-?\d{5,12})$", re.I | re.U
                ),  # pattern for transitioning license
            ],
        )
