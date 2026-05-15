"""Phone number identifier for detecting phone numbers in various international formats.

This module provides identifiers for recognizing phone numbers from different countries
and formats, including US phone numbers and various international patterns.
"""

import re

from risk_assessment.classification.identifiers import (
    Identifier,
    RegexIdentifier,
    RegexIdentifierWithSpan,
)


class Phone(Identifier):
    """Main phone number identifier supporting multiple formats.

    Combines multiple phone number validators to recognize US and international
    phone number formats.

    Attributes:
        supported_phone_types: List of phone identifier instances to check.

    Example:
        >>> identifier = Phone()
        >>> identifier.is_of_this_type("(555)-123-4567")
        True
        >>> identifier.is_of_this_type("+1 555 123 4567")
        True
    """

    def __init__(self) -> None:
        """Initialize the Phone identifier with multiple format validators."""
        self.supported_phone_types: list[Identifier] = [
            USPhone(),
            PhoneNumber(),
            MissingOnes(),
        ]

    def is_of_this_type(self, text: str) -> bool:
        """Check if text is a valid phone number in any supported format.

        Args:
            text: The text to check.

        Returns:
            True if text matches any phone number pattern, False otherwise.
        """
        return any(identifier.is_of_this_type(text) for identifier in self.supported_phone_types)


class MissingOnes(RegexIdentifier):
    """Identifier for additional phone number formats not covered by other validators.

    Handles various international phone number patterns including formats with
    dots, dashes, spaces, and parentheses.

    Example:
        >>> identifier = MissingOnes()
        >>> identifier.is_of_this_type("0123 4567 8901")
        True
        >>> identifier.is_of_this_type("+44 (0) 20 1234 5678")
        True
    """

    def __init__(self) -> None:
        """Initialize with regex patterns for various phone formats."""
        super().__init__(
            "Phone",
            [
                re.compile(r"^\d{3} \d{4} \d{4}$", re.U),
                re.compile(r"^\d{5} \d{3} ?\d{3}$", re.U),
                re.compile(r"^\d{4}\.\d{3}\.\d{3}$", re.U),
                re.compile(r"^\d{4}-\d{3}-\d{3}$", re.U),
                re.compile(r"^\d{4} \d{3} \d{3}$", re.U),
                re.compile(r"^\d{4}[ \.-]\d{4}$", re.U),
                re.compile(r"^\d{2}\.\d{4}\.\d{4}$", re.U),
                re.compile(r"^\(\d{2}\) ?\d{4} ?\d{4}$", re.U),
                re.compile(r"^\(\d{2}\)-\d{4}-\d{4}$", re.U),
                re.compile(r"^\(\d{2}\)\.\d{4}\.\d{4}$", re.U),
                re.compile(r"^\(\d{2}\) \d{4} \d{4}$", re.U),
                re.compile(r"^\(\d{3,4}\) ?\d{3,4} ?\d{4}$", re.U),
                re.compile(r"^\(\d{5}\) ?\d{3} ?\d{3,4}$", re.U),
                re.compile(r"^\d{4} \d{7}$", re.U),
                re.compile(r"^\d{2} \d{4} \d{4}$", re.U),
                re.compile(r"^\d{2}-\d{4}-\d{4}$", re.U),
                re.compile(r"^\d{4} \d{3} \d{4}$", re.U),
                re.compile(r"^\+\d{2,3} ?\(0\) ?\d{2} ?\d{4} ?\d{4}$", re.U),
                re.compile(r"^\+\d{2}-\d{3}-\d{3}-\d{3}$", re.U),
                re.compile(r"^\+\d{2}\(0\)\d{3} \d{7}$", re.U),
                re.compile(r"^\+\d{2}\(0\)\d{3}\d{6}$", re.U),
                re.compile(r"^\+\d{2}\(0\)\d{2} ?\d{7}$", re.U),
                re.compile(r"^\+\d{2}\(0\)\d{4} ?\d{6}$", re.U),
                re.compile(r"^\+\d{2}\(0\)\d{4} ?\d{3} ?\d{3}$", re.U),
                re.compile(r"^\+\d{2}\.\d\.\d{4}\.\d{4}$", re.U),
                re.compile(r"^\+\d{2}-\d-\d{4}-\d{4}$", re.U),
                re.compile(r"^\+\d{2} \d \d{4} \d{4}$", re.U),
                re.compile(r"^\+\d{4} \d{4} ?\d{4}$", re.U),
                re.compile(r"^\+\d{2}\.\d{3}\.\d{3}\.\d{3}$", re.U),
                re.compile(r"^\+\d{4} \d{7}$", re.U),
                re.compile(r"^\+\d{6} \d{3} ?\d{3}$", re.U),
                re.compile(r"^\+?1 \(\d{3}\) \d{3}-\d{4}$"),
                re.compile(r"^\+\d{2} ?\d{3} ?\d{3} ?\d{3}$"),
                re.compile(r"^\d{8}$"),
            ],
        )


class USPhone(RegexIdentifier):
    """Identifier specifically for US phone number formats.

    Recognizes standard US phone number patterns with area codes.

    Example:
        >>> identifier = USPhone()
        >>> identifier.is_of_this_type("(555)-123-4567")
        True
        >>> identifier.is_of_this_type("555-123-4567")
        True
    """

    def __init__(self) -> None:
        """Initialize with US phone number regex patterns."""
        super().__init__(
            "Phone",
            [
                re.compile(r"^\(\d{3}\)-\d{3}-\d{4}$"),
                re.compile(r"^\d{3}-\d{3}-\d{4}$"),
            ],
        )


_PREFIXES: str = r"(?:(?:Pgr|Ph|[Pp]hone|Fax|Contact):?\s+#?)?"
_EXTENSION: str = r"(?:\s*x\d{3,5})?"


class PhoneNumber(RegexIdentifierWithSpan):
    """Advanced phone number identifier with span detection.

    Recognizes phone numbers with optional prefixes (Phone:, Fax:, Contact:)
    and extensions. Supports international formats and can identify the exact
    span of the phone number within text.

    Example:
        >>> identifier = PhoneNumber()
        >>> identifier.is_of_this_type("Phone: (555) 123-4567")
        True
        >>> identifier.is_of_this_type("Contact: +1-555-123-4567 x1234")
        True
    """

    def __init__(self) -> None:
        """Initialize with comprehensive phone number patterns including prefixes and extensions."""
        super().__init__(
            "Phone",
            [
                re.compile(r"^" + _PREFIXES + r"(\(\d{3}\)[- ]?\d{3}[- ]?\d{4}" + _EXTENSION + r")$"),
                re.compile(
                    r"^" + _PREFIXES + r"((?:\+|00)\d{2}[- ]?\(?\d{3}\)?[- ]?\d{3}[- ]?\d{4}" + _EXTENSION + r")$"
                ),
                re.compile(r"^" + _PREFIXES + r"((?:\+|00)\d{3}[- ]?\d{2}[- ]?\d{3}[- ]?\d{4}" + _EXTENSION + r")$"),
                re.compile(
                    r"^" + _PREFIXES + r"((?:\+|00)\d{3}[- ]?\(?\d{3}\)?[- ]?\d{3}[- ]?\d{4}" + _EXTENSION + r")$"
                ),
                re.compile(r"^" + _PREFIXES + r"(\(?\d{3}\)?[- ]\d{4,5}" + _EXTENSION + r")$"),
                re.compile(r"^" + _PREFIXES + r"(\d{3}-\d{3}-\d{4}" + _EXTENSION + r")$"),
                re.compile(
                    r"^" + _PREFIXES + r"(\d{3}[- ]?(?:\d{2}[- ]?){2}\d{3}" + _EXTENSION + r")$"
                ),  # italy mobile
                re.compile(r"^" + _PREFIXES + r"(0\d{2}[ ]?\d{8}" + _EXTENSION + r")$"),  # uk
                re.compile(r"^" + _PREFIXES + r"(\(\+\d{2,3}\)0\d{10}" + _EXTENSION + r")$"),  # uk
                re.compile(r"^" + _PREFIXES + r"(\+44\(0\)\d{3} \d{3} \d{4}" + _EXTENSION + r")$"),  # uk
                re.compile(
                    r"^" + _PREFIXES + r"((?:\+|00)\d{2,3}[ -]?\(\d{3}\)[ -]?\d{4}[ -]?\d{4}" + _EXTENSION + r")$"
                ),  # US
                re.compile(r"^" + _PREFIXES + r"(\d{3}[- ]?\d{4}" + _EXTENSION + r")$"),  # US
                re.compile(r"^" + _PREFIXES + r"(\(\d{3}\)[- ]\d{3}[- ]?\d{4}" + _EXTENSION + r")$"),  # US
                re.compile(r"^" + _PREFIXES + r"(\d{3}[- ]\d{3}[- ]?\d{4}" + _EXTENSION + r")$"),  # US
                re.compile(r"^" + _PREFIXES + r"((?:\+|00)1[- ]\d{3}[- ]\d{3}[- ]?\d{4}" + _EXTENSION + r")$"),  # US
                re.compile(r"^" + _PREFIXES + r"(1[- ]\d{3}[- ]\d{3}[- ]?\d{4}" + _EXTENSION + r")$"),  # US
                re.compile(r"^" + _PREFIXES + r"(\d{3}[- ]\d{3}[- ]\d{3}[- ]?\d{4}" + _EXTENSION + r")$"),  # US
                re.compile(
                    r"^" + _PREFIXES + r"((?:\+|00)\d{2,3}[- ]\d{3}(?:[- ]\d{2}){3}" + _EXTENSION + r")$"
                ),  # Unknown
                re.compile(
                    r"^" + _PREFIXES + r"((?:\+|00)\d{1,3}\.\d{3}\.\d{3}\.\d{4}" + _EXTENSION + r")$"
                ),  # Unknown
                re.compile(r"^" + _PREFIXES + r"(\d{3}\.\d{3}\.\d{4}" + _EXTENSION + r")$"),  # French
            ],
        )

    def get_span_length_required_to_check(self) -> int:
        """Get the minimum span length needed for phone number detection.

        Returns:
            The minimum number of characters needed to detect a phone number with prefix.
        """
        return len("Contact: ") + 5

    def is_of_this_type_with_span(self, text: str) -> tuple[bool, tuple[int, int] | None]:
        """Check if text contains a phone number and return its span.

        Args:
            text: The text to check.

        Returns:
            A tuple of (is_match, span) where span is (start, end) positions or None.
        """
        return super().is_of_this_type_with_span(text)

    def is_of_this_type(self, text: str) -> bool:
        """Check if text is a valid phone number.

        Args:
            text: The text to check.

        Returns:
            True if text matches a phone number pattern, False otherwise.
        """
        return self.is_of_this_type_with_span(text)[0]
