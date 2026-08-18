import importlib.resources

import pandas as pd
import pytest

from risk_assessment.anonymization import DistinctLDiversity, KAnonymity
from risk_assessment.anonymization.optimal_lattice_anonymization import (
    OLA,
    LatticeNode,
    OLAOptions,
    _generalized_dataset,
)
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
    assert __package__ is not None
    res = importlib.resources.files(__package__).joinpath("data/random1.csv")
    with res.open("r") as iostream:
        dataset = pd.read_csv(iostream, header=None)

    ola = OLA(OLAOptions([KAnonymity(10)], 10))

    (anonymized, report) = ola.anonymize(dataset, [ColumnInformation() for _ in dataset.columns])

    assert len(anonymized) == len(dataset)
    assert report.generalization_levels is not None
    assert len(report.generalization_levels) == 0


def test_select_minimal_loss_raises_when_no_node_has_information_loss():
    ola = OLA(OLAOptions([KAnonymity(3)]))

    with pytest.raises(RuntimeError):
        ola._select_minimal_loss_on_level([LatticeNode([0]), LatticeNode([1])])


def test_anonymize_returns_original_dataset_when_best_node_is_not_anonymous(monkeypatch: pytest.MonkeyPatch):
    dataset = pd.DataFrame({"value": ["a", "b"]})
    column_information = [ColumnInformation(ColumnType.QUASI, ColumnClass.CATEGORICAL, hierarchy=DummyHierarchy())]
    ola = OLA(OLAOptions([KAnonymity(3)]))
    best_node = LatticeNode([0], suppression_rate=0.0, is_anonymous=False, information_loss=0.0)

    class FakeLattice:
        def __init__(self, *args, **kwargs):
            pass

        def explore(self) -> None:
            pass

        def k_minimal_nodes(self) -> list[LatticeNode]:
            return [best_node]

    monkeypatch.setattr("risk_assessment.anonymization.optimal_lattice_anonymization.Lattice", FakeLattice)

    anonymized, report = ola.anonymize(dataset, column_information)

    assert anonymized.equals(dataset)
    assert not report.anonymized


def test_anonymize_raises_when_lattice_has_no_suitable_generalization(monkeypatch: pytest.MonkeyPatch):
    dataset = pd.DataFrame({"value": ["a", "b"]})
    column_information = [ColumnInformation(ColumnType.QUASI, ColumnClass.CATEGORICAL, hierarchy=DummyHierarchy())]
    ola = OLA(OLAOptions([KAnonymity(3)]))

    class FakeLattice:
        def __init__(self, *args, **kwargs):
            pass

        def explore(self) -> None:
            pass

        def k_minimal_nodes(self) -> list[LatticeNode]:
            return []

    monkeypatch.setattr("risk_assessment.anonymization.optimal_lattice_anonymization.Lattice", FakeLattice)

    with pytest.raises(RuntimeError, match="Unable to find suitable generalization"):
        ola.anonymize(dataset, column_information)


def test_generalized_dataset_requires_hierarchy_for_quasi_columns():
    dataset = pd.DataFrame({"value": ["a"]})
    column_information = [ColumnInformation(ColumnType.QUASI, ColumnClass.CATEGORICAL)]

    with pytest.raises(ValueError, match="Hierarchy for column value is not defined"):
        _generalized_dataset(dataset, column_information, [0])


def test_generalized_dataset_rejects_unsupported_column_class():
    dataset = pd.DataFrame({"value": ["a"]})
    column_information = [
        ColumnInformation(
            ColumnType.QUASI,
            ColumnClass.NONE,
            hierarchy=DummyHierarchy(),
        )
    ]

    with pytest.raises(ValueError, match="Support for categorical and numerical at the moment"):
        _generalized_dataset(dataset, column_information, [0])
