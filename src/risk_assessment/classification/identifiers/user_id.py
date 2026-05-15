"""User ID identifier for detecting unique identifier patterns.

This module provides an identifier for recognizing various unique ID formats
commonly used in systems.
"""

import re

from risk_assessment.classification.identifiers import RegexIdentifier


class UniqueIDIdentifier(RegexIdentifier):
    """Identifier for unique ID patterns.

    Recognizes various alphanumeric unique ID formats including:
    - 4-4-4 format (e.g., "a1b2-c3d4-e5f6")
    - 12-character format (e.g., "a1b2c3d4e5f6")
    - 6-6 format (e.g., "a1b2c3-d4e5f6")
    - 3-9 format (e.g., "abc-123456789")
    - UID prefix format (e.g., "UID-12345678")

    Example:
        >>> identifier = UniqueIDIdentifier()
        >>> identifier.is_of_this_type("a1b2-c3d4-e5f6")
        True
        >>> identifier.is_of_this_type("UID-12345678")
        True
    """

    def __init__(self) -> None:
        """Initialize the UniqueIDIdentifier with various ID patterns."""
        super().__init__(
            "UniqueID",
            [
                re.compile(r"^[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}$", re.I | re.U),
                re.compile(r"^[a-z0-9]{12}$", re.I | re.U),
                re.compile(r"^[a-z0-9]{6}-[a-z0-9]{6}$", re.I | re.U),
                re.compile(r"^[a-z0-9]{3}-[a-z0-9]{9}$", re.I | re.U),
                re.compile(r"^UID-[a-z0-9]{8}$", re.I | re.U),
            ],
        )
