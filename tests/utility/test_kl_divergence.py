import math

import numpy as np
from pandas import Series

from risk_assessment.utility import kl_divergence


def test_same_distribution():
    P = [0.05, 0.1, 0.2, 0.05, 0.15, 0.25, 0.08, 0.12]

    assert 0 == kl_divergence(Series(P), Series(P))


def test_different_distributions():
    P = [0.05, 0.1, 0.2, 0.05, 0.15, 0.25, 0.08, 0.12]
    Q = [0.3, 0.1, 0.2, 0.1, 0.1, 0.02, 0.08, 0.1]

    assert math.isclose(kl_divergence(Series(P), Series(Q)), 0.589885181619163)


def test_nan_value():
    P = [0.05, 0.1, 0.2, 0.05, 0.15, 0.25, 0.08, 0.12]
    Q = [0.3, math.nan, 0.2, 0.1, 0.1, 0.02, 0.08, 0.1]

    assert kl_divergence(Series(P), Series(Q)) == np.inf


def test_missing_value():
    P = [0.05, 0.1, 0.2, 0.05, 0.15, 0.25, 0.08, 0.12]
    Q = [0.3, 0.2, 0.1, 0.1, 0.02, 0.08, 0.1]

    assert kl_divergence(Series(P, index=list(range(len(P)))), Series(Q, index=[0, 2, 3, 4, 5, 6, 7])) == np.inf
