import re

from risk_assessment.classification.identifiers import RegexIdentifier


class UniqueIDIdentifier(RegexIdentifier):
    def __init__(self) -> None:
        super().__init__(
            "UniqueID",
            [
                re.compile(r"^[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}$", re.I | re.U),
                re.compile(r"^[a-z0-9]{12}$", re.I | re.U),
                re.compile(r"^[a-z0-9]{6}-[a-z0-9]{6}$", re.I | re.U),
                re.compile(r"^[a-z0-9]{3}-[a-z0-9]{9}$", re.I | re.U),
                re.compile(r"^UID-[a-z0-9]{8}$", re.I | re.U),
            ],
        )
