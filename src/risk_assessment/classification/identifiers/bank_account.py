import re

from risk_assessment.classification.identifiers import RegexIdentifierWithSpan


class JapanBankAccountNumber(RegexIdentifierWithSpan):
    def __init__(self) -> None:
        return super().__init__(
            "JapanBankAccountNumber",
            [
                re.compile(r"^(\d{7,8}\d{4}[ -]?\d{3})$", re.UNICODE),
            ],
        )
