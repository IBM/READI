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
    anonymized: bool
    suppression_rate: float = 0.0
    generalization_levels: list[int] | None = None


class AnonymizationAlgorithm(ABC):
    @abstractmethod
    def anonymize(
        self, dataset: DataFrame, column_information: list[ColumnInformation]
    ) -> tuple[DataFrame, AnonymizationReport]:
        pass


class PrivacyConstraint(ABC):
    @abstractmethod
    def check(self, dataset: DataFrame, column_information: list[ColumnInformation]) -> bool:
        pass


@dataclass
class KAnonymity(PrivacyConstraint):
    k: int

    def check(self, dataset: DataFrame, column_information: list[ColumnInformation]) -> bool:
        return len(dataset) >= self.k


@dataclass
class DistinctLDiversity(PrivacyConstraint):
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
    def __init__(self, t: float):
        self.t = t
        self.histograms: list[Series | None] | None = None
        self.orders: list[Series | None] | None = None
        self.total_count: int | None = None

    def initialize(self, dataset: DataFrame, column_information: list[ColumnInformation]) -> None:
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
