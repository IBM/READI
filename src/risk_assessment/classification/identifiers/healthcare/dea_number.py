import re

from risk_assessment.classification.identifiers import RegexIdentifier


class DEANumber(RegexIdentifier):
    def __init__(self) -> None:
        super().__init__(
            "DEANumber",
            [
                # re.compile(r"^[A-Z]{2}\d{7}$", re.U),
                re.compile(r"^[ABCDEFGHJKLMPRSTUX][A-Z9]\d{6}\d$", re.U),
                re.compile(r"^[ABCDEFGHJKLMPRSTUX][A-Z9]\d{6}\d-\w{3,}$", re.U),
            ],
        )

    def is_of_this_type(self, text: str) -> bool:
        return super().is_of_this_type(text) and self._checksum(text)

    def _checksum(self, text: str) -> bool:
        numbers = text.split("-")[0][2:]

        calc_135 = int(numbers[0]) + int(numbers[2]) + int(numbers[4])
        calc_246 = int(numbers[1]) + int(numbers[3]) + int(numbers[5])
        calc_246 *= 2

        check = str(calc_135 + calc_246)[-1]

        return numbers[-1] == check
