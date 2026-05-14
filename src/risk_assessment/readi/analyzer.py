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
    class DetectionType(Enum):
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
        entities = [extractor.extract(text) for extractor in self.entity_extractors]

        return self.aggregator.aggregate(entities, text)
