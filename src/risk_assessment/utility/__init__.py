"""Utility functions for statistical analysis and data profiling.

This module provides tools for extracting statistics from datasets, computing
entropy and divergence metrics, and analyzing data distributions. These utilities
are useful for data quality assessment and privacy risk evaluation.
"""

import math
from dataclasses import dataclass
from typing import Any

import numpy as np
from numpy import dtype
from pandas import DataFrame, Series
from pandas.api.types import is_numeric_dtype


@dataclass
class ColumnStatistic:
    """Statistics for a single dataset column.

    Holds statistical information about a column, with different metrics
    depending on whether the column is numerical or categorical.

    Attributes:
        column_name: Name of the column.
        column_type: Data type of the column (numpy dtype).
        non_null: Number of non-null values in the column.
        mean: Mean value (for numerical columns only).
        median: Median value (for numerical columns only).
        std: Standard deviation (for numerical columns only).
        histograms: Value counts (for categorical columns only).

    Example:
        >>> import pandas as pd
        >>> from pandas import Series
        >>> # Numerical column statistics
        >>> num_stats = ColumnStatistic(
        ...     column_name="age",
        ...     column_type=pd.Int64Dtype(),
        ...     non_null=100,
        ...     mean=35.5,
        ...     median=34.0,
        ...     std=12.3
        ... )

        >>> # Categorical column statistics
        >>> cat_stats = ColumnStatistic(
        ...     column_name="category",
        ...     column_type=pd.StringDtype(),
        ...     non_null=100,
        ...     histograms=Series({"A": 50, "B": 30, "C": 20})
        ... )
    """

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
    """Complete statistical profile of a dataset.

    Contains statistics for all columns in a dataset along with the
    overall dataset size.

    Attributes:
        size: Total number of rows in the dataset.
        column_statistics: List of ColumnStatistic objects, one per column.

    Example:
        >>> stats = DatasetStatistics(
        ...     size=1000,
        ...     column_statistics=[
        ...         ColumnStatistic("col1", pd.Int64Dtype(), 1000, mean=50.0),
        ...         ColumnStatistic("col2", pd.StringDtype(), 1000, histograms=Series({"A": 500}))
        ...     ]
        ... )
    """

    size: int
    column_statistics: list[ColumnStatistic]


def _numeric_column_statistics(column_name: Any, column_type: dtype, data: Series) -> ColumnStatistic:
    """Compute statistics for a numerical column.

    Args:
        column_name: Name of the column.
        column_type: Data type of the column.
        data: Series containing the column data.

    Returns:
        ColumnStatistic with mean, median, and standard deviation.

    Example:
        >>> import pandas as pd
        >>> data = pd.Series([1, 2, 3, 4, 5])
        >>> stats = _numeric_column_statistics("numbers", data.dtype, data)
        >>> print(f"Mean: {stats.mean}, Median: {stats.median}")
        Mean: 3.0, Median: 3.0
    """
    mean_val = data.mean()
    median_val = data.median()
    std_val = data.std()
    return ColumnStatistic(
        column_name,
        column_type,
        data.count(),
        mean=float(mean_val) if not isinstance(mean_val, Series) else float(mean_val.iloc[0]),
        median=float(median_val) if not isinstance(median_val, Series) else float(median_val.iloc[0]),
        std=float(std_val) if not isinstance(std_val, Series) else float(std_val.iloc[0]),
    )


def _categorical_column_statistics(column_name: Any, column_type: dtype, data: Series) -> ColumnStatistic:
    """Compute statistics for a categorical column.

    Args:
        column_name: Name of the column.
        column_type: Data type of the column.
        data: Series containing the column data.

    Returns:
        ColumnStatistic with value count histograms.

    Example:
        >>> import pandas as pd
        >>> data = pd.Series(["A", "B", "A", "C", "B", "A"])
        >>> stats = _categorical_column_statistics("category", data.dtype, data)
        >>> print(stats.histograms)
        A    3
        B    2
        C    1
    """
    return ColumnStatistic(column_name, column_type, data.count(), histograms=data.value_counts())


def extract_statistics(dataset: DataFrame) -> DatasetStatistics:
    """Extract comprehensive statistics from a dataset.

    Analyzes each column in the dataset and computes appropriate statistics
    based on the column type (numerical or categorical).

    Args:
        dataset: pandas DataFrame to analyze.

    Returns:
        DatasetStatistics containing statistics for all columns.

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     "age": [25, 30, 35, 40],
        ...     "category": ["A", "B", "A", "C"]
        ... })
        >>> stats = extract_statistics(df)
        >>> print(f"Dataset size: {stats.size}")
        Dataset size: 4
        >>> print(f"Number of columns: {len(stats.column_statistics)}")
        Number of columns: 2
    """
    column_statistics: list[ColumnStatistic] = [
        (
            _numeric_column_statistics(column_name, column_type, Series(dataset[column_name]))
            if is_numeric_dtype(column_type)
            else _categorical_column_statistics(column_name, column_type, Series(dataset[column_name]))
        )
        for column_name, column_type in zip(dataset.columns, dataset.dtypes, strict=False)
    ]

    return DatasetStatistics(len(dataset), column_statistics)


def calculate_entropy(histograms: Series, number_of_records: int) -> float:
    """Calculate Shannon entropy of a categorical distribution.

    Entropy measures the uncertainty or randomness in a distribution.
    Higher entropy indicates more uniform distribution, while lower
    entropy indicates more concentrated distribution.

    Args:
        histograms: Series containing value counts for each category.
        number_of_records: Total number of records.

    Returns:
        Shannon entropy value (in nats, using natural logarithm).

    Example:
        >>> import pandas as pd
        >>> # Uniform distribution (high entropy)
        >>> uniform = pd.Series([25, 25, 25, 25])
        >>> entropy_uniform = calculate_entropy(uniform, 100)
        >>> print(f"Uniform entropy: {entropy_uniform:.2f}")

        >>> # Concentrated distribution (low entropy)
        >>> concentrated = pd.Series([90, 5, 3, 2])
        >>> entropy_concentrated = calculate_entropy(concentrated, 100)
        >>> print(f"Concentrated entropy: {entropy_concentrated:.2f}")
    """
    return -sum([value / number_of_records * math.log(value / number_of_records) for value in histograms.values])


def kl_divergence(X: Series, Y: Series) -> float:
    """Calculate Kullback-Leibler divergence between two distributions.

    KL divergence measures how one probability distribution differs from
    a reference distribution. It is asymmetric: KL(X||Y) ≠ KL(Y||X).

    Args:
        X: First probability distribution (Series with probabilities).
        Y: Second probability distribution (reference, Series with probabilities).

    Returns:
        KL divergence value. Returns infinity if distributions are incompatible
        (e.g., Y has zero probability where X has non-zero probability).

    Note:
        Both X and Y should contain probability values (summing to 1.0).

    Example:
        >>> import pandas as pd
        >>> # Similar distributions (low divergence)
        >>> X = pd.Series([0.5, 0.3, 0.2], index=["A", "B", "C"])
        >>> Y = pd.Series([0.4, 0.35, 0.25], index=["A", "B", "C"])
        >>> div = kl_divergence(X, Y)
        >>> print(f"KL divergence: {div:.4f}")

        >>> # Very different distributions (high divergence)
        >>> X = pd.Series([0.9, 0.05, 0.05], index=["A", "B", "C"])
        >>> Y = pd.Series([0.1, 0.45, 0.45], index=["A", "B", "C"])
        >>> div = kl_divergence(X, Y)
        >>> print(f"KL divergence: {div:.4f}")
    """
    divergence = 0.0
    for x_i in X.index:
        if x_i not in Y:
            return np.inf

        x_val = X[x_i]
        y_val = Y[x_i]

        # Extract scalar values if needed
        x = float(x_val.item() if isinstance(x_val, Series) else x_val)
        y = float(y_val.item() if isinstance(y_val, Series) else y_val)

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
    """Calculate Jensen-Shannon divergence between two distributions.

    JS divergence is a symmetric and smoothed version of KL divergence.
    It measures the similarity between two probability distributions and
    is always finite (unlike KL divergence).

    Args:
        X: First probability distribution (Series with probabilities).
        Y: Second probability distribution (Series with probabilities).

    Returns:
        JS divergence value (always between 0 and ln(2) for binary distributions).
        Lower values indicate more similar distributions.

    Note:
        JS divergence is symmetric: JS(X, Y) = JS(Y, X).

    Example:
        >>> import pandas as pd
        >>> # Identical distributions (zero divergence)
        >>> X = pd.Series([0.5, 0.3, 0.2], index=["A", "B", "C"])
        >>> Y = pd.Series([0.5, 0.3, 0.2], index=["A", "B", "C"])
        >>> div = js_divergence(X, Y)
        >>> print(f"JS divergence (identical): {div:.6f}")

        >>> # Different distributions
        >>> X = pd.Series([0.7, 0.2, 0.1], index=["A", "B", "C"])
        >>> Y = pd.Series([0.2, 0.3, 0.5], index=["A", "B", "C"])
        >>> div = js_divergence(X, Y)
        >>> print(f"JS divergence (different): {div:.4f}")
    """
    M = (X.add(Y, fill_value=0)) / 2

    return (kl_divergence(X, M) + kl_divergence(Y, M)) / 2


def extract_histograms(data: Series | DataFrame, normalize: bool = False) -> Series:
    """Extract value count histograms from data.

    Computes the frequency of each unique value in the data, optionally
    normalized to probabilities.

    Args:
        data: Series or DataFrame to analyze.
        normalize: If True, return probabilities (0.0-1.0) instead of counts.

    Returns:
        Series with value counts or probabilities, sorted by frequency (descending).

    Example:
        >>> import pandas as pd
        >>> data = pd.Series(["A", "B", "A", "C", "B", "A"])
        >>>
        >>> # Raw counts
        >>> counts = extract_histograms(data, normalize=False)
        >>> print(counts)
        A    3
        B    2
        C    1

        >>> # Normalized probabilities
        >>> probs = extract_histograms(data, normalize=True)
        >>> print(probs)
        A    0.50
        B    0.33
        C    0.17
    """
    return data.value_counts(normalize=normalize)
