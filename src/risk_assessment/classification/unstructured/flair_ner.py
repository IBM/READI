from typing import Any

from flair.data import Sentence
from flair.models import SequenceTagger

from risk_assessment.classification.unstructured import Entity, EntityExtractor


def find_sentences_shift(text: str, sentences: list[Any]) -> list[int]:
    sentence_shift: list[int] = [0]
    for i, _sentence in enumerate(sentences):
        if i < len(sentences) - 1:
            next_sentence_start = text.find(sentences[i + 1].text)
            sentence_shift.append(next_sentence_start)
    return sentence_shift


class FLAIREntityExtractor(EntityExtractor):
    def __init__(
        self,
        model_name: str,
        type_mapping: dict[str, str] | None = None,
        nlp_model: Any = None,
        nlp_model_name: str = "spacy",
    ) -> None:
        if type_mapping is None:
            type_mapping = {}
        super().__init__(type_mapping)

        self.model = SequenceTagger.load(model_name)
        self.model_name = model_name
        self.nlp_model = nlp_model
        self.nlp_model_name = nlp_model_name

    def split_text_into_sentences(self, text: str) -> list[str]:
        if self.nlp_model_name == "spacy":
            sentences = list(self.nlp_model(text).sents)
        else:
            sentences = [text]
        return sentences

    def extract(self, text: str) -> list[Entity]:
        sentences = self.split_text_into_sentences(text)
        entities: list[Entity] = []
        sentences_shift = find_sentences_shift(text, sentences)
        for k, single_sentence in enumerate(sentences):
            sentence = Sentence(single_sentence)
            self.model.predict(sentence)
            for entity in sentence.get_spans("ner"):
                entities.append(
                    Entity(
                        entity.start_position + sentences_shift[k],
                        entity.end_position + sentences_shift[k],
                        self._convert_type(entity.get_label("ner").value),
                        frozenset(["FLAIR"]),
                    ),
                )

        return entities
