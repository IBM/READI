"""Publication identifier for detecting ISBN, ISSN, and CODEN codes.

This module provides identifiers for recognizing publication identifiers
including ISBN (books), ISSN (serials), and CODEN (scientific publications).
"""

import re

from risk_assessment.classification.identifiers import Identifier


class ISBN(Identifier):
    """Identifier for ISBN (International Standard Book Number).

    Validates both ISBN-10 and ISBN-13 formats with checksum verification.

    Example:
        >>> identifier = ISBN()
        >>> identifier.is_of_this_type("978-0-306-40615-7")
        True
        >>> identifier.is_of_this_type("0-306-40615-2")
        True
    """

    _pattern = re.compile(r"(\d{3})[ \-]?(\d{1,5})[ \-]?(\d{1,7})[ \-]?(\d{1,6})[ \-]?(\d)")
    _pattern_10 = re.compile(r"(\d{1,5})[ \-]?(\d{1,7})[ \-]?(\d{1,6})[ \-]?([0-9X])")

    def _check_isbn_10(self, text: str) -> bool:
        """Check if text is a valid ISBN-10.

        Args:
            text: The text to check.

        Returns:
            True if valid ISBN-10 with correct checksum, False otherwise.
        """
        match = ISBN._pattern_10.match(text)

        if match and 10 == sum([len(group) for group in match.groups()]):
            return self._valid_checksum_10("".join(match.groups()))
        return False

    def _valid_checksum_10(self, digits: str) -> bool:
        """Validate ISBN-10 checksum.

        Args:
            digits: The 10-digit ISBN string.

        Returns:
            True if checksum is valid, False otherwise.
        """
        parity = 10 if digits[-1] == "X" else int(digits[-1])

        checksum = (
            sum([position * int(digit) for position, digit in zip(range(len(digits), 1, -1), digits, strict=False)])
            % 11
        )

        return (11 - checksum) % 11 == parity

    def _check_isbn(self, text: str) -> bool:
        """Check if text is a valid ISBN-13.

        Args:
            text: The text to check.

        Returns:
            True if valid ISBN-13 with correct checksum, False otherwise.
        """
        match = ISBN._pattern.match(text)

        if match:
            groups = list(match.groups())

            if sum([len(group) for group in groups]) == 13 and self._match_prefix(groups[0]):
                return self._valid_checksum("".join(groups))

        return False

    def _valid_checksum(self, digits: str) -> bool:
        """Validate ISBN-13 checksum.

        Args:
            digits: The 13-digit ISBN string.

        Returns:
            True if checksum is valid, False otherwise.
        """
        even_sum = sum([3 * int(digit) for position, digit in enumerate(digits) if position % 2 == 1])
        odd_sum = sum([int(digit) for position, digit in enumerate(digits) if position % 2 == 0])
        return (even_sum + odd_sum) % 10 == 0

    def _match_prefix(self, prefix: str) -> bool:
        """Check if prefix is valid for ISBN-13.

        Args:
            prefix: The 3-digit prefix.

        Returns:
            True if prefix is 978 or 979, False otherwise.
        """
        return prefix == "978" or prefix == "979"

    def is_of_this_type(self, text: str) -> bool:
        """Check if text is a valid ISBN (10 or 13).

        Args:
            text: The text to check.

        Returns:
            True if valid ISBN-10 or ISBN-13, False otherwise.
        """
        return self._check_isbn(text) or self._check_isbn_10(text)


class CODEN(Identifier):
    """Identifier for CODEN (bibliographic codes for scientific publications).

    CODEN is a 6-character alphanumeric code.

    Example:
        >>> identifier = CODEN()
        >>> identifier.is_of_this_type("NATUAS")
        True
    """

    _pattern = re.compile(r"^[0-9A-Z]{6}$")

    def is_of_this_type(self, text: str) -> bool:
        """Check if text is a valid CODEN.

        Args:
            text: The text to check.

        Returns:
            True if text is a 6-character alphanumeric code, False otherwise.
        """
        match = CODEN._pattern.match(text.strip())

        return match is not None


class ISSN(Identifier):
    """Identifier for ISSN (International Standard Serial Number).

    ISSN is an 8-digit code for periodicals with checksum validation.

    Example:
        >>> identifier = ISSN()
        >>> identifier.is_of_this_type("0378-5955")
        True
    """

    _pattern = re.compile(r"^([0-9]{4})-?([0-9]{3})([0-9xX])$")

    def is_of_this_type(self, text: str) -> bool:
        """Check if text is a valid ISSN.

        Args:
            text: The text to check.

        Returns:
            True if valid ISSN with correct checksum, False otherwise.
        """
        match = ISSN._pattern.match(text)

        if match:
            return self._validate_checksum(match.group(1) + match.group(2) + match.group(3))

        return False

    def _validate_checksum(self, digits: str) -> bool:
        """Validate ISSN checksum.

        Args:
            digits: The 8-digit ISSN string.

        Returns:
            True if checksum is valid, False otherwise.
        """
        parity = 10 if digits[-1] == "X" else int(digits[-1])

        checksum = (
            sum([position * int(digit) for position, digit in zip(range(len(digits), 1, -1), digits, strict=False)])
            % 11
        )

        return (11 - checksum) % 11 == parity
