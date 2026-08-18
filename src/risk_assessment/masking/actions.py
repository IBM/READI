"""Masking action callables for de-identifying detected entities.

Each function (or factory) in this module implements the signature
``(entity_type: str, entity_text: str) -> str`` and can be used directly
as a transformation in :func:`~risk_assessment.masking.cleanse_dataframe_field`.

Available actions:

- :func:`tagging_factory` — replaces each unique value with a stable
  sequential label (``TYPE-1``, ``TYPE-2``, …).
- :func:`redact_factory` — replaces the entity with a fixed-length redaction
  symbol (default ``"XXX"``).
- :func:`tagging_with_hash` — replaces with a hash-based label for
  deterministic but non-reversible pseudonymisation.
- :func:`redact_size_preserving` — replaces every character with ``"X"``,
  preserving the original length.
- :func:`format_preserving_redact` — replaces alphanumeric characters with
  ``"X"`` while keeping punctuation and spaces, preserving the original format.
- :func:`no_action` — returns the entity text unchanged (pass-through).
"""

from abc import ABC, abstractmethod
from collections import defaultdict
from collections.abc import Callable
from hashlib import sha256


class MappingStorage(ABC):
    """Abstract storage for a type-keyed entity-to-label mapping.

    Implementations persist the mapping between original entity text and its
    assigned anonymized label so that the same value is always replaced
    consistently within a session.
    """

    @abstractmethod
    def get_or_create(self, type_name: str, value: str) -> str:
        """Return the label for ``value``, creating one if it does not exist.

        Args:
            type_name: The entity type (e.g. ``"Email"``).
            value: The raw entity text to look up or register.

        Returns:
            The anonymized label for this value.
        """
        pass


class InMemoryMappingStorage(MappingStorage):
    """In-memory implementation of :class:`MappingStorage`.

    Labels are assigned sequentially per entity type (``TYPE-1``, ``TYPE-2``,
    …) and held in a class-level dictionary for the lifetime of the process.
    """

    _known_mapping: dict[str, dict[str, str]] = defaultdict(dict)

    def get_or_create(self, type_name: str, value: str) -> str:
        """Return or create a sequential label for ``value`` under ``type_name``."""
        type_dict: dict[str, str] = self._known_mapping[type_name]

        if value not in type_dict:
            type_dict[value] = f"{type_name.upper()}-{len(type_dict) + 1}"

        return type_dict[value]


def tagging_factory(storage: MappingStorage = InMemoryMappingStorage()) -> Callable[[str, str], str]:
    """Create a tagging transformation that assigns stable sequential labels.

    Each unique ``(entity_type, entity_text)`` pair receives a label of the
    form ``TYPE-N`` the first time it is seen; subsequent occurrences receive
    the same label.

    Args:
        storage: Backing store for the entity-to-label mapping.
            Defaults to a shared :class:`InMemoryMappingStorage` instance.

    Returns:
        A ``(entity_type, entity_text) -> label`` callable.
    """

    def _tagging_operator(entity_type: str, entity_text: str) -> str:
        return storage.get_or_create(entity_type, entity_text)

    return _tagging_operator


def redact_factory(symbol: str = "X", size: int = 3) -> Callable[[str, str], str]:
    """Create a fixed-length redaction transformation.

    Args:
        symbol: Character used for redaction. Defaults to ``"X"``.
        size: Number of times ``symbol`` is repeated. Defaults to 3.

    Returns:
        A ``(entity_type, entity_text) -> redacted_text`` callable that always
        returns ``symbol * size`` regardless of the input.
    """
    return lambda x, y: symbol * size


def tagging_with_hash(entity_type: str, entity_text: str) -> str:
    """Replace entity text with a hash-based deterministic label.

    The label is of the form ``TYPE-<last5hexchars>`` derived from the SHA-256
    hash of the entity text.  The same text always produces the same label,
    but the mapping is not reversible.

    Args:
        entity_type: The entity type (e.g. ``"SSN"``).
        entity_text: The raw sensitive text to pseudonymise.

    Returns:
        A string of the form ``"TYPE-xxxxx"``.
    """
    return f"{entity_type.upper()}-{sha256(entity_text.encode()).hexdigest()[-5:]}"


def redact_size_preserving(_: str, entity_text: str) -> str:
    """Replace every character in the entity with ``"X"``, preserving length.

    Args:
        _: Entity type (unused).
        entity_text: The text to redact.

    Returns:
        A string of ``"X"`` characters with the same length as ``entity_text``.
    """
    return "X" * len(entity_text)


def format_preserving_redact(_: str, enity_text: str) -> str:
    """Redact alphanumeric characters while preserving punctuation and spaces.

    Each letter or digit in ``enity_text`` is replaced by ``"X"``; all other
    characters (spaces, hyphens, dots, etc.) are kept unchanged.  This keeps
    the visual structure of identifiers like phone numbers or credit cards.

    Args:
        _: Entity type (unused).
        enity_text: The text to redact.

    Returns:
        The format-preserving redacted string.
    """
    return "".join(["X" if c.isalnum() else c for c in enity_text])


def no_action(value: str, _: str) -> str:
    """Pass-through transformation — returns the entity text unchanged.

    Args:
        value: The entity type (returned as-is).
        _: Entity text (unused).

    Returns:
        ``value`` unchanged.
    """
    return value
