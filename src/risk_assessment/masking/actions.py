from abc import ABC, abstractmethod
from collections import defaultdict
from collections.abc import Callable
from hashlib import sha256


class MappingStorage(ABC):
    @abstractmethod
    def get_or_create(self, type_name: str, value: str) -> str:
        pass


class InMemoryMappingStorage(MappingStorage):
    _known_mapping: dict[str, dict[str, str]] = defaultdict(dict)

    def get_or_create(self, type_name: str, value: str) -> str:
        type_dict: dict[str, str] = self._known_mapping[type_name]

        if value not in type_dict:
            type_dict[value] = f"{type_name.upper()}-{len(type_dict) + 1}"

        return type_dict[value]


def tagging_factory(storage: MappingStorage = InMemoryMappingStorage()) -> Callable[[str, str], str]:
    def _tagging_operator(entity_type: str, entity_text: str) -> str:
        return storage.get_or_create(entity_type, entity_text)

    return _tagging_operator


def redact_factory(symbol: str = "X", size: int = 3) -> Callable[[str, str], str]:
    return lambda x, y: symbol * size


def tagging_with_hash(entity_type: str, entity_text: str) -> str:
    return f"{entity_type.upper()}-{sha256(entity_text.encode()).hexdigest()[-5:]}"


def redact_size_preserving(_: str, entity_text: str) -> str:
    return "X" * len(entity_text)


def format_preserving_redact(_: str, enity_text: str) -> str:
    return "".join(["X" if c.isalnum() else c for c in enity_text])


def no_action(value: str, _: str) -> str:
    return value
