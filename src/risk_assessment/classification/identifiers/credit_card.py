import re

from risk_assessment.classification.identifiers import LuhnIdentifier


class CreditCard(LuhnIdentifier):
    patterns = [
        re.compile(r"^4\d{15}$"),  # visa
        re.compile(r"^4\d{3}(?:[- ]?\d{4}){3}$"),  # visa with formatting
        re.compile(r"^4\d{3}(?:[- ]?\d{4}){2}[- ]\d{3}$"),  # visa with formatting
        re.compile(r"^(?:5[1-5]\d{2}|222[1-9]|22[3-9]\d|2[3-6]\d{2}|27[01]\d|2720)\d{12}$"),  # MasterCard
        re.compile(r"^(?:5[1-5]\d{2}|222[1-9]|22[3-9]\d|2[3-6]\d{2}|27[01]\d|2720)\d{12}$"),  # MasterCard v2
        re.compile(r"^3[47]\d{13}$"),  # AMEX
        re.compile(r"^3[47]\d{2}-\d{4}-\d{4}-\d{3}$"),  # AMEX v2
        re.compile(r"^3[47]\d{2} \d{4} \d{4} \d{3}$"),  # AMEX v3
        re.compile(r"^3(?:0[0-5]|[68]\d)\d{11}$"),  # Diners Club
        re.compile(r"^6(?:011|5\d{2})\d{12}$"),  # Discover
        re.compile(r"^(?:2131|1800|35\d{3})\d{11}$"),  # JCB
        re.compile(r"^(?:5018|5020|5038|5893|6304|6759|6761|6762|6763)\d{8,15}$"),  # MAESTRO
        re.compile(r"^6759\d{8,15}$"),  # MAESTRO UK 1
        re.compile(r"^67677[04]\d{6,13}$"),  # MAESTRO UK
    ]

    def is_of_this_type(self, text: str) -> bool:
        for pattern in self.patterns:
            if pattern.match(text) and self.check_luhn(text):
                return True
        return False

    def debug_values(self, text: str) -> int:
        for pattern in self.patterns:
            if pattern.match(text):
                if self.check_luhn(text):
                    return 0
                else:
                    return 1
        return 2
