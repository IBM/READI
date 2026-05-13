import re

from risk_assessment.classification.identifiers import RegexIdentifier


class MedicareBeneficiaryIdentifier(RegexIdentifier):
    C = r"[1-9]"
    A = r"[ACDEFGHJKMNPQRTUVWXY]"
    N = r"[0-9]"

    def __init__(self) -> None:
        super().__init__(
            "MBI",
            [
                re.compile(
                    r"[1-9][ACDEFGHJKMNPQRTUVWXY][ACDEFGHJKMNPQRTUVWXY0-9]\d[ -]?[ACDEFGHJKMNPQRTUVWXY][ACDEFGHJKMNPQRTUVWXY0-9]\d[ -]?[ACDEFGHJKMNPQRTUVWXY]{2}\d{2}",
                    re.I | re.U,
                )
            ],
        )
