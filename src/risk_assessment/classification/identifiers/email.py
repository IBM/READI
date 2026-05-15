"""Email address identifier for detecting email addresses in text.

This module provides an identifier that recognizes email addresses using
regex pattern matching.
"""

import re

from risk_assessment.classification.identifiers import Identifier


class Email(Identifier):
    """Identifier for detecting email addresses.

    Uses a regex pattern to identify valid email address formats. The pattern
    matches standard email formats with alphanumeric characters, dots, hyphens,
    underscores, and plus signs in the local part, and standard domain formats.

    Attributes:
        pattern: Compiled regex pattern for matching email addresses.

    Example:
        >>> identifier = Email()
        >>> print(identifier.is_of_this_type("user@example.com"))
        True
        >>> print(identifier.is_of_this_type("john.doe+tag@company.co.uk"))
        True
        >>> print(identifier.is_of_this_type("not-an-email"))
        False
        >>> print(identifier.is_of_this_type("missing@domain"))
        False

    Note:
        The pattern requires a complete match (anchored with ^ and $), so it
        works best when the text contains only the email address. For finding
        emails within larger text, use entity extraction methods instead.
    """

    pattern = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$")

    def is_of_this_type(self, text: str) -> bool:
        """Check if the text is a valid email address.

        Args:
            text: The text string to check.

        Returns:
            True if the text matches the email pattern, False otherwise.

        Example:
            >>> identifier = Email()
            >>> identifier.is_of_this_type("admin@example.org")
            True
            >>> identifier.is_of_this_type("invalid.email")
            False
        """
        m = self.pattern.match(text)

        if m:
            return True
        return False
