from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any

import numpy as np
import numpy.typing as npt
import pandas as pd
from pandas import DataFrame, Series

from risk_assessment.anonymization import AnonymizationAlgorithm, AnonymizationReport, PrivacyConstraint
from risk_assessment.metrics.informationloss import ColumnClass, ColumnInformation, ColumnType
from risk_assessment.utility.hierarchy import GeneralizationHierarchy, GeneralizationNode


class MondrianSplitStrategy(Enum):
    HIERARCHY_BASED = auto()
    ORDER_BASED = auto()


@dataclass
class Interval:
    low: float
    high: float
    median: float | None = None

    def range(self) -> float:
        return self.high - self.low


@dataclass
class MondrianOptions:
    privacy_constraints: list[PrivacyConstraint]
    split_strategy: MondrianSplitStrategy = MondrianSplitStrategy.ORDER_BASED


def _get_index_for_value(value: Any, hierarchy: GeneralizationHierarchy) -> float:
    return hierarchy.index_for_value(value)


def _extract_categorical_indices(values: Series, hierarchy: GeneralizationHierarchy) -> list[float]:
    return [_get_index_for_value(value, hierarchy) for value in values.unique()]


# def _find_common_ancestor(values: Series, hierarchy: GeneralizationHierarchy) -> str:
def _find_common_ancestor(values: npt.NDArray[Any], hierarchy: GeneralizationHierarchy) -> str:
    ancestors: list[GeneralizationNode] | None = None

    for value in values:
        node: GeneralizationNode | None = hierarchy[value]

        if ancestors is None:
            ancestors = []
            while node is not None:
                ancestors.append(node)
                node = node.parent
        else:
            while node is not None:
                try:
                    index = ancestors.index(node)
                    ancestors = ancestors[index:]
                    break
                except ValueError:
                    pass
                node = node.parent

    if ancestors is None:
        raise RuntimeError("No nodes for the values")

    return ancestors[0].value


class MondrianPartition:
    def __init__(
        self,
        dataset: DataFrame,
        middles: list[str | None],
        widths: list[Interval | None],
        column_information: list[ColumnInformation],
        options: MondrianOptions,
    ):
        self._dataset = dataset
        self._middles = middles
        self._widths = widths
        self._column_information = column_information
        self._option = options
        self._quasi_columns: list[int] = [
            index for index, c_i in enumerate(column_information) if c_i.column_type == ColumnType.QUASI
        ]
        self._sensitive_columns: list[int] = [
            index for index, c_i in enumerate(column_information) if c_i.column_type == ColumnType.SENSITIVE
        ]
        self._allowed_split: list[bool] = [True for _ in range(len(self._quasi_columns))]

    def disallow(self, index: int) -> None:
        self._allowed_split[index] = False

    def choose_dimension(self) -> int:
        max_width = -1.0
        max_dimension = -1

        for i in range(len(self._allowed_split)):
            if not self._allowed_split[i]:
                continue

            normalized_with = self._get_normalized_width(self._quasi_columns[i])

            if normalized_with > max_width:
                max_width = normalized_with
                max_dimension = i

        if max_width > 1:
            raise RuntimeError("Normalized width is greater than 1")

        if max_dimension == -1:
            for i in range(len(self._allowed_split)):
                self._allowed_split[i] = False

        return max_dimension

    def _get_normalized_width(self, index: int) -> float:
        column_information = self._column_information[index]
        dividend: float

        if column_information.column_class == ColumnClass.CATEGORICAL:
            hierarchy = column_information.hierarchy
            if None is hierarchy:
                raise ValueError(f"Missing hierarchy for column {index}")

            dividend = len(hierarchy[hierarchy.top_term])

        elif column_information.column_class == ColumnClass.NUMERIC:
            value_range = column_information.range
            if None is value_range:
                raise ValueError(f"Missing value range for column {index}")

            dividend = value_range.range()
        else:
            raise ValueError(f"ColumnClass type not supported {str(column_information.column_class)}")

        width = self._widths[index]

        if None is width:
            raise ValueError(f"Column {index} does not have assiciated width")

        try:
            return width.range() / dividend
        except ZeroDivisionError:
            return float("nan")

    def split(self, dimension: int) -> list[MondrianPartition]:
        real_dimension = self._quasi_columns[dimension]
        if self._column_information[real_dimension].column_class == ColumnClass.CATEGORICAL:
            return self._split_categorical(real_dimension)
        elif self._column_information[real_dimension].column_class == ColumnClass.NUMERIC:
            return self._split_numerical(real_dimension)
        else:
            raise ValueError(f"Column class not supported {self._column_information[real_dimension].column_class}")

    def _split_categorical(self, dimension: int) -> list[MondrianPartition]:
        if self._option.split_strategy == MondrianSplitStrategy.ORDER_BASED:
            return self._split_categorical_order_based(dimension)
        elif self._option.split_strategy == MondrianSplitStrategy.HIERARCHY_BASED:
            return self._split_categorical_hierarchy_based(dimension)
        else:
            raise ValueError(f"Split strategy not supported; {self._option.split_strategy}")

    def _split_categorical_order_based(self, dimension: int) -> list[MondrianPartition]:
        column_name = self._dataset.columns[dimension]
        hierarchy = self._column_information[dimension].hierarchy

        if hierarchy is None:
            raise ValueError(f"Missing hierarchy for column {dimension}")

        categorical_indices: list[float] = _extract_categorical_indices(self._dataset[column_name], hierarchy)
        categorical_indices.sort()

        median = np.median(categorical_indices)

        left_dataset = self._dataset[
            self._dataset[column_name].apply(lambda value: _get_index_for_value(value, hierarchy)) < median
        ]

        if 0 == len(left_dataset):
            return []

        left_middles = list(self._middles)

        left_middles[dimension] = _find_common_ancestor(left_dataset[column_name].unique(), hierarchy)

        if not self._check_constraints(left_dataset, left_middles):
            return []

        left_widths = list(self._widths)
        left_widths[dimension] = Interval(
            min(categorical_indices), max([index for index in categorical_indices if index < median])
        )

        right_dataset = self._dataset[
            self._dataset[column_name].apply(lambda value: _get_index_for_value(value, hierarchy)) >= median
        ]

        if 0 == len(right_dataset):
            return []

        right_middles = list(self._middles)
        right_middles[dimension] = _find_common_ancestor(right_dataset[column_name].unique(), hierarchy)

        if not self._check_constraints(right_dataset, right_middles):
            return []

        right_widths = list(self._widths)
        right_widths[dimension] = Interval(
            min([index for index in categorical_indices if index >= median]), max(categorical_indices)
        )

        return [
            MondrianPartition(left_dataset, left_middles, left_widths, self._column_information, self._option),
            MondrianPartition(right_dataset, right_middles, right_widths, self._column_information, self._option),
        ]

    def _split_categorical_hierarchy_based(self, dimension: int) -> list[MondrianPartition]:
        column_name = self._dataset.columns[dimension]
        hierarchy = self._column_information[dimension].hierarchy

        if hierarchy is None:
            raise ValueError(f"Missing hierarchy for column {dimension}")

        middle_value = self._middles[dimension]
        children = hierarchy[middle_value].children

        if 0 == len(children):
            return []

        sub_dataset: list[DataFrame] = [
            DataFrame(self._dataset[self._dataset[column_name].apply(lambda value, c=child: c.cover(value))])
            for child in children
        ]

        partitions: list[MondrianPartition] = []

        for child, dataset in zip(children, sub_dataset, strict=False):
            if 0 == len(dataset):
                continue
            middles = list(self._middles)
            middles[dimension] = child.value

            if not self._check_constraints(dataset, middles):
                return []

            widths = list(self._widths)
            widths[dimension] = Interval(0, len(child))

            partitions.append(
                MondrianPartition(dataset, middles, widths, self._column_information, self._option),
            )

        return partitions

    def _split_numerical(self, dimension: int) -> list[MondrianPartition]:
        column_name = self._dataset.columns[dimension]
        values: Series = Series(self._dataset[column_name])

        median = np.median(values)

        left_dataset = DataFrame(self._dataset[self._dataset[column_name] < median])

        if 0 == len(left_dataset):
            return []

        left_middles = list(self._middles)

        left_middles[dimension] = f"{min(left_dataset[column_name])}-{max(left_dataset[column_name])}"

        if not self._check_constraints(left_dataset, left_middles):
            return []

        left_widths = list(self._widths)
        left_widths[dimension] = Interval(min(left_dataset[column_name]), max(left_dataset[column_name]))

        right_dataset = DataFrame(self._dataset[self._dataset[column_name] >= median])

        if 0 == len(right_dataset):
            return []

        right_middles = list(self._middles)
        right_middles[dimension] = f"{min(right_dataset[column_name])}-{max(right_dataset[column_name])}"

        if not self._check_constraints(right_dataset, right_middles):
            return []

        right_widths = list(self._widths)
        right_widths[dimension] = Interval(min(right_dataset[column_name]), max(right_dataset[column_name]))

        return [
            MondrianPartition(left_dataset, left_middles, left_widths, self._column_information, self._option),
            MondrianPartition(right_dataset, right_middles, right_widths, self._column_information, self._option),
        ]

    def _check_constraints(self, dataset: DataFrame, middles: list[str | None]) -> bool:
        for constraint in self._option.privacy_constraints:
            if not constraint.check(dataset, self._column_information):
                return False
        return True

    def anonymize_dataset(self) -> DataFrame:
        self._dataset = self._dataset.copy()
        for index, middle in enumerate(self._middles):
            if middle is None:
                continue

            column_name = self._dataset.columns[index]
            self._dataset[column_name] = self._dataset[column_name].astype(object)
            self._dataset[column_name] = middle

        return self._dataset

    @staticmethod
    def generate_middle_key(min: float, max: float) -> str:
        if min == max:
            return str(min)

        return f"{min}-{max}"


def _calculate_cardinality(data: Series) -> float:
    return len(data.unique())


def _create_middles_and_widths(
    dataset: DataFrame, column_information: list[ColumnInformation]
) -> tuple[list[str | None], list[Interval | None]]:
    middle: list[str | None] = []
    width: list[Interval | None] = []
    for index, column_name in enumerate(dataset.columns):
        c_i = column_information[index]

        if c_i.column_type == ColumnType.QUASI:
            if c_i.column_class == ColumnClass.CATEGORICAL:
                hierarchy = c_i.hierarchy
                if None is hierarchy:
                    raise ValueError(f"Missing hierarchy for {column_name}")

                middle.append(hierarchy.top_term)
                width.append(Interval(0, _calculate_cardinality(dataset[column_name])))

            elif c_i.column_class == ColumnClass.NUMERIC:
                value_range = c_i.range
                if None is value_range:
                    raise ValueError(f"Missing value range for {column_name}")

                middle.append(MondrianPartition.generate_middle_key(value_range.min, value_range.max))
                width.append(Interval(value_range.min, value_range.max))
            else:
                raise ValueError(f"ColumnClass type not supported {str(c_i.column_class)}")
        else:
            middle.append(None)
            width.append(None)

    return (middle, width)


class Mondrian(AnonymizationAlgorithm):
    def __init__(self, options: MondrianOptions):
        self.options = options

    def anonymize(
        self, dataset: DataFrame, column_information: list[ColumnInformation]
    ) -> tuple[DataFrame, AnonymizationReport]:
        if len(column_information) != len(dataset.columns):
            raise ValueError(
                f"Dataset and column information are inconsisten in shape {len(dataset)} vs {len(column_information)}"
            )

        if None is dataset or 0 == len(dataset):
            return (dataset, AnonymizationReport(False))

        middles, widths = _create_middles_and_widths(dataset, column_information)

        partitions = self._anonymize(MondrianPartition(dataset, middles, widths, column_information, self.options), 0)

        return (self._anonymize_dataset(partitions), AnonymizationReport(True, 0.0))

    def _anonymize(self, partition: MondrianPartition, level: int) -> list[MondrianPartition]:
        dimension: int = partition.choose_dimension()

        if -1 == dimension:
            return [partition]

        sub_partitions: list[MondrianPartition] = partition.split(dimension)

        if 0 == len(sub_partitions):
            partition.disallow(dimension)
            return self._anonymize(partition, level + 1)
        else:
            return sum(
                [self._anonymize(sub_partition, level + 1) for sub_partition in sub_partitions],
                [],
            )

    def _anonymize_dataset(self, partitions: list[MondrianPartition]) -> DataFrame:
        return pd.concat([partition.anonymize_dataset() for partition in partitions])
