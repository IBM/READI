"""Time identifier for detecting day of the week names.

This module provides identifiers for recognizing day names in English
and multiple international languages.
"""

from collections.abc import Iterable
from pathlib import Path

from risk_assessment.classification.identifiers import DictionaryIdentifier


class DayOfTheWeek(DictionaryIdentifier):
    """Identifier for English day of the week names.

    Recognizes full and abbreviated English day names.

    Example:
        >>> identifier = DayOfTheWeek()
        >>> identifier.is_of_this_type("Monday")
        True
        >>> identifier.is_of_this_type("Fri")
        True
    """

    def __init__(self) -> None:
        """Initialize the DayOfTheWeek identifier with English day names."""
        super().__init__(
            "DayOfWeek",
            {
                "Monday",
                "Mon",
                "Tuesday",
                "Tue",
                "Wednesday",
                "Wed",
                "Thursday",
                "Thu",
                "Friday",
                "Fri",
                "Saturday",
                "Sat",
                "Sunday",
                "Sun",
            },
            False,
        )


def _load_all_day_of_week() -> Iterable[str]:
    """Load day of the week names from multiple languages.

    Returns:
        Iterable of day names in various languages.
    """
    with (Path(__file__).parent / "data" / "all_day_of_the_week_names.txt").open("r") as input:
        return {day.strip().casefold() for day in input}


class InternationalDayOfTheWeek(DictionaryIdentifier):
    """Identifier for international day of the week names.

    Recognizes day names in multiple languages.

    Example:
        >>> identifier = InternationalDayOfTheWeek()
        >>> identifier.is_of_this_type("lunes")  # Spanish for Monday
        True
        >>> identifier.is_of_this_type("montag")  # German for Monday
        True
    """

    def __init__(self) -> None:
        """Initialize the InternationalDayOfTheWeek identifier with multi-language day names."""
        super().__init__(
            "DayOfWeek",
            _load_all_day_of_week(),
        )
