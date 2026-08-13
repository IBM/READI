from dataclasses import dataclass
from typing import Any

from pandas import DataFrame, Index
from scipy.stats import hypergeom

from risk_assessment.metrics.informationloss import ColumnInformation


def _for_linking(columns: Index, column_information: list[ColumnInformation]) -> list[Any]:
    return [columns[index] for index, c_i in enumerate(column_information) if c_i.for_linking]


@dataclass
class ZayatzEstimatorOptions:
    population_size: int


def zayatz_estimator(
    sample: DataFrame, column_information: list[ColumnInformation], options: ZayatzEstimatorOptions
) -> float:
    sum = 0.0

    equivalence_class_sizes: dict[int, int] = {}

    for partition_size in sample.groupby(by=_for_linking(sample.columns, column_information)).size():
        if partition_size in equivalence_class_sizes:
            equivalence_class_sizes[partition_size] += 1
        else:
            equivalence_class_sizes[partition_size] = 1

    if 1 not in equivalence_class_sizes:
        return 0.0

    outliers = equivalence_class_sizes[1]

    number_equivalence_classes = len(equivalence_class_sizes)

    for size, count in equivalence_class_sizes.items():
        distribution = hypergeom(options.population_size, size, len(sample))
        sum += distribution.pmf(1) * (count / number_equivalence_classes)

    distribution = hypergeom(options.population_size, 1, len(sample))
    probability = ((outliers / number_equivalence_classes) * distribution.pmf(1)) / sum

    return (probability * outliers) / (len(sample) / options.population_size)
