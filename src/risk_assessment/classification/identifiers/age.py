"""Age identifier for detecting age values in various formats.

This module provides identifiers for recognizing age values, including numeric ages,
age expressions with units (years, months, weeks), and age-related phrases.
"""

from contextlib import suppress
from re import I, Pattern, U, compile

from word2number.w2n import word_to_num

from risk_assessment.classification.identifiers import Identifier


class Age(Identifier):
    """Basic age identifier for numeric age values.

    Validates that a value represents a plausible human age (18-91 years).

    Example:
        >>> identifier = Age()
        >>> identifier.is_of_this_type("25")
        True
        >>> identifier.is_of_this_type(45)
        True
        >>> identifier.is_of_this_type("150")
        False
    """

    def is_of_this_type(self, text: str | int) -> bool:
        """Check if text or integer represents a valid age.

        Args:
            text: The text string or integer to check.

        Returns:
            True if the value is between 18 and 91 (inclusive), False otherwise.
        """
        int_value: int = 10_000_000

        if isinstance(text, str):
            with suppress(ValueError):
                int_value = int(text, base=10)

                if text != str(int_value):
                    return False

        elif isinstance(text, int):
            int_value = text

        return 17 < int_value <= 91


class AgeImproved(Identifier):
    """Advanced age identifier supporting multiple age expression formats.

    Recognizes various age patterns including:
    - Numeric ages with units (years, months, weeks)
    - Age with gender suffixes (e.g., "25 year old man")
    - Date of birth patterns
    - Death age patterns
    - Word-based age expressions

    Attributes:
        SUFFIXES: Regex pattern for gender/person suffixes.
        age_pattern_with_gender: List of patterns matching ages with gender suffixes.
        age_pattern: List of patterns matching various age formats.

    Example:
        >>> identifier = AgeImproved()
        >>> identifier.is_of_this_type("25 year old")
        True
        >>> identifier.is_of_this_type("30-year-old")
        True
        >>> identifier.is_of_this_type("45 yo")
        True
        >>> identifier.is_of_this_type("died at age 80")
        True
    """

    SUFFIXES = r"(?:man|woman|male|female|daughter|son|niece|nephew|lady|gentleman)"

    age_pattern_with_gender: list[Pattern[str]] = [
        compile(r"^([0-9]+)\s*yrs\.?\s+" + SUFFIXES, I | U),
        compile(r"^([0-9]+)\s*years\.?\s+" + SUFFIXES, I | U),
        compile(r"^([0-9]+)\s*y/o\.?\s+" + SUFFIXES, I | U),
        compile(r"^([0-9]+)\s*yo\.?\s+" + SUFFIXES, I | U),
    ]

    age_pattern: list[Pattern[str]] = [
        compile(r"^([0-9]+)\s+year old$", I | U),
        compile(r"^([0-9]+)-year old$", I | U),
        compile(r"^([0-9]+)-year-old$", I | U),
        compile(r"^([0-9]+)\s+years\s+of\s+age$", I | U),
        compile(r"^([0-9]+)\s+years old$", I | U),
        compile(r"^([0-9]+)-years old$", I | U),
        compile(r"^([0-9]+)-years-old$", I | U),
        compile(r"^([0-9]+)\s+yrs\.?\s+old$", I | U),
        compile(r"^([0-9]+)-yrs\.?\s+old$", I | U),
        compile(r"^([0-9]+)-yrs-old$", I | U),
        compile(r"^([0-9]+)\s+yr(\.)? old$", I | U),
        compile(r"^([0-9]+)-yr(\.)? old$", I | U),
        compile(r"^([0-9]+)-yr-old$", I | U),
        compile(r"^([0-9]+)\s+yo$", I | U),
        compile(r"^([0-9]+)\s+y/o$", I | U),
        compile(r"^([0-9]+)\s+([0-9]+)/[0-9]+\s+y/?o$", I | U),
        compile(r"^([0-9]+) weeks old$", I | U),
        compile(r"^([0-9]+)weeks old$", I | U),
        compile(r"^([0-9]+)-weeks old$", I | U),
        compile(r"^([0-9]+)-weeks-old$", I | U),
        compile(r"^([0-9]+) months old$", I | U),
        compile(r"^([0-9]+)months old$", I | U),
        compile(r"^([0-9]+)-months old$", I | U),
        compile(r"^([0-9]+)-months-old$", I | U),
        compile(r"^at age\s+([0-9]+)$", I | U),
        compile(r"^at age\s+of\s+([0-9]+)$", I | U),
        compile(r"^at age\s+([0-9]+) and ([0-9]+)$", I | U),
        compile(r"^at age\s+([0-9]+) and ([0-9]+)/[0-9]+$", I | U),
        compile(r"^at the age of ([0-9]+)$", I | U),
        compile(r"^([0-9]+) year and ([0-9]+) month$", I | U),
        compile(r"^([0-9]+) years and ([0-9]+) months$", I | U),
        compile(r"^([0-9]+) yrs and ([0-9]+) month$", I | U),
        compile(r"^([0-9]+)yr and ([0-9]+)mo$", I | U),
        compile(r"^([0-9]+) yrs ([0-9]+)/[0-9]+ mo$", I | U),
        compile(r"^([0-9]+) years ([0-9]+)/[0-9]+ mo$", I | U),
        compile(r"^dob:?\s+([0-9]+)$", I | U),
        compile(r"^dob:?\s+\d{1,2}(?:\s+|-)\d{1,2}(?:\s+|-)\d{4}$", I | U),
        compile(r"^date\s+of\s+birth\s*:\s+([0-9]+)/([0-9]+)/([0-9]+)$", I | U),
        compile(r"^date\s+of\s+birth\s*:\s+([0-9]+)$", I | U),
        compile(r"^dob:\s+[0-9][0-9]-([0-9]+)-([0-9]+)$", I | U),  # DOB: 03-28-1934
        compile(r"^dob:\s+[0-9][0-9]/([0-9]+)/([0-9]+)$", I | U),  # DOB: 03/28/1934
        compile(r"^dob\s+[0-9][0-9]-([0-9]+)-([0-9]+)"),  # DOB 03-28-1934
        compile(r"age:?\s*([1-9][0-9]*)$", I | U),
        compile(r"alive\s+([1-9][0-9]*)$", I | U),
        compile(r"comment:\s*age\s+([1-9][0-9]*)$", I | U),
        compile(r"comments:\s*age\s+([1-9][0-9]*)$", I | U),
        compile(r"comments:\s*died\s+age\s+([1-9][0-9]*)$", I | U),
        compile(r"^died\s+age\s+([0-9]+)$", I | U),
        compile(r"^deceased\s+age\s+([0-9]+)$", I | U),
        compile(r"^deceased\s+([0-9]+)$", I | U),
        compile(r"^died\s+at\s+([0-9]+)$", I | U),
        compile(r"^died\s+([0-9]+)-old\s+age$", I | U),
        compile(r"^died\s+of\s+([\w|'|-]+\s+){1,3}at\s+([0-9]+)$", I | U),
        compile(r"^died\s+of\s+([\w|'|-]+\s+){1,3}at\s+age\s+(of\s+)?([0-9]+)$", I | U),
        compile(r"^passed\s+away\s+at\s+age\s+([0-9]+)$", I | U),
    ]

    def _try_birthday_patterns(self, input: str) -> bool:
        """Check if text matches birthday-related age patterns.

        Args:
            input: The text to check.

        Returns:
            True if text matches birthday patterns like "on his 25th birthday", False otherwise.
        """
        input = input.lower()
        if (input.startswith("on his") or input.startswith("on her")) and input.endswith("birthday"):
            middle_part = input[len("on his") : -len("birthday")].strip()

            return valid_number(middle_part)

        return False

    def _try_word_pattern(self, text: str) -> bool:
        """Check if text matches word-based age patterns.

        Args:
            text: The text to check.

        Returns:
            True if text matches patterns like "twenty-five years old", False otherwise.
        """
        if self._try_birthday_patterns(text):
            return True

        for suffix in ["year old", "years old", "yrs old", "months old", "days old", "weeks old", "-years-old"]:
            if text.endswith(suffix):
                text = text[0 : -len(suffix)]
                if valid_number(text):
                    return True

        return False

    def is_of_this_type(self, text: str) -> bool:
        """Check if text represents an age in any supported format.

        Args:
            text: The text to check.

        Returns:
            True if text matches any age pattern, False otherwise.
        """
        return (
            any(pattern.match(text) for pattern in self.age_pattern)
            or any(pattern.match(text) for pattern in self.age_pattern_with_gender)
            or self._try_word_pattern(text)
        )


def valid_number(text: str) -> bool:
    """Check if text represents a valid number using word-to-number conversion.

    Args:
        text: The text to check (e.g., "twenty-five", "thirty").

    Returns:
        True if text can be converted to an integer, False otherwise.
    """
    try:
        num = word_to_num(text.strip().casefold())

        if type(num) is int:
            return True
    except Exception:
        return False

    return False
