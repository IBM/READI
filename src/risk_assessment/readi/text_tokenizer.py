"""Token-level and sentence-level text tokenizers for the READI pipeline.

This module provides the tokenization layer used by entity extractors that
require text to be split into word/token spans with their positions preserved
relative to the original string.

Classes:

- :class:`BaseTokenizer` — abstract interface for span tokenizers.
- :class:`TextTokenizer` — composes a :class:`~risk_assessment.readi.sentence_tokenizer.SentenceTokenizer`
  with a span tokenizer to produce token spans aligned to the full document.
- :class:`LMTokenizer` — HuggingFace ``AutoTokenizer``-backed span tokenizer
  for language-model based extractors.
- :class:`JapaneseTokenizer` — MeCab-backed morphological tokenizer for
  Japanese text.
"""

import warnings
from abc import ABC, abstractmethod

import MeCab
from nltk.tokenize import WordPunctTokenizer
from transformers import AutoTokenizer

from risk_assessment.readi.sentence_tokenizer import SentenceTokenizer

warnings.simplefilter(action="ignore", category=FutureWarning)


class BaseTokenizer(ABC):
    """Abstract base class for span tokenizers.

    A span tokenizer maps raw text to a list of ``(start, end)`` character
    positions, one per token.
    """

    @abstractmethod
    def span_tokenize(self, text: str) -> list[tuple[int, int]]:
        """Tokenize *text* and return character-level spans.

        Args:
            text: Input text.

        Returns:
            List of ``(start, end)`` tuples (end exclusive) for each token.
        """
        raise NotImplementedError()


class TextTokenizer:
    """Two-level tokenizer: first splits text into sentences, then into tokens.

    Combines a :class:`~risk_assessment.readi.sentence_tokenizer.SentenceTokenizer`
    with a span tokenizer so that all token spans are expressed as offsets
    within the full document rather than within individual sentences.

    Attributes:
        sentence_tokenizer: Sentence-level splitter.
        span_tokenizer: Token-level splitter applied to each sentence.
    """

    def __init__(
        self, sentence_tokenizer: SentenceTokenizer, span_tokenizer: WordPunctTokenizer | BaseTokenizer
    ) -> None:
        self.sentence_tokenizer: SentenceTokenizer = sentence_tokenizer
        self.span_tokenizer = span_tokenizer

    def __split_text_into_sentences(
        self,
        text: str,
    ) -> list[tuple[int, int]]:
        return self.sentence_tokenizer.span_tokenize(text)

    def _split_sentence(
        self,
        spans: list[tuple[int, int]],
        max_sentence_tokens_length: int,
    ) -> list[tuple[int, int]]:
        sentence_pos_update: list[tuple[int, int]] = []
        for i in range(0, len(spans), max_sentence_tokens_length):
            span_chunk = spans[i : i + max_sentence_tokens_length]
            sentence_pos = (span_chunk[0][0], span_chunk[-1][1])
            sentence_pos_update.append(sentence_pos)
        return sentence_pos_update

    def tokenize_sentence_with_pos_in_text(
        self,
        sentence: str,
        sentence_position: int,
    ) -> tuple[list[str], list[tuple[int, int]]]:
        # sentence_position - int - starting position of sentence within the text

        span_tokens = self.span_tokenizer.span_tokenize(sentence)
        spans_sentence_level = [[span[0], span[1]] for span in span_tokens]
        sentence_by_token = [sentence[span[0] : span[1]] for span in spans_sentence_level]
        spans = [(span[0] + sentence_position, span[1] + sentence_position) for span in spans_sentence_level]
        return sentence_by_token, spans

    def tokenize_sentences(
        self,
        sentences: list[str],
        sentence_positions: list[tuple[int, int]],
    ) -> tuple[list[list[str]], list[list[tuple[int, int]]]]:
        """Tokenize a list of sentences, aligning spans to the full document.

        Args:
            sentences: Pre-split sentence strings.
            sentence_positions: ``(start, end)`` positions of each sentence
                within the original document.

        Returns:
            A tuple ``(tokens_per_sentence, spans_per_sentence)`` where each
            inner list corresponds to one sentence.
        """
        sentences_by_token: list[list[str]] = []
        sentences_by_spans: list[list[tuple[int, int]]] = []
        for i, sentence in enumerate(sentences):
            sentence_by_token, spans = self.tokenize_sentence_with_pos_in_text(sentence, sentence_positions[i][0])
            sentences_by_token.append(sentence_by_token)
            sentences_by_spans.append(spans)
        return sentences_by_token, sentences_by_spans

    def tokenize_text(
        self, text: str, max_sentence_tokens_length: int = 800
    ) -> tuple[list[str], list[tuple[int, int]]]:
        sentence_positions: list[tuple[int, int]] = self.__split_text_into_sentences(text)
        sentence_list: list[str] = []
        for sentence_pos in sentence_positions:
            sentence: str = text[sentence_pos[0] : sentence_pos[1]]
            sentence_list.append(sentence)
        return sentence_list, sentence_positions


class LMTokenizer(BaseTokenizer):
    """HuggingFace language-model tokenizer that returns character-level spans.

    Wraps an ``AutoTokenizer`` and converts its token-to-character mappings
    into ``(start, end)`` spans compatible with the READI pipeline.

    Attributes:
        device: Target device string (e.g. ``"cpu"`` or ``"cuda"``).
        tokenizer: Loaded HuggingFace tokenizer instance.
    """

    def __init__(self, model_name: str = "FacebookAI/roberta-base", device: str = "cpu") -> None:
        """Load the tokenizer from a HuggingFace model name or local path.

        Args:
            model_name: Model identifier passed to ``AutoTokenizer.from_pretrained``.
                Defaults to ``"FacebookAI/roberta-base"``.
            device: Device string for downstream model inference. Defaults to ``"cpu"``.
        """
        self.device = device
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)  # nosec

    def span_tokenize(self, text: str) -> list[tuple[int, int]]:
        tokenized_text = self.tokenizer(text)
        num_of_tokens = len(tokenized_text["input_ids"])
        token_spans: list[tuple[int, int]] = []
        for i in range(num_of_tokens):
            charspan = tokenized_text.token_to_chars(i)
            if charspan:
                token_spans.append((charspan.start, charspan.end))
        return token_spans


class JapaneseTokenizer(BaseTokenizer):
    """MeCab-based morphological tokenizer for Japanese text.

    Uses MeCab to split Japanese text into morpheme spans aligned to the
    original whitespace-separated substrings.

    Attributes:
        preprocessor: MeCab tagger instance used for morphological analysis.
    """

    def __init__(self) -> None:
        """Initialise MeCab tagger."""
        self.preprocessor = MeCab.Tagger()

    def span_tokenize(self, text: str) -> list[tuple[int, int]]:
        text_by_spaces = text.split()
        shift = 0
        subset_mapping: list[int] = [shift]

        for subset in text_by_spaces[:-1]:
            subset_mapping.append(shift + len(subset) + 1)
            shift += len(subset) + 1

        spans: list[tuple[int, int]] = []
        for subset, subset_shift in zip(text_by_spaces, subset_mapping, strict=False):
            preprocessed_text = self.preprocessor.parse(subset)
            rows = preprocessed_text.split("\n")
            morphemes = [row.split("\t")[0] for row in rows][:-2]
            subset_spans = []
            shift = subset_shift
            for morpheme in morphemes:
                subset_spans.append((shift, len(morpheme) + shift))
                shift += len(morpheme)
            spans.extend(subset_spans)

        return spans
