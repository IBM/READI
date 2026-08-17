import importlib.resources

import pandas as pd
import pytest

from risk_assessment.anonymization import DistinctLDiversity, KAnonymity
from risk_assessment.anonymization.optimal_lattice_anonymization import OLA, OLAOptions
from risk_assessment.metrics.informationloss import ColumnClass, ColumnInformation, ColumnType
from risk_assessment.utility.hierarchy import MaterializedHierarchy
from risk_assessment.utility.hierarchy.datatypes import DummyHierarchy


def test_ola_with_headers():
    date_hierarchy = MaterializedHierarchy(
        [
            ["01/01/2008", "Jan_2008", "2008"],
            ["02/01/2008", "Jan_2008", "2008"],
            ["03/01/2008", "Jan_2008", "2008"],
        ]
    )

    gender_hierarchy = MaterializedHierarchy(
        [
            ["M", "Person"],
            ["F", "Person"],
        ]
    )

    age_hierarchy = MaterializedHierarchy(
        [
            ["13", "10-14", "10-19", "0-49", "0-99"],
            ["18", "15-19", "10-19", "0-49", "0-99"],
            ["19", "15-19", "10-19", "0-49", "0-99"],
            ["21", "20-24", "20-29", "0-49", "0-99"],
            ["22", "20-24", "20-29", "0-49", "0-99"],
            ["23", "20-24", "20-29", "0-49", "0-99"],
        ]
    )

    column_information: list[ColumnInformation] = [
        ColumnInformation(ColumnType.QUASI, ColumnClass.CATEGORICAL, hierarchy=date_hierarchy),
        ColumnInformation(ColumnType.QUASI, ColumnClass.CATEGORICAL, hierarchy=gender_hierarchy),
        ColumnInformation(ColumnType.QUASI, ColumnClass.CATEGORICAL, hierarchy=age_hierarchy),
    ]

    dataset = pd.DataFrame(
        [
            {
                "date": "01/01/2008",
                "sex": "M",
                "age": "18",
            },
            {
                "date": "01/01/2008",
                "sex": "M",
                "age": "18",
            },
            {
                "date": "01/01/2008",
                "sex": "M",
                "age": "18",
            },
            {
                "date": "01/01/2008",
                "sex": "M",
                "age": "13",
            },
            {
                "date": "01/01/2008",
                "sex": "M",
                "age": "19",
            },
            {
                "date": "02/01/2008",
                "sex": "F",
                "age": "18",
            },
            {
                "date": "02/01/2008",
                "sex": "F",
                "age": "22",
            },
            {
                "date": "02/01/2008",
                "sex": "F",
                "age": "23",
            },
            {
                "date": "02/01/2008",
                "sex": "F",
                "age": "21",
            },
            {
                "date": "01/01/2008",
                "sex": "M",
                "age": "22",
            },
        ]
    )

    options = OLAOptions([KAnonymity(3)], suppression=20.0)

    ola = OLA(options)

    anonymized, report = ola.anonymize(dataset, column_information)

    # with 20% suppression rate, we must have at least 10*0.8 rows on the final dataset
    assert len(anonymized) >= 0.8 * len(dataset)

    assert report.suppression_rate <= 20.0

    equivalence_class_sizes = anonymized.groupby(
        by=[
            anonymized.columns[index]
            for index, c_i in enumerate(column_information)
            if c_i.column_type == ColumnType.QUASI
        ]
    ).size()

    for equivalence_class_size in equivalence_class_sizes:
        assert equivalence_class_size >= 3


def test_ola():
    date_hierarchy = MaterializedHierarchy(
        [
            ["01/01/2008", "Jan_2008", "2008"],
            ["02/01/2008", "Jan_2008", "2008"],
            ["03/01/2008", "Jan_2008", "2008"],
        ]
    )

    gender_hierarchy = MaterializedHierarchy(
        [
            ["M", "Person"],
            ["F", "Person"],
        ]
    )

    age_hierarchy = MaterializedHierarchy(
        [
            ["13", "10-14", "10-19", "0-49", "0-99"],
            ["18", "15-19", "10-19", "0-49", "0-99"],
            ["19", "15-19", "10-19", "0-49", "0-99"],
            ["21", "20-24", "20-29", "0-49", "0-99"],
            ["22", "20-24", "20-29", "0-49", "0-99"],
            ["23", "20-24", "20-29", "0-49", "0-99"],
        ]
    )

    column_information: list[ColumnInformation] = [
        ColumnInformation(ColumnType.QUASI, ColumnClass.CATEGORICAL, hierarchy=date_hierarchy),
        ColumnInformation(ColumnType.QUASI, ColumnClass.CATEGORICAL, hierarchy=gender_hierarchy),
        ColumnInformation(ColumnType.QUASI, ColumnClass.CATEGORICAL, hierarchy=age_hierarchy),
    ]

    dataset = pd.DataFrame(
        [
            line.split(",")
            for line in """01/01/2008,M,18
01/01/2008,M,18
01/01/2008,M,18
01/01/2008,M,13
01/01/2008,M,19
02/01/2008,F,18
02/01/2008,F,22
02/01/2008,F,23
02/01/2008,F,21
01/01/2008,M,22""".split("\n")
        ]
    )
    dataset.rename(columns={number: f"Column {number}" for number in range(len(column_information))}, inplace=True)

    options = OLAOptions([KAnonymity(3)], suppression=20.0)

    ola = OLA(options)

    anonymized, report = ola.anonymize(dataset, column_information)

    # with 20% suppression rate, we must have at least 10*0.8 rows on the final dataset
    assert len(anonymized) >= 0.8 * len(dataset)

    assert report.suppression_rate <= 20.0

    equivalence_class_sizes = anonymized.groupby(
        by=[
            anonymized.columns[index]
            for index, c_i in enumerate(column_information)
            if c_i.column_type == ColumnType.QUASI
        ]
    ).size()

    for equivalence_class_size in equivalence_class_sizes:
        assert equivalence_class_size >= 3


def test_ola_ldiversity_distinct():
    date_hierarchy = MaterializedHierarchy(
        [
            ["01/01/2008", "Jan_2008", "2008"],
            ["02/01/2008", "Jan_2008", "2008"],
            ["03/01/2008", "Jan_2008", "2008"],
        ]
    )

    gender_hierarchy = MaterializedHierarchy(
        [
            ["M", "Person"],
            ["F", "Person"],
        ]
    )

    age_hierarchy = MaterializedHierarchy(
        [
            ["13", "10-14", "10-19", "0-49", "0-99"],
            ["18", "15-19", "10-19", "0-49", "0-99"],
            ["19", "15-19", "10-19", "0-49", "0-99"],
            ["21", "20-24", "20-29", "0-49", "0-99"],
            ["22", "20-24", "20-29", "0-49", "0-99"],
            ["23", "20-24", "20-29", "0-49", "0-99"],
        ]
    )

    column_information: list[ColumnInformation] = [
        ColumnInformation(ColumnType.QUASI, ColumnClass.CATEGORICAL, hierarchy=date_hierarchy),
        ColumnInformation(ColumnType.QUASI, ColumnClass.CATEGORICAL, hierarchy=gender_hierarchy),
        ColumnInformation(ColumnType.QUASI, ColumnClass.CATEGORICAL, hierarchy=age_hierarchy),
        ColumnInformation(ColumnType.SENSITIVE),
    ]

    dataset = pd.DataFrame(
        [
            line.split(",")
            for line in """01/01/2008,M,18,Cancer
01/01/2008,M,18,Cancer
01/01/2008,M,18,HIV
01/01/2008,M,13,HIV
01/01/2008,M,19,HIV
02/01/2008,F,18,Pneumonia
02/01/2008,F,22,Pneumonia
02/01/2008,F,23,Pneumonia
02/01/2008,F,21,Flu
01/01/2008,M,22,Flu""".split("\n")
        ]
    )
    dataset.rename(columns={number: f"Column {number}" for number in range(len(column_information))}, inplace=True)

    options = OLAOptions([KAnonymity(3), DistinctLDiversity(2)], suppression=20.0)

    ola = OLA(options)

    anonymized, report = ola.anonymize(dataset, column_information)

    # with 20% suppression rate, we must have at least 10*0.8 rows on the final dataset
    assert len(anonymized) >= 0.8 * len(dataset)

    assert report.suppression_rate <= 20.0

    equivalence_class_sizes = anonymized.groupby(
        by=[
            anonymized.columns[index]
            for index, c_i in enumerate(column_information)
            if c_i.column_type == ColumnType.QUASI
        ]
    ).size()

    for equivalence_class_size in equivalence_class_sizes:
        assert equivalence_class_size >= 3


def test_inconsistency_in_input_structure_missing_column_information():
    ola = OLA(OLAOptions([KAnonymity(3)]))

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
        ola.anonymize(dataset, column_information)


def test_inconsistency_in_input_structure_additional_column_information():
    ola = OLA(OLAOptions([KAnonymity(3)]))

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
        ola.anonymize(dataset, column_information)


def test_no_transofrmation_is_applied_with_no_quasi():
    res = importlib.resources.files(__package__).joinpath("data/random1.csv")
    with res.open("r") as iostream:
        dataset = pd.read_csv(iostream, header=None)

    ola = OLA(OLAOptions([KAnonymity(10)], 10))

    (anonymized, report) = ola.anonymize(dataset, [ColumnInformation() for _ in dataset.columns])

    assert len(anonymized) == len(dataset)
    assert report.generalization_levels is not None
    assert len(report.generalization_levels) == 0
