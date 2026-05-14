from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from multiprocessing.pool import Pool
from threading import Lock


@dataclass(eq=True, frozen=True)
class Entity:
    start: int
    end: int
    entity_type: str
    source: frozenset[str]
    pos_tags: frozenset[str] = field(default=frozenset())
    confidence: float | None = None


class EntityExtractor(ABC):
    pool: Pool | None = None
    lock: Lock = Lock()

    def __init__(self, type_mapping: dict[str, str]):
        self.type_mapping = type_mapping

    def _convert_type(self, in_type: str) -> str:
        return self.type_mapping.get(in_type, in_type)

    @abstractmethod
    def extract(self, text: str) -> list[Entity]:
        raise NotImplementedError("Abstract method")


def merge_overlapping(entities: list[Entity]) -> list[Entity]:
    entities.sort(key=lambda entity: entity.end)
    entities.sort(key=lambda entity: entity.start)

    entity_types: set[str] = {entity.entity_type for entity in entities}

    saved: list[Entity] = []

    for entity_type in entity_types:
        type_entity = [entity for entity in entities if entity.entity_type == entity_type]

        current_pointer = 0

        while current_pointer < len(type_entity):
            current_entity = type_entity[current_pointer]
            next_pointer = current_pointer + 1

            deleted = False
            while next_pointer < len(type_entity):
                next_entity = type_entity[next_pointer]

                if current_entity.end < next_entity.start:
                    break

                if current_entity.start <= next_entity.start:
                    if current_entity.end < next_entity.end:
                        # delete current, break and not increase current
                        type_entity[current_pointer] = Entity(
                            start=current_entity.start,
                            end=next_entity.end,
                            entity_type=current_entity.entity_type,
                            source=current_entity.source | next_entity.source,
                            pos_tags=current_entity.pos_tags | next_entity.pos_tags,
                        )
                        del type_entity[next_pointer]
                        deleted = True
                        break
                    else:
                        # delete "next", next but not increase next
                        del type_entity[next_pointer]
                else:
                    if current_entity.end < next_entity.end:
                        # delete current, break and not increase current
                        del type_entity[current_pointer]
                        deleted = True
                        break
                    else:
                        # delete "next", next but not increase next
                        del type_entity[next_pointer]

                next_pointer += 1

            if not deleted:
                current_pointer += 1

        saved += type_entity

    return saved


class MultiSourceEntityExtractor(EntityExtractor):
    def __init__(self, type_mapping: dict[str, str]):
        super().__init__(type_mapping)

    @abstractmethod
    def _extract(self, text: str) -> list[Entity]:
        raise NotImplementedError("Abstract method")

    def extract(self, text: str) -> list[Entity]:
        return merge_overlapping(self._extract(text))


@dataclass
class TypeScore:
    type_name: str
    type_score: float
