from sys import stderr

import spacy
from spacy.language import Language

from risk_assessment.classification.unstructured import Entity, EntityExtractor
from risk_assessment.classification.unstructured.pos_utility import (
    part_of_speech_mapper,
)


class SpacyPOSEntityExtractor(EntityExtractor):
    def __init__(self, model_name: str = "en_core_web_sm", type_mapping: dict[str, str] | None = None):
        if type_mapping is None:
            type_mapping = {}
        super().__init__(type_mapping)
        spacy.prefer_gpu()
        try:
            self.model = spacy.load(model_name)
        except OSError:
            print(
                "Downloading language model for the spaCy POS tagger\n(don't worry, this will only happen once)",
                file=stderr,
            )
            from spacy.cli import download

            download(model_name)
            self.model = spacy.load(model_name)

    def get_nlp_model(self) -> Language:
        return self.model

    def extract(self, text: str) -> list[Entity]:
        document = self.model(text)

        return [
            Entity(
                entity.idx,
                entity.idx + len(entity.text),
                "",
                frozenset(["SPACY_POS"]),
                frozenset([part_of_speech_mapper(entity.pos_)]),
            )
            for entity in document
        ]
