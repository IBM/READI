import importlib.resources
import math

import pandas as pd
import pytest

from risk_assessment.anonymization import KAnonymity, PrivacyConstraint
from risk_assessment.anonymization.optimal_lattice_anonymization import AnonymityChecker, LatticeNode
from risk_assessment.metrics.informationloss import ColumnClass, ColumnInformation, ColumnType
from risk_assessment.utility.hierarchy import MaterializedHierarchy


@pytest.mark.xfail(reason="Importlib issue should be fixed")
def test_anonymity_checked():
    k = 3

    date_hierarchy = MaterializedHierarchy(
        [
            ["01/01/2008", "Jan 2008", "2008"],
            ["02/01/2008", "Jan 2008", "2008"],
            ["03/01/2008", "Jan 2008", "2008"],
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

    column_information = [
        ColumnInformation(ColumnType.QUASI, ColumnClass.CATEGORICAL, hierarchy=date_hierarchy),
        ColumnInformation(ColumnType.QUASI, ColumnClass.CATEGORICAL, hierarchy=gender_hierarchy),
        ColumnInformation(ColumnType.QUASI, ColumnClass.CATEGORICAL, hierarchy=age_hierarchy),
    ]

    assert __package__ is not None
    res = importlib.resources.files(__package__).joinpath("data/testOLA.csv")
    with res.open("r") as iostream:
        dataset = pd.read_csv(iostream, header=None)
    dataset.rename(columns={number: f"Column {number}" for number in range(len(column_information))}, inplace=True)

    privacy_constraint: list[PrivacyConstraint] = [KAnonymity(k)]

    anonymity_checker = AnonymityChecker(dataset, column_information, privacy_constraint, lambda d, a, c_i: -1.0)

    node: LatticeNode = LatticeNode([0, 0, 0])

    suppression_rate = anonymity_checker.calculate_suppression_rate(node)

    # total records : 10,  only 3 rows are 3-anonymous
    assert math.isclose(70.0, suppression_rate)

    node = LatticeNode([0, 0, 1])
    suppression_rate = anonymity_checker.calculate_suppression_rate(node)

    """
    we generalize age by 1 level. the new dataset should look like:
        01/01/2008,M,15-19 x
        01/01/2008,M,15-19 x
        01/01/2008,M,15-19 x
        01/01/2008,M,10-14
        01/01/2008,M,15-19 x
        02/01/2008,F,15-19
        02/01/2008,F,20-24 x
        02/01/2008,F,20-24 x
        02/01/2008,F,20-24 x
        01/01/2008,M,20-24

        total records: 10, 3-anonymous rows: 7
    """
    assert math.isclose(30.0, suppression_rate)

    node = LatticeNode([2, 1, 4])
    suppression_rate = anonymity_checker.calculate_suppression_rate(node)

    # we generalize everything, suppression rate is 0
    assert math.isclose(0, suppression_rate)

    node = LatticeNode([1, 0, 0])
    """
     dataset looks like:
        JAN_2008,M,18, x
        JAN_2008,M,18, x
        JAN_2008,M,18, x
        JAN_2008,M,13,
        JAN_2008,M,19,
        JAN_2008,F,18,
        JAN_2008,F,22,
        JAN_2008,F,23,
        JAN_2008,F,21,
        JAN_2008,M,22,
    """
    suppression_rate = anonymity_checker.calculate_suppression_rate(node)
    assert math.isclose(70, suppression_rate)
