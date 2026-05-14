import logging

from risk_assessment.classification.unstructured import Entity, EntityExtractor

logger = logging.getLogger(__name__)

try:
    from presidio_analyzer import AnalyzerEngine, RecognizerRegistry, RecognizerResult
    from presidio_analyzer.nlp_engine import NlpEngine

    class PresidioEntityExtractor(EntityExtractor):
        NAME: str = "PRESIDIO"

        def __init__(
            self,
            type_mapping: dict[str, str],
            *,
            registry: RecognizerRegistry | None = None,
            nlp_engine: NlpEngine | None = None,
            default_score_threshold: float = 0,
            supported_languages: list[str] | None = None,
        ):
            if supported_languages is None:
                supported_languages = ["en"]
            self.type_mapping = type_mapping

            self.analyzer = AnalyzerEngine(
                registry=registry,
                nlp_engine=nlp_engine,
                default_score_threshold=default_score_threshold,
                supported_languages=supported_languages,
            )

        def extract(self, text: str) -> list[Entity]:
            return [
                self._build_entity(result)
                for result in self.analyzer.analyze(text, language="en")  # this needs to be fixed
            ]

        def _build_entity(self, result: RecognizerResult) -> Entity:
            return Entity(
                start=result.start,
                end=result.end,
                entity_type=self._convert_type(result.entity_type),
                source=frozenset([PresidioEntityExtractor.NAME]),
                confidence=result.score,
            )

except ModuleNotFoundError:
    logger.warning("Unable to load Presidio classes")
