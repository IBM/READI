import importlib.resources

import pandas as pd  # type: ignore
from pandas import DataFrame

from risk_assessment.anonymization import DistinctLDiversity, EntropyLDiversity, KAnonymity, TCloseness
from risk_assessment.metrics.informationloss import ColumnClass, ColumnInformation, ColumnType
from risk_assessment.utility import extract_histograms
from risk_assessment.utility.hierarchy import MaterializedHierarchy


def test_kanonymity():
    column_information = [
        ColumnInformation(ColumnType.QUASI),
    ]

    kanonymity = KAnonymity(5)

    assert not kanonymity.check(
        DataFrame(
            data=[
                [1],
                [1],
                [1],
            ],
        ),
        column_information,
    )

    assert kanonymity.check(
        DataFrame(
            data=[
                [1],
                [1],
                [1],
                [1],
                [1],
            ],
        ),
        column_information,
    )


def test_ldiversity():
    column_information = [
        ColumnInformation(ColumnType.QUASI),
        ColumnInformation(ColumnType.SENSITIVE),
    ]

    constraint = DistinctLDiversity(2)

    assert not constraint.check(
        DataFrame(
            data=[
                [1, 1],
                [1, 1],
                [1, 1],
            ],
        ),
        column_information,
    )

    assert constraint.check(
        DataFrame(
            data=[
                [1, 1],
                [1, 2],
                [1, 3],
            ],
        ),
        column_information,
    )


def test_entropy_ldiversity():
    column_information = [
        ColumnInformation(ColumnType.QUASI),
        ColumnInformation(ColumnType.SENSITIVE),
    ]

    constraint = EntropyLDiversity(2)

    assert not constraint.check(
        DataFrame(
            data=[
                [1, 1],
                [1, 1],
                [1, 1],
            ],
        ),
        column_information,
    )

    assert constraint.check(
        DataFrame(
            data=[
                [1, 1],
                [1, 2],
                [1, 3],
            ],
        ),
        column_information,
    )


def test_tcloseness_hierarchical_distance():
    partition_values = ["gastric ulcer", "gastritis", "stomach cancer"]

    # hierarchy = MaterializedHierarchy(
    #     [
    #         ["bronchitis", "respiratory infection", "vascular and respiratory diseases", "all diseases"],
    #         ["colitis", "colon diseases", "digestive system diseases", "all diseases"],
    #         ["colon cancer", "colon diseases", "digestive system diseases", "all diseases"],
    #         ["flu", "respiratory infection", "vascular and respiratory diseases", "all diseases"],
    #         ["gastric ulcer", "stomach diseases", "digestive system diseases", "all diseases"],
    #         ["gastritis", "stomach diseases", "digestive system diseases", "all diseases"],
    #         ["pneumonia", "respiratory infection", "vascular and respiratory diseases", "all diseases"],
    #         ["pulmonary edema", "vascular diseases", "vascular and respiratory diseases", "all diseases"],
    #         ["pulmonary embolism", "vascular diseases", "vascular and respiratory diseases", "all diseases"],
    #         ["stomach cancer", "stomach diseases", "digestive system diseases", "all diseases"],
    #     ]
    # )

    total_histogram = extract_histograms(
        pd.Series(
            [
                "gastric ulcer",
                "gastritis",
                "stomach cancer",
                "gastritis",
                "flu",
                "bronchitis",
                "bronchitis",
                "pneumonia",
                "stomach cancer",
            ]
        )
    )
    total_count = 9

    distance = TCloseness.equal_distance(partition_values, total_histogram, total_count)

    assert abs(distance - 0.44444) < 0.00001


def test_tcloseness_hierarchical_distance2():
    partition_values = ["gastric ulcer", "stomach cancer", "pneumonia"]

    total_histogram = extract_histograms(
        pd.Series(
            [
                "gastric ulcer",
                "gastritis",
                "stomach cancer",
                "gastritis",
                "flu",
                "bronchitis",
                "bronchitis",
                "pneumonia",
                "stomach cancer",
            ]
        )
    )
    total_count = 9

    distance = TCloseness.equal_distance(partition_values, total_histogram, total_count)

    assert abs(distance - 0.5555555555) < 0.0000000001


def test_tcloseness_numeric():
    res = importlib.resources.files(__package__).joinpath("data/100_with_row_id.csv")
    with res.open("r") as iostream:
        dataset = pd.read_csv(iostream, header=None)

    column_information: list[ColumnInformation] = [
        ColumnInformation(ColumnType.SENSITIVE, ColumnClass.NUMERIC),
    ]
    for _ in range(1, len(dataset.columns)):
        column_information.append(ColumnInformation())

    constraint = TCloseness(0.5)
    constraint.initialize(dataset, column_information)

    assert constraint.check(dataset, column_information)


def test_tcloseness_categorical():
    res = importlib.resources.files(__package__).joinpath("data/100_with_row_id.csv")
    with res.open("r") as iostream:
        dataset = pd.read_csv(iostream, header=None)

    column_information: list[ColumnInformation] = [
        ColumnInformation(ColumnType.SENSITIVE, ColumnClass.CATEGORICAL),
    ]
    for _ in range(1, len(dataset.columns)):
        column_information.append(ColumnInformation())

    constraint = TCloseness(0.5)
    constraint.initialize(dataset, column_information)

    assert constraint.check(dataset, column_information)


def test_tcloseness_numeric_fail():
    dataset = pd.DataFrame([3, 4, 5, 6, 11, 8, 7, 9, 10])

    column_information: list[ColumnInformation] = [
        ColumnInformation(ColumnType.SENSITIVE, ColumnClass.CATEGORICAL),
    ]
    for _ in range(1, len(dataset.columns)):
        column_information.append(ColumnInformation())

    constraint = TCloseness(0.1)
    constraint.initialize(dataset, column_information)

    partition = pd.DataFrame([3, 4, 5])

    assert not constraint.check(partition, column_information)
