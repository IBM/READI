import csv
from pathlib import Path
from random import randint

import pandas as pd
import pytest

from risk_assessment.utility import extract_histograms, kl_divergence


@pytest.mark.skip("Data file missing in repo")
def test_samples(tmp_path: Path) -> None:
    with (Path(__file__).parent / "data" / "florida_link.txt").open() as iostream:
        dataset = pd.read_csv(iostream, header=None)

    original_histograms = [extract_histograms(dataset[column]) for column in dataset.columns]

    with (tmp_path / "histogram_scores.csv").open("w") as outfile:
        writer = csv.writer(outfile, quoting=csv.QUOTE_MINIMAL)
        for _ in range(500):
            sample = dataset.sample(randint(10_000, len(dataset)))
            sample_histograms = [extract_histograms(sample[column]) for column in sample.columns]

            writer.writerow(
                [len(sample)] + [kl_divergence(sh, oh) for sh, oh in zip(sample_histograms, original_histograms)]
            )
