"""National identifier for detecting national ID numbers from various countries.

This module provides identifiers for recognizing national identification numbers,
social security numbers, tax identification numbers, and similar government-issued
identifiers from countries around the world.
"""

import re

from risk_assessment.classification.identifiers import (
    Identifier,
    LuhnIdentifier,
    RegexIdentifierWithSpan,
)


class CFPBrazil(Identifier):
    """Identifier for Brazilian CPF (Cadastro de Pessoas Físicas) numbers.

    CPF is the Brazilian individual taxpayer registry identification.
    Format: XXX.XXX.XXX-XX or variations without punctuation.

    Example:
        >>> identifier = CFPBrazil()
        >>> identifier.is_of_this_type("123.456.789-09")
        True
    """

    pattern = re.compile(r"^(\d{3}[.]\d{3}[.]\d{3}[-]\d{2})$|^(\d{9}[-]\d{2})$|^(\d{9}[-]\d{2})$|^(\d{11})$")

    def _verify(self, digits: str, checksum: str) -> bool:
        """Verify CPF checksum digits.

        Args:
            digits: The first 9 digits of the CPF.
            checksum: The 2 checksum digits.

        Returns:
            True if checksum is valid, False otherwise.
        """
        v1 = 0
        v2 = 0
        for i in range(9):
            v1 += int(digits[i]) * (9 - i % 10)
            v2 += int(digits[i]) * (9 - (i + 1) % 10)
        v1 = (v1 % 11) % 10
        v2 = ((v2 + v1 * 9) % 11) % 10
        if v1 == int(checksum[1]) and v2 == int(checksum[0]):
            return True
        return False

    def is_of_this_type(self, text: str) -> bool:
        """Check if text is a valid Brazilian CPF number.

        Reference: https://en.wikipedia.org/wiki/CPF_number

        Args:
            text: The text to check.

        Returns:
            True if text is a valid CPF with correct checksum, False otherwise.
        """
        if re.match(self.pattern, text):
            text_wo_punct = text.replace("-", "").replace(".", "")
            digits: str = text_wo_punct[:9]
            checksum: str = text_wo_punct[9:]
            return self._verify(digits, checksum)
        return False


class NIRFrance(Identifier):
    """Identifier for French NIR (Numéro d'Inscription au Répertoire) numbers.

    Also known as French Social Security Number.
    Format: 15 digits with optional spaces.

    Example:
        >>> identifier = NIRFrance()
        >>> identifier.is_of_this_type("1 85 02 75 116 001 42")
        True
    """

    pattern = re.compile(
        r"^(([7182]\d{14})|([7182])( )(\d{2})( )(\d{2})( )(\d{2})( )(\d{3})( )(\d{3})( )(\d{2})|([7128]\d{12} \d{2})|([7182]\d{4}2[AB]\d{8})|([7182])( )(\d{2})( )(\d{2})( )(2[AB])( )(\d{3})( )(\d{3})( )(\d{2}))$"
    )

    def is_of_this_type(self, text: str) -> bool:
        """Check if text is a valid French NIR number.

        Reference: https://fr.wikipedia.org/wiki/Numéro_de_sécurité_sociale_en_France

        Args:
            text: The text to check.

        Returns:
            True if text is a valid NIR with correct check digit, False otherwise.
        """
        if re.match(self.pattern, text):
            text_wo_punct = re.sub("[ ]", "", text)
            text_wo_letters = re.sub("2A", "18", text_wo_punct)
            text_wo_letters = re.sub("2B", "19", text_wo_letters)
            check_digit = int(text_wo_letters[:13]) % 97
            if check_digit == int(text_wo_letters[13:]):
                return True
        return False


class TINGermany(Identifier):
    """Identifier for German TIN (Tax Identification Number / Steueridentifikationsnummer).

    Format: 11 digits with specific validation rules.

    Example:
        >>> identifier = TINGermany()
        >>> identifier.is_of_this_type("12 345 678 901")
        True
    """

    pattern = re.compile(
        r"^(([1-9]\d{11})|([1-9]\d \d{3} \d{3} \d{3})|([1-9][0-9])([,])(d{3})([,])(\d{3})([,])(\d{3})|([1-9][0-9])([.])(d{3})([.])(\d{3})([.])(\d{3})|([1-9][0-9])([\/])(d{3})([\/])(\d{3})([\/])(\d{3})|([1-9]\d{10}))$"
    )  # noqa

    def check_last_digit(self, first_ten_digits: list[str], check_digit: str) -> bool:
        """Verify the check digit of a German TIN.

        Args:
            first_ten_digits: List of the first 10 digits.
            check_digit: The check digit to verify.

        Returns:
            True if check digit is valid, False otherwise.
        """
        check_number = 10
        for digit in first_ten_digits:
            check_sum = (int(digit) + check_number) % 10
            if check_sum == 0:
                check_sum = 10

            check_number = (check_sum * 2) % 11
        check_number = (11 - check_number) % 10
        return int(check_digit) == check_number

    def is_of_this_type(self, text: str) -> bool:
        """Check if text is a valid German TIN.

        Args:
            text: The text to check.

        Returns:
            True if text is a valid TIN with correct structure and check digit, False otherwise.
        """
        if re.match(self.pattern, text):
            text_wo_punct = re.sub("[ ./,]", "", text)

            counts: dict[str, int] = {}
            digits = list(text_wo_punct)
            if self.check_last_digit(digits[:10], digits[10]):
                repetition_exists = False
                for i in range(10):
                    if digits[i] in counts:
                        counts[digits[i]] += 1
                        repetition_exists = True
                    else:
                        counts[digits[i]] = 1
                    if i < 8:
                        if digits[i] == digits[i + 1] == digits[i + 2]:
                            return False

                if not repetition_exists:
                    return False

                found: bool = False
                for item in counts:
                    if counts[item] == 3 or counts[item] == 2:
                        if found:
                            return False
                        found = True

                return found

        return False


class AadhaarNumber(Identifier):
    pattern = re.compile(r"^(([2-9]\d{3} \d{4} \d{4})|([2-9]\d{11}))$")

    def is_of_this_type(self, text: str) -> bool:
        # https://en.wikipedia.org/wiki/Aadhaar

        if re.match(self.pattern, text):
            return True
        # Add checksum validation
        return False


class ICDIndonesia(Identifier):
    pattern = re.compile(
        r"^(\d{2}[01237]\d{3}[01234567]\d[01]\d{7})$|^(\d{2}[01237]\d{3}( )[01234567]\d[01]\d{3}( )\d{4})$"
    )

    def is_of_this_type(self, text: str) -> bool:
        # https://id.wikipedia.org/wiki/Nomor_Induk_Kependudukan

        if re.match(self.pattern, text):
            return True
        return False


class ItalianFiscalCode(Identifier):
    pattern = re.compile(
        "[a-z]{3}"  # surname
        +
        # "\\s*" +   optional space
        "[a-z]{3}"  # first surname
        +
        # "\\s*" +   optional space
        "\\d{2}"
        + "([abcdehlmprst])"
        + "([0-7][0-9])"  # year of birth  # month of birth  # day of birth
        +
        # "\\s*" +   optional space
        "([a-z][0-9]{3})"  # town of birth
        +
        # "\\s*" +   optional space
        "[a-z]",  # checksum
        re.IGNORECASE,
    )

    odd_characters: dict[str, int] = {
        "0": 1,
        "1": 0,
        "2": 5,
        "3": 7,
        "4": 9,
        "5": 13,
        "6": 15,
        "7": 17,
        "8": 19,
        "9": 21,
        "A": 1,
        "B": 0,
        "C": 5,
        "D": 7,
        "E": 9,
        "F": 13,
        "G": 15,
        "H": 17,
        "I": 19,
        "J": 21,
        "K": 2,
        "L": 4,
        "M": 18,
        "N": 20,
        "O": 11,
        "P": 3,
        "Q": 6,
        "R": 8,
        "S": 12,
        "T": 14,
        "U": 16,
        "V": 10,
        "W": 22,
        "X": 25,
        "Y": 24,
        "Z": 23,
    }

    even_characters: dict[str, int] = dict(
        list({str(i): i for i in range(10)}.items()) + list({chr(ord("A") + i): i for i in range(26)}.items()),
    )

    def is_of_this_type(self, text: str) -> bool:
        text = text.replace(" ", "")

        if len(text) == 16 and self.pattern.match(text) and self.validate_checksum(text):
            return True
        return False

    def validate_checksum(self, text: str) -> bool:
        data = text.strip().upper()

        checksum = 0

        position = 1

        for i in range(len(data) - 1):
            if position == 16:
                break

            character = data[i]

            if not character.isalnum():
                continue

            value = (
                ItalianFiscalCode.even_characters[character]
                if 0 == position % 2
                else ItalianFiscalCode.odd_characters[character]
            )

            if value is None:
                return False  # invalid character which is still letter or digit

            checksum += value

            position += 1

        checksum_character = data[-1]

        return checksum_character == chr(ord("A") + checksum % 26)


class MyNumberJapan(Identifier):
    pattern = re.compile(
        r"^((\d{4}.\d{4}.\d{4})|(\d{4},\d{4},\d{4})|(\d{4}-\d{4}-\d{4})|(\d{4} \d{4} \d{4})|(\d{12}))$"
    )

    def is_of_this_type(self, text: str) -> bool:
        # https://ja.wikipedia.org/wiki/個人番号

        if re.match(self.pattern, text):
            text_wo_separators = re.sub(r"[ -.,]", "", text)
            if not text_wo_separators.isnumeric():
                return False
            check_digit = 0
            for i in range(1, 12):
                check_digit += int(text_wo_separators[i]) * (i % 2 + 1)
            check_digit = 9 - check_digit % 9
            if int(text_wo_separators[0]) == check_digit:
                return True
        return False


def _valid_birth_date(day: int, month: int, year: int) -> bool:
    """Check if a date is valid.

    Args:
        day: Day of month.
        month: Month number.
        year: Year.

    Returns:
        True if the date is valid, False otherwise.
    """
    from datetime import date

    try:
        date(year, month, day)
        return True
    except ValueError:
        return False


class IsraelID(LuhnIdentifier):
    _pattern = re.compile(r"^\d{8}[\- ]?\d$")

    def is_of_this_type(self, text: str) -> bool:
        match = IsraelID._pattern.match(text)

        if match:
            return self.check_luhn(text.replace("-", "").replace(" ", ""))

        return False


class MexicoCURP(Identifier):
    pattern = re.compile(r"^[A-Z][AEIOU][A-Z]{2}(\d{2})(\d{2})(\d{2})[HMX]([A-Z]{2})[A-Z]{3}([A-Z0-9])(\d)")
    #  http://www.statoids.com/umx.html
    states: set[str] = {
        "AS",
        "BC",
        "BS",
        "CC",
        "CS",
        "CH",
        "DF",
        "CL",
        "CM",
        "DG",
        "GT",
        "GR",
        "HG",
        "JC",
        "MC",
        "MN",
        "MS",
        "NT",
        "NL",
        "OC",
        "PL",
        "QO",
        "QR",
        "SP",
        "SL",
        "SR",
        "TC",
        "TS",
        "TL",
        "VZ",
        "YN",
        "ZS",
        "NE",  # code for people born abroad
    }
    CURP_CHARACTERS = "0123456789ABCDEFGHIJKLMNÑOPQRSTUVWXYZ"

    def is_of_this_type(self, text: str) -> bool:
        match = MexicoCURP.pattern.match(text)

        if match:
            year_2d = match.group(1)
            month = int(match.group(2), base=10)
            day = int(match.group(3), base=10)
            state = match.group(4)
            century_flag = match.group(5)
            # parity = match.group(6)  # noqa

            if all(c.isdigit() for c in century_flag):
                year = int(f"20{year_2d}")
            else:
                year = int(f"19{year_2d}")

            if state in self.states:
                if _valid_birth_date(day, month, year):
                    if _valid_curp_parity(text):
                        return True

        return False


def _valid_curp_parity(text: str) -> bool:
    """Validate the parity check digit of a Mexican CURP.

    Args:
        text: The CURP string to validate.

    Returns:
        True if the parity check digit is valid, False otherwise.
    """
    start = 18
    return text[-1] == str(
        -sum((start - i) * MexicoCURP.CURP_CHARACTERS.index(n) for i, n in enumerate(text[:-1])) % 10
    )


class CanadaSIN(LuhnIdentifier):
    _pattern = re.compile(r"^\d{3}[\- ]?\d{3}[\- ]?\d{3}$")

    def is_of_this_type(self, text: str) -> bool:
        match = CanadaSIN._pattern.match(text)

        if match:
            return self.check_luhn(text.replace("-", "").replace(" ", ""))

        return False


class PRChinaID(Identifier):
    pattern = re.compile(r"^(\d{17}[Xx])$|^(\d{18})$")

    def checksum(self, number: str) -> int:
        return (1 - 2 * int(number, 13)) % 11

    def is_of_this_type(self, text: str) -> bool:
        # https://en.wikipedia.org/wiki/Resident_Identity_Card

        if re.match(self.pattern, text):
            if self.checksum(text[:17]) == 10:
                return True
        return False


class RussianInternalPassport(Identifier):
    pattern = re.compile(r"^(\d{2}[- ]\d{2}[ ]\d{6})$|^(\d{4}[ ]\d{6})|(\d{10})$")
    area_codes = [
        "01",
        "03",
        "04",
        "05",
        "07",
        "08",
        "10",
        "11",
        "12",
        "14",
        "15",
        "17",
        "18",
        "19",
        "20",
        "22",
        "24",
        "25",
        "26",
        "27",
        "28",
        "29",
        "30",
        "32",
        "33",
        "34",
        "36",
        "37",
        "38",
        "40",
        "41",
        "42",
        "44",
        "45",
        "46",
        "47",
        "47",
        "49",
        "50",
        "52",
        "53",
        "54",
        "56",
        "57",
        "58",
        "60",
        "61",
        "63",
        "64",
        "65",
        "66",
        "68",
        "69",
        "70",
        "71",
        "73",
        "75",
        "76",
        "77",
        "78",
        "79",
        "80",
        "81",
        "82",
        "83",
        "84",
        "85",
        "86",
        "87",
        "88",
        "89",
        "90",
        "91",
        "92",
        "93",
        "94",
        "95",
        "96",
        "97",
        "98",
        "99",
    ]

    def is_of_this_type(self, text: str) -> bool:
        if re.match(self.pattern, text):
            text_wo_separators = re.sub(r"[ -.,]", "", text)
            if text_wo_separators[:2] not in self.area_codes:
                return False
            return True
        return False


class RussianInternationalPassport(Identifier):
    pattern = re.compile(r"^(\d{2}[- ]\d{7})|(\d{2}[ ]\d{7})|(\d{9})$")
    passport_type = ["1", "2", "6", "7"]

    def is_of_this_type(self, text: str) -> bool:
        if re.match(self.pattern, text):
            text_wo_separators = re.sub(r"[ -.,]", "", text)
            if text_wo_separators[0] not in self.passport_type:
                return False
            return True
        return False


class RRNSouthKorea(Identifier):
    pattern = re.compile(
        r"^(\d{2}[01]\d[0123]\d-\d{7})$|^(\d{2}[01]\d[0123]\d{8})$|^(\d\d[01]\d[0123]\d-\d{7})$|%(\d{2}[01]\d[0123]\d[ ]\d{7})$"
    )

    def is_of_this_type(self, text: str) -> bool:
        # https://en.wikipedia.org/wiki/Resident_registration_number

        if re.match(self.pattern, text):
            text_wo_hyphen = re.sub(r"[-]", "", text)
            if (
                text[6] in ["3", "4", "7", "8"]
                and int(text[:2]) > 20
                or (text[6] in ["3", "4", "7", "8"] and int(text[:2]) == 20 and int(text[2:4]) in [11, 12])
            ):
                return True
            else:
                numbers = list(text_wo_hyphen)
                check_weights = [2, 3, 4, 5, 6, 7, 8, 9, 2, 3, 4, 5]

                check_number = (
                    11
                    - sum([int(number) * weight for number, weight in zip(numbers[:-1], check_weights, strict=False)])
                    % 11
                ) % 10
                if check_number == int(numbers[12]):
                    return True
                else:
                    return False

        return False


class NUSSSpain(Identifier):
    pattern = re.compile(r"^\d{2}\d{8}\d{2}$", re.U)

    def is_of_this_type(self, text: str) -> bool:
        """
                El número de afiliación a la Seguridad Social está formado por los siguientes apartados: • Código de la provincia donde se asigna el número de la Seguridad Social al ciudadano (2 dígitos) • Número secuencial asignado (8 dígitos) • Dígitos de control (2 dígitos)
        11:44
        12 numbers.
        2 for the province
        8 sequence
        2 control
        =
        12
        11:44
        https://www.seg-social.es/wps/wcm/connect/wss/99d52a02-2968-4f38-b594-290ce13c29fb/T62-Provincia.pdf?MOD=AJPERES
        11:45
        Para el cálculo de los dígitos de control:
        1. Se toman los dos primeros apartados (número de la provincia y número del asegurado) y se unen, concatenándolos y haciendo un solo número. En nuestro ejemplo: 2812345678.
        2. Realizamos la división entera de este número entre el número primo 97, lo que nos producirá un resto comprendido entre 0 (para los números que sean múltiplos de 97) y 96; es decir, tomamos el resto de la división entera. Es lo que matemáticamente se conoce como la operación Mod 97. En nuestro ejemplo: 2812345678 Mod 97 = 40
        3. Si el resto de la división entera es inferior a 10, le ponemos un cero delante, así un resto 0 lo convertiremos en 00, el 1 en 01,...
        4. El resto de la división, con dos cifras, forma los dígitos de control. En nuestro ejemplo: 40
        """
        if self.pattern.match(text):
            return int(text[10:]) == int(text[:10]) % 90
        return False


class DNISpain(Identifier):
    pattern = re.compile(
        r"^(\d{8}[ ][-][ ][a-zA-Z])$|^(\d{8}[ ][-][a-zA-Z])$|^(\d{8}[- ][a-zA-Z])$|^(\d{8}[a-zA-Z])$|^(\d{8}[-][a-zA-Z])$"
    )
    remainder_vs_letter = [
        "T",
        "R",
        "W",
        "A",
        "G",
        "M",
        "Y",
        "F",
        "P",
        "D",
        "X",
        "B",
        "N",
        "J",
        "Z",
        "S",
        "Q",
        "V",
        "H",
        "L",
        "C",
        "K",
        "E",
    ]

    def is_of_this_type(self, text: str) -> bool:
        # https://en.wikipedia.org/wiki/Documento_Nacional_de_Identidad_(Spain)

        if self.pattern.match(text):
            text_wo_punct = re.sub(r"[ -]", "", text)
            check_digit = int(text_wo_punct[:8]) % 23
            return self.remainder_vs_letter[check_digit] == text[-1]

        return False


class NIESpain(Identifier):
    starting = set("XYZ")
    pattern = re.compile(
        r"^([XYZ]\d{7}[ ][-][ ][A-Z])$|^([XYZ]\d{7}[ ][-][A-Z])$|^([XYZ]\d{7}[- ][A-Z])$|^([XYZ]\d{7}[a-zA-Z])$|^([XYZ]\d{7}[-][A-Z])$",
        re.U | re.I,
    )
    remainder_vs_letter = [
        "T",
        "R",
        "W",
        "A",
        "G",
        "M",
        "Y",
        "F",
        "P",
        "D",
        "X",
        "B",
        "N",
        "J",
        "Z",
        "S",
        "Q",
        "V",
        "H",
        "L",
        "C",
        "K",
        "E",
    ]

    def is_of_this_type(self, text: str) -> bool:
        # https://es.wikipedia.org/wiki/N%C3%BAmero_de_identidad_de_extranjero

        if self.pattern.match(text):
            text_wo_punct = re.sub(r"[ -]", "", text).replace("X", "0").replace("Y", "1").replace("Z", "2")
            check_digit = int(text_wo_punct[:8]) % 23
            return self.remainder_vs_letter[check_digit] == text[-1]

        return False


class NIFSpain(Identifier):
    nie = NIESpain()
    dni = DNISpain()
    pattern = re.compile(
        r"^(?:[ABCDEFGHJNPQRSUVWKLMXYZ]\d{7}[ ][-][ ][A-Z0-9])$|^(?:[ABCDEFGHJNPQRSUVWKLMXYZ]\d{7}[ ][-][A-Z0-9])$|^(?:[ABCDEFGHJNPQRSUVWKLMXYZ]\d{7}[- ][A-Z0-9])$|^(?:[ABCDEFGHJNPQRSUVWKLMXYZ]\d{7}[A-Z0-9])$|^(?:\d{7}[-][A-Z0-9])$",
        re.I | re.U,
    )

    mapping = ["J", "A", "B", "C", "D", "E", "F", "G", "H", "I"]
    use_letter = set("KLMNPQRSW")

    def is_of_this_type(self, text: str) -> bool:
        # https://es.wikipedia.org/wiki/N%C3%BAmero_de_identificaci%C3%B3n_fiscal
        if text[0].isnumeric():
            return self.dni.is_of_this_type(text)
        if text[0] in NIESpain.starting:
            return self.nie.is_of_this_type(text)

        if self.pattern.match(text):
            text_wo_punct = re.sub(r"[ -]", "", text)
            A = sum(int(x) for x in text_wo_punct[2:8:2])
            B = sum(self._single_digit_from_double(int(x)) for x in text_wo_punct[1:8:2])

            C = str(A + B)

            if C[-1] == "0":
                code = 0
            else:
                code = 10 - int(C[-1])

            if text[0] in NIFSpain.use_letter:
                return text[-1] == NIFSpain.mapping[code]
            else:
                return text[-1] == str(code)

        return False

    def _single_digit_from_double(self, x: int) -> int:
        return sum(int(d) for d in f"{x * 2}")


class TFNAustralia(Identifier):
    pattern = re.compile(r"^\d{9}$")
    weight_array = [1, 4, 3, 7, 5, 8, 6, 9, 10]

    def is_of_this_type(self, text: str) -> bool:
        if re.match(self.pattern, text):
            # https://en.wikipedia.org/wiki/Tax_file_number http://www.mathgen.ch/codes/tfn.html#anaoreport
            check_sum = sum([int(i) * weight for i, weight in zip(text, self.weight_array, strict=False)])
            if not check_sum % 11:
                return True

        return False


class SSNUK(Identifier):
    def is_of_this_type(self, text: str) -> bool:
        compressed = text.replace(" ", "").upper()

        if not (len(compressed) == len(text) or len(compressed) + 4 == len(text)):
            # accept only 1 word or 1 space every 2 characters (left to right)
            return False

        if len(compressed) != 9:
            return False

        first = compressed[0]

        if not first.isalpha() or first in "DFIQUV":
            return False

        second = compressed[1]

        if not second.isalpha() or second in "DFIQUVO":
            return False

        for c in compressed[2:-1]:
            if not c.isdigit():
                return False

        if ord("A") <= ord(compressed[8]) <= ord("D"):
            return True

        return False


class SSN(Identifier):
    """Identifier for US Social Security Numbers (SSN).

    Format: XXX-XX-XXXX where X is a digit.
    Validates format and excludes invalid area numbers (000, 666).

    Example:
        >>> identifier = SSN()
        >>> identifier.is_of_this_type("123-45-6789")
        True
        >>> identifier.is_of_this_type("000-12-3456")
        False
    """

    def is_of_this_type(self, text: str) -> bool:
        """Check if text is a valid US Social Security Number.

        Args:
            text: The text to check.

        Returns:
            True if text is a valid SSN format with valid area number, False otherwise.
        """
        parts = text.split("-")

        if len(parts) != 3:
            return False

        [first, second, third] = parts

        if len(first) != 3 or len(second) != 2 or len(third) != 4:
            return False

        if not first.isdigit() or not second.isdigit() or not third.isdigit():
            return False

        if first == "000" or first == "666":
            return False

        return True


class USPassport(RegexIdentifierWithSpan):
    """Identifier for US Passport numbers.

    Format: One letter followed by 8 digits, optionally prefixed with keywords
    like "passport", "passport#", etc.

    Example:
        >>> identifier = USPassport()
        >>> identifier.is_of_this_type("A12345678")
        True
        >>> identifier.is_of_this_type("Passport: B98765432")
        True
    """

    def __init__(self) -> None:
        """Initialize the USPassport identifier with regex pattern."""
        super().__init__(
            "USPassport",
            [
                re.compile(
                    r"^(?:passport#|passport #|passportid|passports|passportno|passport no|passportnumber|passport number|passportnumbers|passport numbers)?\s*([a-zA-Z]\d{8})$"
                ),
            ],
        )


class PESELPoland(Identifier):
    # https://en.wikipedia.org/wiki/PESEL
    # YYMMDDZZZXQ
    checksum_weights = [1, 3, 7, 9, 1, 3, 7, 9, 1, 3]

    days = [f"{day:02d}" for day in range(1, 32)]
    months_XX = [f"{month:02d}" for month in range(1, 13)]
    month_XXI = [f"{month + 20:02d}" for month in range(1, 13)]
    month_XXII = [f"{month + 40:02d}" for month in range(1, 13)]
    month_XXIII = [f"{month + 60:02d}" for month in range(1, 13)]
    month_XIX = [f"{month + 80:02d}" for month in range(1, 13)]
    months = set(month_XIX + months_XX + month_XXI + month_XXII + month_XXIII)

    def _check_birthdate(self, day: str, month: str) -> bool:
        if day not in self.days:
            return False
        if month not in self.months:
            return False
        return True

    def is_of_this_type(self, text: str) -> bool:
        text = text.strip()
        text = text.replace(" ", "")

        if not len(text) == 11:
            return False

        if not text.isnumeric():
            return False

        dob_part = text[:6]
        if not self._check_birthdate(day=text[4:6], month=dob_part[2:4]):
            return False

        checksum = 0
        for item, weight in zip(text[:-1], self.checksum_weights, strict=False):
            checksum += int(item) * weight

        check_digit = (10 - checksum % 10) % 10
        if check_digit != int(text[-1]):
            return False

        return True


class NationalIdentity(Identifier):
    """Composite identifier for national identity numbers from multiple countries.

    Combines identifiers for national IDs from various countries. Can operate in
    safe mode (only IDs with checksum validation) or include IDs without checksums.

    Supported countries include: Brazil, France, Germany, Italy, Japan, Canada,
    Israel, Mexico, Spain, China, South Korea, Australia, UK, US, Poland, and more.

    Attributes:
        safe: If True, only check IDs with checksum validation. Defaults to True.
        with_check: List of identifiers with checksum validation.
        without_check: List of identifiers without checksum validation.

    Example:
        >>> identifier = NationalIdentity(safe=True)
        >>> identifier.is_of_this_type("123-45-6789")  # US SSN
        True
    """

    def __init__(self, safe: bool = True) -> None:
        """Initialize the NationalIdentity identifier.

        Args:
            safe: If True, only validate IDs with checksums. Defaults to True.
        """
        self.safe = safe

        self.with_check: list[Identifier] = [
            CFPBrazil(),
            NIRFrance(),
            TINGermany(),
            ItalianFiscalCode(),
            MyNumberJapan(),
            CanadaSIN(),
            IsraelID(),
            MexicoCURP(),
            NUSSSpain(),
            NIFSpain(),
            PRChinaID(),
            RRNSouthKorea(),
            TFNAustralia(),
            SSNUK(),
            SSN(),
            PESELPoland(),
        ]

        self.without_check: list[Identifier] = [
            AadhaarNumber(),
            ICDIndonesia(),
            RussianInternalPassport(),
            RussianInternationalPassport(),
        ]

    def is_of_this_type(self, text: str) -> bool:
        """Check if text is a valid national identity number.

        Args:
            text: The text to check.

        Returns:
            True if text matches any supported national ID format, False otherwise.
        """
        if self.safe:
            return any(identifier.is_of_this_type(text) for identifier in self.with_check)
        else:
            return any(identifier.is_of_this_type(text) for identifier in self.with_check) or any(
                identifier.is_of_this_type(text) for identifier in self.without_check
            )
