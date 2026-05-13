import re

from risk_assessment.classification.identifiers import Identifier


class ISBN(Identifier):
    _pattern = re.compile(r"(\d{3})[ \-]?(\d{1,5})[ \-]?(\d{1,7})[ \-]?(\d{1,6})[ \-]?(\d)")
    _pattern_10 = re.compile(r"(\d{1,5})[ \-]?(\d{1,7})[ \-]?(\d{1,6})[ \-]?([0-9X])")

    def _check_isbn_10(self, text: str) -> bool:
        match = ISBN._pattern_10.match(text)

        if match and 10 == sum([len(group) for group in match.groups()]):
            return self._valid_checksum_10("".join(match.groups()))
        return False

    def _valid_checksum_10(self, digits: str) -> bool:
        parity = 10 if digits[-1] == "X" else int(digits[-1])

        checksum = (
            sum([position * int(digit) for position, digit in zip(range(len(digits), 1, -1), digits, strict=False)])
            % 11
        )

        return (11 - checksum) % 11 == parity

    def _check_isbn(self, text: str) -> bool:
        match = ISBN._pattern.match(text)

        if match:
            groups = list(match.groups())

            if sum([len(group) for group in groups]) == 13 and self._match_prefix(groups[0]):
                return self._valid_checksum("".join(groups))

        return False

    def _valid_checksum(self, digits: str) -> bool:
        even_sum = sum([3 * int(digit) for position, digit in enumerate(digits) if position % 2 == 1])
        odd_sum = sum([int(digit) for position, digit in enumerate(digits) if position % 2 == 0])
        return (even_sum + odd_sum) % 10 == 0

    def _match_prefix(self, prefix: str) -> bool:
        return prefix == "978" or prefix == "979"

    def is_of_this_type(self, text: str) -> bool:
        return self._check_isbn(text) or self._check_isbn_10(text)


class CODEN(Identifier):
    _pattern = re.compile(r"^[0-9A-Z]{6}$")

    def is_of_this_type(self, text: str) -> bool:
        match = CODEN._pattern.match(text.strip())

        return match is not None


class ISSN(Identifier):
    _pattern = re.compile(r"^([0-9]{4})-?([0-9]{3})([0-9xX])$")

    def is_of_this_type(self, text: str) -> bool:
        match = ISSN._pattern.match(text)

        if match:
            return self._validate_checksum(match.group(1) + match.group(2) + match.group(3))

        return False

    def _validate_checksum(self, digits: str) -> bool:
        parity = 10 if digits[-1] == "X" else int(digits[-1])

        checksum = (
            sum([position * int(digit) for position, digit in zip(range(len(digits), 1, -1), digits, strict=False)])
            % 11
        )

        return (11 - checksum) % 11 == parity
