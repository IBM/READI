import math

import numpy as np
from pandas import Series

from risk_assessment.utility import js_divergence


def test_same_distribution():
    P = [0.05, 0.1, 0.2, 0.05, 0.15, 0.25, 0.08, 0.12]

    assert 0 == js_divergence(Series(P), Series(P))


def test_simmetrical():
    P = [0.05, 0.1, 0.2, 0.05, 0.15, 0.25, 0.08, 0.12]
    Q = [0.3, 0.1, 0.2, 0.1, 0.1, 0.02, 0.08, 0.1]

    assert js_divergence(Series(P), Series(Q)) == js_divergence(Series(Q), Series(P))


def test_different_distributions():
    P = [0.05, 0.1, 0.2, 0.05, 0.15, 0.25, 0.08, 0.12]
    Q = [0.3, 0.1, 0.2, 0.1, 0.1, 0.02, 0.08, 0.1]

    assert math.isclose(js_divergence(Series(P), Series(Q)), 0.11467783201953419)


def test_nan_value():
    P = [0.05, 0.1, 0.2, 0.05, 0.15, 0.25, 0.08, 0.12]
    Q = [0.3, math.nan, 0.2, 0.1, 0.1, 0.02, 0.08, 0.1]

    assert js_divergence(Series(P), Series(Q)) is not np.inf


def test_missing_value():
    P = [0.05, 0.1, 0.2, 0.05, 0.15, 0.25, 0.08, 0.12]
    Q = [0.3, 0.2, 0.1, 0.1, 0.02, 0.08, 0.1]

    assert js_divergence(Series(P, index=list(range(len(P)))), Series(Q, index=[0, 2, 3, 4, 5, 6, 7])) != np.inf
