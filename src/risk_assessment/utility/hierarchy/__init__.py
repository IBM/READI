from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sized
from typing import Any

from pandas import Series


class GeneralizationNode:
    def __init__(self, value: Any, parent: GeneralizationNode | None, is_leaf: bool, max_height: int):
        self.value = value
        self.parent = parent
        self.is_leaf = is_leaf
        self.parent = parent

        self.children: list[GeneralizationNode] = []
        self.ancestors: list[GeneralizationNode]
        self.level: int
        self.number_of_leaves: int = 0

        self.coverage: dict[str, GeneralizationNode] = {}

        if parent is not None:
            self.ancestors = [parent] + parent.ancestors
            parent.children.append(self)
            self.level = parent.level - 1

            for ancestor in self.ancestors:
                ancestor.coverage[self.value] = self
                if is_leaf:
                    ancestor.number_of_leaves += 1
        else:
            self.level = max_height - 1
            self.ancestors = []

    def __len__(self) -> int:
        return self.number_of_leaves

    def cover(self, value: str) -> bool:
        return value in self.coverage

    def leaves(self) -> list[Any]:
        if self.is_leaf:
            return []

        return sum([[child] if child.is_leaf else child.leaves() for child in self.children], [])


class NumericalRange:
    def __init__(self, series: Series):
        self.series = series.astype(float)
        self.min = min(self.series)
        self.max = max(self.series)

    def range(self) -> float:
        return self.max - self.min

    def contains(self, value: Any) -> bool:
        return True if (float(value) in self.series.unique()) else False

    def __min__(self) -> float:
        return self.min

    def __max__(self) -> float:
        return self.max

    def __len__(self) -> int:
        return len(self.series)


class GeneralizationHierarchy(ABC, Sized):
    top_term: str

    @abstractmethod
    def leaves_for_node(self, value: Any) -> int:
        pass

    @abstractmethod
    def node_level(self, value: Any) -> int:
        pass

    @abstractmethod
    def index_for_value(self, value: Any) -> int:
        pass

    @abstractmethod
    def encode(self, value: Any, level: int, random_on_fail: bool = False) -> str:
        pass

    @abstractmethod
    def __getitem__(self, key: str | None) -> GeneralizationNode:
        pass


class MaterializedHierarchy(GeneralizationHierarchy):
    top_term: Any

    def __init__(self, paths: list[list[Any]]):
        self.terms: list[list[Any]] = []
        self.nodes: dict[str, GeneralizationNode] = {}
        self.leaves: dict[Any, list[Any]] = {}
        self.indices: dict[Any, int] = {}
        self.terms_added = 0
        self.max_height = max([len(path) for path in paths])

        for path in paths:
            self._add(path)

    def _add(self, path: list[Any]) -> None:
        leaf = path[0]
        self.leaves[leaf] = path
        self.terms.append(path)
        self.indices[leaf] = self.terms_added

        if self.terms_added == 0:
            top_term: str = path[-1]
            self.top_term = top_term
            self.nodes[self.top_term] = GeneralizationNode(self.top_term, None, False, self.max_height)

        self._add_nodes(path)
        self.terms_added += 1

    def _add_nodes(self, original_path: list[Any]) -> None:
        path = original_path[:]
        path.reverse()

        for i in range(len(path)):
            value = path[i]

            if value not in self.nodes:
                parent_value = path[i - 1]
                self.nodes[value] = GeneralizationNode(
                    value,
                    self.nodes[parent_value],
                    (i == len(path) - 1),
                    len(path),
                )

    def __getitem__(self, key: str | None) -> GeneralizationNode:
        if key in self.nodes:
            return self.nodes[key]
        elif str(key) in self.nodes:
            return self.nodes[str(key)]
        raise KeyError(f"{str(key)} ({type(key)})")

    def __len__(self) -> int:
        return self.max_height

    def leaves_for_node(self, value: Any) -> int:
        if value in self.nodes:
            return len([node for node in self[value].children if node.is_leaf])

        return 0

    def node_level(self, value: Any) -> int:
        return self[value].level

    def encode(self, value: Any, level: int, random_on_fail: bool = False) -> str:
        if level >= len(self):
            return self.top_term

        if level == 0:
            return value

        try:
            node: GeneralizationNode = self[value]
            return node.ancestors[level - 1].value
        except KeyError as e:
            if random_on_fail:
                raise Exception("Not implemented yet") from e
        return self.top_term

    def index_for_value(self, value: Any) -> int:
        return self.indices[value]
