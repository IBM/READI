import logging

logger = logging.getLogger(__name__)

try:
    from presidio_analyzer import AnalyzerEngine, EntityRecognizer, RecognizerResult
    from presidio_analyzer.nlp_engine import NlpArtifacts
    from regex.regex import (
        DOTALL,
        IGNORECASE,
        MULTILINE,
    )

    from risk_assessment.classification.unstructured import Entity, EntityExtractor
    from risk_assessment.classification.unstructured.aggregator import Aggregator

    class PresidioWrapper(AnalyzerEngine):
        def __init__(self, aggregator: Aggregator, extractors: list[EntityExtractor]) -> None:
            self.aggregator = aggregator
            self.extractors = extractors

        def analyze(
            self,
            text: str,
            language: str,
            entities: list[str] | None = None,
            correlation_id: str | None = None,
            score_threshold: float | None = None,
            return_decision_process: bool | None = False,
            ad_hoc_recognizers: list[EntityRecognizer] | None = None,
            context: list[str] | None = None,
            allow_list: list[str] | None = None,
            allow_list_match: str | None = "exact",
            regex_flags: int | None = DOTALL | MULTILINE | IGNORECASE,
            nlp_artifacts: NlpArtifacts | None = None,
        ) -> list[RecognizerResult]:
            return [
                self._to_recognizer_result(entity)
                for entity in self.aggregator.aggregate(
                    [extractor.extract(text) for extractor in self.extractors], text
                )
            ]

        def _to_recognizer_result(self, entity: Entity) -> RecognizerResult:
            return RecognizerResult(
                entity_type=entity.entity_type,
                start=entity.start,
                end=entity.end,
                score=entity.confidence if entity.confidence is not None else 0,
            )

except ModuleNotFoundError:
    logger.warning("Not able to access Presidio classes")
