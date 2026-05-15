"""Medical record number identifier for detecting MRN patterns.

This module provides an identifier for recognizing medical record numbers
used by healthcare facilities to identify patient records.
"""

import re

from risk_assessment.classification.identifiers import RegexIdentifier


class MedicalRecordNumber(RegexIdentifier):
    """Identifier for medical record numbers (MRN).

    Recognizes various formats of medical record numbers including
    alphanumeric patterns, MED-prefixed, and MRN-prefixed formats.

    Example:
        >>> identifier = MedicalRecordNumber()
        >>> identifier.is_of_this_type("A12345")
        True
        >>> identifier.is_of_this_type("MED123456")
        True
        >>> identifier.is_of_this_type("MRN-1234")
        True
    """

    def __init__(self) -> None:
        """Initialize the MedicalRecordNumber identifier with regex patterns."""
        super().__init__(
            "MedicalRecordNumber",
            [
                re.compile(r"^[a-z]\d{5,7}$", re.I | re.U),
                re.compile(r"^MED\d{6,8}$", re.I | re.U),
                re.compile(r"^MRN-\d{4,6}$", re.I | re.U),
            ],
        )
