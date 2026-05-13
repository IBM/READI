import re
from re import Pattern

from risk_assessment.classification.identifiers import Identifier

_valid_period_digits: set[str] = {
    "01",
    "02",
    "03",
    "04",
    "05",
    "06",
    "07",
    "08",
    "09",
    "10",
    "11",
    "12",
}


class AccountsOfficeReferenceNumber(Identifier):
    pattern: Pattern[str] = re.compile(r"^\d{3}P[a-z]\d{7}(?:\d|X)(\d{4})?$", re.I)  # 13 or 16 characters

    def is_of_this_type(self, text: str) -> bool:
        match = self.pattern.match(text)

        if match is not None:
            additional_digits = match.group(1)

            if additional_digits is None:
                return True  # 13 characters "validated"
            else:
                # validation to be c
                return additional_digits[2:] in _valid_period_digits

        return False
