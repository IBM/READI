"""Classification strategies for determining the best data type for dataset columns.

This module provides various strategies for classifying dataset columns based on
the frequency and priority of identified data types. It includes both simple
frequency-based approaches and more advanced priority-weighted strategies.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


class DatasetClassificationStrategy(ABC):
    """Abstract base class for dataset classification strategies.

    This class defines the interface for strategies that determine the best
    data type for a dataset column based on raw counts of identified types.
    """

    @abstractmethod
    def find_best_type(self, raw_counts: dict[str, int], size: int) -> str:
        """Find the best data type for a column based on raw counts.

        Args:
            raw_counts: Dictionary mapping type names to their occurrence counts.
            size: Total number of values in the column.

        Returns:
            The name of the best matching data type.
        """
        pass


class FrequencyBasedDatasetClassificationStrategy(DatasetClassificationStrategy):
    """Simple frequency-based classification strategy.

    Selects the data type with the highest occurrence count as the best type.
    This is the simplest classification approach that doesn't consider type
    priorities or frequency thresholds.

    Example:
        >>> strategy = FrequencyBasedDatasetClassificationStrategy()
        >>> raw_counts = {"Email": 50, "Phone": 30, "UNKNOWN": 20}
        >>> best = strategy.find_best_type(raw_counts, 100)
        >>> print(best)
        'Email'
    """

    def find_best_type(self, raw_counts: dict[str, int], size: int) -> str:
        """Find the type with the highest occurrence count.

        Args:
            raw_counts: Dictionary mapping type names to their occurrence counts.
            size: Total number of values in the column (not used in this strategy).

        Returns:
            The name of the type with the highest count.
        """
        best_type = max(raw_counts.items(), key=lambda t: t[1])

        return best_type[0]


@dataclass
class PriorityBasedDatasetClassificationStrategy(DatasetClassificationStrategy):
    """Priority-weighted classification strategy.

    Selects the best data type by applying configurable weights to occurrence counts.
    This allows certain types to be prioritized over others even if they have
    lower raw counts.

    Attributes:
        weights: Dictionary mapping type names to their priority weights.
        default_weight: Weight to apply to types not in the weights dictionary.

    Example:
        >>> strategy = PriorityBasedDatasetClassificationStrategy(
        ...     weights={"Email": 2.0, "Phone": 1.5},
        ...     default_weight=1.0
        ... )
        >>> raw_counts = {"Email": 30, "Phone": 40, "UNKNOWN": 50}
        >>> best = strategy.find_best_type(raw_counts, 120)
        >>> print(best)  # Email wins: 30 * 2.0 = 60 > 40 * 1.5 = 60
        'Email'
    """

    weights: dict[str, float] = field(default_factory=dict)
    default_weight: float = 1.0

    def find_best_type(self, raw_counts: dict[str, int], size: int) -> str:
        """Find the type with the highest weighted count.

        Args:
            raw_counts: Dictionary mapping type names to their occurrence counts.
            size: Total number of values in the column (not used in this strategy).

        Returns:
            The name of the type with the highest weighted count.
        """
        best_type = max(
            [
                (k, v * self.weights[k]) if k in self.weights else (k, v * self.default_weight)
                for (k, v) in raw_counts.items()
            ],
            key=lambda t: t[1],
        )

        return best_type[0]


@dataclass
class IdentificationConfiguration:
    """Configuration for advanced dataset classification.

    This configuration class holds parameters that control how data types are
    identified and prioritized during classification, including frequency
    thresholds and type-specific priorities.

    Attributes:
        priority: Default priority value for types not in the priorities dict.
        frequency_thr: Default minimum frequency threshold (0-100) for type identification.
        classification_strategy: Name of the classification strategy to use.
        priorities: Dictionary mapping type names to their priority values.
        consider_empty_for_frequency: Whether to include empty values in frequency calculations.
        frequency_thresholds: Dictionary mapping type names to their specific frequency thresholds.

    Example:
        >>> config = IdentificationConfiguration(
        ...     priority=1,
        ...     frequency_thr=10.0,
        ...     classification_strategy="priority",
        ...     priorities={"Email": 2.0, "Phone": 1.5},
        ...     consider_empty_for_frequency=False,
        ...     frequency_thresholds={"Email": 5.0}
        ... )
    """

    priority: int
    frequency_thr: float
    classification_strategy: str
    priorities: dict[str, float]
    consider_empty_for_frequency: bool
    frequency_thresholds: dict[str, float] = field(default_factory=dict)

    def get_frequency_thr_for_type(self, type_name: str) -> float:
        """Get the frequency threshold for a specific type.

        Args:
            type_name: Name of the data type.

        Returns:
            The frequency threshold for the type, or the default if not specified.
        """
        if self.frequency_thresholds:
            if type_name not in self.frequency_thresholds.keys():
                return self.frequency_thr
            return self.frequency_thresholds[type_name]
        return self.frequency_thr

    def get_priority_for_type(self, type_name: str) -> float:
        """Get the priority value for a specific type.

        Args:
            type_name: Name of the data type.

        Returns:
            The priority value for the type, or the default if not specified.
        """
        if self.priorities:
            if type_name not in self.priorities.keys():
                return self.priority
            return self.priorities[type_name]
        return self.priority

    def get_consider_empty_for_frequency(self) -> bool:
        """Check if empty values should be considered in frequency calculations.

        Returns:
            True if empty values should be included, False otherwise.
        """
        return self.consider_empty_for_frequency


def type_identified_less_than_required_frequency(
    type_name: str,
    type_confidence: float,
    identification_config: IdentificationConfiguration,
) -> bool:
    """Check if a type's confidence is below its required frequency threshold.

    Args:
        type_name: Name of the data type being checked.
        type_confidence: Confidence/frequency percentage (0-100) for the type.
        identification_config: Configuration containing frequency thresholds.

    Returns:
        True if the confidence is below the threshold, False otherwise.

    Example:
        >>> config = IdentificationConfiguration(
        ...     priority=1, frequency_thr=10.0, classification_strategy="priority",
        ...     priorities={}, consider_empty_for_frequency=False
        ... )
        >>> type_identified_less_than_required_frequency("Email", 5.0, config)
        True
        >>> type_identified_less_than_required_frequency("Email", 15.0, config)
        False
    """
    return type_confidence < identification_config.get_frequency_thr_for_type(type_name)


def calculate_frequency(
    count: int,
    identified: int,
    unknown: int = 0,
    empty: int = 0,
    consider_empty_fo_confidence: bool = False,
) -> int:
    """Calculate the frequency percentage of a type occurrence.

    Computes the percentage of values that match a specific type, optionally
    including empty values in the calculation.

    Args:
        count: Number of occurrences of the specific type.
        identified: Total number of identified (non-unknown) values.
        unknown: Number of unknown/unidentified values (not currently used).
        empty: Number of empty values.
        consider_empty_fo_confidence: Whether to include empty values in the total.

    Returns:
        Frequency percentage (0-100), or -1 if total count is zero.

    Example:
        >>> calculate_frequency(count=30, identified=100, empty=10,
        ...                     consider_empty_fo_confidence=False)
        30
        >>> calculate_frequency(count=30, identified=100, empty=10,
        ...                     consider_empty_fo_confidence=True)
        27
    """
    total_count = identified
    if consider_empty_fo_confidence:
        total_count += empty
    if total_count == 0:
        return -1
    return int(100.0 * count / total_count)


class DatasetClassificationStrategyAdvanced(ABC):
    """Abstract base class for advanced classification strategies.

    Advanced strategies consider frequency thresholds, priorities, and
    configuration settings when determining the best data type for a column.
    """

    @abstractmethod
    def find_best_type(
        self,
        raw_counts: dict[str, int],
        priority: dict[str, float],
        size: int,
        identification_config: IdentificationConfiguration,
    ) -> str | None:
        """Find the best data type using advanced classification logic.

        Args:
            raw_counts: Dictionary mapping type names to their occurrence counts.
            priority: Dictionary mapping type names to their priority values.
            size: Total number of values in the column.
            identification_config: Configuration for identification thresholds and settings.

        Returns:
            The name of the best matching data type, or None if no type meets the criteria.
        """
        pass


class FrequencyBasedDatasetClassificationStrategyAdvanced(DatasetClassificationStrategyAdvanced):
    """Advanced frequency-based classification with threshold filtering.

    This strategy selects the type with the highest frequency that meets its
    minimum frequency threshold. When frequencies are equal, priority values
    are used as a tiebreaker.

    Example:
        >>> config = IdentificationConfiguration(
        ...     priority=1, frequency_thr=10.0, classification_strategy="frequency",
        ...     priorities={"Email": 2.0, "Phone": 1.5},
        ...     consider_empty_for_frequency=False
        ... )
        >>> strategy = FrequencyBasedDatasetClassificationStrategyAdvanced()
        >>> raw_counts = {"Email": 50, "Phone": 30, "UNKNOWN": 5}
        >>> priorities = {"Email": 2.0, "Phone": 1.5, "UNKNOWN": 1.0}
        >>> best = strategy.find_best_type(raw_counts, priorities, 100, config)
        >>> print(best)
        'Email'
    """

    def find_best_type(
        self,
        raw_counts: dict[str, int],
        priority: dict[str, float],
        size: int,
        identification_config: IdentificationConfiguration,
    ) -> str | None:
        """Find the type with the highest frequency above its threshold.

        Args:
            raw_counts: Dictionary mapping type names to their occurrence counts.
            priority: Dictionary mapping type names to their priority values.
            size: Total number of values in the column.
            identification_config: Configuration for identification thresholds and settings.

        Returns:
            The name of the type with the highest frequency above threshold,
            or None if no type meets the criteria.
        """
        best_type: str | None = None
        best_type_frequency = -1
        consider_empty_for_confidence = identification_config.get_consider_empty_for_frequency()
        for item in raw_counts.items():
            frequency = calculate_frequency(item[1], size, consider_empty_for_confidence)

            if type_identified_less_than_required_frequency(item[0], frequency, identification_config):
                continue
            if frequency > best_type_frequency:
                best_type_frequency = frequency
                best_type = item[0]
            elif frequency == best_type_frequency:
                if best_type:
                    if priority[item[0]] > priority[best_type]:
                        best_type_frequency = frequency
                        best_type = item[0]

        return best_type


@dataclass
class PriorityBasedDatasetClassificationStrategyAdvanced(DatasetClassificationStrategyAdvanced):
    """Advanced priority-based classification with threshold filtering.

    This strategy selects the type with the highest priority that meets its
    minimum frequency threshold. When priorities are equal, frequency is used
    as a tiebreaker.

    Attributes:
        weights: Dictionary mapping type names to their priority weights (not currently used).
        default_weight: Default weight for types not in the weights dictionary (not currently used).

    Example:
        >>> config = IdentificationConfiguration(
        ...     priority=1, frequency_thr=10.0, classification_strategy="priority",
        ...     priorities={"Email": 2.0, "Phone": 1.5},
        ...     consider_empty_for_frequency=False
        ... )
        >>> strategy = PriorityBasedDatasetClassificationStrategyAdvanced()
        >>> raw_counts = {"Email": 30, "Phone": 40, "UNKNOWN": 20}
        >>> priorities = {"Email": 2.0, "Phone": 1.5, "UNKNOWN": 1.0}
        >>> best = strategy.find_best_type(raw_counts, priorities, 100, config)
        >>> print(best)  # Email wins due to higher priority
        'Email'
    """

    weights: dict[str, float] = field(default_factory=dict)
    default_weight: float = 1.0

    def find_best_type(
        self,
        raw_counts: dict[str, int],
        priority: dict[str, float],
        size: int,
        identification_config: IdentificationConfiguration,
    ) -> str | None:
        """Find the type with the highest priority above its frequency threshold.

        Args:
            raw_counts: Dictionary mapping type names to their occurrence counts.
            priority: Dictionary mapping type names to their priority values.
            size: Total number of values in the column.
            identification_config: Configuration for identification thresholds and settings.

        Returns:
            The name of the type with the highest priority above threshold,
            or None if no type meets the criteria.
        """
        best_type: str | None = None
        best_priority = -1.0
        best_frequency = -1
        consider_empty_for_confidence = identification_config.get_consider_empty_for_frequency()
        for item in raw_counts.items():
            frequency = calculate_frequency(item[1], size, consider_empty_for_confidence)

            if type_identified_less_than_required_frequency(item[0], frequency, identification_config):
                continue

            type_priority = identification_config.get_priority_for_type(item[0])

            if (
                best_type is None
                or type_priority > best_priority
                or (type_priority == best_priority and frequency > best_frequency)
            ):
                best_type = item[0]
                best_frequency = frequency
                best_priority = type_priority

        return best_type
