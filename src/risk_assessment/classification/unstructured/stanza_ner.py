import stanza
import torch

from risk_assessment.classification.unstructured import Entity, EntityExtractor


class STANZAEntityExtractor(EntityExtractor):
    def __init__(self, type_mapping: dict[str, str] | None = None, language: str = "en"):
        if type_mapping is None:
            type_mapping = {}
        super().__init__(type_mapping)
        self.use_gpu = torch.cuda.is_available()
        self.nlp = stanza.Pipeline(
            lang=language,
            processors="tokenize,pos,ner",
            logging_level="ERROR",
            use_gpu=self.use_gpu,
        )
        # full NER packages list:  "ncbi_disease", "ontonotes", "connl03", "anatem", "bc5cdr","bc4chemd", "bionlp13cg", "jnlpba", "linnaeus", "linnaeus" "i2b2", "radiology"

    def get_labels_list(self) -> list[str]:
        labels_list: list[str] = []
        for i in range(len(self.nlp.processors["ner"].model_paths)):
            labels_sublist = self.nlp.processors["ner"].get_known_tags(i)
            for label in labels_sublist:
                if label not in labels_list:
                    labels_list.append(label)
        return labels_list

    def extract(self, text: str) -> list[Entity]:
        doc = self.nlp(text)

        return [
            Entity(entity.start_char, entity.end_char, self._convert_type(entity.type), frozenset(["STANZA"]))
            for entity in doc.entities
        ]
