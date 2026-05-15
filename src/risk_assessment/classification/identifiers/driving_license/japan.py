"""Japan driving license identifier for detecting Japanese driver's licenses.

This module provides an identifier for recognizing Japanese driving license
numbers with support for both English and Japanese text prefixes.
"""

import re

from risk_assessment.classification.identifiers import RegexIdentifierWithSpan


class JapanDrivingLicense(RegexIdentifierWithSpan):
    """Identifier for Japanese driving license numbers.

    Recognizes 12-digit Japanese driving license numbers with optional
    prefixes in English or Japanese.

    Attributes:
        _prefixes: List of valid prefixes in English and Japanese.

    Example:
        >>> identifier = JapanDrivingLicense()
        >>> identifier.is_of_this_type("Japan dl# 123456789012")
        True
        >>> identifier.is_of_this_type("123456789012")
        True
    """

    _prefixes = [
        r"Japan dl#",
        r"Japan dls#",
        r"Japan driver license",
        r"Japan driver’s license",
        r"Japan drivers licenses",
        r"Japan lic#",
        r"Japanese state identification",
        r"Japanese state identification number",
        r"低所得国＃",
        r"免許証",
        r"状態ID",
        r"状態の識別",
        r"状態の識別番号",
        r"運転免許",
        r"運転免許証",
        r"運転免許証番号",
    ]

    def __init__(self) -> None:
        """Initialize the JapanDrivingLicense identifier with regex pattern."""
        super().__init__(
            "JapanDrivingLicense",
            [
                re.compile(r"^(?:(?:" + r"|".join(JapanDrivingLicense._prefixes) + r")\s*)?(\d{12})$", re.I | re.U),
            ],
        )
