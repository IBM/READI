"""Default configuration for PII detection without machine learning models.

This module provides a lightweight PII detection configuration that uses only
dictionary-based and regex-based identifiers without heavy ML models like spaCy.
This configuration is faster and requires less memory than the full PII detection,
making it suitable for resource-constrained environments or when speed is critical.

The configuration includes:
- Dictionary and regex-based entity extractors (DRL)
- NLTK POS tagging for basic linguistic analysis
- No transformer models or spaCy models
- Optimized for speed over accuracy

Use this configuration when:
- You need faster processing times
- Memory/compute resources are limited
- You don't need the highest accuracy
- You're processing large volumes of text

Example:
    >>> from risk_assessment.readi.analyzer import READIAnalyzer
    >>> analyzer = READIAnalyzer(
    ...     detection_type=READIAnalyzer.DetectionType.PII_NO_MODEL
    ... )
    >>> text = "Contact John Doe at john@example.com or 555-1234"
    >>> entities = analyzer.detect(text)
"""

import nltk

from risk_assessment.classification.identifiers import (
    IBAN,
    IP,
    SWIFT,
    URI,
    AgeImproved,
    AustralianMedicareNumber,
    Country,
    CreditCard,
    DateTime,
    Email,
    GenderLong,
    HealthcareBeneficiaryNumber,
    Identifier,
    NationalIdentity,
    Person,
    Phone,
    ZipCode,
)
from risk_assessment.classification.unstructured import (
    EntityExtractor,
    MultiSourceEntityExtractor,
)
from risk_assessment.classification.unstructured.aggregator import (
    AggregatorConfiguration,
)
from risk_assessment.classification.unstructured.drl import (
    DRLEntityExtractor,
    ImprovedDRLEntityExtractor,
)
from risk_assessment.classification.unstructured.nltk import NLTKPoSTagger

nltk.download("averaged_perceptron_tagger", quiet=True)


from nltk import TreebankWordTokenizer, WordPunctTokenizer  # noqa: E402
from nltk.tag import PerceptronTagger  # noqa: E402

#: Tokenizer used for text processing
TOKENIZER = TreebankWordTokenizer()

#: List of identifier instances for detecting various PII types
IDENTIFIERS: list[Identifier] = [
    AgeImproved(),
    Country(False),
    CreditCard(),
    DateTime(),
    Email(),
    GenderLong(),
    HealthcareBeneficiaryNumber(),
    IBAN(),
    IP(allow_double_colon=False),
    NationalIdentity(safe=True),
    Person(),
    SWIFT(),
    Phone(),
    AustralianMedicareNumber(),
    ZipCode(),
    URI(),
]

#: Identifiers to use for validation (excludes URI which is last in the list)
IDENTIFIERS_TO_VALIDATE: list[Identifier] = IDENTIFIERS[:-1]

#: List of entity extractors that will be used for PII detection.
#: This configuration uses only lightweight extractors without ML models:
#: - NLTKPoSTagger: Basic part-of-speech tagging
#: - ImprovedDRLEntityExtractor: Dictionary and regex-based detection
#: - DRLEntityExtractor: Specialized URI detection
ENTITY_EXTRACTORS: list[EntityExtractor | MultiSourceEntityExtractor] = [
    NLTKPoSTagger(TOKENIZER, PerceptronTagger()),
    ImprovedDRLEntityExtractor(
        identifiers=IDENTIFIERS,
        tokenizer_list=[WordPunctTokenizer(), TOKENIZER],
        max_shinglet_length=15,
        type_mapping={
            "Age": "DateTime",
            "AgeImproved": "DateTime",
            "GenderLong": "Gender",
            "SSN": "NationalIdentity",
            "SSNUK": "NationalIdentity",
            "USPostalAddress": "Location",
            "ZipCode": "Location",
        },
    ),
    DRLEntityExtractor(
        identifiers=[URI()],
        tokenizer=TOKENIZER,
        min_shinglet_length=10,
        max_shinglet_length=35,
    ),
]

AGGREGATOR_CONFIGURATION = AggregatorConfiguration(
    merge_entities=True,
    prioritize_inclusion=True,
    validate_part_of_speech=True,
    identifiers_list=IDENTIFIERS_TO_VALIDATE,
    filter_symbols={",", ".", "-", " ", "!", ":", ";", "\n", "\t"},
    thresholds={"Person": 450},
    pos_insensitive_types={
        "AustralianMedicareNumber",
        "CreditCard",
        "DEANumber",
        "Date",
        "DateTime",
        "Email",
        "HealthcareBeneficiaryNumber",
        "IBAN",
        "IMEI",
        "IP",
        "MedicalTerm",
        "MedicalRecordNumber",
        "NationalIdentity",
        "Organization",
        "Phone",
        "SWIFT",
        "USPhone",
        "UniqueID",
        "ZipCode",
        "URI",
    },
    to_report_only={
        "ATC",
        "Age",
        "AgeImproved",
        "AustralianMedicareNumber",
        "CreditCard",
        "DEANumber",
        "DateTime",
        "Email",
        "Gender",
        "Gene",
        "HealthcareBeneficiaryNumber",
        "IBAN",
        "IP",
        "Location",
        "MedicalTerm",
        "MedicalRecordNumber",
        "NDC",
        "NORP",
        "NationalIdentity",
        "Net.EmailAddress",
        "Net.IPAddress",
        "Net.MacAddress",
        "Person",
        "Phone",
        "PhoneNumber",
        "SSN",
        "SWIFT",
        "URI",
        "USPhone",
        "UniqueID",
        "ZipCode",
    },
    weights={
        "QUANTITY": {"SPACY": 6000},
        "CARDINAL": {"SPACY": 6000},
        "NORP": {"SPACY": 6000},
        "ZipCode": {"DRL": 100},
        "Location": {
            "DRL": 1300,
            "SPACY": 500,
        },
        "Person": {
            "DRL": 100,
            "SPACY": 450,
            "SPACY_ML": 450,
        },
        "USPhone": {"DRL": 1000},
        "URI": {"DRL": 4000},
        "IP": {"DRL": 4000},
        "SSN": {"DRL": 2000, "DEBERTA_PII": 1000},
        "NationalIdentity": {"DRL": 1500},
        "DateTime": {
            "DRL": 1000,
            "SPACY": 450,
        },
        "Email": {"DRL": 2000},
        "IBAN": {"DRL": 4000},
        "CreditCard": {"DRL": 1000},
        "MedicalTerm": {"DRL": 100},
        "Quantity": {"SPACY": 2000},
        "Gene": {"DRL": 100},
        "SWIFT": {"DRL": 1000},
        "ATC": {"DRL": 1000},
        "NDC": {"DRL": 1000},
        "Age": {"DRL": 6000},
        "PERCENT": {"SPACY": 6000},
        "AccountsOfficeReferenceNumber": {"DRL": 1000},
        "NationalIdentifier": {"DRL": 1000},
        "DEANumber": {"DRL": 1000},
        "HealthcareBeneficiaryNumber": {"DRL": 1000},
        "UniqueID": {"DRL": 1000},
        "MedicalRecordNumber": {"DRL": 1000},
        "AustralianMedicareNumber": {"DRL": 1000},
        "Phone": {
            "DRL": 500,
        },
    },
)
