from dataclasses import dataclass
from re import Pattern


@dataclass
class IBANCountryValidator:
    pattern: Pattern[str]

    def validate(self, text: str) -> bool:
        """
        Validating the IBAN

        An IBAN is validated by converting it into an integer and performing a basic mod-97 operation (as described in ISO 7064) on it. If the IBAN is valid, the remainder equals 1.
        The algorithm of IBAN validation is as follows:
            Check that the total IBAN length is correct as per the country. If not, the IBAN is invalid
            Move the four initial characters to the end of the string
            Replace each letter in the string with two digits, thereby expanding the string, where A = 10, B = 11, ..., Z = 35
            Interpret the string as a decimal integer and compute the remainder of that number on division by 97

            If the remainder is 1, the check digit test is passed and the IBAN might be valid.
        """
        text = text[4:] + text[0:4]

        return 1 == self.convert_to_int(text.upper()) % 97

    def convert_to_int(self, iban: str) -> int:
        return int("".join([c if c.isdigit() else str(10 + ord(c) - ord("A")) for c in iban.upper()]))

    def is_valid(self, text: str) -> bool:
        if self.get_pattern().fullmatch(text) and self.validate(text):
            return True
        return False

    def get_pattern(self) -> Pattern[str]:
        return self.pattern
