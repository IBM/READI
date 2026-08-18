import importlib.resources

import pandas as pd
import pytest
from pandas import DataFrame

from risk_assessment.anonymization import AnonymizationReport, KAnonymity
from risk_assessment.anonymization.mondrian import (
    Interval,
    Mondrian,
    MondrianOptions,
    MondrianPartition,
    MondrianSplitStrategy,
    _create_middles_and_widths,
    _find_common_ancestor,
)
from risk_assessment.metrics.informationloss import ColumnClass, ColumnInformation, ColumnType
from risk_assessment.utility.hierarchy import MaterializedHierarchy, NumericalRange
from risk_assessment.utility.hierarchy.datatypes import DummyHierarchy


def test_mondrian_numerical():
    dataset = DataFrame(
        data=[
            [1, 7, 2, 4],
            [6, 6, 12, 4],
            [5, 7, 11, 4],
            [10, 7, 5, 4],
            [10, 7, 11, 4],
        ],
        columns=None,
    )

    column_information = [
        ColumnInformation(ColumnType.QUASI, range=NumericalRange(dataset[0]), column_class=ColumnClass.NUMERIC),
        ColumnInformation(ColumnType.QUASI, range=NumericalRange(dataset[1]), column_class=ColumnClass.NUMERIC),
        ColumnInformation(ColumnType.QUASI, range=NumericalRange(dataset[2]), column_class=ColumnClass.NUMERIC),
        ColumnInformation(),
    ]

    mondrian = Mondrian(MondrianOptions([KAnonymity(2)]))

    anonymized, report = mondrian.anonymize(dataset, column_information)

    assert anonymized is not None
    assert len(anonymized) == len(dataset)

    assert report is not None


def test_mondrian_numerical_hole():
    dataset = DataFrame(
        data=[
            [1, 7, 2, 4],
            [6, 6, 12, 4],
            [5, 7, 11, 4],
            [10, 7, 5, 4],
            [10, 7, 11, 4],
        ],
        columns=None,
    )

    column_information = [
        ColumnInformation(ColumnType.QUASI, range=NumericalRange(dataset[0]), column_class=ColumnClass.NUMERIC),
        ColumnInformation(ColumnType.QUASI, range=NumericalRange(dataset[1]), column_class=ColumnClass.NUMERIC),
        ColumnInformation(),
        ColumnInformation(ColumnType.QUASI, range=NumericalRange(dataset[3]), column_class=ColumnClass.NUMERIC),
    ]

    mondrian = Mondrian(MondrianOptions([KAnonymity(2)]))

    anonymized, report = mondrian.anonymize(dataset, column_information)

    assert anonymized is not None
    assert len(anonymized) == len(dataset)

    assert report is not None


def test_mondrian_numerical_100():
    K = 3

    assert __package__ is not None
    res = importlib.resources.files(__package__).joinpath("data/100.csv")
    with res.open("r") as iostream:
        dataset = pd.read_csv(iostream, header=None)
        dataset.rename(columns={number: f"Column {number}" for number in range(5)}, inplace=True)

    mondrian = Mondrian(MondrianOptions([KAnonymity(K)]))

    anonymized: DataFrame
    report: AnonymizationReport

    column_information = [
        ColumnInformation(),
        ColumnInformation(
            ColumnType.QUASI, range=NumericalRange(dataset["Column 1"]), column_class=ColumnClass.NUMERIC
        ),
        ColumnInformation(
            ColumnType.QUASI, range=NumericalRange(dataset["Column 2"]), column_class=ColumnClass.NUMERIC
        ),
        ColumnInformation(),
        ColumnInformation(
            ColumnType.QUASI, range=NumericalRange(dataset["Column 4"]), column_class=ColumnClass.NUMERIC
        ),
    ]

    assert len(column_information) == len(dataset.columns)

    anonymized, report = mondrian.anonymize(dataset, column_information)

    assert anonymized is not None
    assert len(anonymized) == len(dataset)

    assert report

    equivalence_class_sizes = anonymized.groupby(
        by=[
            anonymized.columns[index]
            for index, c_i in enumerate(column_information)
            if c_i.column_type == ColumnType.QUASI
        ]
    ).size()

    for equivalence_class_size in equivalence_class_sizes:
        assert equivalence_class_size >= K


def test_mondrian_categorical():
    dataset = DataFrame(
        data=[
            ["Greece"],
            ["Italy"],
            ["Egypt"],
            ["Singapore"],
            ["China"],
        ],
        columns=None,
    )

    hierarchy = MaterializedHierarchy(
        [
            ["Greece", "Europe", "*"],
            ["Italy", "Europe", "*"],
            ["Egypt", "Africa", "*"],
            ["Kenya", "Africa", "*"],
            ["Singapore", "Asia", "*"],
            ["China", "Asia", "*"],
        ]
    )

    column_information = [
        ColumnInformation(
            column_type=ColumnType.QUASI,
            column_class=ColumnClass.CATEGORICAL,
            hierarchy=hierarchy,
        ),
    ]
    k = 2

    mondrian = Mondrian(MondrianOptions([KAnonymity(k)], MondrianSplitStrategy.ORDER_BASED))

    anonymized, report = mondrian.anonymize(dataset, column_information)

    assert anonymized is not None
    assert len(anonymized) == len(dataset)

    equivalence_class_sizes = anonymized.groupby(
        by=[
            anonymized.columns[index]
            for index, c_i in enumerate(
                column_information,
            )
            if c_i.column_type == ColumnType.QUASI
        ],
    ).size()

    for equivalence_class_size in equivalence_class_sizes:
        assert equivalence_class_size >= k

    assert report


def test_mondrian_categorical_hierarchy_based():
    dataset = DataFrame(
        data=[
            ["Greece"],
            ["Italy"],
            ["Egypt"],
            ["Singapore"],
            ["China"],
        ],
        columns=None,
    )

    hierarchy = MaterializedHierarchy(
        [
            ["Greece", "Europe", "*"],
            ["Italy", "Europe", "*"],
            ["Egypt", "Africa", "*"],
            ["Kenya", "Africa", "*"],
            ["Singapore", "Asia", "*"],
            ["China", "Asia", "*"],
        ]
    )

    column_information = [
        ColumnInformation(
            column_type=ColumnType.QUASI,
            column_class=ColumnClass.CATEGORICAL,
            hierarchy=hierarchy,
        ),
    ]
    k = 2

    mondrian = Mondrian(MondrianOptions([KAnonymity(k)], split_strategy=MondrianSplitStrategy.HIERARCHY_BASED))

    anonymized, report = mondrian.anonymize(dataset, column_information)

    assert anonymized is not None
    assert len(anonymized) == len(dataset)

    equivalence_class_sizes = anonymized.groupby(
        by=[
            anonymized.columns[index]
            for index, c_i in enumerate(
                column_information,
            )
            if c_i.column_type == ColumnType.QUASI
        ],
    ).size()

    for equivalence_class_size in equivalence_class_sizes:
        assert equivalence_class_size >= k

    assert report


def test_inconsistency_in_input_structure_missing_column_information():
    mondrian = Mondrian(MondrianOptions([KAnonymity(3)]))

    column_information: list[ColumnInformation] = [
        ColumnInformation(ColumnType.QUASI, ColumnClass.CATEGORICAL, hierarchy=DummyHierarchy()),
        ColumnInformation(ColumnType.NORMAL, ColumnClass.CATEGORICAL, hierarchy=DummyHierarchy()),
        ColumnInformation(ColumnType.QUASI, ColumnClass.CATEGORICAL, hierarchy=DummyHierarchy()),
    ]

    dataset = pd.DataFrame(
        data=[
            [1, 2, 3, 4],
            [1, 2, 3, 4],
            [1, 2, 3, 4],
            [1, 2, 3, 4],
        ],
    )

    with pytest.raises(ValueError):
        mondrian.anonymize(dataset, column_information)


def test_inconsistency_in_input_structure_additional_column_information():
    mondrian = Mondrian(MondrianOptions([KAnonymity(3)]))

    column_information: list[ColumnInformation] = [
        ColumnInformation(ColumnType.QUASI, ColumnClass.CATEGORICAL, hierarchy=DummyHierarchy()),
        ColumnInformation(ColumnType.NORMAL, ColumnClass.CATEGORICAL, hierarchy=DummyHierarchy()),
        ColumnInformation(ColumnType.QUASI, ColumnClass.CATEGORICAL, hierarchy=DummyHierarchy()),
    ]

    dataset = pd.DataFrame(
        data=[
            [1, 2],
            [1, 2],
            [1, 2],
        ],
    )

    with pytest.raises(ValueError):
        mondrian.anonymize(dataset, column_information)


def test_find_common_ancestor_raises_for_empty_values():
    hierarchy = MaterializedHierarchy(
        [
            ["Greece", "Europe", "*"],
            ["Italy", "Europe", "*"],
        ]
    )

    with pytest.raises(RuntimeError, match="No nodes for the values"):
        _find_common_ancestor(pd.Series(dtype=object).to_numpy(), hierarchy)


def test_create_middles_and_widths_requires_hierarchy_for_categorical_quasi():
    dataset = DataFrame({"country": ["Greece", "Italy"]})
    column_information = [ColumnInformation(ColumnType.QUASI, ColumnClass.CATEGORICAL)]

    with pytest.raises(ValueError, match="Missing hierarchy for country"):
        _create_middles_and_widths(dataset, column_information)


def test_create_middles_and_widths_requires_range_for_numeric_quasi():
    dataset = DataFrame({"age": [20, 30]})
    column_information = [ColumnInformation(ColumnType.QUASI, ColumnClass.NUMERIC)]

    with pytest.raises(ValueError, match="Missing value range for age"):
        _create_middles_and_widths(dataset, column_information)


def test_partition_choose_dimension_returns_minus_one_when_all_widths_are_nan():
    dataset = DataFrame({0: [5, 5, 5], 1: [7, 7, 7]})
    column_information = [
        ColumnInformation(ColumnType.QUASI, ColumnClass.NUMERIC, range=NumericalRange(dataset[0])),
        ColumnInformation(ColumnType.QUASI, ColumnClass.NUMERIC, range=NumericalRange(dataset[1])),
    ]
    partition = MondrianPartition(
        dataset,
        ["5", "7"],
        [Interval(5, 5), Interval(7, 7)],
        column_information,
        MondrianOptions([KAnonymity(2)]),
    )

    assert partition.choose_dimension() == -1


def test_partition_split_raises_for_unsupported_quasi_column_class():
    dataset = DataFrame({0: ["a", "b"]})
    column_information = [ColumnInformation(ColumnType.QUASI, ColumnClass.NONE)]
    partition = MondrianPartition(
        dataset,
        [None],
        [Interval(0, 1)],
        column_information,
        MondrianOptions([KAnonymity(1)]),
    )

    with pytest.raises(ValueError, match="Column class not supported"):
        partition.split(0)


def test_partition_normalized_width_requires_width_entry():
    dataset = DataFrame({0: [1, 2]})
    column_information = [
        ColumnInformation(ColumnType.QUASI, ColumnClass.NUMERIC, range=NumericalRange(dataset[0])),
    ]
    partition = MondrianPartition(
        dataset,
        ["1-2"],
        [None],
        column_information,
        MondrianOptions([KAnonymity(1)]),
    )

    with pytest.raises(ValueError, match="Column 0 does not have assiciated width"):
        partition._get_normalized_width(0)
