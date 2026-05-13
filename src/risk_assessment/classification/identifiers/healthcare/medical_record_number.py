import re

from risk_assessment.classification.identifiers import RegexIdentifier


class MedicalRecordNumber(RegexIdentifier):
    def __init__(self) -> None:
        super().__init__(
            "MedicalRecordNumber",
            [
                re.compile(r"^[a-z]\d{5,7}$", re.I | re.U),
                re.compile(r"^MED\d{6,8}$", re.I | re.U),
                re.compile(r"^MRN-\d{4,6}$", re.I | re.U),
            ],
        )
