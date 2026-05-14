import warnings
from typing import Any

import torch
from transformers import (
    AutoModelForTokenClassification,
    AutoTokenizer,
    pipeline,
)
from transformers.utils import logging

from risk_assessment.classification.unstructured import Entity, EntityExtractor

warnings.filterwarnings("ignore")

logging.set_verbosity_error()
logging.get_verbosity()


class HFEntityExtractor(EntityExtractor):
    """
    HuggingFace compatible EntityExtrator

    Mostly any token classification model published according to HF standard should be compatible with this class.
    """

    def __init__(
        self,
        model_path: str,
        type_mapping: dict[str, str] | None = None,
        extractor_name: str = "HF",
        score_thr: float = 0.7,
    ):
        if type_mapping is None:
            type_mapping = {}
        super().__init__(type_mapping)

        self.model = AutoModelForTokenClassification.from_pretrained(model_path)  # nosec
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)  # nosec
        if torch.backends.mps.is_available():
            self.device = "mps"
        elif torch.cuda.is_available():
            self.device = "cuda:0"
        else:
            self.device = "cpu"

        self.ner = pipeline(
            "ner", model=self.model, tokenizer=self.tokenizer, device=self.device, aggregation_strategy="first"
        )
        self.score_thr = score_thr
        self.extractor_name = extractor_name

    def extract(self, text: str) -> list[Entity]:
        entities = self.ner(text)
        # entities = self.__connect_entities(entities)
        filter_entities = self.__filter_spaces(entities, text)

        return [
            Entity(
                entity["start"],
                entity["end"],
                self._convert_type(entity["entity_group"]),
                frozenset([self.extractor_name]),
            )
            for entity in filter_entities
            if entity["score"] > self.score_thr
        ]

    def __filter_spaces(self, entity_list: list[dict[str, Any]], text: str) -> list[dict[str, Any]]:
        filter_entities: list[dict[str, Any]] = []
        for i in range(len(entity_list)):
            start = entity_list[i]["start"]
            end = entity_list[i]["end"]
            if text[entity_list[i]["start"] : entity_list[i]["end"]] != " ":
                if text[entity_list[i]["start"] : entity_list[i]["end"]][0] == " ":
                    start += 1
                    start = start if start < len(text) else len(text)
                if text[entity_list[i]["start"] : entity_list[i]["end"]][-1] == " ":
                    end -= 1
                    end = end if end < len(text) else len(text)
                    end = end if end > 0 else 0
                new_entity = {
                    "start": start,
                    "end": end,
                    "score": entity_list[i]["score"],
                    "entity_group": entity_list[i]["entity_group"],
                    "word": entity_list[i]["word"],
                }
                filter_entities.append(new_entity)
        return filter_entities

    def __connect_adjacent_entities(self, entity_list: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if entity_list:
            final_entity_list: list[dict[str, Any]] = []
            subgroups = []

            current_tag = entity_list[0]["entity"]
            current_end = entity_list[0]["end"]

            group = [entity_list[0]]
            for i in range(1, len(entity_list) + 1):
                if i == len(entity_list) and len(group) > 0:
                    subgroups.append(group)
                else:
                    next_tag = entity_list[i]["entity"]
                    if current_tag == next_tag and entity_list[i]["start"] == current_end:
                        group.append(entity_list[i])
                    else:
                        subgroups.append(group)
                        group = [entity_list[i]]
                        current_tag = entity_list[i]["entity"]
                        current_end = entity_list[i]["end"]

            for group in subgroups:
                entity: dict[str, Any] = {}
                for key, value in group[0].items():
                    entity[key] = value

                for i in range(1, len(group)):
                    entity["word"] = entity["word"] + " " + group[i]["word"]
                    entity["end"] = group[i]["end"]
                final_entity_list.append(entity)

            return final_entity_list
        return entity_list

    def __connect_entities(self, entity_list: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if entity_list:
            final_entity_list: list[dict[str, Any]] = []
            for i in range(len(entity_list)):
                entity_list[i]["word"] = entity_list[i]["word"].replace("#", "")

            current_tag = entity_list[0]["entity"]

            subgroups = []
            group = [entity_list[0]]
            for i in range(1, len(entity_list) + 1):
                if i == len(entity_list) and len(group) > 0:
                    subgroups.append(group)
                else:
                    next_tag = entity_list[i]["entity"]
                    if "I-" in next_tag and current_tag[2:] == next_tag[2:]:
                        group.append(entity_list[i])
                    else:
                        subgroups.append(group)
                        group = [entity_list[i]]
                        current_tag = entity_list[i]["entity"]

            for group in subgroups:
                entity: dict[str, Any] = {}
                for key, value in group[0].items():
                    entity[key] = value
                for i in range(1, len(group)):
                    entity["word"] = entity["word"] + " " + group[i]["word"]
                    entity["end"] = group[i]["end"]
                final_entity_list.append(entity)

            for i, entity in enumerate(final_entity_list):
                final_entity_list[i]["entity"] = entity["entity"][2:]

            return self.__connect_adjacent_entities(final_entity_list)
        return entity_list
