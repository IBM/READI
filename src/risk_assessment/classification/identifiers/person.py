import importlib.resources
import re
from collections.abc import Callable, Iterable
from datetime import datetime

from risk_assessment.classification.identifiers import DictionaryIdentifier, Identifier


def _load_names(file_name: str) -> set[str]:
    resource = importlib.resources.files(__package__).joinpath(file_name)
    with resource.open("r") as reader:
        return {name.strip().casefold() for name in reader if len(name.strip())}


class Name(Identifier):
    def __init__(
        self,
        female: str = "data/female_first_names.csv",
        male: str = "data/male_first_names.csv",
        other: str = "data/male_first_names.csv",
        loader: Callable[[str], set[str]] = _load_names,
    ) -> None:
        self._female_names = loader(female)
        self._male_names = loader(male)
        self._other_names = loader(other)

    def is_of_this_type(self, text: str) -> bool:
        text = text.casefold()
        return text in self._female_names or text in self._male_names or text in self._other_names


class Surname(Identifier):
    def __init__(self, data_file: str = "data/surnames.csv", loader: Callable[[str], set[str]] = _load_names) -> None:
        self._surnames = loader(data_file)

    def is_of_this_type(self, text: str) -> bool:
        return text.casefold() in self._surnames


class PersonPrefix(Identifier):
    def __init__(
        self, prefixes: Iterable[str] = ["Mrs.", "Ms.", "Miss", "Mr.", "Dr.", "Mrs", "Ms", "Mr", "Dr", "Mx", "Mx."]
    ) -> None:
        self._prefixes = {prefix.casefold() for prefix in prefixes}

    def is_of_this_type(self, text: str) -> bool:
        return text.casefold() in self._prefixes


class PersonSuffix(Identifier):
    def __init__(
        self,
        suffixes: Iterable[str] = ["MD", "DDS", "PhD", "DVM", "Jr.", "Sr.", "I", "II", "III", "IV", "V"],
    ) -> None:
        self._suffixes = {suffix.casefold() for suffix in suffixes}

    def is_of_this_type(self, text: str) -> bool:
        return text.casefold() in self._suffixes


class Person(Identifier):
    def __init__(
        self,
        name: Name = Name(),
        surname: Surname = Surname(),
        prefixes: PersonPrefix = PersonPrefix(),
        suffixes: PersonSuffix = PersonSuffix(),
    ) -> None:
        self._name = name
        self._surname = surname
        self._prefix = prefixes
        self._suffix = suffixes

    def is_of_this_type(self, text: str) -> bool:
        parts = text.casefold().split()

        if len(parts) == 1:
            return self._name.is_of_this_type(text) or self._surname.is_of_this_type(text)
        elif len(parts) == 2:
            return (self._name.is_of_this_type(parts[0]) and self._surname.is_of_this_type(parts[1])) or (
                self._name.is_of_this_type(parts[1]) and self._surname.is_of_this_type(parts[0])
            )
        else:
            valid_parts = [
                part
                for part in parts
                if self._name.is_of_this_type(part)
                or self._surname.is_of_this_type(part)
                or self._suffix.is_of_this_type(part)
                or self._prefix.is_of_this_type(part)
            ]
            return float(len(valid_parts)) >= float(len(parts)) * 0.9


class Job(DictionaryIdentifier):
    def __init__(self) -> None:
        super().__init__("Job Title", _load_names("data/job-titles.csv"), False)


class Gender(DictionaryIdentifier):
    def __init__(self) -> None:
        super().__init__("Gender", ["male", "m", "f", "female"], False)


class GenderLong(DictionaryIdentifier):
    def __init__(self) -> None:
        super().__init__("Gender", ["male", "female"], False)


class Etnicity(DictionaryIdentifier):
    def __init__(self) -> None:
        super().__init__(
            "Etnicity",
            [
                "American Indian",
                "Amerindian",
                "Asian",
                "Indian",
                "Black",
                "African American",
                "White",
                "Caucasian",
                "European",
                "Other",
            ],
            False,
        )


class YearOfBirth(Identifier):
    def __init__(self) -> None:
        self.pattern = re.compile(r"^\d{4}$")
        self.current_year = datetime.now().date().year
        self.lower_bound = self.current_year - 120

    def is_of_this_type(self, text: str) -> bool:
        if not self.pattern.match(text):
            return False

        try:
            value = int(text, 10)

            return str(value) == text and (self.lower_bound <= value <= self.current_year)

        except ValueError:
            return False


def _load_marital_status() -> Iterable[str]:
    res = importlib.resources.files(__package__).joinpath("data/en/marital_status.csv")

    terms: set[str] = set()

    with res.open("r") as input:
        for line in input:
            parts = line.split(",")
            for part in parts:
                terms.add(part.casefold())

    return terms


class MaritalStatus(DictionaryIdentifier):
    def __init__(self) -> None:
        super().__init__("MaritalStatus", _load_marital_status(), False)


def _load_religions() -> Iterable[str]:
    res = importlib.resources.files(__package__).joinpath("data/en/religions.csv")

    terms: set[str] = set()

    with res.open("r") as input:
        for line in input:
            parts = line.split(",")
            terms.add(parts[0].casefold())
            terms.add(parts[1].casefold())

    return terms


class Religion(DictionaryIdentifier):
    def __init__(self) -> None:
        super().__init__("Religion", _load_religions(), False)
