from dataclasses import dataclass
from enum import Enum, auto
from hashlib import md5
from math import log2
from typing import Any

from pandas import (
    DataFrame,  # type: ignore
    Series,  # type: ignore
    concat,  # type: ignore
)
from pandas.core.groupby.generic import DataFrameGroupBy  # type: ignore
from pandas.core.indexes.base import Index  # type: ignore

from risk_assessment.utility.hierarchy import GeneralizationHierarchy, NumericalRange


@dataclass
class AverageEquivalenceClassSizeOptions:
    normalized: bool
    k: int


@dataclass
class DiscernibilityOptions:
    k: int


@dataclass
class NonUniformEntropyOptions:
    k: int


class ColumnType(Enum):
    NORMAL = auto()
    DIRECT = auto()
    QUASI = auto()
    SENSITIVE = auto()


class ColumnClass(Enum):
    NUMERIC = auto()
    CATEGORICAL = auto()
    NONE = auto()


@dataclass
class ColumnInformation:
    column_type: ColumnType = ColumnType.NORMAL
    column_class: ColumnClass = ColumnClass.NONE
    weight: float = 1.0
    hierarchy: GeneralizationHierarchy | None = None
    range: NumericalRange | None = None
    max_level: int = -1
    for_linking: bool = False


def _extract_quasi_identifiers(data: DataFrame, column_information: list[ColumnInformation]) -> list[str]:
    return [data.columns[index] for index, c_i in enumerate(column_information) if c_i.column_type == ColumnType.QUASI]


def average_equivalence_class_size(
    original: DataFrame,
    anonymized: DataFrame,
    column_information: list[ColumnInformation],
    options: AverageEquivalenceClassSizeOptions,
) -> float:
    partition_sizes = anonymized.groupby(by=_extract_quasi_identifiers(anonymized, column_information)).size()

    number_equivalence_classes = 0.0

    for partition_size in partition_sizes:
        if partition_size > 0:  # type: ignore
            number_equivalence_classes += 1.0  # type: ignore

    number_of_records = len(original)
    average_equivalence_class_size = number_of_records / number_equivalence_classes

    if options.normalized:
        return average_equivalence_class_size / options.k
    else:
        return average_equivalence_class_size


def _report_for_column_with_transformation_level() -> float:
    raise Exception("Not implemented yet")


def _get_loss_categorical(value: Any, column_information: ColumnInformation) -> float:
    if column_information.hierarchy is None:
        raise ValueError("Column information is missing hierarchical information")

    hierarchy: GeneralizationHierarchy = column_information.hierarchy
    level: int = hierarchy.node_level(value)

    if level < 0:
        raise RuntimeError(f"Unknown level for value {value}, column info: {str(column_information)}")

    if level == 0:
        return 0.0

    return level / (len(hierarchy) - 1.0)


def _report_for_column_without_transformation_level(
    original: Series, anonymized: Series, column_information: ColumnInformation
) -> float:
    # if column_information.column_class != ColumnClass.CATEGORICAL:
    #     raise ValueError("Cannot process non categorical colums")

    weight = column_information.weight
    precision = 0.0
    cells = 0

    for value in anonymized.values:
        cells += 1
        precision += weight * _get_loss_categorical(value, column_information)

    suppressed_rows = len(original) - len(anonymized)

    precision += weight * 1 * suppressed_rows

    return precision / len(original)


def _report_for_column(
    original: DataFrame,
    anonymized: DataFrame,
    column_information: ColumnInformation,
    transformation_levels: list[int] | None,
) -> float:
    if transformation_levels is None:
        return _report_for_column_without_transformation_level(original, anonymized, column_information)
    else:
        return _report_for_column_with_transformation_level()


def _categorical_precision_report_per_quasi_column(
    original: DataFrame,
    anonymized: DataFrame,
    column_information: list[ColumnInformation],
    transformation_levels: list[int] | None,
) -> list[float]:
    results: list[float] = []

    for index, c_i in enumerate(column_information):
        if c_i.column_type == ColumnType.QUASI:
            report: float = _report_for_column(
                original.iloc[:, index], anonymized.iloc[:, index], column_information[index], transformation_levels
            )  # for index, c_i in enumerate(column_information) if c_i.column_type == ColumnType.QUASI
            results.append(report)

    return results


def categorical_precision(
    original: DataFrame,
    anonymized: DataFrame,
    column_information: list[ColumnInformation],
    transformation_levels: list[int] | None = None,
) -> float:
    column_results: list[float] = _categorical_precision_report_per_quasi_column(
        original, anonymized, column_information, transformation_levels
    )
    sum_of_results = sum(column_results)

    return sum_of_results / len(column_results)


def discernibility(
    original: DataFrame,
    anonymized: DataFrame,
    column_information: list[ColumnInformation],
    options: DiscernibilityOptions,
) -> float:
    partition_sizes = anonymized.groupby(by=_extract_quasi_identifiers(anonymized, column_information)).size()

    number_of_records = len(original)

    value = 0.0
    non_anonymous_partitions = 0

    for partition_size in partition_sizes:
        if partition_size >= options.k:  # type: ignore
            value += partition_size**2  # type: ignore
        else:
            value += partition_size * number_of_records  # type: ignore
            non_anonymous_partitions += partition_size  # type: ignore

    value += number_of_records * (number_of_records - len(anonymized) - non_anonymous_partitions)

    return value


def discernibility_star(
    original: DataFrame, anonymized: DataFrame, column_information: list[ColumnInformation]
) -> float:
    partitions_sizes = anonymized.groupby(by=_extract_quasi_identifiers(anonymized, column_information)).size()

    value = 0.0

    for partition_size in partitions_sizes:
        if partition_size > 0:  # type: ignore
            value += partition_size**2  # type: ignore

    return value


def _calculate_frequencies_for_column(values: Series) -> dict[Any, float]:
    frequencies: dict[str, int] = {}

    for value in values:
        if value not in frequencies:
            frequencies[value] = 0
        frequencies[value] += 1

    return {value: float(frequency) / len(values) for value, frequency in frequencies.items()}


def _calculate_frequencies(df: DataFrame, column_information: list[ColumnInformation]) -> list[dict[Any, float] | None]:
    frequencies: list[dict[Any, float] | None] = []
    number_of_columns = len(df.columns)

    for i in range(number_of_columns):
        if column_information[i].column_type == ColumnType.QUASI:
            frequencies.append(_calculate_frequencies_for_column(df[df.columns[i]]))
        else:
            frequencies.append(None)

    return frequencies


def _calculate_max_entropy(column_frequencies: dict[Any, float], values: Series) -> float:
    return sum([-log2(column_frequencies[value]) for value in values])


def _generate_column_name_mapping(column_names: Index) -> dict[Any, str]:
    base_attempt = {
        value: md5(str(value).encode()).hexdigest()  # nosec
        for value in column_names  # nosec
    }

    for original, mapped in base_attempt.items():
        while mapped in column_names:
            mapped = md5(mapped.encode()).hexdigest()  # nosec
            base_attempt[original] = mapped

    return base_attempt


def non_uniform_entropy(
    original: DataFrame,
    anonymized: DataFrame,
    column_information: list[ColumnInformation],
    options: NonUniformEntropyOptions,
) -> float:
    # assumption: original and anonymized datasets are of the same size and that datasets' records are in the same order
    original_frequencies = _calculate_frequencies(original, column_information)
    anonymized_frequencies = _calculate_frequencies(anonymized, column_information)

    column_names = anonymized.columns
    column_name_mapping = _generate_column_name_mapping(column_names)

    original.rename(columns=column_name_mapping, inplace=True)

    concatenated_df: DataFrame = concat([anonymized, original], axis=1)
    anonymized_partitions: DataFrameGroupBy = concatenated_df.groupby(
        by=_extract_quasi_identifiers(anonymized, column_information)
    )

    nue_value = 0.0

    for _, data in anonymized_partitions:
        if len(data) >= options.k:
            # access both anonymized and non anonymized values to compute value
            for index, c_i in enumerate(column_information):
                if c_i.column_type != ColumnType.QUASI:
                    continue

                original_column_frequencies = original_frequencies[index]
                if None is original_column_frequencies:
                    raise ValueError("processing incorrect type column")

                anonymized_column_frequencies = anonymized_frequencies[index]
                if None is anonymized_column_frequencies:
                    raise ValueError("Processing incorrect type column")

                for _, row in data.iterrows():
                    true_column_name = column_names[index]
                    anonymized_value = row[true_column_name]

                    mapped_column_name = column_name_mapping[true_column_name]
                    original_value = row[mapped_column_name]

                    nue_value += c_i.weight * -log2(
                        original_column_frequencies[original_value] / anonymized_column_frequencies[anonymized_value]
                    )
        else:
            # access only non-anonymized values
            for index, c_i in enumerate(column_information):
                if c_i.column_type != ColumnType.QUASI:
                    continue

                original_column_frequencies = original_frequencies[index]
                if None is original_column_frequencies:
                    raise ValueError("processing incorrect type column")

                true_column_name = column_names[index]
                mapped_column_name = column_name_mapping[true_column_name]

                for original_value in data[mapped_column_name]:
                    nue_value += c_i.weight * -log2(original_column_frequencies[original_value])

    return nue_value


def non_uniform_entropy_upper_bound(
    original: DataFrame, _: DataFrame, column_information: list[ColumnInformation]
) -> float:
    frequencies = _calculate_frequencies(original, column_information)

    return sum(
        [
            _calculate_max_entropy(column_frequencies, original[original.columns[index]])
            for index, column_frequencies in enumerate(frequencies)
            if column_frequencies is not None
        ]
    )


def _normalize_data_with(series: Series, column_information: ColumnInformation) -> float:
    data_range = column_information.range
    if data_range is None:
        raise ValueError("Not implemented yet ")

    return (series.max - series.min()) / data_range.range()


def _compute_normalized_certain_penalty(data: DataFrame, column_information: list[ColumnInformation]) -> float:
    return sum(
        [
            _normalize_data_with(data[data.columns[index]], c_i)
            for index, c_i in enumerate(column_information)
            if c_i.column_type == ColumnType.QUASI
        ]
    )


def global_certain_penalty(_: DataFrame, anonymized: DataFrame, column_information: list[ColumnInformation]) -> float:
    quasi_identifiers = _extract_quasi_identifiers(anonymized, column_information)

    global_certain_penalty = sum(
        [
            len(partition) * _compute_normalized_certain_penalty(partition, column_information)
            for _, partition in anonymized.groupby(by=quasi_identifiers)
        ]
    )

    return global_certain_penalty / (len(quasi_identifiers) * len(anonymized))


def _get_value_loss(value: Any, column_information: ColumnInformation) -> float:
    if column_information.column_class == ColumnClass.CATEGORICAL:
        hierarchy = column_information.hierarchy

        if None is hierarchy:
            raise RuntimeError("Missing hierarchy")

        leaves = hierarchy[value].number_of_leaves

        if leaves == 0:
            return 0.0

        return (leaves - 1) / (hierarchy.leaves_for_node(hierarchy.top_term) - 1)
    elif column_information.column_class == ColumnClass.NUMERIC:
        numeric_range = column_information.range

        if numeric_range is None:
            raise RuntimeError("Missing numeric range")

        string_representation = str(value)

        if "-" in string_representation:
            try:
                [a, b] = string_representation.split("-")
            except ValueError as e:
                raise RuntimeError("Wrong number of values") from e

            return (float(b) - float(a)) / (numeric_range.max - numeric_range.min)
        return 0.0
    raise RuntimeError("Column class not supported")


def generalized_loss_metric(
    dataset: DataFrame, anonymized: DataFrame, column_information: list[ColumnInformation]
) -> float:
    loss_per_column: list[float] = [0.0 for _ in range(len(dataset.columns))]

    for row in anonymized.iterrows():
        for index, c_i in enumerate(column_information):
            if c_i.column_type == ColumnType.QUASI:
                loss = _get_value_loss(row[1][anonymized.columns[index]], c_i)
                loss_per_column[index] += loss

    if len(anonymized) < len(dataset):
        # with suppression
        loss = len(dataset) - len(anonymized)
        for index, c_i in enumerate(column_information):
            if c_i.column_type == ColumnType.QUASI:
                loss_per_column[index] += loss

    return sum(
        [loss * c_i.weight / len(dataset) for loss, c_i in zip(loss_per_column, column_information, strict=False)]
    )
