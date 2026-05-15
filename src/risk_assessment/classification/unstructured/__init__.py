"""Unstructured text classification for entity extraction and PII/PHI detection.

This module provides the core abstractions and utilities for extracting entities
(sensitive information) from unstructured text using various methods including
NER models, regex patterns, and dictionary lookups.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from multiprocessing.pool import Pool
from threading import Lock


@dataclass(eq=True, frozen=True)
class Entity:
    """Represents a detected entity (sensitive information) in text.

    An entity is a span of text that has been identified as containing
    sensitive information, along with metadata about its type, source,
    and confidence.

    Attributes:
        start: Starting character position in the text (inclusive).
        end: Ending character position in the text (exclusive).
        entity_type: Type of entity (e.g., "Person", "Email", "SSN").
        source: Set of extractor names that detected this entity.
        pos_tags: Part-of-speech tags for the entity tokens.
        confidence: Optional confidence score (0.0-1.0) for the detection.

    Example:
        >>> text = "Contact John Doe at john@example.com"
        >>> entity = Entity(
        ...     start=8,
        ...     end=16,
        ...     entity_type="Person",
        ...     source=frozenset(["SPACY", "DRL"]),
        ...     pos_tags=frozenset(["PROPN"]),
        ...     confidence=0.95
        ... )
        >>> print(text[entity.start:entity.end])
        'John Doe'
    """

    start: int
    end: int
    entity_type: str
    source: frozenset[str]
    pos_tags: frozenset[str] = field(default=frozenset())
    confidence: float | None = None


class EntityExtractor(ABC):
    """Abstract base class for entity extractors.

    Entity extractors analyze text and identify spans containing sensitive
    information. Different extractors use different methods (NER models,
    regex, dictionaries) and can be combined for comprehensive detection.

    Attributes:
        pool: Optional multiprocessing pool for parallel processing.
        lock: Thread lock for thread-safe operations.
        type_mapping: Dictionary for mapping extractor-specific types to standard types.

    Example:
        >>> class CustomExtractor(EntityExtractor):
        ...     def __init__(self):
        ...         super().__init__(type_mapping={"PERSON": "Person"})
        ...
        ...     def extract(self, text: str) -> list[Entity]:
        ...         # Custom extraction logic
        ...         return []
    """

    pool: Pool | None = None
    lock: Lock = Lock()

    def __init__(self, type_mapping: dict[str, str]):
        """Initialize the entity extractor.

        Args:
            type_mapping: Dictionary mapping extractor-specific entity types
                to standardized types (e.g., {"PERSON": "Person", "ORG": "Organization"}).
        """
        self.type_mapping = type_mapping

    def _convert_type(self, in_type: str) -> str:
        """Convert an entity type using the type mapping.

        Args:
            in_type: Original entity type from the extractor.

        Returns:
            Mapped entity type, or the original type if no mapping exists.
        """
        return self.type_mapping.get(in_type, in_type)

    @abstractmethod
    def extract(self, text: str) -> list[Entity]:
        """Extract entities from text.

        Args:
            text: Text to analyze for entities.

        Returns:
            List of Entity objects representing detected sensitive information.

        Raises:
            NotImplementedError: This is an abstract method that must be implemented by subclasses.
        """
        raise NotImplementedError("Abstract method")


def merge_overlapping(entities: list[Entity]) -> list[Entity]:
    """Merge overlapping entities of the same type.

    When multiple extractors detect overlapping spans of the same entity type,
    this function merges them into single entities that span the union of the
    overlapping regions. Sources and POS tags are combined.

    Args:
        entities: List of Entity objects, potentially with overlaps.

    Returns:
        List of Entity objects with overlaps merged. Entities of different
        types are never merged, even if they overlap.

    Example:
        >>> # Two extractors detect overlapping "Person" entities
        >>> e1 = Entity(0, 8, "Person", frozenset(["SPACY"]))
        >>> e2 = Entity(5, 12, "Person", frozenset(["DRL"]))
        >>> merged = merge_overlapping([e1, e2])
        >>> print(f"Merged: {merged[0].start}-{merged[0].end}")
        Merged: 0-12
        >>> print(merged[0].source)
        frozenset({'SPACY', 'DRL'})
    """
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
    """Entity extractor that automatically merges overlapping detections.

    This is a specialized extractor that combines multiple detection methods
    internally and automatically merges overlapping entities of the same type.
    Subclasses implement _extract() instead of extract().

    Example:
        >>> class CombinedExtractor(MultiSourceEntityExtractor):
        ...     def __init__(self):
        ...         super().__init__(type_mapping={})
        ...
        ...     def _extract(self, text: str) -> list[Entity]:
        ...         # Run multiple detection methods
        ...         entities = []
        ...         # ... detection logic ...
        ...         return entities  # Will be automatically merged
    """

    def __init__(self, type_mapping: dict[str, str]):
        """Initialize the multi-source entity extractor.

        Args:
            type_mapping: Dictionary mapping entity types to standardized types.
        """
        super().__init__(type_mapping)

    @abstractmethod
    def _extract(self, text: str) -> list[Entity]:
        """Internal extraction method to be implemented by subclasses.

        Args:
            text: Text to analyze for entities.

        Returns:
            List of Entity objects (may contain overlaps).

        Raises:
            NotImplementedError: This is an abstract method that must be implemented by subclasses.
        """
        raise NotImplementedError("Abstract method")

    def extract(self, text: str) -> list[Entity]:
        """Extract entities and automatically merge overlaps.

        Calls _extract() and then merges any overlapping entities of the same type.

        Args:
            text: Text to analyze for entities.

        Returns:
            List of Entity objects with overlaps merged.
        """
        return merge_overlapping(self._extract(text))


@dataclass
class TypeScore:
    """Score for an entity type detection.

    Used to track confidence scores for different entity type predictions,
    particularly when multiple models or methods provide scores for the
    same text span.

    Attributes:
        type_name: Name of the entity type (e.g., "Person", "Email").
        type_score: Confidence score for this type (typically 0.0-1.0).

    Example:
        >>> scores = [
        ...     TypeScore("Person", 0.95),
        ...     TypeScore("Organization", 0.75),
        ...     TypeScore("Location", 0.60)
        ... ]
        >>> best = max(scores, key=lambda s: s.type_score)
        >>> print(f"Best type: {best.type_name} ({best.type_score})")
        Best type: Person (0.95)
    """

    type_name: str
    type_score: float
