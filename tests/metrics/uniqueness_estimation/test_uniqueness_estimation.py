import math

from pandas import DataFrame  # type: ignore

from risk_assessment.metrics.informationloss import ColumnClass, ColumnInformation, ColumnType
from risk_assessment.metrics.uniqueness_estimation import ZayatzEstimatorOptions, zayatz_estimator
from risk_assessment.utility.hierarchy.datatypes.yob import YOBHierarchy


def _generate_random_sample(equivalence_classes: dict[int, int]) -> DataFrame:
    index = 0

    data: list[list[int]] = []

    for eq_size, counter in equivalence_classes.items():
        for _ in range(counter):
            for _ in range(eq_size):
                data.append([index])
            index += 1

    return DataFrame(data)


def _sample(population: DataFrame, size: int) -> DataFrame:
    return population.sample(size)


def test_correctness_zayatz():
    # Context:
    # N = 56372 be the population size, 22026 unique records
    # n = 9383 be the sample size

    population_size = 56_372
    sample_size = 9383

    original_equivalence_sizes: dict[int, int] = {
        1: 22026,
        2: 2954,
        3: 1090,
        4: 560,
        5: 354,
        6: 223,
        7: 173,
        8: 109,
        9: 106,
        10: 87,
        11: 64,
        12: 53,
        13: 54,
        14: 48,
        15: 26,
        16: 37,
        17: 25,
        18: 14,
        19: 21,
        20: 16,
        21: 18,
        22: 12,
        23: 23,
        24: 18,
        25: 15,
        26: 11,
        27: 9,
        28: 7,
        29: 7,
        30: 9,
        31: 8,
        32: 12,
        33: 5,
        34: 7,
        35: 6,
        36: 8,
        37: 7,
        38: 3,
        39: 4,
        40: 3,
        41: 6,
        42: 5,
        43: 2,
        44: 1,
        45: 4,
        46: 6,
        47: 3,
        48: 3,
        49: 1,
        50: 2,
        51: 2,
        52: 3,
        53: 3,
        54: 1,
        55: 4,
        56: 1,
        57: 2,
        58: 2,
        59: 1,
        60: 4,
    }

    population_data = _generate_random_sample(original_equivalence_sizes)
    sample_data = _sample(population_data, sample_size)

    estimate = zayatz_estimator(
        sample_data,
        [ColumnInformation(ColumnType.QUASI, ColumnClass.CATEGORICAL, hierarchy=YOBHierarchy(), for_linking=True)],
        ZayatzEstimatorOptions(population_size),
    )

    estimated_ratio = estimate / population_size
    real_ratio = 22026 / population_size
    assert math.isclose(
        estimated_ratio, real_ratio, abs_tol=0.1
    ), f"{estimated_ratio} not close to {real_ratio} by {abs(estimated_ratio - real_ratio)}"
