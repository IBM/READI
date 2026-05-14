from abc import ABC, abstractmethod
from dataclasses import dataclass, field


class DatasetClassificationStrategy(ABC):
    @abstractmethod
    def find_best_type(self, raw_counts: dict[str, int], size: int) -> str:
        pass


class FrequencyBasedDatasetClassificationStrategy(DatasetClassificationStrategy):
    def find_best_type(self, raw_counts: dict[str, int], size: int) -> str:
        best_type = max(raw_counts.items(), key=lambda t: t[1])

        return best_type[0]


@dataclass
class PriorityBasedDatasetClassificationStrategy(DatasetClassificationStrategy):
    weights: dict[str, float] = field(default_factory=dict)
    default_weight: float = 1.0

    def find_best_type(self, raw_counts: dict[str, int], size: int) -> str:
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
    priority: int
    frequency_thr: float
    classification_strategy: str
    priorities: dict[str, float]
    consider_empty_for_frequency: bool
    frequency_thresholds: dict[str, float] = field(default_factory=dict)

    def get_frequency_thr_for_type(self, type_name: str) -> float:
        if self.frequency_thresholds:
            if type_name not in self.frequency_thresholds.keys():
                return self.frequency_thr
            return self.frequency_thresholds[type_name]
        return self.frequency_thr

    def get_priority_for_type(self, type_name: str) -> float:
        if self.priorities:
            if type_name not in self.priorities.keys():
                return self.priority
            return self.priorities[type_name]
        return self.priority

    def get_consider_empty_for_frequency(self) -> bool:
        return self.consider_empty_for_frequency


def type_identified_less_than_required_frequency(
    type_name: str,
    type_confidence: float,
    identification_config: IdentificationConfiguration,
) -> bool:
    return type_confidence < identification_config.get_frequency_thr_for_type(type_name)


def calculate_frequency(
    count: int,
    identified: int,
    unknown: int = 0,
    empty: int = 0,
    consider_empty_fo_confidence: bool = False,
) -> int:
    total_count = identified
    if consider_empty_fo_confidence:
        total_count += empty
    if total_count == 0:
        return -1
    return int(100.0 * count / total_count)


class DatasetClassificationStrategyAdvanced(ABC):
    @abstractmethod
    def find_best_type(
        self,
        raw_counts: dict[str, int],
        priority: dict[str, float],
        size: int,
        identification_config: IdentificationConfiguration,
    ) -> str | None:
        pass


class FrequencyBasedDatasetClassificationStrategyAdvanced(DatasetClassificationStrategyAdvanced):
    def find_best_type(
        self,
        raw_counts: dict[str, int],
        priority: dict[str, float],
        size: int,
        identification_config: IdentificationConfiguration,
    ) -> str | None:
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
    weights: dict[str, float] = field(default_factory=dict)
    default_weight: float = 1.0

    def find_best_type(
        self,
        raw_counts: dict[str, int],
        priority: dict[str, float],
        size: int,
        identification_config: IdentificationConfiguration,
    ) -> str | None:
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
