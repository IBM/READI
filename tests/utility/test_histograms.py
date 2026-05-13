import math

from pandas import DataFrame

from risk_assessment.utility import extract_histograms


def test_histograms_correctness():
    dataset = DataFrame(
        data=[
            [1],
            [1],
            [1],
            [2],
            [2],
            [3],
        ],
    )

    histogram = extract_histograms(dataset)

    assert len(histogram) == 3

    correct_values = {
        1: 3,
        2: 2,
        3: 1,
    }

    for key, value in zip(histogram.index, histogram.values):
        assert correct_values[key[0]] == value


def test_histograms_normalized():
    dataset = DataFrame(
        data=[
            [1],
            [1],
            [1],
            [2],
            [2],
            [3],
        ],
    )

    histogram = extract_histograms(dataset, True)

    assert len(histogram) == 3

    correct_values = {
        1: 3 / len(dataset),
        2: 2 / len(dataset),
        3: 1 / len(dataset),
    }

    for key, value in zip(histogram.index, histogram.values):
        assert math.isclose(correct_values[key[0]], value)
