import re
from re import Pattern

from risk_assessment.classification.identifiers import Identifier


class JapanAddress(Identifier):
    patterns: list[Pattern[str]] = [
        re.compile(
            r"^\d+\s+\w+\s+\w{3,}-\w{2,5}\s+\w{3,}(?:-\w{2,3})?,\s+\w{3,}\s+(?:〒\s*)?\d{3}-\d{4}\s+JAPAN$", re.I | re.U
        ),  # rural
        re.compile(
            r"^\d+-\d+,\s+\w{3,}\s+\d+-chome\s+\w{3,}(?:-\w{3,})*-(?:shi|gun|ku|machi|cho),\s+\w+(?:-(?:ken|fu|to))?\s+(?:〒\s*)?\d{3}-\d{4}\s+JAPAN$",
            re.I | re.U,
        ),  # city
        re.compile(
            r"^\d+-\d+-\d+,\s+\w{3,}\s+\w{3,}(?:-\w{3,})*-(?:shi|gun|ku|machi|cho),\s+\w+(?:-(?:ken|fu|to))?\s+(?:〒\s*)?\d{3}-\d{4}\s+JAPAN$",
            re.I | re.U,
        ),  # city, compressed       # re.compile(r"", re.I | re.U),  # city
        re.compile(
            r"^\d+-\d+,\s+\w{3,}\s+\w{3,}(?:-\w{3,})*-(?:shi|gun|ku|machi|cho),\s+\w+(?:-(?:ken|fu|to))?\s+(?:〒\s*)?\d{3}-\d{4}\s+JAPAN$$",
            re.I | re.U,
        ),  # city as prefecture
        re.compile(
            r"^JAPAN\s+(?:〒\s*)?\d{3}-\d{4}\s+\w+(?:-(?:ken|fu|to))?\s+\w{3,}(?:-\w{3,})*-(?:shi|gun|ku|machi|cho)\s+\w{3,}\s+\d+(?:-chome)?(?:\s+|-)\d+-\d+$",
            re.I | re.U,
        ),  # oneliner
        # from RWD
        re.compile(r"^〒?(:?\d+-\d+)\s+\w+\s*\d+$"),
    ]

    def is_of_this_type(self, text: str) -> bool:
        return any(pattern.match(text) for pattern in self.patterns)
