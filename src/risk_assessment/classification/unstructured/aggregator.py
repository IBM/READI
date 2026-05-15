from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass, field
from itertools import chain

from risk_assessment.classification.identifiers import Identifier
from risk_assessment.classification.unstructured import Entity, TypeScore
from risk_assessment.classification.unstructured.pos_utility import is_verb_or_adverb


def _compute_confidence_score(best_type: TypeScore, all_scores: list[TypeScore]) -> float:
    if len(all_scores) == 1:
        return 1.0

    score = sum((best_type.type_score - type_score.type_score) / best_type.type_score for type_score in all_scores)
    if score == 0:  # all scores are the same
        return 1.0 / len(all_scores)
    return score / (len(all_scores) - 1)


@dataclass(kw_only=True, frozen=True)
class AggregatorConfiguration:
    prioritize_inclusion: bool = True
    prune_negative_scores: bool = True
    weights: dict[str, dict[str, float]] = field(default_factory=dict)
    default_weight: float = 1.0
    thresholds: dict[str, float] = field(default_factory=dict)
    to_report_only: set[str] | None = None
    identifiers_list: list[Identifier] = field(default_factory=list)
    filter_symbols: set[str] = field(default_factory=set)
    drop_repetition: bool = True
    validate_part_of_speech: bool = False
    pos_insensitive_types: set[str] = field(default_factory=set)
    merge_entities: bool = False
    merge_contiguos_only: bool = False

    def get_type_score(self, type_name: str, source_names: frozenset[str]) -> float:
        if type_name in self.weights:
            type_scores = self.weights[type_name]

            return sum(type_scores.get(source_name, self.default_weight) for source_name in source_names)

        return self.default_weight

    def validate_threshold(self, type_score: TypeScore) -> bool:
        if type_score.type_name in self.thresholds:
            if self.thresholds[type_score.type_name] > type_score.type_score:
                return False
        return True

    def is_reliable(self, source_names: frozenset[str], type_name: str) -> bool:
        if type_name in self.weights:
            type_scores = self.weights[type_name]

            return any(type_scores.get(source_name, self.default_weight) > 0.0 for source_name in source_names)

        return True

    def is_pos_dependent(self, entity: Entity) -> bool:
        return entity.entity_type not in self.pos_insensitive_types and is_verb_or_adverb(entity)


@dataclass
class Aggregator:
    configuration: AggregatorConfiguration = field(default_factory=AggregatorConfiguration)

    def aggregate(self, entities: list[list[Entity]], text: str) -> list[Entity]:
        entities_to_be_merged = self.validate_entities(list(chain(*entities)), text)

        entities_to_be_merged = self.remove_repetition(entities_to_be_merged)
        if self.configuration.prune_negative_scores:
            entities_to_be_merged = self.drop_unreliable(entities_to_be_merged)

        if self.configuration.prioritize_inclusion:
            (entities_to_be_merged, merged_from_overlap) = self.aggregate_over_contained(entities_to_be_merged)
        else:
            merged_from_overlap = []

        merged_from_overlap = self.filter_according_to_threshold(merged_from_overlap)

        merged_entities = self.split_and_merge(entities_to_be_merged)

        return self.filter_if_instructed(
            self.merge_adjacent_entities(
                self.filter_based_on_part_of_speech(merged_entities + merged_from_overlap),
                text,
            ),
        )

    def filter_based_on_part_of_speech(self, entities: list[Entity]) -> list[Entity]:
        if self.configuration.validate_part_of_speech:
            return [entity for entity in entities if not self.configuration.is_pos_dependent(entity)]

        return entities

    def filter_according_to_threshold(self, entities: list[Entity]) -> list[Entity]:
        return [
            entity
            for entity in entities
            if self.configuration.validate_threshold(
                TypeScore(entity.entity_type, self.configuration.get_type_score(entity.entity_type, entity.source)),
            )
        ]

    def filter_if_instructed(self, entities: list[Entity]) -> list[Entity]:
        if self.configuration.to_report_only is None:
            return entities
        else:
            return [entity for entity in entities if entity.entity_type in self.configuration.to_report_only]

    def aggregate_over_contained(self, entities: list[Entity]) -> tuple[list[Entity], list[Entity]]:
        def build_marker(entity: Entity) -> tuple[int, int, str, frozenset[str]]:
            return (entity.start, entity.end, entity.entity_type, entity.source)

        entities.sort(key=lambda entity: entity.end)
        entities.sort(key=lambda entity: entity.start)

        spent: set[tuple[int, int, str, frozenset[str]]] = set()
        merged_entities: list[Entity] = []

        for large in entities:
            large_marker = build_marker(large)

            if large_marker in spent:
                continue

            included_entities: list[tuple[int, int, str, frozenset[str]]] = []

            for small in entities:
                small_marker = build_marker(small)

                if small_marker in spent:
                    continue
                if small_marker == large_marker:
                    continue

                if small.start > large.end:
                    break
                if small.end < large.end:
                    break

                if small.start < large.start and small.end > large.end:
                    # small is large
                    break
                if small.start < large.start and small.end < large.end:
                    # overlapping on the left, cannot process this way
                    break
                if small.start >= large.start and small.end > large.end:
                    # overlapping on the right, cannot process this way
                    break

                if small.start >= large.start and small.end <= large.end:
                    included_entities.append(small_marker)
            else:
                spent.add(large_marker)
                spent.update(included_entities)

                merged_entities.append(large)

        return ([entity for entity in entities if build_marker(entity) not in spent], merged_entities)

    def drop_unreliable(self, entities: list[Entity]) -> list[Entity]:
        return [entity for entity in entities if self.configuration.is_reliable(entity.source, entity.entity_type)]

    def remove_repetition(self, entities: list[Entity]) -> list[Entity]:
        repetition_counter = Counter(
            [(entity.start, entity.end, entity.entity_type, entity.source) for entity in entities]
        )

        unique_entities: list[Entity] = []

        for entity in entities:
            marker = (entity.start, entity.end, entity.entity_type, entity.source)

            value = repetition_counter[marker]

            if value > 1:
                repetition_counter[marker] = -1
            elif value < 0:
                continue

            unique_entities.append(entity)
        return unique_entities

    def merge_adjacent_entities(self, entities: list[Entity], text: str) -> list[Entity]:
        if not self.configuration.merge_entities:
            return entities

        if len(entities) <= 1:
            return entities

        entities.sort(key=lambda entity: entity.end)
        entities.sort(key=lambda entity: entity.start)

        merged: list[Entity] = []

        current = entities[0]

        for other in entities[1:]:
            if current.entity_type == other.entity_type and self.entities_are_divided_by_blanks(text, current, other):
                current = Entity(
                    current.start,
                    other.end,
                    current.entity_type,
                    current.source | other.source,
                    current.pos_tags | other.pos_tags,
                    current.confidence,  # as for 'first' strategy of transformers token classification https://huggingface.co/transformers/v4.10.1/_modules/transformers/pipelines/token_classification.html
                )
            else:
                merged.append(current)
                current = other

        merged.append(current)

        return merged

    def entities_are_divided_by_blanks(self, text: str, entity1: Entity, entity2: Entity) -> bool:
        if entity1.end == entity2.start:
            return True

        if self.configuration.merge_contiguos_only:
            return False

        text_in_between = text[entity1.end : entity2.start]

        return not text_in_between or text_in_between.isspace() or not text_in_between.strip()

    def split_and_merge(self, entities: list[Entity]) -> list[Entity]:
        if len(entities) <= 1:
            return entities

        split_points: list[int] = self.find_split_point(entities)

        merged: list[Entity] = []

        start = split_points[0]

        for split_point_iterator in range(1, len(split_points)):
            end = split_points[split_point_iterator]

            generated_entity = self.generate_entity(start, end, entities)
            if generated_entity is not None:
                merged.append(generated_entity)

            start = end

        return merged

    def drop_repetitions(self, entities: list[Entity]) -> list[Entity]:
        unique_entities: dict[tuple[str, frozenset[str]], Entity] = {}

        for entity in entities:
            key = (entity.entity_type, entity.source)
            if key in unique_entities:
                continue
            unique_entities[key] = entity

        return list(unique_entities.values())

    def generate_entity(self, start: int, end: int, entities: list[Entity]) -> Entity | None:
        entities_involved: list[Entity] = self.find_involved_entities(entities, start, end)

        if not len(entities_involved):
            return None

        if self.configuration.drop_repetition:
            entities_involved = self.drop_repetitions(entities_involved)

        best_type_response: tuple[str, float] | None = self.get_best_type_by_weighted_voting_and_threshold(
            entities_involved
        )

        # This occurs if no types meet the score threshold
        if best_type_response is None:
            return None

        (best_type, confidence_score) = best_type_response

        best_source: frozenset[str] = self.compose_source_for_best_type(entities_involved, best_type)

        return Entity(
            start,
            end,
            best_type,
            best_source,
            self.merge_pos_tags(entity.pos_tags for entity in entities_involved),
            confidence=confidence_score,
        )

    def merge_pos_tags(self, tags: Iterable[frozenset[str]]) -> frozenset[str]:
        return frozenset(chain.from_iterable(tags))

    def compose_source_for_best_type(self, entities: list[Entity], best_type: str) -> frozenset[str]:
        return frozenset(chain.from_iterable(entity.source for entity in entities if entity.entity_type == best_type))

    def find_involved_entities(self, entities: list[Entity], start: int, end: int) -> list[Entity]:
        return [entity for entity in entities if entity.start <= start and entity.end >= end]

    def get_best_type_by_weighted_voting_and_threshold(self, entities: list[Entity]) -> tuple[str, float] | None:
        scores = self.compute_type_scores(entities)
        return self.decide_best_type_based_on_weight_and_threshold(scores)

    def decide_best_type_based_on_weight_and_threshold(self, scores: list[TypeScore]) -> tuple[str, float] | None:
        valid_scores: list[TypeScore] = [score for score in scores if self.configuration.validate_threshold(score)]

        if len(valid_scores):
            best_type = max(valid_scores, key=lambda x: x.type_score)

            return (best_type.type_name, _compute_confidence_score(best_type, valid_scores))
        return None

    def compute_type_scores(self, entities: list[Entity]) -> list[TypeScore]:
        scores: dict[str, float] = {}

        for entity in entities:
            entity_type = entity.entity_type
            if entity_type == "":
                continue

            source = entity.source

            type_score = self.configuration.get_type_score(entity_type, source)

            if entity_type in scores:
                scores[entity_type] += type_score
            else:
                scores[entity_type] = type_score

        return [TypeScore(ts[0], ts[1]) for ts in scores.items()]

    def find_split_point(self, entities: list[Entity]) -> list[int]:
        limits = [[entity.start, entity.end] for entity in entities]
        split_points = set(chain(*limits))

        return sorted(split_points)

    def validate_entities(self, entity_list: list[Entity], text: str) -> list[Entity]:
        # validated_entitites: list[Entity] = []
        # for entity in entity_list:
        #     if self.validate_entity(entity, text):
        #         validated_entitites.append(entity)
        # return validated_entitites

        return [entity for entity in entity_list if self.validate_entity(entity, text)]

    def validate_entity(self, entity: Entity, text: str) -> bool:
        if text[entity.start : entity.end] in self.configuration.filter_symbols:
            return False

        if self.configuration.identifiers_list and frozenset(["DRL"]) == entity.source:
            indentifier = None

            for current_indentifier in self.configuration.identifiers_list:
                if entity.entity_type == current_indentifier.__str__():
                    indentifier = current_indentifier
                    break

            if not indentifier:
                return True

            span_to_validate = [entity.start, entity.end]
            if indentifier.is_need_span():
                span_to_validate = [max(0, entity.start - indentifier.get_span_length_required_to_check()), entity.end]  # type: ignore
                for i in range(span_to_validate[0], entity.start):
                    if indentifier.is_of_this_type(text[i : span_to_validate[1]]):
                        return True

            elif indentifier.is_of_this_type(text[span_to_validate[0] : span_to_validate[1]]):
                return True
            else:
                return False

        return True
