"""Person-related identifiers for detecting names, demographics, and personal attributes.

This module provides identifiers for recognizing person names, job titles, gender,
ethnicity, year of birth, marital status, and religion.
"""

import re
from collections.abc import Callable, Iterable
from datetime import datetime
from pathlib import Path

from risk_assessment.classification.identifiers import DictionaryIdentifier, Identifier


def _load_names(file_name: str) -> set[str]:
    """Load names from a file into a set.

    Args:
        file_name: Path to the file containing names (one per line).

    Returns:
        Set of lowercase names from the file.
    """
    with (Path(__file__).parent / file_name).open("r") as reader:
        return {name.strip().casefold() for name in reader if len(name.strip())}


class Name(Identifier):
    """Identifier for first names (given names).

    Loads and validates first names from data files, supporting female, male,
    and other name categories.

    Attributes:
        _female_names: Set of female first names.
        _male_names: Set of male first names.
        _other_names: Set of other first names.

    Example:
        >>> identifier = Name()
        >>> identifier.is_of_this_type("John")
        True
        >>> identifier.is_of_this_type("Mary")
        True
    """

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
        """Check if text is a valid first name.

        Args:
            text: The text to check.

        Returns:
            True if text matches any known first name, False otherwise.
        """
        text = text.casefold()
        return text in self._female_names or text in self._male_names or text in self._other_names


class Surname(Identifier):
    """Identifier for surnames (last names/family names).

    Loads and validates surnames from a data file.

    Attributes:
        _surnames: Set of known surnames.

    Example:
        >>> identifier = Surname()
        >>> identifier.is_of_this_type("Smith")
        True
        >>> identifier.is_of_this_type("Johnson")
        True
    """

    def __init__(self, data_file: str = "data/surnames.csv", loader: Callable[[str], set[str]] = _load_names) -> None:
        """Initialize the Surname identifier.

        Args:
            data_file: Path to the surnames data file. Defaults to "data/surnames.csv".
            loader: Function to load names from file. Defaults to _load_names.
        """
        self._surnames = loader(data_file)

    def is_of_this_type(self, text: str) -> bool:
        """Check if text is a valid surname.

        Args:
            text: The text to check.

        Returns:
            True if text matches a known surname, False otherwise.
        """
        return text.casefold() in self._surnames


class PersonPrefix(Identifier):
    """Identifier for person name prefixes/titles.

    Recognizes common titles like Mr., Mrs., Dr., etc.

    Attributes:
        _prefixes: Set of valid person prefixes.

    Example:
        >>> identifier = PersonPrefix()
        >>> identifier.is_of_this_type("Dr.")
        True
        >>> identifier.is_of_this_type("Mrs")
        True
    """

    def __init__(
        self, prefixes: Iterable[str] = ["Mrs.", "Ms.", "Miss", "Mr.", "Dr.", "Mrs", "Ms", "Mr", "Dr", "Mx", "Mx."]
    ) -> None:
        self._prefixes = {prefix.casefold() for prefix in prefixes}

    def is_of_this_type(self, text: str) -> bool:
        """Check if text is a valid person prefix.

        Args:
            text: The text to check.

        Returns:
            True if text matches a known prefix, False otherwise.
        """
        return text.casefold() in self._prefixes


class PersonSuffix(Identifier):
    """Identifier for person name suffixes.

    Recognizes common suffixes like Jr., Sr., PhD, MD, etc.

    Attributes:
        _suffixes: Set of valid person suffixes.

    Example:
        >>> identifier = PersonSuffix()
        >>> identifier.is_of_this_type("Jr.")
        True
        >>> identifier.is_of_this_type("PhD")
        True
    """

    def __init__(
        self,
        suffixes: Iterable[str] = ["MD", "DDS", "PhD", "DVM", "Jr.", "Sr.", "I", "II", "III", "IV", "V"],
    ) -> None:
        self._suffixes = {suffix.casefold() for suffix in suffixes}

    def is_of_this_type(self, text: str) -> bool:
        """Check if text is a valid person suffix.

        Args:
            text: The text to check.

        Returns:
            True if text matches a known suffix, False otherwise.
        """
        return text.casefold() in self._suffixes


class Person(Identifier):
    """Identifier for full person names.

    Validates person names by checking combinations of first names, surnames,
    prefixes, and suffixes. Handles single names, two-part names, and longer
    names with titles.

    Attributes:
        _name: Name identifier instance.
        _surname: Surname identifier instance.
        _prefix: PersonPrefix identifier instance.
        _suffix: PersonSuffix identifier instance.

    Example:
        >>> identifier = Person()
        >>> identifier.is_of_this_type("John Smith")
        True
        >>> identifier.is_of_this_type("Dr. Jane Doe")
        True
        >>> identifier.is_of_this_type("Mary Johnson Jr.")
        True
    """

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
        """Check if text represents a valid person name.

        Validates single names, two-part names, and longer names with at least
        90% of parts being valid name components.

        Args:
            text: The text to check.

        Returns:
            True if text represents a valid person name, False otherwise.
        """
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
    """Identifier for job titles and occupations.

    Example:
        >>> identifier = Job()
        >>> identifier.is_of_this_type("Software Engineer")
        True
        >>> identifier.is_of_this_type("Doctor")
        True
    """

    def __init__(self) -> None:
        """Initialize the Job identifier with job titles from data file."""
        super().__init__("Job Title", _load_names("data/job-titles.csv"), False)


class Gender(DictionaryIdentifier):
    """Identifier for gender values (short forms).

    Recognizes common gender abbreviations and full forms.

    Example:
        >>> identifier = Gender()
        >>> identifier.is_of_this_type("M")
        True
        >>> identifier.is_of_this_type("female")
        True
    """

    def __init__(self) -> None:
        """Initialize the Gender identifier with gender terms."""
        super().__init__("Gender", ["male", "m", "f", "female"], False)


class GenderLong(DictionaryIdentifier):
    """Identifier for gender values (full forms only).

    Recognizes only full gender terms, not abbreviations.

    Example:
        >>> identifier = GenderLong()
        >>> identifier.is_of_this_type("male")
        True
        >>> identifier.is_of_this_type("female")
        True
    """

    def __init__(self) -> None:
        """Initialize the GenderLong identifier with full gender terms."""
        super().__init__("Gender", ["male", "female"], False)


class Etnicity(DictionaryIdentifier):
    """Identifier for ethnicity values.

    Recognizes common ethnicity terms and racial categories.

    Example:
        >>> identifier = Etnicity()
        >>> identifier.is_of_this_type("Asian")
        True
        >>> identifier.is_of_this_type("Caucasian")
        True
    """

    def __init__(self) -> None:
        """Initialize the Etnicity identifier with ethnicity terms."""
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
    """Identifier for year of birth values.

    Validates 4-digit years within a plausible range (current year - 120 to current year).

    Attributes:
        pattern: Regex pattern for 4-digit years.
        current_year: Current year.
        lower_bound: Minimum valid year (120 years ago).

    Example:
        >>> identifier = YearOfBirth()
        >>> identifier.is_of_this_type("1990")
        True
        >>> identifier.is_of_this_type("1850")
        False
    """

    def __init__(self) -> None:
        """Initialize the YearOfBirth identifier with current year bounds."""
        self.pattern = re.compile(r"^\d{4}$")
        self.current_year = datetime.now().date().year
        self.lower_bound = self.current_year - 120

    def is_of_this_type(self, text: str) -> bool:
        """Check if text is a valid year of birth.

        Args:
            text: The text to check.

        Returns:
            True if text is a 4-digit year within valid range, False otherwise.
        """
        if not self.pattern.match(text):
            return False

        try:
            value = int(text, 10)

            return str(value) == text and (self.lower_bound <= value <= self.current_year)

        except ValueError:
            return False


def _load_marital_status() -> Iterable[str]:
    """Load marital status terms from data file.

    Returns:
        Iterable of marital status terms.
    """
    terms: set[str] = set()

    with (Path(__file__).parent / "data" / "en" / "marital_status.csv").open("r") as input:
        for line in input:
            parts = line.split(",")
            for part in parts:
                terms.add(part.casefold())

    return terms


class MaritalStatus(DictionaryIdentifier):
    """Identifier for marital status values.

    Example:
        >>> identifier = MaritalStatus()
        >>> identifier.is_of_this_type("married")
        True
        >>> identifier.is_of_this_type("single")
        True
    """

    def __init__(self) -> None:
        """Initialize the MaritalStatus identifier with marital status terms."""
        super().__init__("MaritalStatus", _load_marital_status(), False)


def _load_religions() -> Iterable[str]:
    """Load religion terms from data file.

    Returns:
        Iterable of religion terms.
    """
    terms: set[str] = set()

    with (Path(__file__).parent / "data" / "en" / "religions.csv").open("r") as input:
        for line in input:
            parts = line.split(",")
            terms.add(parts[0].casefold())
            terms.add(parts[1].casefold())

    return terms


class Religion(DictionaryIdentifier):
    """Identifier for religion values.

    Example:
        >>> identifier = Religion()
        >>> identifier.is_of_this_type("Christian")
        True
        >>> identifier.is_of_this_type("Buddhist")
        True
    """

    def __init__(self) -> None:
        """Initialize the Religion identifier with religion terms."""
        super().__init__("Religion", _load_religions(), False)
