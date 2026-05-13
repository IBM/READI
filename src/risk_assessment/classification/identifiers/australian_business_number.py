import re

from risk_assessment.classification.identifiers import Identifier


def _is_valid(text: str) -> bool:
    text = text.replace(" ", "")
    weights: list[int] = [
        10,
        1,
        3,
        5,
        7,
        9,
        11,
        13,
        15,
        17,
        19,
    ]

    digits = [int(c) for c in text]

    digits[0] -= 1

    sum_of_weights = sum(d * w for (d, w) in zip(digits, weights, strict=False))

    return 0 == sum_of_weights % 89


class AustralianBusinessNumber(Identifier):
    pattern = re.compile(r"^\d{2}\s?\d{3}\s?\d{3}\s?\d{3}$")

    def is_of_this_type(self, text: str) -> bool:
        return self.pattern.match(text) is not None and _is_valid(text)
