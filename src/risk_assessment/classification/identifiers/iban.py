"""IBAN identifier for detecting International Bank Account Numbers.

This module provides an identifier for recognizing and validating IBAN
(International Bank Account Number) from various countries.
"""

import logging
import re

from risk_assessment.classification.identifiers import Identifier

from .iban_country import IBANCountryValidator

logger = logging.getLogger(__name__)


class IBAN(Identifier):
    """Identifier for IBAN (International Bank Account Number).

    Validates IBANs from multiple countries using country-specific patterns
    and validation rules. Supports over 70 countries.

    Attributes:
        prefixes: Dictionary mapping country codes to their validators.

    Example:
        >>> identifier = IBAN()
        >>> identifier.is_of_this_type("GB82 WEST 1234 5698 7654 32")
        True
        >>> identifier.is_of_this_type("DE89 3704 0044 0532 0130 00")
        True
    """

    prefixes: dict[str, IBANCountryValidator] = {
        "AD": IBANCountryValidator(re.compile(r"^AD\d{10}[A-Z0-9]{12}$")),
        "AE": IBANCountryValidator(re.compile(r"^AE\d{19,32}$")),
        "AL": IBANCountryValidator(re.compile(r"^AL\d{10}[A-Z0-9]{16}$")),
        "AT": IBANCountryValidator(re.compile(r"^AT\d{16,32}$")),
        "AZ": IBANCountryValidator(re.compile(r"^AZ\d{2}[A-Z]{4}\d{20}$")),
        "BA": IBANCountryValidator(re.compile(r"^BA\d{16}$")),
        "BE": IBANCountryValidator(re.compile(r"^BE\d{12,32}$")),
        "BG": IBANCountryValidator(re.compile(r"^BG\d{2}[A-Z]{4}\d{6}[A-Z0-9]{8}$")),
        "BH": IBANCountryValidator(re.compile(r"^BH\d{2}[A-Z]{4}[A-Z0-9]{14}$")),
        "BR": IBANCountryValidator(re.compile(r"^BR\d{25}[A-Z][A-Z0-9]$")),
        "BY": IBANCountryValidator(re.compile(r"^BY\d{2}[A-Z]{4}\d{4}[A-Z0-9]{16}$")),
        "CH": IBANCountryValidator(re.compile(r"^CH\d{19}$")),
        "CR": IBANCountryValidator(re.compile(r"^CR\d{18,32}$")),
        "CY": IBANCountryValidator(re.compile(r"^CY\d{8}[A-Z0-9]{16,22}$")),
        "CZ": IBANCountryValidator(re.compile(r"^CZ\d{22}$")),
        "DE": IBANCountryValidator(re.compile(r"^DE\d{20}$")),
        "DK": IBANCountryValidator(re.compile(r"^DK\d{16}$")),
        "DO": IBANCountryValidator(re.compile(r"^DO\d{2}[A-Z]{4}\d{20}$")),
        "EE": IBANCountryValidator(re.compile(r"^EE\d{18}$")),
        "EG": IBANCountryValidator(re.compile(r"^EG\d{27}$")),
        "ES": IBANCountryValidator(re.compile(r"^ES\d{22}$")),
        "FI": IBANCountryValidator(re.compile(r"^FI\d{16}$")),
        "FO": IBANCountryValidator(re.compile(r"^FO\d{16}$")),
        "FR": IBANCountryValidator(re.compile(r"^FR\d{10}[A-Z0-9]{11}\d{2,}$")),
        "GB": IBANCountryValidator(re.compile(r"^GB\d{2}[A-Z]{4}\d{14}$")),
        "GE": IBANCountryValidator(re.compile(r"^GE\d{2}[A-Z]{2}\d{16}$")),
        "GI": IBANCountryValidator(re.compile(r"^GI\d{2}[A-Z]{4}\d{15}$")),
        "GL": IBANCountryValidator(re.compile(r"^GL\d{16}$")),
        "GR": IBANCountryValidator(re.compile(r"^GR\d{7}[A-Z0-9]{16,19}$")),
        "GT": IBANCountryValidator(re.compile(r"^GT\d{2}[A-Z0-9]{24}$")),
        "HR": IBANCountryValidator(re.compile(r"^HR\d{17,32}$")),
        "HU": IBANCountryValidator(re.compile(r"^HU\d{26}$")),
        "IE": IBANCountryValidator(re.compile(r"^IE\d{2}[A-Z]{4}\d{14}$")),
        "IL": IBANCountryValidator(re.compile(r"^IL\d{21}$")),
        "IQ": IBANCountryValidator(re.compile(r"^IQ\d{2}[A-Z]{4}\d{15}$")),
        "IS": IBANCountryValidator(re.compile(r"^IS\d{24}$")),
        "IT": IBANCountryValidator(re.compile(r"^IT\d{2}[A-Z]\d{22}$")),
        "JO": IBANCountryValidator(re.compile(r"^JO\d{2}[A-Z]{4}\d{22}$")),
        "KW": IBANCountryValidator(re.compile(r"^KW\d{2}[A-Z]{4}[A-Z0-9]{22}$")),
        "KZ": IBANCountryValidator(re.compile(r"^KZ\d{5}[A-Z0-9]{13}$")),
        "LB": IBANCountryValidator(re.compile(r"^LB\d{6}[A-Z0-9]{20}$")),
        "LC": IBANCountryValidator(re.compile(r"^LC\d{2}[A-Z]{4}[A-Z0-9]{24}$")),
        "LI": IBANCountryValidator(re.compile(r"^LI\d{7}[A-Z0-9]{12}$")),
        "LT": IBANCountryValidator(re.compile(r"^LT\d{17,}$")),
        "LU": IBANCountryValidator(re.compile(r"^LU\d{18}$")),
        "LV": IBANCountryValidator(re.compile(r"^LV\d{2}[A-Z]{4}[A-Z0-9]{13}$")),
        "MC": IBANCountryValidator(re.compile(r"^MC\d{12}[A-Z0-9]{11}\d{2}$")),
        "MD": IBANCountryValidator(re.compile(r"^MD\d{2}[A-Z]{2}[A-Z0-9]{18}$")),
        "ME": IBANCountryValidator(re.compile(r"^ME\d{20}$")),
        "MK": IBANCountryValidator(re.compile(r"^MK\d{5}[A-Z0-9]{10}\d{2}$")),
        "MO": IBANCountryValidator(re.compile(r"^MO\d{2}[A-Z]{2}[A-Z0-9]{18}$")),
        "MR": IBANCountryValidator(re.compile(r"^MR\d{25}$")),
        "MT": IBANCountryValidator(re.compile(r"^MT\d{2}[A-Z]{4}\d{5}[A-Z0-9]{18}$")),
        "MU": IBANCountryValidator(re.compile(r"^MU\d{2}[A-Z]{4}\d{16}000[A-Z]{3}$")),
        "NL": IBANCountryValidator(re.compile(r"^NL\d{2}[A-Z]{4}\d{10}$")),
        "NO": IBANCountryValidator(re.compile(r"^NO\d{13}$")),
        "PK": IBANCountryValidator(re.compile(r"^PK\d{2}[A-Z0-9]{4}\d{16}$")),
        "PL": IBANCountryValidator(re.compile(r"^PL\d{26}$")),
        "PS": IBANCountryValidator(re.compile(r"^PS\d{2}[A-Z0-9]{4}\d{21}$")),
        "PT": IBANCountryValidator(re.compile(r"^PT\d{23}$")),
        "QA": IBANCountryValidator(re.compile(r"^QA\d{2}[A-Z]{4}[A-Z0-9]{21}$")),
        "RO": IBANCountryValidator(re.compile(r"^RO\d{2}[A-Z]{4}[A-Z0-9]{16}$")),
        "RS": IBANCountryValidator(re.compile(r"^RS\d{20}$")),
        "SA": IBANCountryValidator(re.compile(r"^SA\d{4}[A-Z0-9]{18}$")),
        "SC": IBANCountryValidator(re.compile(r"^SC\d{2}[A-Z]{4}\d{20}[A-Z]{3}$")),
        "SE": IBANCountryValidator(re.compile(r"^SE\d{22}$")),
        "SI": IBANCountryValidator(re.compile(r"^SI\d{17}$")),
        "SK": IBANCountryValidator(re.compile(r"^SK\d{22}$")),
        "SM": IBANCountryValidator(re.compile(r"^SM\d{2}[A-Z]\d{10}[A-Z0-9]{12}$")),
        "ST": IBANCountryValidator(re.compile(r"^ST\d{23}$")),
        "TL": IBANCountryValidator(re.compile(r"^TL\d{21}$")),
        "TN": IBANCountryValidator(re.compile(r"^TN\d{22}$")),
        "TR": IBANCountryValidator(re.compile(r"^TR\d{7}0[A-Z0-9]{16}$")),
        "UA": IBANCountryValidator(re.compile(r"^UA\d{8}[A-Z0-9]{19}$")),
        "VA": IBANCountryValidator(re.compile(r"^VA\d{20}$")),
        "VG": IBANCountryValidator(re.compile(r"^VG\d{2}[A-Z]{4}\d{16}$")),
        "XK": IBANCountryValidator(re.compile(r"^XK\d{18}$")),
    }

    def is_of_this_type(self, text: str) -> bool:
        """Check if text is a valid IBAN.

        Args:
            text: The text to check (spaces are automatically removed).

        Returns:
            True if text is a valid IBAN for a supported country, False otherwise.
        """
        text = text.replace(" ", "")
        prefix = text[:2]

        if self.is_valid_prefix(prefix):
            return self.get_country_validator(prefix).is_valid(text)

        return False

    def is_valid_prefix(self, prefix: str) -> bool:
        """Check if the country prefix is supported.

        Args:
            prefix: Two-letter country code.

        Returns:
            True if the country code is supported, False otherwise.
        """
        return prefix in self.prefixes

    def get_country_validator(self, country_prefix: str) -> IBANCountryValidator:
        """Get the validator for a specific country.

        Args:
            country_prefix: Two-letter country code.

        Returns:
            The IBANCountryValidator for the specified country.
        """
        return self.prefixes[country_prefix]
