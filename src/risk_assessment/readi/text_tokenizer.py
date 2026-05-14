import warnings
from abc import ABC, abstractmethod

import MeCab
from nltk.tokenize import WordPunctTokenizer
from transformers import AutoTokenizer

from risk_assessment.readi.sentence_tokenizer import SentenceTokenizer

warnings.simplefilter(action="ignore", category=FutureWarning)


class BaseTokenizer(ABC):
    @abstractmethod
    def span_tokenize(self, text: str) -> list[tuple[int, int]]:
        raise NotImplementedError()


class TextTokenizer:
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

    def tokenize_sentenses(
        self,
        sentences: list[str],
        sentence_positions: list[tuple[int, int]],
    ) -> tuple[list[list[str]], list[list[tuple[int, int]]]]:
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
    def __init__(self, model_name: str = "FacebookAI/roberta-base", device: str = "cpu") -> None:
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
    def __init__(self) -> None:
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
