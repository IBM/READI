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
    @abstractmethod
    def is_of_this_type(self, text: str) -> bool:
        raise NotImplementedError()

    def __str__(self) -> str:
        return self.__class__.__name__

    def is_need_span(self) -> bool:
        return False


class LuhnIdentifier(Identifier):
    def check_luhn(self, text: str) -> bool:
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
    def __init__(self, type_name: str, data: Iterable[str], case_sensitive: bool = True):
        self.type_name = type_name
        self.case_sensitive = case_sensitive

        self.data = set(data) if self.case_sensitive else {datapoint.casefold() for datapoint in data}

    def __str__(self) -> str:
        return self.type_name

    def is_of_this_type(self, text: str) -> bool:
        if not self.case_sensitive:
            text = text.casefold()
        if text in self.data:
            return True

        return False


@dataclass
class RegexIdentifier(Identifier):
    type_name: str
    patterns: list[Pattern[str]]

    def __str__(self) -> str:
        return self.type_name

    def is_of_this_type(self, text: str) -> bool:
        for pattern in self.patterns:
            if pattern.match(text):
                return True

        return False


@dataclass
class RegexIdentifierWithSpan(RegexIdentifier):
    type_name: str
    patterns: list[Pattern[str]]

    def __str__(self) -> str:
        return super().__str__()

    def get_span_length_required_to_check(self) -> int:  # type: ignore
        pass

    def is_of_this_type(self, text: str) -> bool:
        return self.is_of_this_type_with_span(text)[0]

    def is_of_this_type_with_span(self, text: str) -> tuple[bool, tuple[int, int] | None]:
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
        return True


class LanguageBasedDictionaryIdentifier(DictionaryIdentifier):
    def __init__(self, type_name: str, data: dict[str, list[str]], case_sensitive: bool = True):
        super().__init__(type_name, sum(data.values(), []), case_sensitive)
        self.languages = set(data.keys())
        self._original = data

    def is_of_this_type(self, text: str) -> bool:
        return self.is_of_this_type_with_language(text, "*")

    def is_of_this_type_with_language(self, text: str, language: str = "*") -> bool:
        if language not in self.languages and language != "*":
            _enrich_with_language(self, language)

        return super().is_of_this_type(text)

    def get_seed(self) -> str:
        return choice(list(self._original.keys()))  # nosec

    def get_terms(self, language: str) -> Iterable[str]:
        yield from self._original[language]

    def add_language(self, language: str, terms: list[str]) -> None:
        self._original[language] = terms
        for t in terms:
            if self.case_sensitive:
                self.data.add(t)
            else:
                self.data.add(t.casefold())


def _enrich_with_language(identifier: LanguageBasedDictionaryIdentifier, language: str) -> None:
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
    type_name: str
    response: bool = False

    def __str__(self) -> str:
        return self.type_name

    def is_of_this_type(self, text: str) -> bool:
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
from .healthcare import UMLS  # noqa
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
