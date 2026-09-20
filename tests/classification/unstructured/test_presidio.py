"""Tests for PresidioEntityExtractor.

Since presidio_analyzer is an optional dependency, the module is patched at
import time so these tests run regardless of whether the library is installed.
"""

import sys
from types import ModuleType
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Build a minimal presidio_analyzer stub so the conditional import in
# presidio.py resolves to our mock classes, not ModuleNotFoundError.
# ---------------------------------------------------------------------------

_presidio_stub = ModuleType("presidio_analyzer")
_nlp_engine_stub = ModuleType("presidio_analyzer.nlp_engine")


class _RecognizerResult:
    """Minimal stand-in for presidio_analyzer.RecognizerResult."""

    def __init__(self, entity_type: str, start: int, end: int, score: float):
        self.entity_type = entity_type
        self.start = start
        self.end = end
        self.score = score


class _RecognizerRegistry:
    pass


class _NlpEngine:
    pass


class _AnalyzerEngine:
    """Minimal stand-in for presidio_analyzer.AnalyzerEngine."""

    def __init__(self, **kwargs):
        self._kwargs = kwargs

    def analyze(self, text: str, language: str) -> list[_RecognizerResult]:
        return []


setattr(_presidio_stub, "AnalyzerEngine", _AnalyzerEngine)
setattr(_presidio_stub, "RecognizerRegistry", _RecognizerRegistry)
setattr(_presidio_stub, "RecognizerResult", _RecognizerResult)
setattr(_nlp_engine_stub, "NlpEngine", _NlpEngine)

# Register the stubs before importing the module under test.
sys.modules.setdefault("presidio_analyzer", _presidio_stub)
sys.modules.setdefault("presidio_analyzer.nlp_engine", _nlp_engine_stub)

# Now it is safe to import – the try/except in presidio.py will succeed.
from risk_assessment.classification.unstructured import Entity  # noqa: E402
from risk_assessment.classification.unstructured.presidio import PresidioEntityExtractor  # noqa: E402

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

TYPE_MAPPING: dict[str, str] = {
    "PERSON": "Person",
    "EMAIL_ADDRESS": "Email",
    "PHONE_NUMBER": "Phone",
    "LOCATION": "Location",
}


def _make_extractor(**kwargs) -> PresidioEntityExtractor:
    return PresidioEntityExtractor(type_mapping=TYPE_MAPPING, **kwargs)


def _stub_result(entity_type: str, start: int, end: int, score: float = 0.85) -> _RecognizerResult:
    return _RecognizerResult(entity_type=entity_type, start=start, end=end, score=score)


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------


def test_default_construction():
    extractor = _make_extractor()
    assert extractor.type_mapping == TYPE_MAPPING
    assert extractor.analyzer is not None


def test_name_constant():
    assert PresidioEntityExtractor.NAME == "PRESIDIO"


def test_custom_score_threshold_is_forwarded():
    """AnalyzerEngine must receive the custom threshold."""
    with patch("risk_assessment.classification.unstructured.presidio.AnalyzerEngine") as mock_engine_cls:
        mock_engine_cls.return_value = MagicMock()
        _make_extractor(default_score_threshold=0.5)
        call_kwargs = mock_engine_cls.call_args.kwargs
        assert call_kwargs["default_score_threshold"] == 0.5


def test_default_language_is_english():
    """supported_languages defaults to ['en'] when not supplied."""
    with patch("risk_assessment.classification.unstructured.presidio.AnalyzerEngine") as mock_engine_cls:
        mock_engine_cls.return_value = MagicMock()
        _make_extractor()
        call_kwargs = mock_engine_cls.call_args.kwargs
        assert call_kwargs["supported_languages"] == ["en"]


def test_custom_supported_languages():
    with patch("risk_assessment.classification.unstructured.presidio.AnalyzerEngine") as mock_engine_cls:
        mock_engine_cls.return_value = MagicMock()
        _make_extractor(supported_languages=["en", "de"])
        call_kwargs = mock_engine_cls.call_args.kwargs
        assert call_kwargs["supported_languages"] == ["en", "de"]


def test_registry_forwarded_when_provided():
    registry = _RecognizerRegistry()
    with patch("risk_assessment.classification.unstructured.presidio.AnalyzerEngine") as mock_engine_cls:
        mock_engine_cls.return_value = MagicMock()
        _make_extractor(registry=registry)
        call_kwargs = mock_engine_cls.call_args.kwargs
        assert call_kwargs["registry"] is registry


def test_registry_omitted_when_none():
    with patch("risk_assessment.classification.unstructured.presidio.AnalyzerEngine") as mock_engine_cls:
        mock_engine_cls.return_value = MagicMock()
        _make_extractor(registry=None)
        call_kwargs = mock_engine_cls.call_args.kwargs
        assert "registry" not in call_kwargs


def test_nlp_engine_forwarded_when_provided():
    engine = _NlpEngine()
    with patch("risk_assessment.classification.unstructured.presidio.AnalyzerEngine") as mock_engine_cls:
        mock_engine_cls.return_value = MagicMock()
        _make_extractor(nlp_engine=engine)
        call_kwargs = mock_engine_cls.call_args.kwargs
        assert call_kwargs["nlp_engine"] is engine


def test_nlp_engine_omitted_when_none():
    with patch("risk_assessment.classification.unstructured.presidio.AnalyzerEngine") as mock_engine_cls:
        mock_engine_cls.return_value = MagicMock()
        _make_extractor(nlp_engine=None)
        call_kwargs = mock_engine_cls.call_args.kwargs
        assert "nlp_engine" not in call_kwargs


# ---------------------------------------------------------------------------
# extract()
# ---------------------------------------------------------------------------


def test_extract_returns_empty_list_for_no_results():
    extractor = _make_extractor()
    extractor.analyzer.analyze = MagicMock(return_value=[])
    assert extractor.extract("no entities here") == []


def test_extract_returns_entity_list():
    extractor = _make_extractor()
    extractor.analyzer.analyze = MagicMock(
        return_value=[
            _stub_result("PERSON", 11, 19, score=0.9),
            _stub_result("EMAIL_ADDRESS", 23, 42, score=0.95),
        ]
    )
    entities = extractor.extract("Hello I'm John Doe at jdoe@example.com")
    assert len(entities) == 2


def test_extract_calls_analyzer_with_english():
    extractor = _make_extractor()
    extractor.analyzer.analyze = MagicMock(return_value=[])
    extractor.extract("some text")
    extractor.analyzer.analyze.assert_called_once_with("some text", language="en")


def test_extract_entity_spans_are_correct():
    extractor = _make_extractor()
    extractor.analyzer.analyze = MagicMock(return_value=[_stub_result("PERSON", 5, 13)])
    entities = extractor.extract("Hi, John Doe")
    assert entities[0].start == 5
    assert entities[0].end == 13


def test_extract_entity_confidence_is_forwarded():
    extractor = _make_extractor()
    extractor.analyzer.analyze = MagicMock(return_value=[_stub_result("PERSON", 0, 8, score=0.77)])
    entities = extractor.extract("John Doe")
    assert entities[0].confidence == pytest.approx(0.77)


def test_extract_source_is_presidio():
    extractor = _make_extractor()
    extractor.analyzer.analyze = MagicMock(return_value=[_stub_result("PERSON", 0, 8)])
    entities = extractor.extract("John Doe")
    assert entities[0].source == frozenset(["PRESIDIO"])


# ---------------------------------------------------------------------------
# Type mapping
# ---------------------------------------------------------------------------


def test_known_type_is_mapped():
    extractor = _make_extractor()
    extractor.analyzer.analyze = MagicMock(return_value=[_stub_result("PERSON", 0, 8)])
    entities = extractor.extract("John Doe")
    assert entities[0].entity_type == "Person"


def test_unknown_type_passes_through_unchanged():
    extractor = _make_extractor()
    extractor.analyzer.analyze = MagicMock(return_value=[_stub_result("CRYPTO", 0, 5)])
    entities = extractor.extract("1BvBM")
    assert entities[0].entity_type == "CRYPTO"


def test_all_mapped_types_are_converted():
    presidio_to_standard = {
        "PERSON": "Person",
        "EMAIL_ADDRESS": "Email",
        "PHONE_NUMBER": "Phone",
        "LOCATION": "Location",
    }
    extractor = _make_extractor()
    for presidio_type, expected_type in presidio_to_standard.items():
        extractor.analyzer.analyze = MagicMock(return_value=[_stub_result(presidio_type, 0, 5)])
        entities = extractor.extract("dummy")
        assert entities[0].entity_type == expected_type, f"{presidio_type} should map to {expected_type}"


def test_empty_type_mapping_returns_raw_types():
    extractor = PresidioEntityExtractor(type_mapping={})
    extractor.analyzer.analyze = MagicMock(return_value=[_stub_result("PERSON", 0, 8)])
    entities = extractor.extract("John Doe")
    assert entities[0].entity_type == "PERSON"


# ---------------------------------------------------------------------------
# _build_entity()
# ---------------------------------------------------------------------------


def test_build_entity_returns_entity_dataclass():
    extractor = _make_extractor()
    result = _stub_result("PERSON", 3, 11, score=0.88)
    entity = extractor._build_entity(result)
    assert isinstance(entity, Entity)
    assert entity.start == 3
    assert entity.end == 11
    assert entity.entity_type == "Person"
    assert entity.confidence == pytest.approx(0.88)
    assert entity.source == frozenset(["PRESIDIO"])


def test_build_entity_score_zero():
    extractor = _make_extractor()
    result = _stub_result("PERSON", 0, 4, score=0.0)
    entity = extractor._build_entity(result)
    assert entity.confidence == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# Multiple entities in one extraction
# ---------------------------------------------------------------------------


def test_extract_multiple_entity_types():
    extractor = _make_extractor()
    extractor.analyzer.analyze = MagicMock(
        return_value=[
            _stub_result("PERSON", 0, 8, score=0.9),
            _stub_result("EMAIL_ADDRESS", 12, 30, score=0.95),
            _stub_result("PHONE_NUMBER", 34, 46, score=0.8),
        ]
    )
    entities = extractor.extract("John Doe – jdoe@example.com – 555-123-4567")
    types = {e.entity_type for e in entities}
    assert types == {"Person", "Email", "Phone"}


def test_extract_preserves_order():
    extractor = _make_extractor()
    results = [
        _stub_result("PERSON", 0, 4),
        _stub_result("LOCATION", 10, 16),
        _stub_result("EMAIL_ADDRESS", 20, 38),
    ]
    extractor.analyzer.analyze = MagicMock(return_value=results)
    entities = extractor.extract("Ann lives in Paris. ann@example.com")
    assert [e.start for e in entities] == [0, 10, 20]
