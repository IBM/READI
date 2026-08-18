"""Privacy constraints and base classes for data anonymization algorithms.

This module provides the foundational abstractions for dataset anonymization,
including the abstract base classes for anonymization algorithms and privacy
constraints, as well as concrete implementations of the most common privacy
models: k-Anonymity, l-Diversity (Distinct and Entropy variants), and
t-Closeness.

Typical usage::

    from risk_assessment.anonymization import KAnonymity, TCloseness
    from risk_assessment.anonymization.mondrian import Mondrian, MondrianOptions

    constraints = [KAnonymity(k=5), TCloseness(t=0.2)]
    options = MondrianOptions(privacy_constraints=constraints)
    mondrian = Mondrian(options)
    anonymized_df, report = mondrian.anonymize(df, column_information)
"""

import math
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

import pandas as pd
from pandas import DataFrame, Series

from risk_assessment.metrics.informationloss import ColumnClass, ColumnInformation, ColumnType
from risk_assessment.utility import calculate_entropy, extract_histograms


@dataclass
class AnonymizationReport:
    """Result report produced by an anonymization algorithm.

    Attributes:
        anonymized: Whether the dataset was successfully anonymized.
        suppression_rate: Fraction of rows suppressed (0.0–100.0). Defaults to 0.0.
        generalization_levels: Per-column generalization levels applied, if available.
    """

    anonymized: bool
    suppression_rate: float = 0.0
    generalization_levels: list[int] | None = None


class AnonymizationAlgorithm(ABC):
    """Abstract base class for anonymization algorithms.

    Subclasses implement the ``anonymize`` method to transform a dataset so that
    it satisfies the configured privacy constraints.
    """

    @abstractmethod
    def anonymize(
        self, dataset: DataFrame, column_information: list[ColumnInformation]
    ) -> tuple[DataFrame, AnonymizationReport]:
        """Anonymize the dataset.

        Args:
            dataset: The input DataFrame to anonymize.
            column_information: Metadata describing each column's type, class,
                and associated hierarchy or range.

        Returns:
            A tuple of ``(anonymized_dataset, report)`` where ``report``
            summarises whether anonymization succeeded and at what cost.
        """
        pass


class PrivacyConstraint(ABC):
    """Abstract base class for privacy constraints.

    A privacy constraint defines the condition that each equivalence class
    (partition) in an anonymized dataset must satisfy.
    """

    @abstractmethod
    def check(self, dataset: DataFrame, column_information: list[ColumnInformation]) -> bool:
        """Check whether the partition satisfies this constraint.

        Args:
            dataset: A single equivalence-class partition of the full dataset.
            column_information: Metadata describing each column.

        Returns:
            True if the constraint is satisfied, False otherwise.
        """
        pass


@dataclass
class KAnonymity(PrivacyConstraint):
    """k-Anonymity privacy constraint.

    A partition satisfies k-Anonymity when it contains at least *k* records,
    ensuring that each individual is indistinguishable from at least k-1 others
    with respect to the quasi-identifier attributes.

    Attributes:
        k: Minimum required equivalence-class size.
    """

    k: int

    def check(self, dataset: DataFrame, column_information: list[ColumnInformation]) -> bool:
        """Return True if the partition has at least k records."""
        return len(dataset) >= self.k


@dataclass
class DistinctLDiversity(PrivacyConstraint):
    """Distinct l-Diversity privacy constraint.

    A partition satisfies Distinct l-Diversity when every sensitive attribute
    column contains at least *l* distinct values, limiting the ability to infer
    a specific sensitive value for any individual.

    Attributes:
        l: Minimum number of distinct sensitive values required per partition.
    """

    l: int  # noqa: E741

    def check(self, dataset: DataFrame, column_information: list[ColumnInformation]) -> bool:
        for sensitive_column in [
            column_name
            for index, column_name in enumerate(dataset.columns)
            if column_information[index].column_type == ColumnType.SENSITIVE
        ]:
            unique_values = dataset[sensitive_column].unique()

            if len(unique_values) < self.l:
                return False

        return True


@dataclass
class EntropyLDiversity(PrivacyConstraint):
    """Entropy l-Diversity privacy constraint.

    A partition satisfies Entropy l-Diversity when, for every sensitive column,
    the Shannon entropy of the value distribution is at least log(l).  This is
    a stronger guarantee than Distinct l-Diversity because it also requires the
    values to be roughly evenly distributed.

    Attributes:
        l: Minimum entropy threshold expressed as log(l).
    """

    l: int  # noqa: E741

    def check(self, dataset: DataFrame, column_information: list[ColumnInformation]) -> bool:
        for sensitive_column in [
            column_name
            for index, column_name in enumerate(dataset.columns)
            if column_information[index].column_type == ColumnType.SENSITIVE
        ]:
            if not self._check_entropy(dataset, sensitive_column):
                return False

        return True

    def _check_entropy(self, dataset: DataFrame, column: str) -> bool:
        if len(dataset) < self.l:
            return False

        return self._check_histogram_entropy(dataset[column].value_counts(), len(dataset))

    def _check_histogram_entropy(self, histogram: Series, number_record: int) -> bool:
        entropy: float = calculate_entropy(histogram, number_record)

        return math.log(self.l) <= entropy


def _numeric_histogram_and_oder(values: Series) -> tuple[Series, Series]:
    ordered_values = values.copy()
    ordered_values.sort_values()

    return (
        values.value_counts(),
        ordered_values,
    )


def _categorica_histogram_and_oder(values: Series) -> tuple[Series, Series]:
    ordered_values = values.copy()
    ordered_values.sort_values()

    return (
        values.value_counts(),
        ordered_values,
    )


def _initialize_histograms_and_order(
    dataset: DataFrame, column_information: list[ColumnInformation]
) -> tuple[list[Series | None], list[Series | None]]:
    histograms: list[Series | None] = []
    orders: list[Series | None] = []

    for index, c_i in enumerate(column_information):
        if c_i.column_type == ColumnType.SENSITIVE:
            if c_i.column_class == ColumnClass.NUMERIC:
                (histogram, order) = _numeric_histogram_and_oder(dataset[dataset.columns[index]])
            elif c_i.column_class == ColumnClass.CATEGORICAL:
                (histogram, order) = _categorica_histogram_and_oder(dataset[dataset.columns[index]])
            else:
                raise ValueError(f"Unsupported column class {c_i.column_class} for {dataset.columns[index]}")

            histograms.append(histogram)
            orders.append(order)
        else:
            histograms.append(None)
            orders.append(None)

    return (histograms, orders)


class TCloseness(PrivacyConstraint):
    """t-Closeness privacy constraint.

    A partition satisfies t-Closeness when the distribution of each sensitive
    attribute within the partition is no further than *t* from the distribution
    in the full dataset, measured using the Earth Mover's Distance (categorical)
    or the ordered-distance metric (numerical).

    Call :meth:`initialize` with the full dataset before using :meth:`check`.

    Attributes:
        t: Maximum allowed distance between the partition and global distributions.
    """

    def __init__(self, t: float):
        self.t = t
        self.histograms: list[Series | None] | None = None
        self.orders: list[Series | None] | None = None
        self.total_count: int | None = None

    def initialize(self, dataset: DataFrame, column_information: list[ColumnInformation]) -> None:
        """Pre-compute global histograms and value ordering from the full dataset.

        Must be called once before :meth:`check` is used on individual partitions.

        Args:
            dataset: The complete (un-partitioned) dataset.
            column_information: Metadata describing each column.
        """
        (self.histograms, self.orders) = _initialize_histograms_and_order(dataset, column_information)
        self.total_count = len(dataset)

    def check(self, dataset: DataFrame, column_information: list[ColumnInformation]) -> bool:
        if self.histograms is None or self.orders is None or self.total_count is None:
            raise RuntimeError("TCloseness is expected to be initialized with dataset information")

        for index, c_i in enumerate(column_information):
            if c_i.column_type == ColumnType.SENSITIVE:
                order = self.orders[index]
                histogram = self.histograms[index]

                if order is None or histogram is None:
                    raise RuntimeError("Sensitive column has uninitialized histogram or order")

                if not self._check(dataset[dataset.columns[index]], c_i, histogram, order):
                    return False

        return True

    def _check(self, values: Series, column_information: ColumnInformation, histogram: Series, order: Series) -> bool:
        if column_information.column_class == ColumnClass.CATEGORICAL:
            return self._check_categorical(values, histogram, order)
        elif column_information.column_class == ColumnClass.NUMERIC:
            return self._check_numerical(values, histogram, order)

        else:
            raise ValueError(f"Unsupported column class {column_information.column_class}")

    def _check_numerical(self, values: Series, histogram: Series, order: Series) -> bool:
        local_histogram = values.value_counts()

        sum = 0.0
        distance = 0.0

        local_count = len(values)

        for q in order:
            q_frequency = histogram[q] / self.total_count
            p_frequency = (local_histogram[q] if q in local_histogram else 0.0) / local_count

            sum += p_frequency - q_frequency
            distance += abs(sum)

        t_value = distance / (len(order) - 1)

        return t_value <= self.t

    def _check_categorical(self, values: Series, histogram: Series, order: Series) -> bool:
        sum = 0.0

        local_histogram = values.value_counts()

        local_count = len(values)

        for key in histogram.keys():
            value = histogram[key]
            q_frequency = value / self.total_count
            p_frequency = (local_histogram[key] if key in local_histogram else 0.0) / local_count

            sum += abs(p_frequency - q_frequency)

        t_value = sum / 2

        return t_value <= self.t

    @staticmethod
    def equal_distance(partition_values: list[str], total_histogram: Series, total_count: int) -> float:
        partition_histogram = extract_histograms(pd.Series(partition_values))

        partition_size = len(partition_values)

        sum = 0.0

        for key in total_histogram.keys():
            count = int(total_histogram[key] or 0)
            q_freq = count / total_count
            p_freq = int(partition_histogram.get(key) or 0) / partition_size

            sum += abs(p_freq - q_freq)

        return sum / 2.0
