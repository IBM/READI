from collections import Counter
from collections.abc import Iterable
from itertools import chain
from typing import Any

import nltk
from nltk.tokenize import TreebankWordTokenizer
from nltk.tokenize.api import TokenizerI

from risk_assessment.classification.identifiers import (
    Identifier,
    RegexIdentifierWithSpan,
)
from risk_assessment.classification.unstructured import (
    Entity,
    MultiSourceEntityExtractor,
)
from risk_assessment.classification.unstructured.nltk import NLTKPoSTagger
from risk_assessment.readi.text_tokenizer import BaseTokenizer

nltk.download("averaged_perceptron_tagger_eng", quiet=True)

from nltk.tag import PerceptronTagger  # noqa: E402


def _generate_shinglets(
    spans: list[tuple[int, int]], max_length: int = 5, min_length: int = 1
) -> Iterable[tuple[int, int]]:
    if max_length < 1:
        raise ValueError("max_length needs to be greater than 1")
    if min_length <= 0:
        raise ValueError("min_length needs to be a positive number")
    if max_length < min_length:
        raise ValueError(f"max_lenght ({max_length}) needs to be greater than min_length ({min_length})")

    for i, span in enumerate(spans):
        last_span_index = min(len(spans), i + max_length)

        for j in range(i + min_length - 1, last_span_index):
            next_span = spans[j]

            yield (span[0], next_span[1])


def _delete_repetition(entities: list[Entity]) -> list[Entity]:
    return list(set(entities))


class DRLEntityExtractor(MultiSourceEntityExtractor):
    def __init__(
        self,
        type_mapping: dict[str, str] | None = None,
        identifiers: list[Identifier] | None = None,
        tokenizer: TokenizerI | BaseTokenizer = TreebankWordTokenizer(),
        pos_detector: NLTKPoSTagger = NLTKPoSTagger(TreebankWordTokenizer(), PerceptronTagger()),
        max_shinglet_length: int = 5,
        min_shinglet_length: int = 1,
        name: str = "DRL",
    ):
        if identifiers is None:
            identifiers = []
        if type_mapping is None:
            type_mapping = {}
        super().__init__(type_mapping)
        self.tokenizer = tokenizer
        self.identifiers = identifiers
        self.max_shinglet_length = max_shinglet_length
        self.min_shinglet_length = min_shinglet_length
        self.name = name
        self.pos_detector = pos_detector

    def _extract(self, text: str) -> list[Entity]:
        spans = list(self.tokenizer.span_tokenize(text))

        identified_entities: list[Entity] = []

        if MultiSourceEntityExtractor.pool is not None:
            MultiSourceEntityExtractor.pool.starmap(
                self._process_shinglet,
                (
                    (begin, end, text[begin:end], identified_entities)
                    for begin, end in _generate_shinglets(
                        spans, max_length=self.max_shinglet_length, min_length=self.min_shinglet_length
                    )
                ),
            )
        else:
            for begin, end in _generate_shinglets(
                spans, max_length=self.max_shinglet_length, min_length=self.min_shinglet_length
            ):
                self._process_shinglet(begin, end, text[begin:end], identified_entities)

        return _delete_repetition(identified_entities)

    def _process_shinglet(self, begin: int, end: int, snippet: str, identified_entities: list[Entity]) -> None:
        for identifier in self.identifiers:
            if isinstance(identifier, RegexIdentifierWithSpan):
                response = identifier.is_of_this_type_with_span(snippet)
                if response[0] and response[1] is not None:
                    identified_entities.append(
                        Entity(
                            begin + response[1][0],
                            begin + response[1][1],
                            self._convert_type(str(identifier)),
                            frozenset([self.name]),
                        )
                    )
            else:
                if identifier.is_of_this_type(snippet):
                    identified_entities.append(
                        Entity(begin, end, self._convert_type(str(identifier)), frozenset([self.name]))
                    )


class ImprovedDRLEntityExtractor(DRLEntityExtractor):
    def __init__(
        self,
        type_mapping: dict[str, str] | None = None,
        identifiers: list[Identifier] | None = None,
        tokenizer_list: list[Any] | None = None,
        pos_detector: NLTKPoSTagger = NLTKPoSTagger(TreebankWordTokenizer(), PerceptronTagger()),
        max_shinglet_length: int = 5,
        min_shinglet_length: int = 1,
        name: str = "DRL",
    ) -> None:
        if tokenizer_list is None:
            tokenizer_list = []
        if identifiers is None:
            identifiers = []
        if type_mapping is None:
            type_mapping = {}
        super().__init__(
            type_mapping=type_mapping,
            identifiers=identifiers,
            pos_detector=pos_detector,
            max_shinglet_length=max_shinglet_length,
            min_shinglet_length=min_shinglet_length,
            name=name,
        )
        self.tokenizer_list: list[Any] = tokenizer_list

    def _extract(self, text: str) -> list[Entity]:
        spans = self.tokenize(text)
        identified_entities: list[Entity] = []

        if MultiSourceEntityExtractor.pool is not None:
            MultiSourceEntityExtractor.pool.starmap(
                self._process_shinglet,
                (
                    (begin, end, text[begin:end], identified_entities)
                    for begin, end in _generate_shinglets(
                        spans, max_length=self.max_shinglet_length, min_length=self.min_shinglet_length
                    )
                ),
            )
        else:
            for begin, end in _generate_shinglets(
                spans, max_length=self.max_shinglet_length, min_length=self.min_shinglet_length
            ):
                self._process_shinglet(begin, end, text[begin:end], identified_entities)

        return _delete_repetition(identified_entities)

    def find_split_point(self, spans: list[tuple[int, int]]) -> list[int]:
        split_points = set(chain(*spans))
        return sorted(split_points)

    def merge_spans(self, split_points: list[int]) -> list[tuple[int, int]]:
        if len(split_points) == 0:
            return []

        merged_spans: list[tuple[int, int]] = []
        start = split_points[0]

        for split_point_iterator in range(1, len(split_points)):
            end = split_points[split_point_iterator]
            merged_spans.append((start, end))
            start = end
        return merged_spans

    def tokenize(self, text: str) -> list[tuple[int, int]]:
        spans_aggregated: list[tuple[int, int]] = []
        for tokenizer in self.tokenizer_list:
            spans_aggregated.extend(list(tokenizer.span_tokenize(text)))

        # remove repetitions
        repetition_counter = Counter([(span[0], span[1]) for span in spans_aggregated])
        unique_spans: list[tuple[int, int]] = []
        for span in spans_aggregated:
            marker = (span[0], span[1])

            value = repetition_counter[marker]

            if value > 1:
                repetition_counter[marker] = -1
            elif value < 0:
                continue

            unique_spans.append(span)

        split_points = self.find_split_point(unique_spans)
        merged_spans = self.merge_spans(split_points)
        filtered_spans: list[tuple[int, int]] = []
        for span in merged_spans:
            if text[span[0] : span[1]] != " ":
                filtered_spans.append(span)
        return filtered_spans
