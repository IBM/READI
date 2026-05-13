import re

from risk_assessment.classification.identifiers import RegexIdentifier


class HealthcareBeneficiaryNumber(RegexIdentifier):
    def __init__(self) -> None:
        super().__init__(
            "HealthcareBeneficiaryNumber",
            [
                re.compile(r"^[a-z]\d{7,9}$", re.I | re.U),
                re.compile(r"^HPBN-\d{6,8}$", re.I | re.U),
            ],
        )
