"""Recommended identifier lists for common use cases.

This module provides pre-configured lists of identifiers for specific
compliance requirements like HIPAA.
"""

from risk_assessment.classification.identifiers import (
    IBAN,
    IP,
    SSN,
    SWIFT,
    URI,
    City,
    Country,
    CreditCard,
    DateTime,
    Email,
    ICDv9,
    ICDv10,
    Identifier,
    Person,
    Phone,
    UnitedStateState,
    USPhone,
    USPostalAddress,
    ZipCode,
)

"""List of identifiers for HIPAA (Health Insurance Portability and Accountability Act) compliance.

Includes identifiers for the 18 types of Protected Health Information (PHI)
specified by HIPAA regulations.
"""
HIPAA: list[Identifier] = [
    Person(),
    USPostalAddress(),
    City(),
    Country(),
    UnitedStateState(),
    Email(),
    ZipCode(),
    DateTime(),
    Phone(),
    USPhone(),
    ICDv9(),
    ICDv10(),
    URI(),
    SSN(),
    IP(),
    SWIFT(),
    IBAN(),
    CreditCard(),
]
