from typing import Any

from risk_assessment.utility.hierarchy import GeneralizationHierarchy, GeneralizationNode


class DummyHierarchy(GeneralizationHierarchy):
    def encode(self, value: Any, level: int, random_on_fail: bool = False) -> str:
        if level == 0:
            return value
        return "*"

    def __getitem__(self, key: str | None) -> GeneralizationNode:
        raise NotImplementedError()

    def __len__(self) -> int:
        raise NotImplementedError()

    def index_for_value(self, value: Any) -> int:
        raise NotImplementedError()

    def leaves_for_node(self, value: Any) -> int:
        raise NotImplementedError()

    def node_level(self, value: Any) -> int:
        raise NotImplementedError()
