"""Tests for READIAnalyzer."""

import pytest

from risk_assessment.classification.identifiers import Email, Phone
from risk_assessment.classification.unstructured import Entity, EntityExtractor
from risk_assessment.classification.unstructured.aggregator import AggregatorConfiguration
from risk_assessment.classification.unstructured.drl import DRLEntityExtractor
from risk_assessment.readi.analyzer import READIAnalyzer

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_custom_analyzer(*identifiers):
    """Return a CUSTOM analyzer wired to DRL-only detection for the given identifiers."""
    extractors: list[EntityExtractor] = [DRLEntityExtractor(identifiers=list(identifiers))]
    config = AggregatorConfiguration(
        merge_entities=True,
        to_report_only={i.__class__.__name__ for i in identifiers},
    )
    return READIAnalyzer(
        detection_type=READIAnalyzer.DetectionType.CUSTOM,
        entity_extractors=extractors,
        aggregator_configuration=config,
    )


def _entity_types(entities: list[Entity]) -> set[str]:
    return {e.entity_type for e in entities}


def _spans(text: str, entities: list[Entity]) -> list[str]:
    return [text[e.start : e.end] for e in entities]


# ---------------------------------------------------------------------------
# DetectionType enum
# ---------------------------------------------------------------------------


def test_detection_type_members():
    dt = READIAnalyzer.DetectionType
    assert dt.PHI in dt
    assert dt.PII in dt
    assert dt.PII_NO_MODEL in dt
    assert dt.CUSTOM in dt


# ---------------------------------------------------------------------------
# Initialization – built-in detection types
# ---------------------------------------------------------------------------


def test_init_phi_sets_detection_type():
    analyzer = READIAnalyzer(detection_type=READIAnalyzer.DetectionType.PHI)
    assert analyzer.detection_type is READIAnalyzer.DetectionType.PHI
    assert analyzer.aggregator is not None
    assert len(analyzer.entity_extractors) > 0


def test_init_pii_no_model_sets_detection_type():
    analyzer = READIAnalyzer(detection_type=READIAnalyzer.DetectionType.PII_NO_MODEL)
    assert analyzer.detection_type is READIAnalyzer.DetectionType.PII_NO_MODEL
    assert analyzer.aggregator is not None
    assert len(analyzer.entity_extractors) > 0


def test_init_default_is_phi():
    analyzer = READIAnalyzer()
    assert analyzer.detection_type is READIAnalyzer.DetectionType.PHI


# ---------------------------------------------------------------------------
# Initialization – CUSTOM detection type validation
# ---------------------------------------------------------------------------


def test_init_custom_raises_without_extractors():
    config = AggregatorConfiguration()
    with pytest.raises(ValueError, match="entity_extractors"):
        READIAnalyzer(
            detection_type=READIAnalyzer.DetectionType.CUSTOM,
            entity_extractors=None,
            aggregator_configuration=config,
        )


def test_init_custom_raises_with_empty_extractors():
    config = AggregatorConfiguration()
    with pytest.raises(ValueError, match="entity_extractors"):
        READIAnalyzer(
            detection_type=READIAnalyzer.DetectionType.CUSTOM,
            entity_extractors=[],
            aggregator_configuration=config,
        )


def test_init_custom_raises_without_aggregator_configuration():
    extractors: list[EntityExtractor] = [DRLEntityExtractor(identifiers=[Email()])]
    with pytest.raises(ValueError, match="aggregator_configuration"):
        READIAnalyzer(
            detection_type=READIAnalyzer.DetectionType.CUSTOM,
            entity_extractors=extractors,
            aggregator_configuration=None,
        )


def test_init_custom_succeeds_with_valid_args():
    analyzer = _make_custom_analyzer(Email())
    assert analyzer.detection_type is READIAnalyzer.DetectionType.CUSTOM
    assert len(analyzer.entity_extractors) == 1


# ---------------------------------------------------------------------------
# detect() – empty / trivial input
# ---------------------------------------------------------------------------


def test_detect_empty_string_returns_empty():
    analyzer = _make_custom_analyzer(Email())
    assert analyzer.detect("") == []


def test_detect_no_pii_text_returns_empty():
    analyzer = _make_custom_analyzer(Email())
    result = analyzer.detect("The weather today is sunny and warm.")
    assert result == []


# ---------------------------------------------------------------------------
# detect() – email detection
# ---------------------------------------------------------------------------


def test_detect_single_email():
    analyzer = _make_custom_analyzer(Email())
    text = "Reach me at alice@example.com for details."
    entities = analyzer.detect(text)

    assert len(entities) >= 1
    spans = _spans(text, entities)
    assert any("alice@example.com" in s for s in spans)


def test_detect_multiple_emails():
    analyzer = _make_custom_analyzer(Email())
    text = "Send to alice@example.com and bob@example.org."
    entities = analyzer.detect(text)

    spans = _spans(text, entities)
    assert any("alice@example.com" in s for s in spans)
    assert any("bob@example.org" in s for s in spans)


# ---------------------------------------------------------------------------
# detect() – phone detection
# ---------------------------------------------------------------------------


def test_detect_phone_number():
    analyzer = _make_custom_analyzer(Phone())
    text = "Call us at +1 800 555 0100."
    entities = analyzer.detect(text)

    assert len(entities) >= 1


# ---------------------------------------------------------------------------
# detect() – PII_NO_MODEL with real text
# ---------------------------------------------------------------------------


def test_detect_pii_no_model_finds_email():
    analyzer = READIAnalyzer(detection_type=READIAnalyzer.DetectionType.PII_NO_MODEL)
    text = "Please contact support@company.com for assistance."
    entities = analyzer.detect(text)

    assert any("Email" in e.entity_type for e in entities)
    spans = _spans(text, entities)
    assert any("support@company.com" in s for s in spans)


def test_detect_pii_no_model_returns_list_of_entities():
    analyzer = READIAnalyzer(detection_type=READIAnalyzer.DetectionType.PII_NO_MODEL)
    result = analyzer.detect("No PII here.")
    assert isinstance(result, list)


# ---------------------------------------------------------------------------
# detect() – entity structure
# ---------------------------------------------------------------------------


def test_detected_entity_positions_are_valid():
    analyzer = _make_custom_analyzer(Email())
    text = "Email: test@domain.com."
    entities = analyzer.detect(text)

    for entity in entities:
        assert 0 <= entity.start < entity.end <= len(text)


def test_detected_entity_has_source():
    analyzer = _make_custom_analyzer(Email())
    text = "Email: test@domain.com."
    entities = analyzer.detect(text)

    for entity in entities:
        assert isinstance(entity.source, frozenset)
        assert len(entity.source) > 0
