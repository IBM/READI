from sys import stderr

import spacy

from risk_assessment.classification.unstructured import Entity, EntityExtractor


class SpacyEntityExtractor(EntityExtractor):
    def __init__(
        self,
        model_name: str = "en_core_web_sm",
        type_mapping: dict[str, str] | None = None,
        extractor_name: str = "SPACY",
    ):
        if type_mapping is None:
            type_mapping = {}
        super().__init__(type_mapping)
        spacy.prefer_gpu()
        try:
            self.model = spacy.load(model_name)
        except OSError:
            print(
                "Downloading language model for the spaCy Entity Detector\n(don't worry, this will only happen once)",
                file=stderr,
            )
            from spacy.cli import download

            download(model_name)
            self.model = spacy.load(model_name)

        self.extractor_name = extractor_name

    def extract(self, text: str) -> list[Entity]:
        document = self.model(text)

        return [
            Entity(
                entity.start_char,
                entity.end_char,
                self._convert_type(entity.label_),
                frozenset([self.extractor_name]),
            )
            for entity in document.ents
        ]
