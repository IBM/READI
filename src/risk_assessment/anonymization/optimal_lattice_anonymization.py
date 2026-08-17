from __future__ import annotations

import math
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import Any

from pandas import DataFrame
from pandas.core.groupby import DataFrameGroupBy

from risk_assessment.anonymization import AnonymizationAlgorithm, AnonymizationReport, PrivacyConstraint
from risk_assessment.metrics.informationloss import ColumnClass, ColumnInformation, ColumnType, categorical_precision
from risk_assessment.utility.hierarchy import GeneralizationHierarchy


@dataclass
class OLAOptions:
    privacy_constraints: list[PrivacyConstraint]
    suppression: float = 0.0
    information_loss: Callable[[DataFrame, DataFrame, list[ColumnInformation]], float] = categorical_precision


def hierarchy_encoder_generator(hierarchy: GeneralizationHierarchy, level: int) -> Callable[[Any], Any]:
    def hierarchy_encoder(value: Any) -> Any:
        return hierarchy.encode(value, level)

    return hierarchy_encoder


def _generalized_dataset(
    dataset: DataFrame, column_information: list[ColumnInformation], generalization_levels: list[int]
) -> DataFrame:
    for index, (column, column_name) in enumerate(
        [
            (c_i, column_name)
            for (c_i, column_name) in zip(column_information, dataset.columns, strict=False)
            if c_i.column_type == ColumnType.QUASI
        ]
    ):
        if column.column_class == ColumnClass.CATEGORICAL or column.column_class == ColumnClass.NUMERIC:
            hierarchy = column.hierarchy

            if hierarchy is None:
                raise ValueError(f"Hierarchy for column {str(column_name)} is not defined")

            dataset[column_name] = dataset[column_name].transform(
                # lambda value: hierarchy.encode(value, generalization_levels[index])
                hierarchy_encoder_generator(hierarchy, generalization_levels[index])
            )
        elif column.column_class == ColumnClass.NUMERIC:
            hierarchy = column.hierarchy

            if hierarchy is None:
                raise ValueError(f"Hierarchy for column {str(column_name)} is not defined")

            dataset[column_name] = dataset[column_name].transform(
                # lambda value: hierarchy.encode(value, generalization_levels[index])
                hierarchy_encoder_generator(hierarchy, generalization_levels[index])
            )
        else:
            raise ValueError("Support for categorical and numerical at the moment")

    return dataset


def _partition_dataset(dataset: DataFrame, column_information: list[ColumnInformation]) -> DataFrameGroupBy:
    return dataset.groupby(
        by=[
            dataset.columns[index]
            for index, c_i in enumerate(column_information)
            if c_i.column_type == ColumnType.QUASI
        ]
    )


@dataclass
class AnonymityChecker:
    dataset: DataFrame
    column_information: list[ColumnInformation]
    privacy_constraint: list[PrivacyConstraint]
    information_loss: Callable[[DataFrame, DataFrame, list[ColumnInformation]], float]

    def calculate_suppression_rate(self, node: LatticeNode) -> float:
        generalized_dataset = _generalized_dataset(self.dataset.copy(), self.column_information, node.values)

        partitions = _partition_dataset(generalized_dataset, self.column_information)

        suppressed_rows: int = 0

        for partition in partitions:
            if not self._check_constraints(partition[1]):
                suppressed_rows += len(partition[1])

        node.information_loss = self.information_loss(
            self.dataset,
            generalized_dataset,  # this is wrong, should remove suppressed rows from generalized dataset
            self.column_information,
        )

        return 100.0 * suppressed_rows / len(self.dataset)

    def _check_constraints(self, dataset: DataFrame) -> bool:
        for constraint in self.privacy_constraint:
            if not constraint.check(dataset, self.column_information):
                return False
        return True


@dataclass(eq=True)
class LatticeNode:
    values: list[int]
    suppression_rate: float | None = None
    is_anonymous: bool | None = None
    information_loss: float | None = None
    tagged: bool = False

    def sum(self) -> int:
        return sum(self.values)

    def is_decendent(self, other: LatticeNode) -> bool:
        if self == other:
            return False

        for i in range(len(self.values)):
            if self.values[i] < other.values[i]:
                return False

        return True

    def __str__(self) -> str:
        return ":".join([str(value) for value in self.values])

    def __hash__(self) -> int:
        return hash(str(self.values))


def _calculate_product(levels: list[list[int]]) -> list[list[int]]:
    product_result: list[list[int]] = []

    for k in range(len(levels[0])):
        value = levels[0][k]

        l1: list[int] = [value]

        product_result.append(l1)

    for i in range(1, len(levels)):
        result: list[list[int]] = []

        for k in range(len(levels[i])):
            value = levels[i][k]

            for l2 in product_result:
                new_list: list[int] = list(l2)
                new_list.append(value)

                result.append(new_list)

        product_result = result

    return product_result


class Lattice:
    def __init__(
        self, anonymity_checker: AnonymityChecker, column_information: list[ColumnInformation], suppression: float
    ):
        self._anonymity_checker = anonymity_checker
        self._column_information = column_information
        self._suppression = suppression
        self._quasi_columns: list[int] = [
            index for index, c_i in enumerate(column_information) if c_i.column_type == ColumnType.QUASI
        ]

        self._max_level: list[int] = []
        self._maximum_exploration_level: list[int] = []

        self._nodes_checked = 0

        for quasi_identifier in self._quasi_columns:
            column_info = column_information[quasi_identifier]

            hierarchy = column_info.hierarchy
            if None is hierarchy:
                raise ValueError(f"Missing hierarchy for colum {quasi_identifier}")

            assert hierarchy is not None
            self._max_level.append(len(hierarchy))
            self._maximum_exploration_level.append(column_info.max_level)

        self._lattice: dict[int, set[LatticeNode]] = {}
        self._all_nodes: dict[LatticeNode, LatticeNode] = {}

        levels: list[list[int]] = [list(range(self._max_level[i])) for i in range(len(self._quasi_columns))]

        product_result: list[list[int]] = _calculate_product(levels)

        self._lattice_max_level: int = 0
        self._total_nodes: int = 0

        for values in product_result:
            node = LatticeNode(values)
            level = node.sum()

            if level >= self._lattice_max_level:
                self._lattice_max_level = level

            if level not in self._lattice:
                self._lattice[level] = set()

            nodes: set[LatticeNode] = self._lattice[level]

            self._total_nodes += 1
            nodes.add(node)

            self._all_nodes[node] = node

    def explore(self) -> None:
        if self._nodes_checked != 0:
            raise RuntimeError("Lattice has already been used")

        self._explore(0, self._lattice_max_level, 0)
        self._check_for_holes()

    def _explore(self, min_level: int, max_level: int, current_depth: int) -> None:
        if min_level == max_level:
            return

        current_level: int = (max_level + min_level) // 2

        nodes: set[LatticeNode] = self._lattice[current_level]

        if nodes is None:
            return

        for node in nodes:
            if node.is_anonymous is None:
                self._nodes_checked += 1
                is_anonymous: bool = self._check_anonymity(node)
                self._tag_nodes(node, is_anonymous)

                if is_anonymous:
                    self._explore(min_level, current_level, current_depth + 1)
                else:
                    self._explore(current_level, max_level, current_depth + 1)

    def _check_anonymity(self, node: LatticeNode) -> bool:
        suppression_rate: float = self._anonymity_checker.calculate_suppression_rate(node)
        node.suppression_rate = suppression_rate
        return suppression_rate <= self._suppression

    def _tag_nodes(self, node: LatticeNode, is_anonymous: bool) -> None:
        node.is_anonymous = is_anonymous
        node.tagged = True

        for inner_node in self.successors(node, is_anonymous):
            self._tag_nodes(inner_node, is_anonymous)

    def _check_for_holes(self) -> None:
        levels = list(self._lattice.keys())
        levels.sort()

        for level in levels:
            nodes = self._lattice[level]

            for node in nodes:
                if node.is_anonymous is None:
                    is_anonymous = self._check_anonymity(node)
                    self._tag_nodes(node, is_anonymous)

    def k_minimal_nodes(self) -> list[LatticeNode]:
        levels = list(self._lattice.keys())
        levels.sort()

        matches: list[LatticeNode] = []

        for level in levels:
            nodes = self._lattice[level]

            for node in nodes:
                if node.is_anonymous and self._matches_maximum_exploration_level(node):
                    matches.append(node)

        return matches

    def _matches_maximum_exploration_level(self, node: LatticeNode) -> bool:
        node_leves = node.values

        if len(node_leves) != len(self._maximum_exploration_level):
            return False  # can this happen??

        for index in range(len(node_leves)):
            if self._maximum_exploration_level[index] == -1:
                continue

            if node_leves[index] > self._maximum_exploration_level[index]:
                return False

        return True

    def max_level(self) -> list[int]:
        return list(self._max_level)

    def get_lattice_max_level(self) -> int:
        return self._lattice_max_level

    def get_lattice(self) -> dict[int, set[LatticeNode]]:
        return self._lattice

    def successors(self, node: LatticeNode, is_anonymous: bool) -> Iterable[LatticeNode]:
        target_level = node.sum() + (1 if is_anonymous else -1)

        if target_level < 0:
            return []

        candidate_values: list[list[int]] = [[value, value + 1] for value in node.values]

        possible_nodes: list[LatticeNode] = [LatticeNode(list) for list in _calculate_product(candidate_values)]

        return [
            possible_node[0]
            for possible_node in [(node, node.sum()) for node in possible_nodes]
            if possible_node[1] == target_level
            and possible_node[1] <= self._lattice_max_level
            and possible_node[0] in self._all_nodes
        ]

    @staticmethod
    def matches_maximum_exploration_level(node: LatticeNode, maximum_exploration_level: list[int]) -> bool:
        if len(node.values) != len(maximum_exploration_level):
            return False

        for i in range(len(maximum_exploration_level)):
            if maximum_exploration_level[i] == -1:
                continue

            if node.values[i] > maximum_exploration_level[i]:
                return False

        return True


class OLA(AnonymizationAlgorithm):
    def __init__(self, options: OLAOptions):
        self._options = options

    def anonymize(
        self, dataset: DataFrame, column_information: list[ColumnInformation]
    ) -> tuple[DataFrame, AnonymizationReport]:
        if len(column_information) != len(dataset.columns):
            raise ValueError(
                f"Dataset and column information are inconsisten in shape {len(dataset)} vs {len(column_information)}"
            )

        if None is dataset or 0 == len(dataset):
            return (dataset, AnonymizationReport(False))

        if len([c_i for c_i in column_information if c_i.column_type == ColumnType.QUASI]) == 0:
            return (dataset, AnonymizationReport(True, 0, []))

        anonymity_checker = AnonymityChecker(
            dataset, column_information, self._options.privacy_constraints, self._options.information_loss
        )
        lattice = Lattice(anonymity_checker, column_information, self._options.suppression)
        lattice.explore()

        k_minimal_nodes = lattice.k_minimal_nodes()

        if 0 != len(k_minimal_nodes):
            best_node: LatticeNode = self._select_minimal_loss_on_level(k_minimal_nodes)

            if best_node.is_anonymous:
                if best_node.suppression_rate:
                    return (
                        self._anonymize_dataset_with_suppression(
                            dataset, column_information, best_node, anonymity_checker
                        ),
                        AnonymizationReport(
                            best_node.is_anonymous,
                            best_node.suppression_rate,
                            best_node.values,
                        ),
                    )
                else:
                    return (
                        self._anonymize_dataset(dataset, column_information, best_node),
                        AnonymizationReport(
                            best_node.is_anonymous,
                            0.0,
                            best_node.values,
                        ),
                    )
            else:
                return (dataset, AnonymizationReport(False))
        else:
            raise RuntimeError("Unable to find suitable generalization")

    def _select_minimal_loss_on_level(self, nodes: list[LatticeNode]) -> LatticeNode:
        best_node: LatticeNode | None = None
        best_information_loss = math.inf

        for node in nodes:
            if node is not None and node.information_loss is not None:
                if best_information_loss > node.information_loss:
                    best_information_loss = node.information_loss
                    best_node = node

        if best_node is not None:
            return best_node
        else:
            raise RuntimeError()

    def _anonymize_dataset(
        self, dataset: DataFrame, column_information: list[ColumnInformation], node: LatticeNode
    ) -> DataFrame:
        return _generalized_dataset(dataset, column_information, node.values)

    def _anonymize_dataset_with_suppression(
        self,
        dataset: DataFrame,
        column_information: list[ColumnInformation],
        node: LatticeNode,
        checker: AnonymityChecker,
    ) -> DataFrame:
        dataset = self._anonymize_dataset(dataset, column_information, node)

        partitions = _partition_dataset(dataset, column_information)

        for partition in partitions:
            if not checker._check_constraints(partition[1]):
                dataset.drop(index=partition[1].index, inplace=True)

        return dataset
