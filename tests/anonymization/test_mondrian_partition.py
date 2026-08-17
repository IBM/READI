from pandas import DataFrame

from risk_assessment.anonymization import KAnonymity
from risk_assessment.anonymization.mondrian import Interval, MondrianOptions, MondrianPartition, MondrianSplitStrategy
from risk_assessment.metrics.informationloss import ColumnClass, ColumnInformation, ColumnType
from risk_assessment.utility.hierarchy import MaterializedHierarchy, NumericalRange


def test_mondrian_partition_numerical():
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

    partition = MondrianPartition(
        dataset,
        ["1-10", "6-7", "2-12", None],
        [Interval(1, 10), Interval(6, 7), Interval(2, 12), None],
        column_information,
        MondrianOptions([KAnonymity(2)]),
    )

    assert partition
    assert partition.choose_dimension() == 0

    splits = partition.split(0)

    assert splits
    assert 2 == len(splits)


def test_mondrian_partition_categorical_hierarchy_based():
    dataset = DataFrame(
        data=[
            ["Greece"],
            ["Italy"],
            ["Kenya"],
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

    partition = MondrianPartition(
        dataset,
        [hierarchy.top_term],
        [Interval(0, len(dataset[0].unique()))],
        column_information,
        MondrianOptions([KAnonymity(2)], MondrianSplitStrategy.HIERARCHY_BASED),
    )

    assert partition is not None
    assert partition.choose_dimension() == 0

    splits = partition.split(0)

    assert splits
    assert 3 == len(splits)


def test_mondrian_partition_categorical_order_based():
    dataset = DataFrame(
        data=[
            ["Greece"],
            ["Italy"],
            ["Egypt"],
            ["Kenya"],
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

    partition = MondrianPartition(
        dataset,
        [hierarchy.top_term],
        [Interval(0, len(dataset[0].unique()))],
        column_information,
        MondrianOptions([KAnonymity(2)], MondrianSplitStrategy.ORDER_BASED),
    )

    assert partition is not None
    assert partition.choose_dimension() == 0

    splits = partition.split(0)

    assert splits
    assert 2 == len(splits)
