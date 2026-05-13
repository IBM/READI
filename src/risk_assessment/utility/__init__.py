import math
from dataclasses import dataclass
from typing import Any

import numpy as np
from numpy import dtype
from pandas import DataFrame, Series
from pandas.api.types import is_numeric_dtype


@dataclass
class ColumnStatistic:
    # common attributes
    column_name: Any
    column_type: dtype
    non_null: int
    # if numerical
    mean: float | None = None
    median: float | None = None
    std: float | None = None
    # if categorical
    histograms: Series | None = None


@dataclass
class DatasetStatistics:
    size: int
    column_statistics: list[ColumnStatistic]


def _numeric_column_statistics(column_name: Any, column_type: dtype, data: Series) -> ColumnStatistic:
    return ColumnStatistic(
        column_name, column_type, data.count(), mean=data.mean(), median=data.median(), std=data.std()
    )


def _categorical_column_statistics(column_name: Any, column_type: dtype, data: Series) -> ColumnStatistic:
    return ColumnStatistic(column_name, column_type, data.count(), histograms=data.value_counts())


def extract_statistics(dataset: DataFrame) -> DatasetStatistics:
    column_statistics: list[ColumnStatistic] = [
        (
            _numeric_column_statistics(column_name, column_type, dataset[column_name])
            if is_numeric_dtype(column_type)
            else _categorical_column_statistics(column_name, column_type, dataset[column_name])
        )
        for column_name, column_type in zip(dataset.columns, dataset.dtypes, strict=False)
    ]

    return DatasetStatistics(len(dataset), column_statistics)


def calculate_entropy(histograms: Series, number_of_records: int) -> float:
    return -sum([value / number_of_records * math.log(value / number_of_records) for value in histograms.values])


def kl_divergence(X: Series, Y: Series) -> float:
    divergence = 0.0
    for x_i in X.index:
        if x_i not in Y:
            return np.inf

        x = X[x_i]
        y = Y[x_i]

        if math.isnan(y):
            return np.inf

        if x > 0 and y > 0:
            divergence += x * math.log(x / y) - x + y
        elif x == 0 and y >= 0:
            divergence += y
        else:
            return np.inf

    return divergence


def js_divergence(X: Series, Y: Series) -> float:
    M = (X.add(Y, fill_value=0)) / 2

    return (kl_divergence(X, M) + kl_divergence(Y, M)) / 2


def extract_histograms(data: Series | DataFrame, normalize: bool = False) -> Series:
    return data.value_counts(normalize=normalize)
