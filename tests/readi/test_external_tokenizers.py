"""Tests for external_tokenizers: SpacyTokenizer and STANZASentenceTokenizer."""

import pytest

from risk_assessment.readi.external_tokenizers import SpacyTokenizer

# ---------------------------------------------------------------------------
# SpacyTokenizer
# ---------------------------------------------------------------------------

_TEXT = "Hello world. This is a test."


def test_spacy_tokenizer_returns_list_of_spans():
    spans = SpacyTokenizer().span_tokenize(_TEXT)
    assert isinstance(spans, list)
    assert all(isinstance(s, tuple) and len(s) == 2 for s in spans)


def test_spacy_tokenizer_spans_cover_nonempty_tokens():
    spans = SpacyTokenizer().span_tokenize(_TEXT)
    assert all(_TEXT[s:e] for s, e in spans)


def test_spacy_tokenizer_offsets_are_valid():
    spans = SpacyTokenizer().span_tokenize(_TEXT)
    for start, end in spans:
        assert 0 <= start < end <= len(_TEXT)


def test_spacy_tokenizer_empty_string():
    assert SpacyTokenizer().span_tokenize("") == []


def test_spacy_tokenizer_custom_language():
    from spacy.lang.de import German

    spans = SpacyTokenizer(lang=German).span_tokenize("Hallo Welt.")
    assert len(spans) > 0


# ---------------------------------------------------------------------------
# STANZASentenceTokenizer — skipped when stanza is not installed
# ---------------------------------------------------------------------------

pytest.importorskip("stanza", reason="stanza extra not installed")

from risk_assessment.readi.external_tokenizers import STANZASentenceTokenizer  # noqa: E402

_MULTI_SENT = "Ireland is an island. It is in the North Atlantic Ocean. The climate is mild."


def test_stanza_sent_tokenize_splits_into_sentences():
    sentences = STANZASentenceTokenizer().sent_tokenize(_MULTI_SENT)
    assert isinstance(sentences, list)
    assert len(sentences) == 3


def test_stanza_sent_tokenize_text_matches_original():
    sentences = STANZASentenceTokenizer().sent_tokenize(_MULTI_SENT)
    for sent in sentences:
        assert sent in _MULTI_SENT


def test_stanza_span_tokenize_returns_spans():
    spans = STANZASentenceTokenizer().span_tokenize(_MULTI_SENT)
    assert isinstance(spans, list)
    assert len(spans) == 3
    assert all(isinstance(s, tuple) and len(s) == 2 for s in spans)


def test_stanza_span_tokenize_offsets_are_valid():
    spans = STANZASentenceTokenizer().span_tokenize(_MULTI_SENT)
    for start, end in spans:
        assert 0 <= start < end <= len(_MULTI_SENT)


def test_stanza_span_tokenize_consistent_with_sent_tokenize():
    tok = STANZASentenceTokenizer()
    spans = tok.span_tokenize(_MULTI_SENT)
    sents = tok.sent_tokenize(_MULTI_SENT)
    assert len(spans) == len(sents)
    for (start, end), sent in zip(spans, sents):
        assert _MULTI_SENT[start:end] == sent
