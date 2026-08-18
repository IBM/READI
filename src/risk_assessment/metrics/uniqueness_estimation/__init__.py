"""Population uniqueness estimation using the Zayatz hypergeometric estimator.

Provides a statistical estimate of the proportion of records that are unique
in the full population, based on the equivalence-class size distribution
observed in a sample.  This is useful for quantifying re-identification risk
without access to the complete population dataset.

Reference: Zayatz, L. (1991). *Using the Hypergeometric Model for Disclosure
Avoidance*, US Bureau of the Census Statistical Research Division.
"""

from dataclasses import dataclass
from typing import Any

from pandas import DataFrame, Index
from scipy.stats import hypergeom

from risk_assessment.metrics.informationloss import ColumnInformation


def _for_linking(columns: Index, column_information: list[ColumnInformation]) -> list[Any]:
    return [columns[index] for index, c_i in enumerate(column_information) if c_i.for_linking]


@dataclass
class ZayatzEstimatorOptions:
    """Options for the Zayatz population uniqueness estimator.

    Attributes:
        population_size: Total size of the population from which the sample
            was drawn.  Used by the hypergeometric distribution.
    """

    population_size: int


def zayatz_estimator(
    sample: DataFrame, column_information: list[ColumnInformation], options: ZayatzEstimatorOptions
) -> float:
    """Estimate the proportion of population-unique records in *sample*.

    Uses the Zayatz hypergeometric model to infer, from the sample's
    equivalence-class distribution, how many records in the full population
    have a unique combination of linking attributes.

    Args:
        sample: A sample DataFrame.  Linking columns are identified via
            ``column_information``.
        column_information: Per-column metadata; columns with
            ``for_linking=True`` are used for grouping.
        options: Estimator options including the known population size.

    Returns:
        Estimated fraction of records that are unique in the full population.
        Returns 0.0 if no singleton equivalence classes are found in the sample.
    """
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
