import re

from risk_assessment.classification.identifiers import RegexIdentifierWithSpan


class VoterID(RegexIdentifierWithSpan):
    def __init__(self) -> None:
        super().__init__(
            "VoterID",
            [
                re.compile(r"\s*voter\s+ID\s+number\s+(?:is\s+)?(\d{6,})\.?", re.I | re.U),
            ],
        )

    def get_span_length_required_to_check(self) -> int:
        return len("voter ID number ") + 10  # 10 preserved for additional spaces and symbols
