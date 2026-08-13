import math
from enum import Enum, auto
from typing import Any

import numpy as np

from risk_assessment.utility.hierarchy import GeneralizationHierarchy, GeneralizationNode, NumericalRange


class GeneralizationType(Enum):
    RANGE = auto()
    MEAN = auto()


class NumericalHierarchy(GeneralizationHierarchy):
    def __init__(self, series: NumericalRange, height: int, generalization_type: GeneralizationType):
        self.series = series
        self.min = series.min
        self.max = series.max
        self.range = series.range()
        self.height = height
        self.generalization_type = generalization_type

        if self.generalization_type == GeneralizationType.RANGE:
            self.top_term = str(self.min) + ":" + str(self.max)
        elif self.generalization_type == GeneralizationType.MEAN:
            self.top_term = str((self.min + self.max) / 2)
        else:
            raise ValueError("Support for range and mean at the moment")

    def encode(self, value: Any, level: int, random_on_fail: bool = False) -> str:
        if level >= len(self):
            return self.top_term

        if level == 0:
            return str(float(value))

        try:
            node_range_level = self.range / (np.power(2, self.height - level))
            node_index = int((value - self.min) / node_range_level)
            if (value - self.min) % node_range_level == 0:
                if value != self.min:
                    node_index = node_index - 1
            generalized_range_min = node_index * node_range_level + self.min
            generalized_range_max = (node_index + 1) * node_range_level + self.min
            if self.generalization_type == GeneralizationType.RANGE:
                return str(round(generalized_range_min, 5)) + ":" + str(round(generalized_range_max, 5))
            else:
                return str(round((generalized_range_min + generalized_range_max) / 2, 5))
        except KeyError as e:
            if random_on_fail:
                raise Exception("Not implemented yet") from e
        return self.top_term

    def __len__(self) -> int:
        return self.height

    def gcd(self, a: float, b: float) -> float:
        if b == 0:
            return abs(a)
        else:
            return self.gcd(b, a % b)

    def node_level(self, value: Any) -> int:
        if ":" not in value and self.series.contains(value):
            return 0
        if self.generalization_type == GeneralizationType.MEAN:
            node_range_level = self.gcd(self.max - float(value), float(value) - self.min) * 2
        else:
            node_range_level = float(str(value).split(":")[1]) - float(str(value).split(":")[0])
        number_nodes = (self.max - self.min) / node_range_level

        return int(self.height - math.log(number_nodes, 2))

    def leaves_for_node(self, value: Any) -> int:
        raise NotImplementedError()

    def index_for_value(self, value: Any) -> int:
        raise NotImplementedError()

    def __getitem__(self, key: str | None) -> GeneralizationNode:
        raise NotImplementedError()
