"""Identifier base classes for detecting specific types of sensitive data.

This module provides the foundational classes for building identifiers that
can recognize specific types of sensitive information (PII/PHI) such as emails,
phone numbers, credit cards, national IDs, and more.
"""

import logging
from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass
from random import choice
from re import Pattern
from typing import Any, cast

from SPARQLWrapper import JSON, SPARQLWrapper

logger = logging.getLogger(__name__)


class Identifier(ABC):
    """Abstract base class for all identifiers.

    An identifier is responsible for determining whether a given text string
    matches a specific type of sensitive data (e.g., email, SSN, credit card).
    Subclasses implement the detection logic using various methods like regex,
    dictionaries, checksums, or custom algorithms.

    Example:
        >>> class EmailIdentifier(Identifier):
        ...     def is_of_this_type(self, text: str) -> bool:
        ...         return "@" in text and "." in text  # Simplified
        >>>
        >>> identifier = EmailIdentifier()
        >>> print(identifier.is_of_this_type("user@example.com"))
        True
        >>> print(identifier.is_of_this_type("not an email"))
        False
    """

    @abstractmethod
    def is_of_this_type(self, text: str) -> bool:
        """Check if the text matches this identifier's type.

        Args:
            text: The text string to check.

        Returns:
            True if the text matches this type, False otherwise.

        Raises:
            NotImplementedError: This is an abstract method that must be implemented by subclasses.
        """
        raise NotImplementedError()

    def __str__(self) -> str:
        """Return the string representation of this identifier.

        Returns:
            The class name of the identifier.
        """
        return self.__class__.__name__

    def is_need_span(self) -> bool:
        """Check if this identifier needs span information.

        Some identifiers need to know the exact character positions within
        a larger text context. Override this to return True if needed.

        Returns:
            False by default. Subclasses can override to return True.
        """
        return False


class LuhnIdentifier(Identifier):
    """Base class for identifiers that use the Luhn checksum algorithm.

    The Luhn algorithm is a checksum formula used to validate identification
    numbers like credit cards, IMEI numbers, and some national IDs. This class
    provides the check_luhn() method that subclasses can use.

    Example:
        >>> class CreditCardIdentifier(LuhnIdentifier):
        ...     def is_of_this_type(self, text: str) -> bool:
        ...         if len(text) < 13 or len(text) > 19:
        ...             return False
        ...         return self.check_luhn(text)
        >>>
        >>> identifier = CreditCardIdentifier()
        >>> # Valid test credit card number
        >>> print(identifier.is_of_this_type("4532015112830366"))
        True
    """

    def check_luhn(self, text: str) -> bool:
        """Validate a number using the Luhn checksum algorithm.

        The Luhn algorithm validates identification numbers by computing
        a checksum. It's used for credit cards, IMEI numbers, and other
        numeric identifiers.

        Args:
            text: The text containing the number to validate. Non-numeric
                characters are automatically filtered out.

        Returns:
            True if the number passes the Luhn check, False otherwise.

        Example:
            >>> identifier = LuhnIdentifier()
            >>> # Valid credit card number
            >>> identifier.check_luhn("4532015112830366")
            True
            >>> # Invalid number
            >>> identifier.check_luhn("1234567890")
            False
        """
        text = "".join(d for d in text if d.isnumeric())
        n_digits = len(text)

        check: int = int(text[-1])
        sum = 0
        parity = (n_digits - 2) % 2

        for i in range(n_digits - 2, -1, -1):
            digit: int = int(text[i])

            if parity == i % 2:
                digit *= 2
                if digit > 9:
                    digit -= 9
            sum += digit

        return (10 - sum % 10) % 10 == check


class DictionaryIdentifier(Identifier):
    """Identifier that matches text against a dictionary of known values.

    This identifier checks if the input text exists in a predefined set of
    values. Useful for identifying things like country names, job titles,
    medical terms, or any categorical data.

    Attributes:
        type_name: Name of this identifier type.
        case_sensitive: Whether matching should be case-sensitive.
        data: Set of valid values for this identifier.

    Example:
        >>> countries = ["USA", "Canada", "Mexico", "UK"]
        >>> identifier = DictionaryIdentifier("Country", countries, case_sensitive=False)
        >>> print(identifier.is_of_this_type("usa"))
        True
        >>> print(identifier.is_of_this_type("France"))
        False
    """

    def __init__(self, type_name: str, data: Iterable[str], case_sensitive: bool = True):
        """Initialize the dictionary identifier.

        Args:
            type_name: Name to use for this identifier type.
            data: Iterable of valid values to match against.
            case_sensitive: If False, matching is case-insensitive (default: True).
        """
        self.type_name = type_name
        self.case_sensitive = case_sensitive

        self.data = set(data) if self.case_sensitive else {datapoint.casefold() for datapoint in data}

    def __str__(self) -> str:
        """Return the type name of this identifier."""
        return self.type_name

    def is_of_this_type(self, text: str) -> bool:
        """Check if text exists in the dictionary.

        Args:
            text: Text to check against the dictionary.

        Returns:
            True if text is in the dictionary, False otherwise.
        """
        if not self.case_sensitive:
            text = text.casefold()
        if text in self.data:
            return True

        return False


@dataclass
class RegexIdentifier(Identifier):
    r"""Identifier that uses regular expressions for pattern matching.

    This identifier checks if text matches one or more regex patterns.
    Useful for structured data like emails, phone numbers, IDs with
    specific formats, etc.

    Attributes:
        type_name: Name of this identifier type.
        patterns: List of compiled regex patterns to match against.

    Example:
        >>> import re
        >>> email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        >>> identifier = RegexIdentifier("Email", [email_pattern])
        >>> print(identifier.is_of_this_type("user@example.com"))
        True
        >>> print(identifier.is_of_this_type("not-an-email"))
        False
    """

    type_name: str
    patterns: list[Pattern[str]]

    def __str__(self) -> str:
        """Return the type name of this identifier."""
        return self.type_name

    def is_of_this_type(self, text: str) -> bool:
        """Check if text matches any of the regex patterns.

        Args:
            text: Text to match against the patterns.

        Returns:
            True if text matches at least one pattern, False otherwise.
        """
        for pattern in self.patterns:
            if pattern.match(text):
                return True

        return False


@dataclass
class RegexIdentifierWithSpan(RegexIdentifier):
    r"""Regex identifier that also returns the matched span positions.

    This specialized identifier not only checks if text matches a pattern,
    but also returns the exact character positions of the match. Useful
    when you need to extract or highlight the matched portion.

    Attributes:
        type_name: Name of this identifier type.
        patterns: List of compiled regex patterns with capture groups.

    Example:
        >>> import re
        >>> # Pattern with capture group for the actual SSN
        >>> ssn_pattern = re.compile(r'SSN:\s*(\d{3}-\d{2}-\d{4})')
        >>> identifier = RegexIdentifierWithSpan("SSN", [ssn_pattern])
        >>> text = "SSN: 123-45-6789"
        >>> is_match, span = identifier.is_of_this_type_with_span(text)
        >>> if is_match and span:
        ...     print(f"Found at positions {span[0]}-{span[1]}: {text[span[0]:span[1]]}")
        Found at positions 5-16: 123-45-6789
    """

    type_name: str
    patterns: list[Pattern[str]]

    def __str__(self) -> str:
        """Return the type name of this identifier."""
        return super().__str__()

    def get_span_length_required_to_check(self) -> int:  # type: ignore
        """Get the required span length for checking (not implemented).

        This method is a placeholder for future functionality.
        """
        pass

    def is_of_this_type(self, text: str) -> bool:
        """Check if text matches any pattern.

        Args:
            text: Text to match against the patterns.

        Returns:
            True if text matches at least one pattern, False otherwise.
        """
        return self.is_of_this_type_with_span(text)[0]

    def is_of_this_type_with_span(self, text: str) -> tuple[bool, tuple[int, int] | None]:
        """Check if text matches and return the span of the match.

        Uses the first capture group in the regex pattern to determine
        the exact span of the matched content.

        Args:
            text: Text to match against the patterns.

        Returns:
            Tuple of (is_match, span) where:
            - is_match: True if text matches a pattern
            - span: Tuple of (start, end) positions if matched, None otherwise
        """
        for pattern in self.patterns:
            matcher = pattern.match(text)

            if matcher is not None:
                if len(matcher.groups()) == 1:
                    g = matcher.group(1)
                    begin = text.index(g)
                    end = begin + len(g)
                    return (True, (begin, end))
        return (False, None)

    def is_need_span(self) -> bool:
        """Indicate that this identifier provides span information.

        Returns:
            True, as this identifier provides span positions.
        """
        return True


class LanguageBasedDictionaryIdentifier(DictionaryIdentifier):
    """Dictionary identifier with multi-language support.

    This identifier maintains separate dictionaries for different languages
    and can dynamically enrich its vocabulary by querying DBpedia for
    translations when a new language is encountered.

    Attributes:
        type_name: Name of this identifier type.
        case_sensitive: Whether matching is case-sensitive.
        languages: Set of currently supported language codes.
        data: Combined set of all terms across all languages.

    Example:
        >>> data = {
        ...     "en": ["Monday", "Tuesday", "Wednesday"],
        ...     "es": ["Lunes", "Martes", "Miércoles"]
        ... }
        >>> identifier = LanguageBasedDictionaryIdentifier("DayOfWeek", data)
        >>> print(identifier.is_of_this_type("Monday"))
        True
        >>> print(identifier.is_of_this_type("Lunes"))
        True
    """

    def __init__(self, type_name: str, data: dict[str, list[str]], case_sensitive: bool = True):
        """Initialize the language-based dictionary identifier.

        Args:
            type_name: Name to use for this identifier type.
            data: Dictionary mapping language codes to lists of terms.
            case_sensitive: If False, matching is case-insensitive (default: True).
        """
        super().__init__(type_name, sum(data.values(), []), case_sensitive)
        self.languages = set(data.keys())
        self._original = data

    def is_of_this_type(self, text: str) -> bool:
        """Check if text matches any term in any language.

        Args:
            text: Text to check against all language dictionaries.

        Returns:
            True if text matches a term in any language, False otherwise.
        """
        return self.is_of_this_type_with_language(text, "*")

    def is_of_this_type_with_language(self, text: str, language: str = "*") -> bool:
        """Check if text matches a term, optionally for a specific language.

        If the specified language is not yet loaded, attempts to enrich
        the dictionary by querying DBpedia for translations.

        Args:
            text: Text to check.
            language: Language code (e.g., "en", "es") or "*" for all languages.

        Returns:
            True if text matches a term, False otherwise.
        """
        if language not in self.languages and language != "*":
            _enrich_with_language(self, language)

        return super().is_of_this_type(text)

    def get_seed(self) -> str:
        """Get a random language code from the available languages.

        Returns:
            A random language code from the dictionary.
        """
        return choice(list(self._original.keys()))  # nosec

    def get_terms(self, language: str) -> Iterable[str]:
        """Get all terms for a specific language.

        Args:
            language: Language code to get terms for.

        Yields:
            Terms in the specified language.
        """
        yield from self._original[language]

    def add_language(self, language: str, terms: list[str]) -> None:
        """Add a new language with its terms to the dictionary.

        Args:
            language: Language code to add.
            terms: List of terms in that language.
        """
        self._original[language] = terms
        for t in terms:
            if self.case_sensitive:
                self.data.add(t)
            else:
                self.data.add(t.casefold())


def _enrich_with_language(identifier: LanguageBasedDictionaryIdentifier, language: str) -> None:
    """Enrich an identifier with terms from a new language via DBpedia.

    Queries DBpedia's SPARQL endpoint to find translations of existing terms
    in the identifier's dictionary and adds them for the new language.

    Args:
        identifier: The LanguageBasedDictionaryIdentifier to enrich.
        language: Language code to add (e.g., "fr", "de", "it").

    Note:
        This function requires internet connectivity to query DBpedia.
        Errors during querying are logged but don't raise exceptions.

    Example:
        >>> # Assuming identifier has English terms
        >>> # This will query DBpedia for French translations
        >>> _enrich_with_language(identifier, "fr")
    """
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    sparql.setReturnFormat(JSON)
    seed: str = identifier.get_seed()

    new_terms: set[str] = set()

    for term in identifier.get_terms(seed):
        query = (
            """PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?label
WHERE {
    ?item rdfs:label \""""
            + term
            + '"@'
            + seed
            + """;
          rdfs:label ?label .
}"""
        )
        sparql.setQuery(query)

        try:
            results: dict[str, Any] = cast(dict[str, Any], sparql.queryAndConvert())

            language_terms = [
                str(result["label"]["value"])
                for result in results["results"]["bindings"]
                if result["label"]["xml:lang"] == language
            ]

            for new_term in language_terms:
                if not identifier.case_sensitive:
                    new_terms.add(new_term.casefold())
        except Exception as e:
            logger.info(f"error querying sparql for {term}")
            logger.debug(str(e))
    identifier.add_language(language, list(new_terms))


@dataclass
class DummyIdentifier(Identifier):
    """A dummy identifier for testing purposes.

    This identifier always returns a fixed response regardless of input.
    Useful for testing and debugging classification pipelines.

    Attributes:
        type_name: Name of this identifier type.
        response: Fixed boolean response to return (default: False).

    Example:
        >>> # Always returns True
        >>> always_match = DummyIdentifier("AlwaysMatch", response=True)
        >>> print(always_match.is_of_this_type("anything"))
        True
        >>>
        >>> # Always returns False
        >>> never_match = DummyIdentifier("NeverMatch", response=False)
        >>> print(never_match.is_of_this_type("anything"))
        False
    """

    type_name: str
    response: bool = False

    def __str__(self) -> str:
        """Return the type name of this identifier."""
        return self.type_name

    def is_of_this_type(self, text: str) -> bool:
        """Return the fixed response regardless of input.

        Args:
            text: Text to check (ignored).

        Returns:
            The fixed response value set during initialization.
        """
        return self.response


from .accounts_office_reference_number import AccountsOfficeReferenceNumber  # noqa
from .age import Age  # noqa
from .age import AgeImproved  # noqa
from .american_bankers_association import AmericanBankersAssociationNumber  # noqa
from .au_medicare_number import AustralianMedicareNumber  # noqa
from .australian_business_number import AustralianBusinessNumber  # noqa
from .bank_account import JapanBankAccountNumber  # noqa
from .credit_card import CreditCard  # noqa
from .credit_card_type import CreditCardType  # noqa
from .date import DateTime  # noqa
from .driving_license import DrivingLicense  # noqa
from .driving_license.japan import JapanDrivingLicense  # noqa
from .email import Email  # noqa
from .french_postal_code import FrenchPostalCode  # noqa
from .geography import City  # noqa
from .geography import Country  # noqa
from .geography import CountryCode  # noqa
from .geography import CountryName  # noqa
from .geography import UKPostCode  # noqa
from .geography import UnitedStateState  # noqa
from .geography import ZipCode  # noqa
from .healthcare import ATC  # noqa
from .healthcare import NDC  # noqa
from .healthcare import DEANumber  # noqa
from .healthcare import Gene  # noqa
from .healthcare import HealthcareBeneficiaryNumber  # noqa
from .healthcare import ICDv9  # noqa
from .healthcare import ICDv10  # noqa
from .healthcare import ICDv11  # noqa
from .healthcare import MedicalCode  # noqa
from .healthcare import MedicalRecordNumber  # noqa
from .healthcare import MedicalTerm  # noqa
from .healthcare import MedicareBeneficiaryIdentifier  # noqa
from .hmrc_payee import HMRC_PAYE  # noqa
from .iban import IBAN  # noqa
from .imei import IMEI  # noqa
from .international_zipcode import InternationalZipcode  # noqa
from .japan_address import JapanAddress  # noqa
from .license import CaliforniaFinancingLaw  # noqa
from .license import NationwideMultistateLicensingSystem  # noqa
from .national_identifier import SSN  # noqa
from .national_identifier import SSNUK  # noqa
from .national_identifier import AadhaarNumber  # noqa
from .national_identifier import CanadaSIN  # noqa
from .national_identifier import CFPBrazil  # noqa
from .national_identifier import DNISpain  # noqa
from .national_identifier import ICDIndonesia  # noqa
from .national_identifier import IsraelID  # noqa
from .national_identifier import ItalianFiscalCode  # noqa
from .national_identifier import MexicoCURP  # noqa
from .national_identifier import MyNumberJapan  # noqa
from .national_identifier import NationalIdentity  # noqa
from .national_identifier import NIESpain  # noqa
from .national_identifier import NIFSpain  # noqa
from .national_identifier import NIRFrance  # noqa
from .national_identifier import NUSSSpain  # noqa
from .national_identifier import PESELPoland  # noqa
from .national_identifier import PRChinaID  # noqa
from .national_identifier import RRNSouthKorea  # noqa
from .national_identifier import RussianInternalPassport  # noqa
from .national_identifier import RussianInternationalPassport  # noqa
from .national_identifier import TFNAustralia  # noqa
from .national_identifier import TINGermany  # noqa
from .network import IP  # noqa
from .network import URI  # noqa
from .network import IPv4  # noqa
from .network import IPv6  # noqa
from .person import Etnicity  # noqa
from .person import Gender  # noqa
from .person import GenderLong  # noqa
from .person import Job  # noqa
from .person import MaritalStatus  # noqa
from .person import Name  # noqa
from .person import Person  # noqa
from .person import Religion  # noqa
from .person import Surname  # noqa
from .person import YearOfBirth  # noqa
from .phone import Phone  # noqa
from .phone import PhoneNumber  # noqa
from .phone import USPhone  # noqa
from .publications import CODEN  # noqa
from .publications import ISBN  # noqa
from .publications import ISSN  # noqa
from .swift import SWIFT  # noqa
from .time import DayOfTheWeek  # noqa
from .time import InternationalDayOfTheWeek  # noqa
from .us_postal_address import USPostalAddress  # noqa
from .us_voter_id import VoterID  # noqa
from .user_id import UniqueIDIdentifier  # noqa
from .vehicle import VehicleIdentificationNumber  # noqa
