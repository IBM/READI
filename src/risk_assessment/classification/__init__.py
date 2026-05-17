"""Dataset classification module for identifying sensitive data types in structured data.

This module provides tools for classifying columns in datasets (e.g., pandas DataFrames)
by identifying the types of sensitive data they contain, such as emails, phone numbers,
credit cards, and other PII/PHI identifiers.
"""

from collections import defaultdict
from contextlib import suppress
from dataclasses import dataclass
from typing import Any, cast

from pandas import DataFrame, Series

from risk_assessment.classification.classification_strategy import (
    DatasetClassificationStrategy,
    FrequencyBasedDatasetClassificationStrategy,
)
from risk_assessment.classification.identifiers import Identifier


def create_instance(identifier_fqn: str) -> Identifier:
    """Create an identifier instance from a fully qualified name.

    Dynamically imports and instantiates an identifier class from its
    fully qualified name string.

    Args:
        identifier_fqn: Fully qualified name of the identifier class
            (e.g., "risk_assessment.classification.identifiers.Email").

    Returns:
        An instance of the specified identifier class.

    Raises:
        ValueError: If the identifier doesn't exist or is not a subclass of Identifier.

    Example:
        >>> identifier = create_instance("risk_assessment.classification.identifiers.Email")
        >>> print(type(identifier).__name__)
        'Email'
    """
    parts = identifier_fqn.split(".")
    module_name = ".".join(parts[:-1])
    module = __import__(module_name)
    for comp in parts[1:]:
        module = getattr(module, comp)

    # Verify that module is a class (type) and is a subclass of Identifier
    if not isinstance(module, type):
        raise ValueError(
            f"{identifier_fqn} is not a class. "
            "Expected a subclass of `risk_assessment.classification.identifiers.Identifier`, "
            f"but got {type(module).__name__}"
        )

    try:
        if issubclass(module, Identifier):
            return module()
    except TypeError as e:
        # issubclass() raises TypeError if module is not a class (shouldn't happen due to isinstance check above)
        raise ValueError(f"{identifier_fqn} cannot be checked as a subclass: {e}") from e

    raise ValueError(
        f"{identifier_fqn} is not a subclass of `risk_assessment.classification.identifiers.Identifier`. "
        f"Found class: {module.__name__}"
    )


def create_instance_if_required(identifier: Identifier | str) -> Identifier:
    """Create an identifier instance if a string is provided, otherwise return as-is.

    This is a convenience function that accepts either an identifier instance
    or a fully qualified name string and ensures an instance is returned.

    Args:
        identifier: Either an Identifier instance or a fully qualified name string.

    Returns:
        An Identifier instance.

    Example:
        >>> from risk_assessment.classification.identifiers import Email
        >>> # Using an instance
        >>> email = Email()
        >>> result = create_instance_if_required(email)
        >>> # Using a string
        >>> result = create_instance_if_required("risk_assessment.classification.identifiers.Email")
    """
    if isinstance(identifier, Identifier):
        return identifier
    else:
        return create_instance(identifier)


def build_identifiers(specs: list[Identifier | str]) -> list[Identifier]:
    """Build a list of identifier instances from a mixed list of instances and strings.

    Args:
        specs: List containing Identifier instances and/or fully qualified name strings.

    Returns:
        List of Identifier instances.

    Example:
        >>> from risk_assessment.classification.identifiers import Email
        >>> specs = [Email(), "risk_assessment.classification.identifiers.Phone"]
        >>> identifiers = build_identifiers(specs)
        >>> len(identifiers)
        2
    """
    return [create_instance_if_required(identifier) for identifier in specs]


class DatasetClassificationConfiguration:
    """Configuration for dataset classification.

    This class holds the configuration for classifying dataset columns,
    including which identifiers to use, the classification strategy,
    and how to handle unknown values.

    Attributes:
        identifiers: List of Identifier instances to use for classification.
        strategy: Classification strategy to determine the best type for each column.
        mark_unknown: Whether to mark unidentified values as "UNKNOWN".
        unknown_type: The label to use for unknown/unidentified values.

    Example:
        >>> from risk_assessment.classification.identifiers import Email, Phone
        >>> config = DatasetClassificationConfiguration(
        ...     identifiers=[Email(), Phone()],
        ...     mark_unknown=True,
        ...     unknown_type="UNKNOWN"
        ... )
    """

    def __init__(
        self,
        identifiers: list[Identifier | str],
        strategy: DatasetClassificationStrategy = FrequencyBasedDatasetClassificationStrategy(),
        mark_unknown: bool = True,
        unknown_type: str = "UNKNOWN",
    ) -> None:
        """Initialize the classification configuration.

        Args:
            identifiers: List of Identifier instances or fully qualified name strings.
            strategy: Classification strategy to use (default: frequency-based).
            mark_unknown: Whether to mark unidentified values as unknown (default: True).
            unknown_type: Label for unknown values (default: "UNKNOWN").
        """
        self.identifiers = build_identifiers(identifiers)
        self.strategy = strategy
        self.mark_unknown = mark_unknown
        self.unknown_type = unknown_type


@dataclass
class DatasetClassificationReport:
    """Report containing classification results for a dataset.

    This dataclass holds the complete classification results for all columns
    in a dataset, including the best identified type for each column and
    detailed frequency reports.

    Attributes:
        best_types: Dictionary mapping column names to their best identified type.
        reports: Dictionary mapping column names to their detailed type frequency reports.
            Each report is a dict mapping type names to their frequency (0.0-1.0).
        size: Total number of rows in the dataset.
        ordered_column_names: List of column names in their original order.

    Example:
        >>> report = DatasetClassificationReport(
        ...     best_types={"email_col": "Email", "phone_col": "Phone"},
        ...     reports={
        ...         "email_col": {"Email": 0.95, "UNKNOWN": 0.05},
        ...         "phone_col": {"Phone": 0.80, "UNKNOWN": 0.20}
        ...     },
        ...     size=100,
        ...     ordered_column_names=["email_col", "phone_col"]
        ... )
    """

    best_types: dict[str, str]
    reports: dict[str, dict[str, float]]
    size: int
    ordered_column_names: list[str]


class DatasetClassification:
    """Main class for classifying dataset columns.

    This class performs classification of dataset columns by analyzing each
    column's values against configured identifiers and determining the best
    matching data type using the specified classification strategy.

    Attributes:
        configuration: Configuration specifying identifiers and classification strategy.

    Example:
        >>> import pandas as pd
        >>> from risk_assessment.classification.identifiers import Email, Phone
        >>>
        >>> config = DatasetClassificationConfiguration(
        ...     identifiers=[Email(), Phone()],
        ...     mark_unknown=True
        ... )
        >>> classifier = DatasetClassification(config)
        >>>
        >>> df = pd.DataFrame({
        ...     "emails": ["user@example.com", "admin@test.org"],
        ...     "phones": ["555-1234", "555-5678"]
        ... })
        >>> report = classifier.classify(df)
        >>> print(report.best_types)
        {'emails': 'Email', 'phones': 'Phone'}
    """

    def __init__(self, configuration: DatasetClassificationConfiguration):
        """Initialize the dataset classifier.

        Args:
            configuration: Configuration for classification.
        """
        self.configuration = configuration

    def classify(self, dataset: DataFrame) -> DatasetClassificationReport:
        """Classify all columns in a dataset.

        Analyzes each column in the dataset to identify the type of sensitive
        data it contains, returning a comprehensive report with the best type
        for each column and detailed frequency information.

        Args:
            dataset: pandas DataFrame to classify.

        Returns:
            DatasetClassificationReport containing classification results.

        Example:
            >>> import pandas as pd
            >>> df = pd.DataFrame({"col1": ["user@example.com", "test@test.com"]})
            >>> report = classifier.classify(df)
            >>> print(report.best_types["col1"])
            'Email'
        """
        best_types: dict[str, str] = {}
        reports: dict[str, dict[str, float]] = {}
        size = len(dataset)
        for column_name in dataset.columns:
            # Explicitly cast to Series to satisfy type checker
            column_data: Series = cast(Series, dataset[column_name])
            (column_best_type, column_full_report) = self.analyze_column(column_data, size)
            best_types[column_name] = column_best_type
            reports[column_name] = column_full_report

        return DatasetClassificationReport(best_types, reports, size, list(dataset.columns))

    def compute_raw_report(self, column_values: Series | list[Any]) -> dict[str, int]:
        """Compute raw occurrence counts for each identifier type.

        Analyzes each value in the column against all configured identifiers
        and counts how many times each type is identified.

        Args:
            column_values: List of values from a dataset column.

        Returns:
            Dictionary mapping type names to their occurrence counts.

        Example:
            >>> column_values = ["user@example.com", "test@test.com", "not-an-email"]
            >>> counts = classifier.compute_raw_report(column_values)
            >>> print(counts)
            {'Email': 2, 'UNKNOWN': 1}
        """
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
        """Normalize raw counts to frequency percentages.

        Converts raw occurrence counts to frequencies (0.0-1.0) by dividing
        each count by the total column size.

        Args:
            raw_counts: Dictionary mapping type names to occurrence counts.
            size: Total number of values in the column.

        Returns:
            Dictionary mapping type names to their frequencies (0.0-1.0).

        Example:
            >>> raw_counts = {"Email": 80, "UNKNOWN": 20}
            >>> normalized = classifier.normalize_results(raw_counts, 100)
            >>> print(normalized)
            {'Email': 0.8, 'UNKNOWN': 0.2}
        """
        return {key: (value / size) for key, value in raw_counts.items()}

    def analyze_column(self, column_values: Series | list[Any], size: int) -> tuple[str, dict[str, float]]:
        """Analyze a single column to determine its best type.

        Computes raw counts, normalizes them to frequencies, and uses the
        configured strategy to determine the best matching type.

        Args:
            column_values: List of values from the column.
            size: Total number of values in the column.

        Returns:
            Tuple of (best_type_name, frequency_report) where frequency_report
            maps type names to their frequencies (0.0-1.0).

        Example:
            >>> column_values = ["user@example.com", "test@test.com"]
            >>> best_type, report = classifier.analyze_column(column_values, 2)
            >>> print(best_type)
            'Email'
            >>> print(report)
            {'Email': 1.0}
        """
        raw_counts = self.compute_raw_report(column_values)
        report = self.normalize_results(raw_counts, size)
        column_best_type = self.configuration.strategy.find_best_type(raw_counts, size)

        return (column_best_type, report)
