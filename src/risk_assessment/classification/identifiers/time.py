import importlib.resources
from collections.abc import Iterable

from risk_assessment.classification.identifiers import DictionaryIdentifier


class DayOfTheWeek(DictionaryIdentifier):
    def __init__(self) -> None:
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
    res = importlib.resources.files(__package__).joinpath("data/all_day_of_the_week_names.txt")
    with res.open("r") as input:
        return {day.strip().casefold() for day in input}


class InternationalDayOfTheWeek(DictionaryIdentifier):
    def __init__(self) -> None:
        super().__init__(
            "DayOfWeek",
            _load_all_day_of_week(),
        )
