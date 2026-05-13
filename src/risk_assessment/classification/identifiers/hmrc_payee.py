import re

from risk_assessment.classification.identifiers import RegexIdentifier


class HMRC_PAYE(RegexIdentifier):
    def __init__(self) -> None:
        super().__init__(
            "HMRC_PAYE",
            patterns=[
                re.compile(r"^\d{3}/[a-z]{1,2}\d{3,}$", re.I),
            ],
        )
