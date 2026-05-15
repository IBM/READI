"""READI (Risk Evaluation and Data Identification) Analyzer for detecting sensitive information.

This module provides the main analyzer class for detecting PII (Personally Identifiable
Information) and PHI (Protected Health Information) in unstructured text using multiple
entity extraction methods and intelligent aggregation.
"""

import logging
from enum import Enum, auto

from risk_assessment.classification.unstructured import (
    Entity,
    EntityExtractor,
    MultiSourceEntityExtractor,
)
from risk_assessment.classification.unstructured.aggregator import (
    Aggregator,
    AggregatorConfiguration,
)

logger = logging.getLogger(__name__)


class READIAnalyzer:
    """Main analyzer for detecting sensitive information in unstructured text.

    The READIAnalyzer combines multiple entity extraction methods (NER models,
    regex patterns, dictionary lookups) and uses intelligent aggregation to
    identify and classify sensitive information like names, emails, phone numbers,
    medical terms, and other PII/PHI.

    Attributes:
        aggregator: Aggregator instance for combining and filtering entity detections.
        entity_extractors: List of entity extractors to use for detection.
        detection_type: Type of detection being performed (PHI, PII, etc.).

    Example:
        >>> # Using default PHI detection
        >>> analyzer = READIAnalyzer(detection_type=READIAnalyzer.DetectionType.PHI)
        >>> text = "Patient John Doe, email: john@example.com, SSN: 123-45-6789"
        >>> entities = analyzer.detect(text)
        >>> for entity in entities:
        ...     print(f"{entity.entity_type}: {text[entity.start:entity.end]}")
        Person: John Doe
        Email: john@example.com
        NationalIdentity: 123-45-6789

        >>> # Using custom configuration
        >>> from risk_assessment.classification.identifiers import Email, Phone
        >>> from risk_assessment.classification.unstructured.drl import DRLEntityExtractor
        >>> custom_extractors = [DRLEntityExtractor(identifiers=[Email(), Phone()])]
        >>> custom_config = AggregatorConfiguration(merge_entities=True)
        >>> analyzer = READIAnalyzer(
        ...     detection_type=READIAnalyzer.DetectionType.CUSTOM,
        ...     entity_extractors=custom_extractors,
        ...     aggregator_configuration=custom_config
        ... )
    """

    class DetectionType(Enum):
        """Enumeration of supported detection types.

        Attributes:
            PHI: Protected Health Information detection (medical records, patient data).
            PII: Personally Identifiable Information detection (general personal data).
            PII_NO_MODEL: PII detection without machine learning models (faster, less accurate).
            CUSTOM: Custom detection using user-provided extractors and configuration.
        """

        PHI = auto()
        PII = auto()
        PII_NO_MODEL = auto()
        CUSTOM = auto()

    def __init__(
        self,
        detection_type: DetectionType = DetectionType.PHI,
        entity_extractors: list[EntityExtractor | MultiSourceEntityExtractor] | None = None,
        aggregator_configuration: AggregatorConfiguration | None = None,
    ) -> None:
        """Initialize the READI analyzer.

        Args:
            detection_type: Type of detection to perform. Defaults to PHI.
            entity_extractors: Custom entity extractors (required for CUSTOM detection type).
            aggregator_configuration: Custom aggregator config (required for CUSTOM detection type).

        Raises:
            ValueError: If CUSTOM detection type is used without providing extractors or configuration.
            ValueError: If an unsupported detection type is provided.

        Example:
            >>> # Default PHI detection
            >>> analyzer = READIAnalyzer()

            >>> # PII detection
            >>> analyzer = READIAnalyzer(detection_type=READIAnalyzer.DetectionType.PII)

            >>> # Custom detection
            >>> from risk_assessment.classification.identifiers import Email
            >>> from risk_assessment.classification.unstructured.drl import DRLEntityExtractor
            >>> extractors = [DRLEntityExtractor(identifiers=[Email()])]
            >>> config = AggregatorConfiguration(merge_entities=True)
            >>> analyzer = READIAnalyzer(
            ...     detection_type=READIAnalyzer.DetectionType.CUSTOM,
            ...     entity_extractors=extractors,
            ...     aggregator_configuration=config
            ... )
        """
        if detection_type is READIAnalyzer.DetectionType.PHI:
            from risk_assessment.readi.defaults_phi import (
                AGGREGATOR_CONFIGURATION,
                ENTITY_EXTRACTORS,
            )
        elif detection_type is READIAnalyzer.DetectionType.PII:
            from risk_assessment.readi.defaults_pii import (
                AGGREGATOR_CONFIGURATION,
                ENTITY_EXTRACTORS,
            )
        elif detection_type is READIAnalyzer.DetectionType.PII_NO_MODEL:
            from risk_assessment.readi.defaults_pii_no_model import (
                AGGREGATOR_CONFIGURATION,
                ENTITY_EXTRACTORS,
            )
        elif detection_type is READIAnalyzer.DetectionType.CUSTOM:
            if entity_extractors is None or len(entity_extractors) == 0:
                raise ValueError(f"Missing entity_extractors for {detection_type=}")
            if aggregator_configuration is None:
                raise ValueError(f"Missing aggregator_configuration for {detection_type=}")
            ENTITY_EXTRACTORS = entity_extractors
            AGGREGATOR_CONFIGURATION = aggregator_configuration
        else:
            raise ValueError(f"Unsupported type {detection_type}")

        self.aggregator = Aggregator(AGGREGATOR_CONFIGURATION)
        self.entity_extractors = ENTITY_EXTRACTORS
        self.detection_type = detection_type

    def detect(self, text: str) -> list[Entity]:
        """Detect sensitive entities in the provided text.

        Runs all configured entity extractors on the text and aggregates their
        results using intelligent merging, filtering, and validation to produce
        a final list of detected entities.

        Args:
            text: The text to analyze for sensitive information.

        Returns:
            List of Entity objects representing detected sensitive information.
            Each entity includes start/end positions, type, source extractors,
            and optional confidence scores.

        Example:
            >>> analyzer = READIAnalyzer(detection_type=READIAnalyzer.DetectionType.PHI)
            >>> text = "Dr. Smith treated patient Jane Doe (jane@hospital.org)"
            >>> entities = analyzer.detect(text)
            >>> for entity in entities:
            ...     span = text[entity.start:entity.end]
            ...     print(f"{entity.entity_type}: '{span}' at position {entity.start}-{entity.end}")
            Person: 'Dr. Smith' at position 0-9
            Person: 'Jane Doe' at position 30-38
            Email: 'jane@hospital.org' at position 40-57
        """
        entities = [extractor.extract(text) for extractor in self.entity_extractors]

        return self.aggregator.aggregate(entities, text)
