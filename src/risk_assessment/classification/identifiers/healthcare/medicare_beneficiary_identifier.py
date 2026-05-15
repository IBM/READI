"""Medicare Beneficiary Identifier for detecting MBI numbers.

This module provides an identifier for recognizing Medicare Beneficiary
Identifiers (MBI) used in the US Medicare system.
"""

import re

from risk_assessment.classification.identifiers import RegexIdentifier


class MedicareBeneficiaryIdentifier(RegexIdentifier):
    """Identifier for Medicare Beneficiary Identifier (MBI).

    MBI is an 11-character identifier used by Medicare. The format uses
    specific character positions with defined character sets to avoid
    confusion (e.g., no 'S', 'L', 'O', 'I', 'B', 'Z').

    Attributes:
        C: Character set for numeric positions (1-9).
        A: Character set for alphabetic positions (excluding confusing letters).
        N: Character set for numeric positions (0-9).

    Example:
        >>> identifier = MedicareBeneficiaryIdentifier()
        >>> identifier.is_of_this_type("1EG4-TE5-MK73")
        True
    """

    C = r"[1-9]"
    A = r"[ACDEFGHJKMNPQRTUVWXY]"
    N = r"[0-9]"

    def __init__(self) -> None:
        """Initialize the MedicareBeneficiaryIdentifier with MBI pattern."""
        super().__init__(
            "MBI",
            [
                re.compile(
                    r"[1-9][ACDEFGHJKMNPQRTUVWXY][ACDEFGHJKMNPQRTUVWXY0-9]\d[ -]?[ACDEFGHJKMNPQRTUVWXY][ACDEFGHJKMNPQRTUVWXY0-9]\d[ -]?[ACDEFGHJKMNPQRTUVWXY]{2}\d{2}",
                    re.I | re.U,
                )
            ],
        )
