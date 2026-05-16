"""Geography identifier for detecting geographic locations and postal codes.

This module provides identifiers for recognizing country names, country codes,
city names, US zip codes, UK postcodes, and US state names.
"""

import csv
import logging
import re
from collections.abc import Callable, Iterable
from contextlib import suppress
from pathlib import Path

from risk_assessment.classification.identifiers import DictionaryIdentifier, Identifier

logger = logging.getLogger(__name__)


def _extract_all_langugage_city_names(file: str) -> list[str]:
    """Extract city names from a multi-language file.

    Args:
        file: Path to the file containing city names.

    Returns:
        List of city names.
    """
    with (Path(__file__).parent / file).open("r") as stream:
        return [line.strip() for line in stream.readlines()]


def _extract_city_names(file: str) -> list[str]:
    """Extract city names from a CSV file.

    Args:
        file: Path to the CSV file containing city names.

    Returns:
        List of city names.
    """
    logger.debug("Extracting city names")

    with (Path(__file__).parent / file).open("r") as io_stream:
        reader = csv.reader(io_stream, delimiter=",", quotechar='"')

        return [entry[0] for entry in reader]


def _extract_country_codes(file_name: str) -> list[str]:
    """Extract country codes from a CSV file.

    Args:
        file_name: Path to the CSV file containing country data.

    Returns:
        List of unique country codes.
    """
    logger.debug("Extracting country codes")

    with (Path(__file__).parent / file_name).open("r") as io_stream:
        reader = csv.reader(io_stream, delimiter=",", quotechar='"')
        return list({row[1] for row in reader})


def _extract_country_names(file_name: str) -> list[str]:
    """Extract country names from a CSV file with variations.

    Args:
        file_name: Path to the CSV file containing country data.

    Returns:
        List of country names including variations.
    """
    logger.debug("Extracting country names and codes")

    countries = [
        "Afghanistan",
        "Albania",
        "Algeria",
        "American Samoa",
        "Andorra",
        "Angola",
        "Anguilla",
        "Antarctica",
        "Antigua and Barbuda",
        "Argentina",
        "Armenia",
        "Aruba",
        "Australia",
        "Austria",
        "Azerbaijan",
        "Bahamas",
        "Bahrain",
        "Bangladesh",
        "Barbados",
        "Belarus",
        "Belgium",
        "Belize",
        "Benin",
        "Bermuda",
        "Bhutan",
        "Bolivia",
        "Bosnia and Herzegovina",
        "Botswana",
        "Bouvet Island",
        "Brazil",
        "British Indian Ocean Territory",
        "British Virgin Islands",
        "Brunei Darussalam",
        "Bulgaria",
        "Burkina Faso",
        "Burundi",
        "Cambodia",
        "Cameroon",
        "Canada",
        "Cape Verde",
        "Cayman Islands",
        "Central African Republic",
        "Chad",
        "Chile",
        "China",
        "Christmas Island",
        "Cocos (Keeling) Islands",
        "Colombia",
        "Comoros",
        "Congo",
        "Congo",
        "Cook Islands",
        "Costa Rica",
        "Cote d'Ivoire",
        "Croatia",
        "Cuba",
        "Cyprus",
        "Czech Republic",
        "Denmark",
        "Djibouti",
        "Dominica",
        "Dominican Republic",
        "Ecuador",
        "Egypt",
        "El Salvador",
        "Equatorial Guinea",
        "Eritrea",
        "Estonia",
        "Ethiopia",
        "Faroe Islands",
        "Falkland Islands (Malvinas)",
        "Falkland Islands",
        "Malvinas",
        "Fiji",
        "Finland",
        "France",
        "French Guiana",
        "French Polynesia",
        "French Southern Territories",
        "Gabon",
        "Gambia",
        "Georgia",
        "Germany",
        "Ghana",
        "Gibraltar",
        "Greece",
        "Greenland",
        "Grenada",
        "Guadeloupe",
        "Guam",
        "Guatemala",
        "Guernsey",
        "Guinea",
        "Guinea-Bissau",
        "Guyana",
        "Haiti",
        "Heard Island and McDonald Islands",
        "Holy See (Vatican City State)",
        "Honduras",
        "Hong Kong",
        "Hungary",
        "Iceland",
        "India",
        "Indonesia",
        "Iran",
        "Iraq",
        "Ireland",
        "Isle of Man",
        "Israel",
        "Italy",
        "Jamaica",
        "Japan",
        "Jersey",
        "Jordan",
        "Kazakhstan",
        "Kenya",
        "Kiribati",
        "Korea",
        "Korea",
        "Kuwait",
        "Kyrgyz Republic",
        "Lao People's Democratic Republic",
        "Latvia",
        "Lebanon",
        "Lesotho",
        "Liberia",
        "Libyan Arab Jamahiriya",
        "Liechtenstein",
        "Lithuania",
        "Luxembourg",
        "Macao",
        "Macedonia",
        "Madagascar",
        "Malawi",
        "Malaysia",
        "Maldives",
        "Mali",
        "Malta",
        "Marshall Islands",
        "Martinique",
        "Mauritania",
        "Mauritius",
        "Mayotte",
        "Mexico",
        "Micronesia",
        "Moldova",
        "Monaco",
        "Mongolia",
        "Montenegro",
        "Montserrat",
        "Morocco",
        "Mozambique",
        "Myanmar",
        "Namibia",
        "Nauru",
        "Nepal",
        "Netherlands Antilles",
        "Netherlands",
        "New Caledonia",
        "New Zealand",
        "Nicaragua",
        "Niger",
        "Nigeria",
        "Niue",
        "Norfolk Island",
        "Northern Mariana Islands",
        "Norway",
        "Oman",
        "Pakistan",
        "Palau",
        "Palestinian Territory",
        "Panama",
        "Papua New Guinea",
        "Paraguay",
        "Peru",
        "Philippines",
        "Pitcairn Islands",
        "Poland",
        "Portugal",
        "Puerto Rico",
        "Qatar",
        "Reunion",
        "Romania",
        "Russian Federation",
        "Rwanda",
        "Saint Barthelemy",
        "Saint Helena",
        "Saint Kitts and Nevis",
        "Saint Lucia",
        "Saint Martin",
        "Saint Pierre and Miquelon",
        "Saint Vincent and the Grenadines",
        "Samoa",
        "San Marino",
        "Sao Tome and Principe",
        "Saudi Arabia",
        "Senegal",
        "Serbia",
        "Seychelles",
        "Sierra Leone",
        "Singapore",
        "Slovakia (Slovak Republic)",
        "Slovenia",
        "Solomon Islands",
        "Somalia",
        "South Africa",
        "South Georgia and the South Sandwich Islands",
        "Spain",
        "Sri Lanka",
        "Sudan",
        "Suriname",
        "Svalbard & Jan Mayen Islands",
        "Swaziland",
        "Sweden",
        "Switzerland",
        "Syrian Arab Republic",
        "Taiwan",
        "Tajikistan",
        "Tanzania",
        "Thailand",
        "Timor-Leste",
        "Togo",
        "Tokelau",
        "Tonga",
        "Trinidad and Tobago",
        "Tunisia",
        "Turkey",
        "Turkmenistan",
        "Turks and Caicos Islands",
        "Tuvalu",
        "Uganda",
        "Ukraine",
        "United Arab Emirates",
        "United Kingdom",
        "United States of America",
        "United States Minor Outlying Islands",
        "United States Virgin Islands",
        "Uruguay",
        "Uzbekistan",
        "Vanuatu",
        "Venezuela",
        "Vietnam",
        "Wallis and Futuna",
        "Western Sahara",
        "Yemen",
        "Zambia",
        "Zimbabwe",
    ]

    with (Path(__file__).parent / file_name).open("r") as io_stream:
        reader = csv.reader(io_stream, delimiter=",", quotechar='"')
        country_names: list[str] = []

        for row in reader:
            country_name = row[0]

            country_names.append(country_name)
            if "," in country_name:
                country_name_parts = [part.strip() for part in country_name.split(",")]
                if country_name_parts[0] not in countries:
                    country_names.append(country_name_parts[0])

                full_country_name = f"{country_name_parts[1]} {country_name_parts[0]}"
                if full_country_name not in countries:
                    country_names.append(full_country_name)
            if row[0] not in countries:
                country_names.append(row[0])

        return list(set(country_names + countries))


class CountryName(DictionaryIdentifier):
    """Identifier for country names.

    Example:
        >>> identifier = CountryName()
        >>> identifier.is_of_this_type("United States")
        True
        >>> identifier.is_of_this_type("France")
        True
    """

    def __init__(
        self,
        data_file: str = "data/en/countryList.csv",
        extractor: Callable[[str], Iterable[str]] = _extract_country_names,
    ) -> None:
        super().__init__("CountryName", extractor(data_file), False)


class CountryCode(DictionaryIdentifier):
    """Identifier for country codes (ISO codes).

    Example:
        >>> identifier = CountryCode()
        >>> identifier.is_of_this_type("US")
        True
        >>> identifier.is_of_this_type("FR")
        True
    """

    def __init__(
        self,
        data_file: str = "data/en/countryList.csv",
        extractor: Callable[[str], Iterable[str]] = _extract_country_codes,
    ) -> None:
        super().__init__("CountryCode", extractor(data_file), False)


class Country(Identifier):
    """Identifier for countries (names and optionally codes).

    Example:
        >>> identifier = Country()
        >>> identifier.is_of_this_type("Canada")
        True
        >>> identifier.is_of_this_type("CA")
        True
    """

    def __init__(self, include_code: bool = True) -> None:
        """Initialize the Country identifier.

        Args:
            include_code: If True, match both names and codes. Defaults to True.
        """
        self.names = CountryName()
        self.codes = CountryCode()
        self.include_code = include_code

    def is_of_this_type(self, text: str) -> bool:
        """Check if text is a valid country name or code.

        Args:
            text: The text to check.

        Returns:
            True if text matches a country name or (if enabled) code, False otherwise.
        """
        return self.names.is_of_this_type(text) or (self.include_code and self.codes.is_of_this_type(text))


class City(DictionaryIdentifier):
    """Identifier for city names.

    Example:
        >>> identifier = City()
        >>> identifier.is_of_this_type("New York")
        True
        >>> identifier.is_of_this_type("London")
        True
    """

    def __init__(
        self, data_file: str = "data/en/cityList.csv", extractor: Callable[[str], Iterable[str]] = _extract_city_names
    ) -> None:
        super().__init__("City", extractor(data_file), False)


class ZipCode(Identifier):
    """Identifier for US ZIP codes.

    Validates 5-digit ZIP codes against known US state ranges.

    Example:
        >>> identifier = ZipCode()
        >>> identifier.is_of_this_type("10001")  # NYC
        True
        >>> identifier.is_of_this_type("90210")  # Beverly Hills
        True
    """

    def __init__(self) -> None:
        """Initialize the ZipCode identifier with US state ZIP code ranges."""
        self.valid_codes = {
            "AL": (35004, 36925),
            "AK": (99501, 99950),
            "AZ": (85001, 86556),
            "AR": (71601, 72959),
            "CA": (90001, 96162),
            "CO": (80001, 81658),
            "CT": (6001, 6389),
            "DE": (19701, 19980),
            "DC": (20001, 20039),
            "FL": (32004, 34997),
            "GA": (30001, 31999),
            "HI": (96701, 96898),
            "ID": (83201, 83876),
            "IL": (60001, 62999),
            "IN": (46001, 47997),
            "IA": (50001, 52809),
            "KS": (66002, 67954),
            "KY": (40003, 42788),
            "LA": (70001, 71232),
            "ME": (3901, 4992),
            "MD": (20812, 21930),
            "MA": (1001, 2791),
            "MI": (48001, 49971),
            "MN": (55001, 56763),
            "MS": (38601, 39776),
            "MO": (63001, 65899),
            "MT": (59001, 59937),
            "NE": (68001, 68118),
            "NV": (88901, 89883),
            "NH": (3031, 3897),
            "NJ": (7001, 8989),
            "NM": (87001, 88441),
            "NY": (10001, 14905),
            "NC": (27006, 28909),
            "ND": (58001, 58856),
            "OH": (43001, 45999),
            "OK": (73001, 73199),
            "OR": (97001, 97920),
            "PA": (15001, 19640),
            "RI": (2801, 2940),
            "SC": (29001, 29948),
            "SD": (57001, 57799),
            "TN": (37010, 38589),
            "TX": (75503, 79999),
            "UT": (84001, 84784),
            "VT": (5001, 5495),
            "VA": (22001, 24658),
            "WA": (98001, 99403),
            "WV": (24701, 26886),
            "WI": (53001, 54990),
            "WY": (82001, 83128),
        }

    def is_of_this_type(self, text: str) -> bool:
        """Check if text is a valid US ZIP code.

        Args:
            text: The text to check.

        Returns:
            True if text is a 5-digit ZIP code within valid US ranges, False otherwise.
        """
        text = text.strip()
        if len(text) == 5:
            with suppress(ValueError):
                int_code = int(text, base=10)
                for _, (m, M) in self.valid_codes.items():
                    if m <= int_code <= M:
                        return True

        return False


class UKPostCode(Identifier):
    """Identifier for UK postcodes.

    Validates UK postcode format with area, district, sector, and unit components.

    Example:
        >>> identifier = UKPostCode()
        >>> identifier.is_of_this_type("SW1A 1AA")
        True
        >>> identifier.is_of_this_type("M1 1AE")
        True
    """

    AREA = r"(?:(?:A[BL])|(?:B[ABDHLNRST]?)|(?:C[ABFHMORTVW])|(?:D[ADEGHLNTY])|(?:E[CHNX]?)|(?:F[KY])|(?:G[LUY]?)|(?:H[ADGPRSUX])|(?:I[GPVM])|(?:JE)|(?:K[ATWY])|(?:L[ADELNSU]?)|(?:M[EKL]?)|(?:N[EGNPRW]?)|(?:O[LX])|(?:P[AEHLOR])|(?:R[GHM])|(?:S[AEGKLMNOPRSTWY]?)|(?:T[ADFNQRSW])|(?:UB)|(?:W[ACDFNRSV]?)|(?:YO)|(?:ZE))"
    DISTRICT = r"(?:(?:\d{1,2})|(?:\d\w))"
    SECTOR = r"(?:\d)"
    UNIT = r"(?:\w{2})"

    OUTWARD = r"(?:" + AREA + r"\s?" + DISTRICT + r")"
    INWARD = r"(?:" + SECTOR + r"\s?" + UNIT + r")"

    _pattern = re.compile(r"^" + OUTWARD + r"\s?" + INWARD + r"$", flags=re.IGNORECASE)

    def is_of_this_type(self, text: str) -> bool:
        """Check if text is a valid UK postcode.

        Args:
            text: The text to check.

        Returns:
            True if text matches UK postcode format, False otherwise.
        """
        return self._pattern.match(text) is not None


class UnitedStateState(DictionaryIdentifier):
    """Identifier for US state names and abbreviations.

    Includes all 50 states and US territories.

    Example:
        >>> identifier = UnitedStateState()
        >>> identifier.is_of_this_type("California")
        True
        >>> identifier.is_of_this_type("CA")
        True
    """

    def __init__(self) -> None:
        """Initialize the UnitedStateState identifier with state names and codes."""
        super().__init__(
            "US State",
            [
                "AL",
                "Alabama",
                "AK",
                "Alaska",
                "AZ",
                "Arizona",
                "AR",
                "Arkansas",
                "CA",
                "California",
                "CO",
                "Colorado",
                "CT",
                "Connecticut",
                "DE",
                "Delaware",
                "FL",
                "Florida",
                "GA",
                "Georgia",
                "HI",
                "Hawaii",
                "ID",
                "Idaho",
                "IL",
                "Illinois",
                "IN",
                "Indiana",
                "IA",
                "Iowa",
                "KS",
                "Kansas",
                "KY",
                "Kentucky",
                "LA",
                "Louisiana",
                "ME",
                "Maine",
                "MD",
                "Maryland",
                "MA",
                "Massachusetts",
                "MI",
                "Michigan",
                "MN",
                "Minnesota",
                "MS",
                "Mississippi",
                "MO",
                "Missouri",
                "MT",
                "Montana",
                "NE",
                "Nebraska",
                "NV",
                "Nevada",
                "NH",
                "New Hampshire",
                "NJ",
                "New Jersey",
                "NM",
                "New Mexico",
                "NY",
                "New York",
                "NC",
                "North Carolina",
                "ND",
                "North Dakota",
                "OH",
                "Ohio",
                "OK",
                "Oklahoma",
                "OR",
                "Oregon",
                "PA",
                "Pennsylvania",
                "RI",
                "Rhode Island",
                "SC",
                "South Carolina",
                "SD",
                "South Dakota",
                "TN",
                "Tennessee",
                "TX",
                "Texas",
                "UT",
                "Utah",
                "VT",
                "Vermont",
                "VA",
                "Virginia",
                "WA",
                "Washington",
                "WV",
                "West Virginia",
                "WI",
                "Wisconsin",
                "WY",
                "Wyoming",
                # US Territory
                "DC",
                "District of Columbia",
                "AS",
                "American Samoa",
                "GU",
                "Guam",
                "VI",
                "Vigin Islands",
                "PR",
                "Puerto Rico",
                "FM",
                "Micronesia",
                "MH",
                "Marshall Islands",
                "PW",
                "Palau",
                "MP",
                "Northern Mariana Islands",
            ],
            False,
        )
