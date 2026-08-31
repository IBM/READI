"""Tests for the Flash anonymization algorithm.

Covers:
- FlashOptions dataclass defaults
- _node_priority ordering criteria (c1, c2, c3)
- FlashLattice construction, successor helpers, tagging propagation
- FlashLattice.explore() end-to-end
- Flash.anonymize() happy paths (no suppression, with suppression, l-diversity)
- Flash.anonymize() edge cases (empty dataset, no quasi columns, shape mismatch,
  no suitable generalization)
"""

from __future__ import annotations

import pandas as pd
import pytest

from risk_assessment.anonymization import DistinctLDiversity, KAnonymity
from risk_assessment.anonymization.flash import (
    Flash,
    FlashLattice,
    FlashOptions,
    _node_priority,
)
from risk_assessment.anonymization.optimal_lattice_anonymization import (
    AnonymityChecker,
    LatticeNode,
)
from risk_assessment.metrics.informationloss import (
    ColumnClass,
    ColumnInformation,
    ColumnType,
    categorical_precision,
)
from risk_assessment.utility.hierarchy import MaterializedHierarchy
from risk_assessment.utility.hierarchy.datatypes import DummyHierarchy

# ---------------------------------------------------------------------------
# Shared helpers / fixtures
# ---------------------------------------------------------------------------


def _date_hierarchy():
    return MaterializedHierarchy(
        [
            ["01/01/2008", "Jan_2008", "2008"],
            ["02/01/2008", "Jan_2008", "2008"],
            ["03/01/2008", "Jan_2008", "2008"],
        ]
    )


def _gender_hierarchy():
    return MaterializedHierarchy(
        [
            ["M", "Person"],
            ["F", "Person"],
        ]
    )


def _age_hierarchy():
    return MaterializedHierarchy(
        [
            ["13", "10-14", "10-19", "0-49", "0-99"],
            ["18", "15-19", "10-19", "0-49", "0-99"],
            ["19", "15-19", "10-19", "0-49", "0-99"],
            ["21", "20-24", "20-29", "0-49", "0-99"],
            ["22", "20-24", "20-29", "0-49", "0-99"],
            ["23", "20-24", "20-29", "0-49", "0-99"],
        ]
    )


def _three_col_info():
    return [
        ColumnInformation(ColumnType.QUASI, ColumnClass.CATEGORICAL, hierarchy=_date_hierarchy()),
        ColumnInformation(ColumnType.QUASI, ColumnClass.CATEGORICAL, hierarchy=_gender_hierarchy()),
        ColumnInformation(ColumnType.QUASI, ColumnClass.CATEGORICAL, hierarchy=_age_hierarchy()),
    ]


def _sample_dataset():
    rows = [
        "01/01/2008,M,18",
        "01/01/2008,M,18",
        "01/01/2008,M,18",
        "01/01/2008,M,13",
        "01/01/2008,M,19",
        "02/01/2008,F,18",
        "02/01/2008,F,22",
        "02/01/2008,F,23",
        "02/01/2008,F,21",
        "01/01/2008,M,22",
    ]
    df = pd.DataFrame([r.split(",") for r in rows])
    df.rename(columns={i: f"col_{i}" for i in range(3)}, inplace=True)
    return df


def _make_single_qi_lattice(k=2):
    """FlashLattice with one categorical quasi-identifier (gender, 2 levels)."""
    col_info = [
        ColumnInformation(ColumnType.QUASI, ColumnClass.CATEGORICAL, hierarchy=_gender_hierarchy()),
    ]
    dataset = pd.DataFrame({"sex": ["M", "F", "M", "F"]})
    checker = AnonymityChecker(dataset, col_info, [KAnonymity(k)], categorical_precision)
    return FlashLattice(checker, col_info, 0.0)


def _make_three_qi_lattice():
    """FlashLattice with three categorical quasi-identifiers."""
    col_info = _three_col_info()
    dataset = pd.DataFrame(
        [["01/01/2008", "M", "18"], ["02/01/2008", "F", "22"]],
        columns=["date", "sex", "age"],
    )
    checker = AnonymityChecker(dataset, col_info, [KAnonymity(2)], categorical_precision)
    return FlashLattice(checker, col_info, 0.0)


# ---------------------------------------------------------------------------
# FlashOptions
# ---------------------------------------------------------------------------


def test_flash_options_default_suppression():
    opts = FlashOptions(privacy_constraints=[KAnonymity(2)])
    assert opts.suppression == 0.0


def test_flash_options_default_information_loss():
    opts = FlashOptions(privacy_constraints=[KAnonymity(2)])
    assert opts.information_loss is categorical_precision


def test_flash_options_custom_suppression():
    opts = FlashOptions(privacy_constraints=[KAnonymity(2)], suppression=10.0)
    assert opts.suppression == 10.0


# ---------------------------------------------------------------------------
# _node_priority
# ---------------------------------------------------------------------------

# Two quasi-identifiers: max_levels=[1, 3], distinct_counts=[[2,1],[4,2,1,1]]
_MAX_LEVELS = [1, 3]
_DISTINCT_COUNTS = [[2, 1], [4, 2, 1, 1]]


def test_node_priority_c1_equals_sum_of_levels():
    node = LatticeNode([1, 2])
    c1, _, _ = _node_priority(node, _MAX_LEVELS, _DISTINCT_COUNTS)
    assert c1 == 3


def test_node_priority_bottom_node_all_zeros():
    node = LatticeNode([0, 0])
    c1, c2, c3 = _node_priority(node, _MAX_LEVELS, _DISTINCT_COUNTS)
    assert c1 == 0
    assert c2 == 0.0
    assert c3 == 0.0


def test_node_priority_more_general_has_higher_c1():
    low = LatticeNode([0, 1])
    high = LatticeNode([1, 2])
    assert _node_priority(low, _MAX_LEVELS, _DISTINCT_COUNTS) < _node_priority(high, _MAX_LEVELS, _DISTINCT_COUNTS)


def test_node_priority_empty_node_returns_zeros():
    assert _node_priority(LatticeNode([]), [], []) == (0, 0.0, 0.0)


def test_node_priority_same_c1_differentiates_by_c2():
    # [1,0]: c2 = (1/1 + 0/3)/2 = 0.5
    # [0,1]: c2 = (0/1 + 1/3)/2 ≈ 0.167
    n1 = LatticeNode([1, 0])
    n2 = LatticeNode([0, 1])
    p1 = _node_priority(n1, _MAX_LEVELS, _DISTINCT_COUNTS)
    p2 = _node_priority(n2, _MAX_LEVELS, _DISTINCT_COUNTS)
    assert p1[0] == p2[0]  # same c1
    assert p1[1] > p2[1]  # n1 has higher c2, comes later in traversal


# ---------------------------------------------------------------------------
# FlashLattice — successor helpers
# ---------------------------------------------------------------------------


def test_successors_up_from_bottom_yields_one_per_qi():
    lattice = _make_three_qi_lattice()
    bottom = lattice._node_map[hash(LatticeNode([0, 0, 0]))]
    ups = lattice._successors_up(bottom)
    assert len(ups) == 3
    for n in ups:
        assert n.sum() == 1


def test_successors_up_from_top_is_empty():
    lattice = _make_three_qi_lattice()
    top_values = list(lattice._max_levels)
    top = lattice._node_map[hash(LatticeNode(top_values))]
    assert lattice._successors_up(top) == []


def test_successors_down_from_above_bottom():
    lattice = _make_three_qi_lattice()
    node = lattice._node_map[hash(LatticeNode([1, 0, 0]))]
    downs = lattice._successors_down(node)
    assert len(downs) == 1
    assert downs[0].values == [0, 0, 0]


def test_successors_down_from_bottom_is_empty():
    lattice = _make_three_qi_lattice()
    bottom = lattice._node_map[hash(LatticeNode([0, 0, 0]))]
    assert lattice._successors_down(bottom) == []


def test_successors_are_sorted_by_priority():
    lattice = _make_three_qi_lattice()
    bottom = lattice._node_map[hash(LatticeNode([0, 0, 0]))]
    ups = lattice._successors_up(bottom)
    priorities = [lattice._priority(n) for n in ups]
    assert priorities == sorted(priorities)


# ---------------------------------------------------------------------------
# FlashLattice — tagging propagation
# ---------------------------------------------------------------------------


def test_tag_upward_marks_all_generalizations_anonymous():
    lattice = _make_single_qi_lattice()
    bottom = lattice._node_map[hash(LatticeNode([0]))]
    bottom.is_anonymous = True
    bottom.tagged = True
    lattice._tag_upward(bottom)
    top = lattice._node_map[hash(LatticeNode([1]))]
    assert top.tagged
    assert top.is_anonymous is True


def test_tag_downward_marks_all_specializations_not_anonymous():
    lattice = _make_single_qi_lattice()
    top = lattice._node_map[hash(LatticeNode([1]))]
    top.is_anonymous = False
    top.tagged = True
    lattice._tag_downward(top)
    bottom = lattice._node_map[hash(LatticeNode([0]))]
    assert bottom.tagged
    assert bottom.is_anonymous is False


def test_tag_upward_does_not_retag_already_tagged_nodes():
    lattice = _make_single_qi_lattice()
    top = lattice._node_map[hash(LatticeNode([1]))]
    top.tagged = True
    top.is_anonymous = False  # pre-tagged as non-anonymous

    bottom = lattice._node_map[hash(LatticeNode([0]))]
    bottom.is_anonymous = True
    bottom.tagged = True
    lattice._tag_upward(bottom)

    # top was already tagged — its is_anonymous must not be overwritten
    assert top.is_anonymous is False


# ---------------------------------------------------------------------------
# FlashLattice.explore()
# ---------------------------------------------------------------------------


def test_explore_finds_optimal_node():
    lattice = _make_single_qi_lattice(k=2)
    lattice.explore()
    optimal = lattice.optimal_node()
    assert optimal is not None
    assert optimal.is_anonymous is True


def test_explore_tags_all_nodes():
    lattice = _make_single_qi_lattice(k=2)
    lattice.explore()
    for nodes in lattice._lattice.values():
        for node in nodes:
            assert node.tagged, f"Node {node} was not tagged after explore()"


def test_explore_impossible_k_yields_no_optimal_node():
    col_info = [
        ColumnInformation(ColumnType.QUASI, ColumnClass.CATEGORICAL, hierarchy=_gender_hierarchy()),
    ]
    dataset = pd.DataFrame({"sex": ["M", "F"]})
    checker = AnonymityChecker(dataset, col_info, [KAnonymity(100)], categorical_precision)
    lattice = FlashLattice(checker, col_info, 0.0)
    lattice.explore()
    assert lattice.optimal_node() is None


# ---------------------------------------------------------------------------
# Flash.anonymize() — happy paths
# ---------------------------------------------------------------------------


def test_flash_k2_no_suppression():
    dataset = _sample_dataset()
    col_info = _three_col_info()
    flash = Flash(FlashOptions([KAnonymity(2)], suppression=0.0))
    anonymized, report = flash.anonymize(dataset, col_info)

    assert report.anonymized
    assert report.suppression_rate == 0.0
    assert report.generalization_levels is not None

    quasi_cols = [dataset.columns[i] for i, c in enumerate(col_info) if c.column_type == ColumnType.QUASI]
    for size in anonymized.groupby(quasi_cols).size():
        assert size >= 2


def test_flash_k3_with_suppression():
    dataset = _sample_dataset()
    col_info = _three_col_info()
    flash = Flash(FlashOptions([KAnonymity(3)], suppression=20.0))
    anonymized, report = flash.anonymize(dataset, col_info)

    assert report.anonymized
    assert report.suppression_rate <= 20.0
    assert len(anonymized) >= 0.8 * len(dataset)

    quasi_cols = [dataset.columns[i] for i, c in enumerate(col_info) if c.column_type == ColumnType.QUASI]
    for size in anonymized.groupby(quasi_cols).size():
        assert size >= 3


def test_flash_named_columns():
    col_info = _three_col_info()
    dataset = pd.DataFrame(
        {
            "date": ["01/01/2008"] * 5 + ["02/01/2008"] * 5,
            "sex": ["M"] * 5 + ["F"] * 5,
            "age": ["18", "18", "18", "13", "19", "18", "22", "23", "21", "22"],
        }
    )
    flash = Flash(FlashOptions([KAnonymity(3)], suppression=20.0))
    anonymized, report = flash.anonymize(dataset, col_info)
    assert report.anonymized
    assert len(anonymized) >= 0.8 * len(dataset)


def test_flash_k_anonymity_and_l_diversity():
    col_info = [
        ColumnInformation(ColumnType.QUASI, ColumnClass.CATEGORICAL, hierarchy=_date_hierarchy()),
        ColumnInformation(ColumnType.QUASI, ColumnClass.CATEGORICAL, hierarchy=_gender_hierarchy()),
        ColumnInformation(ColumnType.QUASI, ColumnClass.CATEGORICAL, hierarchy=_age_hierarchy()),
        ColumnInformation(ColumnType.SENSITIVE),
    ]
    rows = [
        "01/01/2008,M,18,Cancer",
        "01/01/2008,M,18,Cancer",
        "01/01/2008,M,18,HIV",
        "01/01/2008,M,13,HIV",
        "01/01/2008,M,19,HIV",
        "02/01/2008,F,18,Pneumonia",
        "02/01/2008,F,22,Pneumonia",
        "02/01/2008,F,23,Pneumonia",
        "02/01/2008,F,21,Flu",
        "01/01/2008,M,22,Flu",
    ]
    df = pd.DataFrame([r.split(",") for r in rows])
    df.rename(columns={i: f"col_{i}" for i in range(4)}, inplace=True)

    flash = Flash(FlashOptions([KAnonymity(3), DistinctLDiversity(2)], suppression=20.0))
    anonymized, report = flash.anonymize(df, col_info)

    assert report.anonymized
    assert report.suppression_rate <= 20.0
    assert len(anonymized) >= 0.8 * len(df)


def test_flash_single_quasi_column():
    col_info = [
        ColumnInformation(ColumnType.QUASI, ColumnClass.CATEGORICAL, hierarchy=_gender_hierarchy()),
        ColumnInformation(ColumnType.SENSITIVE),
    ]
    dataset = pd.DataFrame({"sex": ["M", "F", "M", "F"], "disease": ["A", "B", "A", "B"]})
    flash = Flash(FlashOptions([KAnonymity(2)], suppression=0.0))
    anonymized, report = flash.anonymize(dataset, col_info)
    assert report.anonymized
    assert len(anonymized) == len(dataset)


def test_flash_output_preserves_all_columns():
    dataset = _sample_dataset()
    col_info = _three_col_info()
    flash = Flash(FlashOptions([KAnonymity(2)]))
    anonymized, _ = flash.anonymize(dataset, col_info)
    assert list(anonymized.columns) == list(dataset.columns)


# ---------------------------------------------------------------------------
# Flash.anonymize() — edge cases
# ---------------------------------------------------------------------------


def test_flash_empty_dataset_returns_false_report():
    col_info = _three_col_info()
    empty_df = pd.DataFrame(columns=["date", "sex", "age"])
    flash = Flash(FlashOptions([KAnonymity(2)]))
    _, report = flash.anonymize(empty_df, col_info)
    assert not report.anonymized


def test_flash_column_count_mismatch_raises_value_error():
    dataset = _sample_dataset()
    col_info = [ColumnInformation(ColumnType.QUASI, ColumnClass.CATEGORICAL, hierarchy=DummyHierarchy())]
    flash = Flash(FlashOptions([KAnonymity(2)]))
    with pytest.raises(ValueError):
        flash.anonymize(dataset, col_info)


def test_flash_no_quasi_columns_returns_original_unchanged():
    dataset = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
    col_info = [ColumnInformation(ColumnType.SENSITIVE), ColumnInformation(ColumnType.SENSITIVE)]
    flash = Flash(FlashOptions([KAnonymity(2)]))
    anonymized, report = flash.anonymize(dataset, col_info)
    assert report.anonymized
    assert report.generalization_levels == []
    assert len(anonymized) == len(dataset)


def test_flash_raises_when_no_suitable_generalization():
    col_info = [
        ColumnInformation(ColumnType.QUASI, ColumnClass.CATEGORICAL, hierarchy=_gender_hierarchy()),
    ]
    dataset = pd.DataFrame({"sex": ["M", "F", "M"]})
    flash = Flash(FlashOptions([KAnonymity(100)], suppression=0.0))
    with pytest.raises(RuntimeError):
        flash.anonymize(dataset, col_info)


# ---------------------------------------------------------------------------
# FlashLattice — missing hierarchy raises ValueError
# ---------------------------------------------------------------------------


def test_flash_lattice_raises_on_missing_hierarchy():
    col_info = [ColumnInformation(ColumnType.QUASI, ColumnClass.CATEGORICAL)]  # no hierarchy
    dataset = pd.DataFrame({"sex": ["M", "F"]})
    checker = AnonymityChecker(dataset, col_info, [KAnonymity(2)], categorical_precision)
    with pytest.raises(ValueError, match="Missing hierarchy"):
        FlashLattice(checker, col_info, 0.0)


# ---------------------------------------------------------------------------
# _store — global optimum replacement branches
# ---------------------------------------------------------------------------


def test_flash_lattice_store_replaces_with_lower_level():
    lattice = _make_single_qi_lattice(k=2)
    # Set a high-level global optimum manually
    lattice._global_optimum = LatticeNode([1], information_loss=0.5, is_anonymous=True)
    # A lower-level candidate should replace it
    better = LatticeNode([0], information_loss=0.5, is_anonymous=True)
    lattice._store(better)
    assert lattice._global_optimum is better


def test_flash_lattice_store_replaces_on_same_level_lower_loss():
    lattice = _make_single_qi_lattice(k=2)
    lattice._global_optimum = LatticeNode([1], information_loss=0.8, is_anonymous=True)
    same_level_better = LatticeNode([1], information_loss=0.2, is_anonymous=True)
    lattice._store(same_level_better)
    assert lattice._global_optimum is same_level_better


def test_flash_lattice_store_does_not_replace_on_same_level_higher_loss():
    lattice = _make_single_qi_lattice(k=2)
    original = LatticeNode([1], information_loss=0.2, is_anonymous=True)
    lattice._global_optimum = original
    worse = LatticeNode([1], information_loss=0.9, is_anonymous=True)
    lattice._store(worse)
    assert lattice._global_optimum is original


# ---------------------------------------------------------------------------
# Flash.anonymize() with active suppression (drops violating partitions)
# ---------------------------------------------------------------------------


def test_flash_anonymize_with_suppression_drops_small_partitions():
    """Force the suppression branch in _anonymize_with_suppression."""
    col_info = [
        ColumnInformation(ColumnType.QUASI, ColumnClass.CATEGORICAL, hierarchy=_gender_hierarchy()),
    ]
    # 5 M, 1 F → k=3 forces suppression of the lone-F partition
    dataset = pd.DataFrame({"sex": ["M", "M", "M", "M", "M", "F"]})
    flash = Flash(FlashOptions([KAnonymity(3)], suppression=30.0))
    anonymized, report = flash.anonymize(dataset, col_info)
    assert report.anonymized
    assert len(anonymized) < len(dataset)  # the F row(s) were suppressed
