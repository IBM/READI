from nltk.tag.api import TaggerI
from nltk.tokenize.api import TokenizerI

from risk_assessment.classification.unstructured import Entity, EntityExtractor
from risk_assessment.classification.unstructured.pos_utility import (
    part_of_speech_mapper,
)


class NLTKPoSTagger(EntityExtractor):
    def __init__(self, tokenizer: TokenizerI, tagger: TaggerI) -> None:
        self.tokenizer = tokenizer
        self.tagger = tagger

    def extract(self, text: str) -> list[Entity]:
        spans: list[tuple[int, int]] = list(self.tokenizer.span_tokenize(text))
        tokens: list[str] = self.tokenizer.tokenize(text)

        if len(spans) != len(tokens):
            raise ValueError()

        tags = self.tagger.tag(tokens)

        return [
            Entity(
                start,
                end,
                "",
                frozenset(["NLTKPOS"]),
                frozenset([part_of_speech_mapper(tag)]),
            )
            for (start, end), (_, tag) in zip(spans, tags, strict=False)
        ]
