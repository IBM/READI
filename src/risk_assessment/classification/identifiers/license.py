import re

from risk_assessment.classification.identifiers import RegexIdentifierWithSpan


class NationwideMultistateLicensingSystem(RegexIdentifierWithSpan):
    def __init__(self) -> None:
        super().__init__(
            "NMLS",
            [
                re.compile(r"^(?:NMLS(?:\s+license)?\s+)?(#\d{7,12})$", re.I | re.U),
            ],
        )


class CaliforniaFinancingLaw(RegexIdentifierWithSpan):
    def __init__(self) -> None:
        super().__init__(
            "CFL",
            [
                re.compile(r"^(?:CFL(?:\s+license)?\s+)?(#\d{7,12})$", re.I | re.U),
                re.compile(
                    r"^(?:CFL(?:\s+license)?\s+)?(#60DBO-?\d{5,12})$", re.I | re.U
                ),  # pattern for transitioning license
            ],
        )
