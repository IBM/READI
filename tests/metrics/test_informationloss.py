import math

import pytest
from pandas import DataFrame, Index, Series

from risk_assessment.metrics.informationloss import (
    AverageEquivalenceClassSizeOptions,
    ColumnClass,
    ColumnInformation,
    ColumnType,
    DiscernibilityOptions,
    NonUniformEntropyOptions,
    _calculate_frequencies,
    _calculate_frequencies_for_column,
    _calculate_max_entropy,
    _compute_normalized_certain_penalty,
    _generate_column_name_mapping,
    _get_loss_categorical,
    _get_value_loss,
    _normalize_data_with,
    _report_for_column_without_transformation_level,
    average_equivalence_class_size,
    categorical_precision,
    discernibility,
    discernibility_star,
    generalized_loss_metric,
    global_certain_penalty,
    non_uniform_entropy,
    non_uniform_entropy_upper_bound,
)
from risk_assessment.utility.hierarchy import MaterializedHierarchy, NumericalRange


def _categorical_column_information(weight: float = 1.0) -> ColumnInformation:
    hierarchy = MaterializedHierarchy(
        [
            ["A", "Group1", "*"],
            ["B", "Group1", "*"],
            ["C", "Group2", "*"],
            ["D", "Group2", "*"],
        ]
    )
    return ColumnInformation(ColumnType.QUASI, ColumnClass.CATEGORICAL, weight=weight, hierarchy=hierarchy)


def test_average_equivalence_class_size_normalized_and_not_normalized():
    original = DataFrame({"qi": ["A", "A", "B", "B"]})
    anonymized = DataFrame({"qi": ["G1", "G1", "G2", "G2"]})
    column_information = [ColumnInformation(ColumnType.QUASI)]

    assert (
        average_equivalence_class_size(
            original, anonymized, column_information, AverageEquivalenceClassSizeOptions(normalized=False, k=2)
        )
        == 2.0
    )
    assert (
        average_equivalence_class_size(
            original, anonymized, column_information, AverageEquivalenceClassSizeOptions(normalized=True, k=2)
        )
        == 1.0
    )


def test_get_loss_categorical_handles_missing_unknown_leaf_and_generalized_values():
    column_information = _categorical_column_information()

    with pytest.raises(ValueError, match="missing hierarchical information"):
        _get_loss_categorical("A", ColumnInformation(ColumnType.QUASI, ColumnClass.CATEGORICAL))

    with pytest.raises(KeyError):
        _get_loss_categorical("missing", column_information)

    assert _get_loss_categorical("A", column_information) == 0.0
    assert math.isclose(_get_loss_categorical("Group1", column_information), 0.5)


def test_report_for_column_without_transformation_level_counts_suppressed_rows():
    column_information = _categorical_column_information(weight=2.0)
    original = Series(["A", "B", "C"])
    anonymized = Series(["A", "Group1"])

    assert math.isclose(_report_for_column_without_transformation_level(original, anonymized, column_information), 1.0)


def test_categorical_precision_averages_only_quasi_columns():
    original = DataFrame({"qi": ["A", "B"], "normal": [1, 2]})
    anonymized = DataFrame({"qi": ["Group1", "Group1"], "normal": [1, 2]})
    column_information = [_categorical_column_information(), ColumnInformation()]

    assert math.isclose(categorical_precision(original, anonymized, column_information), 0.5)


def test_discernibility_and_discernibility_star_account_for_non_anonymous_partitions():
    original = DataFrame({"qi": ["A", "A", "B", "B"]})
    anonymized = DataFrame({"qi": ["X", "X", "Y"]})
    column_information = [ColumnInformation(ColumnType.QUASI)]

    assert discernibility(original, anonymized, column_information, DiscernibilityOptions(k=2)) == 8.0
    assert discernibility_star(original, anonymized, column_information) == 5.0


def test_frequency_helpers_and_name_mapping():
    df = DataFrame({"qi": ["A", "A", "B"], "normal": [1, 2, 3]})
    column_information = [ColumnInformation(ColumnType.QUASI), ColumnInformation()]

    frequencies = _calculate_frequencies_for_column(df["qi"])
    assert frequencies == {"A": 2 / 3, "B": 1 / 3}

    frequency_list = _calculate_frequencies(df, column_information)
    assert frequency_list == [{"A": 2 / 3, "B": 1 / 3}, None]

    max_entropy = _calculate_max_entropy(frequencies, df["qi"])
    assert math.isclose(max_entropy, 2.754887502163469)

    mapping = _generate_column_name_mapping(Index(["qi", "normal"]))
    assert set(mapping.keys()) == {"qi", "normal"}
    assert mapping["qi"] != "qi"
    assert mapping["normal"] != "normal"


def test_non_uniform_entropy_and_upper_bound():
    original = DataFrame({"qi": ["A", "B", "A", "B"]})
    anonymized = DataFrame({"qi": ["A", "B", "G", "G"]})
    column_information = [_categorical_column_information()]

    assert math.isclose(
        non_uniform_entropy(original.copy(), anonymized, column_information, NonUniformEntropyOptions(k=2)),
        2.0,
    )
    assert math.isclose(non_uniform_entropy_upper_bound(original, anonymized, column_information), 4.0)


def test_normalized_certain_penalty_helpers_and_global_certain_penalty():
    original = DataFrame({"qi": [1.0, 2.0, 3.0, 4.0], "normal": [10, 20, 30, 40]})
    anonymized = DataFrame({"qi": ["1.0-2.0", "1.0-2.0", "3.0-4.0", "3.0-4.0"], "normal": [10, 20, 30, 40]})
    column_information = [
        ColumnInformation(ColumnType.QUASI, ColumnClass.NUMERIC, range=NumericalRange(original["qi"])),
        ColumnInformation(),
    ]

    with pytest.raises(ValueError, match="Not implemented yet"):
        _normalize_data_with(original["qi"], ColumnInformation(ColumnType.QUASI, ColumnClass.NUMERIC))

    partition = DataFrame({"qi": Series([1.0, 2.0])})
    with pytest.raises(TypeError, match="unsupported operand type"):
        _compute_normalized_certain_penalty(partition, column_information)

    with pytest.raises(TypeError, match="unsupported operand type"):
        global_certain_penalty(original, anonymized, column_information)


def test_get_value_loss_and_generalized_loss_metric_cover_categorical_numeric_and_suppression():
    hierarchy = MaterializedHierarchy(
        [
            ["A", "Group1", "*"],
            ["B", "Group1", "*"],
            ["C", "Group2", "*"],
        ]
    )
    categorical_info = ColumnInformation(ColumnType.QUASI, ColumnClass.CATEGORICAL, hierarchy=hierarchy, weight=2.0)
    numeric_series = Series([1.0, 2.0, 3.0])
    numeric_info = ColumnInformation(
        ColumnType.QUASI,
        ColumnClass.NUMERIC,
        range=NumericalRange(numeric_series),
        weight=1.0,
    )

    assert _get_value_loss("A", categorical_info) == 0.0
    assert math.isclose(_get_value_loss("Group1", categorical_info), -1.0)
    assert _get_value_loss("1.0", numeric_info) == 0.0
    assert math.isclose(_get_value_loss("1.0-2.0", numeric_info), 0.5)

    with pytest.raises(RuntimeError, match="Missing hierarchy"):
        _get_value_loss("A", ColumnInformation(ColumnType.QUASI, ColumnClass.CATEGORICAL))

    with pytest.raises(RuntimeError, match="Missing numeric range"):
        _get_value_loss("1.0-2.0", ColumnInformation(ColumnType.QUASI, ColumnClass.NUMERIC))

    with pytest.raises(RuntimeError, match="Wrong number of values"):
        _get_value_loss("1-2-3", numeric_info)

    with pytest.raises(RuntimeError, match="Column class not supported"):
        _get_value_loss("value", ColumnInformation(ColumnType.QUASI, ColumnClass.NONE))

    dataset = DataFrame({"cat": ["A", "B", "C"], "num": [1.0, 2.0, 3.0]})
    anonymized = DataFrame({"cat": ["A", "Group2"], "num": ["1.0-2.0", "2.0-3.0"]})
    column_information = [categorical_info, numeric_info]

    assert math.isclose(generalized_loss_metric(dataset, anonymized, column_information), 1.3333333333333333)
