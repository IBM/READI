from typing import cast

import stanza
from spacy.lang.en import English
from spacy.language import Language
from stanza.models.common.doc import Document

from risk_assessment.readi.sentence_tokenizer import SentenceTokenizer
from risk_assessment.readi.text_tokenizer import BaseTokenizer


class SpacyTokenizer(BaseTokenizer):
    def __init__(self, lang: type[Language] = English) -> None:
        self.lang = lang
        self.tokenizer = self.lang().tokenizer

    def span_tokenize(self, text: str) -> list[tuple[int, int]]:
        tokens = self.tokenizer(text)
        spans: list[tuple[int, int]] = [(token.idx, token.idx + len(token)) for token in tokens]
        return spans


class STANZASentenceTokenizer(SentenceTokenizer):
    def __init__(self, language: str = "en") -> None:
        super().__init__()
        self.tokenizer = stanza.Pipeline(lang=language, processors="tokenize", verbose=False, logging_level="ERROR")

    def span_tokenize(self, text: str) -> list[tuple[int, int]]:
        tokenized_sentences = cast(Document, self.tokenizer(text))
        sentence_positions: list[tuple[int, int]] = []
        for item in tokenized_sentences.sentences:
            start = item.tokens[0].start_char
            end = item.tokens[-1].end_char
            sentence_positions.append((start, end))
        return sentence_positions

    def sent_tokenize(self, text: str) -> list[str]:
        tokenized_sentences = cast(Document, self.tokenizer(text))
        return [item.text for item in tokenized_sentences.sentences]
