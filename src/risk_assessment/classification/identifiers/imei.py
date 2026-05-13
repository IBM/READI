import re

from risk_assessment.classification.identifiers import LuhnIdentifier


class IMEI(LuhnIdentifier):
    pattern = re.compile(r"^\d{15}$")

    def is_of_this_type(self, text: str) -> bool:
        if text.isnumeric():
            if self.pattern.match(text) and self.check_luhn(text):
                return True
        return False
