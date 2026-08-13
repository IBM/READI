from typing import cast

from risk_assessment.anonymization.optimal_lattice_anonymization import AnonymityChecker, Lattice, LatticeNode
from risk_assessment.metrics.informationloss import ColumnClass, ColumnInformation, ColumnType
from risk_assessment.utility.hierarchy import MaterializedHierarchy


def test_lattice_construction():
    date_hierarchy = MaterializedHierarchy(
        [
            ["01/01/2015", "Jan 2015", "2015"],
            ["02/01/2015", "Jan 2015", "2015"],
            ["03/01/2015", "Jan 2015", "2015"],
        ]
    )

    gender_hierarchy = MaterializedHierarchy(
        [
            ["Male", "Person"],
            ["Female", "Person"],
        ]
    )

    age_hierarchy = MaterializedHierarchy(
        [
            ["10", "10-14", "10-19", "0-49", "0-99"],
            ["20", "20-24", "20-29", "0-49", "0-99"],
        ]
    )

    column_information = [
        ColumnInformation(ColumnType.QUASI, ColumnClass.CATEGORICAL, hierarchy=date_hierarchy),
        ColumnInformation(ColumnType.QUASI, ColumnClass.CATEGORICAL, hierarchy=gender_hierarchy),
        ColumnInformation(ColumnType.QUASI, ColumnClass.CATEGORICAL, hierarchy=age_hierarchy),
    ]

    checker: AnonymityChecker = cast(AnonymityChecker, None)

    lattice = Lattice(checker, column_information, 1.0)

    assert 7 == lattice.get_lattice_max_level()

    lattice_map: dict[int, set[LatticeNode]] = lattice.get_lattice()

    assert 1 == len(lattice_map[0])
    assert 3 == len(lattice_map[1])
    assert 5 == len(lattice_map[2])
    assert 6 == len(lattice_map[3])
    assert 6 == len(lattice_map[4])
    assert 5 == len(lattice_map[5])
    assert 3 == len(lattice_map[6])
    assert 1 == len(lattice_map[7])

    height = lattice.get_lattice_max_level() + 1

    for k in range(height):
        nodes = lattice_map[k]

        for node in nodes:
            assert k == node.sum()


def test_matches_maximum_exploration_level():
    node = LatticeNode([1, 1, 1, 3])

    max_levels = [-1, -1, -1, -1]
    assert Lattice.matches_maximum_exploration_level(node, max_levels)

    max_levels = [-1, -1, -1, 2]
    assert not Lattice.matches_maximum_exploration_level(node, max_levels)

    max_levels = [-1, -1, -1, 4]
    assert Lattice.matches_maximum_exploration_level(node, max_levels)

    max_levels = [1, 1, 1, 3]
    assert Lattice.matches_maximum_exploration_level(node, max_levels)


def test_successor():
    date_hierarchy = MaterializedHierarchy(
        [
            ["01/01/2015", "Jan 2015", "2015"],
            ["02/01/2015", "Jan 2015", "2015"],
            ["03/01/2015", "Jan 2015", "2015"],
        ]
    )

    gender_hierarchy = MaterializedHierarchy(
        [
            ["Male", "Person"],
            ["Female", "Person"],
        ]
    )

    age_hierarchy = MaterializedHierarchy(
        [
            ["10", "10-14", "10-19", "0-49", "0-99"],
            ["20", "20-24", "20-29", "0-49", "0-99"],
        ]
    )

    column_information = [
        ColumnInformation(ColumnType.QUASI, ColumnClass.CATEGORICAL, hierarchy=date_hierarchy),
        ColumnInformation(ColumnType.QUASI, ColumnClass.CATEGORICAL, hierarchy=gender_hierarchy),
        ColumnInformation(ColumnType.QUASI, ColumnClass.CATEGORICAL, hierarchy=age_hierarchy),
    ]

    checker: AnonymityChecker = cast(AnonymityChecker, None)

    lattice = Lattice(checker, column_information, 1.0)

    node = LatticeNode([0, 1, 0])

    expected_successors = [
        LatticeNode([0, 1, 1]),
        LatticeNode([1, 1, 0]),
    ]

    successors = lattice.successors(node, True)

    assert 2 == len(list(successors))

    for node in expected_successors:
        assert node in successors
