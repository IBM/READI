from pathlib import Path

import pandas as pd
from pandas.api.types import is_numeric_dtype

from risk_assessment.utility import extract_statistics


def test_basic_information_no_headers():
    with (Path(__file__).parent / "data" / "adult-10-30000.data.csv").open() as input_stream:
        dataset = pd.read_csv(input_stream, header=None)

    information = extract_statistics(dataset)

    assert information is not None

    assert information.size == 30_000
    assert len(information.column_statistics) == 10
    for i in range(10):
        assert information.column_statistics[i].column_name == i
        if is_numeric_dtype(information.column_statistics[i].column_type):
            assert information.column_statistics[i].mean is not None
            assert information.column_statistics[i].std is not None
            assert information.column_statistics[i].median is not None
            assert information.column_statistics[i].histograms is None
            assert information.column_statistics[i].non_null <= 30_000
        else:
            assert information.column_statistics[i].mean is None
            assert information.column_statistics[i].std is None
            assert information.column_statistics[i].median is None
            assert information.column_statistics[i].histograms is not None
            assert information.column_statistics[i].non_null <= 30_000


def test_basic_information_with_headers():
    with (Path(__file__).parent / "data" / "13f496b9-6bd8-42e0-bbfe-44964d3b199e.csv").open() as input_stream:
        dataset = pd.read_csv(input_stream)

    information = extract_statistics(dataset)

    assert information is not None

    assert information.size == 4_000
    assert len(information.column_statistics) == 15
    for i in range(15):
        assert information.column_statistics[i].column_name == dataset.columns[i]
        if is_numeric_dtype(information.column_statistics[i].column_type):
            assert information.column_statistics[i].mean is not None
            assert information.column_statistics[i].std is not None
            assert information.column_statistics[i].median is not None
            assert information.column_statistics[i].histograms is None
            assert information.column_statistics[i].non_null <= 4_000
        else:
            assert information.column_statistics[i].mean is None
            assert information.column_statistics[i].std is None
            assert information.column_statistics[i].median is None
            assert information.column_statistics[i].histograms is not None
            assert information.column_statistics[i].non_null <= 4_000
