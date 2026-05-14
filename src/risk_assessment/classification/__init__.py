from collections import defaultdict
from dataclasses import dataclass
from typing import Any, cast

from pandas import DataFrame

from risk_assessment.classification.classification_strategy import (
    DatasetClassificationStrategy,
    FrequencyBasedDatasetClassificationStrategy,
)
from risk_assessment.classification.identifiers import Identifier


def create_instance(identifier_fqn: str) -> Identifier:
    parts = identifier_fqn.split(".")
    module_name = ".".join(parts[:-1])
    module = __import__(module_name)
    for comp in parts[1:]:
        module = getattr(module, comp)

    if type(module) is type(Identifier):
        m = module()
        return cast(Identifier, m)

    raise ValueError(
        f"{identifier_fqn} does not exists or is not a subclass of `risk_assessment.classification.identifiers.Identifier`"
    )


def create_instance_if_required(identifier: Identifier | str) -> Identifier:
    if isinstance(identifier, Identifier):
        return identifier
    else:
        return create_instance(identifier)


def build_identifiers(specs: list[Identifier | str]) -> list[Identifier]:
    return [create_instance_if_required(identifier) for identifier in specs]


class DatasetClassificationConfiguration:
    def __init__(
        self,
        identifiers: list[Identifier | str],
        strategy: DatasetClassificationStrategy = FrequencyBasedDatasetClassificationStrategy(),
        mark_unknown: bool = True,
        unknonw_type: str = "UNKNOWN",
    ) -> None:
        self.identifiers = build_identifiers(identifiers)
        self.strategy = strategy
        self.mark_unknown = mark_unknown
        self.unknown_type = unknonw_type


@dataclass
class DatasetClassificationReport:
    best_types: dict[str, str]
    reports: dict[str, dict[str, float]]
    size: int
    ordered_column_names: list[str]


class DatasetClassification:
    def __init__(self, configuration: DatasetClassificationConfiguration):
        self.configuration = configuration

    def classify(self, dataset: DataFrame) -> DatasetClassificationReport:
        best_types: dict[str, str] = {}
        reports: dict[str, dict[str, float]] = {}
        size = len(dataset)
        for column_name in dataset.columns:
            (column_best_type, column_full_report) = self.analyze_column(dataset[column_name], size)
            best_types[column_name] = column_best_type
            reports[column_name] = column_full_report

        return DatasetClassificationReport(best_types, reports, size, list(dataset.columns))

    def compute_raw_report(self, column_values: list[Any]) -> dict[str, int]:
        counts: dict[str, int] = defaultdict(int)

        for value in column_values:
            value = str(value)
            identified: bool = False
            for identifier in self.configuration.identifiers:
                if identifier.is_of_this_type(value):
                    identified = True
                    counts[str(identifier)] += 1
            if self.configuration.mark_unknown and not identified:
                counts[self.configuration.unknown_type] += 1

        return counts

    def normalize_results(self, raw_counts: dict[str, int], size: int) -> dict[str, float]:
        return {key: (value / size) for key, value in raw_counts.items()}

    def analyze_column(self, column_values: list[Any], size: int) -> tuple[str, dict[str, float]]:
        raw_counts = self.compute_raw_report(column_values)
        report = self.normalize_results(raw_counts, size)
        column_best_type = self.configuration.strategy.find_best_type(raw_counts, size)

        return (column_best_type, report)
