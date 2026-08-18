import pytest
from pandas import Series

from risk_assessment.utility.hierarchy import NumericalRange
from risk_assessment.utility.hierarchy.datatypes import DummyHierarchy
from risk_assessment.utility.hierarchy.datatypes.numeric import GeneralizationType, NumericalHierarchy


def test_dummy_hierarchy_encode_and_not_implemented_methods():
    hierarchy = DummyHierarchy()

    assert hierarchy.encode("value", 0) == "value"
    assert hierarchy.encode("value", 1) == "*"

    with pytest.raises(NotImplementedError):
        hierarchy["value"]

    with pytest.raises(NotImplementedError):
        len(hierarchy)

    with pytest.raises(NotImplementedError):
        hierarchy.index_for_value("value")

    with pytest.raises(NotImplementedError):
        hierarchy.leaves_for_node("value")

    with pytest.raises(NotImplementedError):
        hierarchy.node_level("value")


def test_numerical_hierarchy_range_generalization_and_levels():
    hierarchy = NumericalHierarchy(NumericalRange(Series([0.0, 4.0, 8.0])), 3, GeneralizationType.RANGE)

    assert hierarchy.top_term == "0.0:8.0"
    assert len(hierarchy) == 3
    assert hierarchy.encode(4.0, 0) == "4.0"
    assert hierarchy.encode(4.0, 1) == "2.0:4.0"
    assert hierarchy.encode(4.0, 2) == "0.0:4.0"
    assert hierarchy.encode(4.0, 3) == "0.0:8.0"
    assert hierarchy.node_level("4.0") == 0
    assert hierarchy.node_level("0.0:4.0") == 2
    assert hierarchy.gcd(8.0, 4.0) == 4.0


def test_numerical_hierarchy_mean_generalization_and_invalid_type():
    hierarchy = NumericalHierarchy(NumericalRange(Series([0.0, 4.0, 8.0])), 3, GeneralizationType.MEAN)

    assert hierarchy.top_term == "4.0"
    assert hierarchy.encode(4.0, 1) == "3.0"
    assert hierarchy.encode(4.0, 2) == "2.0"
    assert hierarchy.node_level("2.0") == 2

    with pytest.raises(ValueError, match="Support for range and mean at the moment"):
        NumericalHierarchy(NumericalRange(Series([0.0, 1.0])), 2, None)  # ty: ignore


def test_numerical_hierarchy_not_implemented_methods():
    hierarchy = NumericalHierarchy(NumericalRange(Series([0.0, 4.0, 8.0])), 3, GeneralizationType.RANGE)

    with pytest.raises(NotImplementedError):
        hierarchy.leaves_for_node("0.0:8.0")

    with pytest.raises(NotImplementedError):
        hierarchy.index_for_value(4.0)

    with pytest.raises(NotImplementedError):
        hierarchy["0.0:8.0"]
