from re import I, Pattern, U, compile

from risk_assessment.classification.identifiers import Identifier


class JapanAddress(Identifier):
    patterns: list[Pattern[str]] = [
        compile(
            r"^\d+\s+\w+\s+\w{3,}-\w{2,5}\s+\w{3,}(?:-\w{2,3})?,\s+\w{3,}\s+(?:〒\s*)?\d{3}-\d{4}\s+JAPAN$", I | U
        ),  # rural
        compile(
            r"^\d+-\d+,\s+\w{3,}\s+\d+-chome\s+\w{3,}(?:-\w{3,})*-(?:shi|gun|ku|machi|cho),\s+\w+(?:-(?:ken|fu|to))?\s+(?:〒\s*)?\d{3}-\d{4}\s+JAPAN$",
            I | U,
        ),  # city
        compile(
            r"^\d+-\d+-\d+,\s+\w{3,}\s+\w{3,}(?:-\w{3,})*-(?:shi|gun|ku|machi|cho),\s+\w+(?:-(?:ken|fu|to))?\s+(?:〒\s*)?\d{3}-\d{4}\s+JAPAN$",
            I | U,
        ),  # city, compressed
        compile(
            r"^\d+-\d+,\s+\w{3,}\s+\w{3,}(?:-\w{3,})*-(?:shi|gun|ku|machi|cho),\s+\w+(?:-(?:ken|fu|to))?\s+(?:〒\s*)?\d{3}-\d{4}\s+JAPAN$$",
            I | U,
        ),  # city as prefecture
        compile(
            r"^JAPAN\s+(?:〒\s*)?\d{3}-\d{4}\s+\w+(?:-(?:ken|fu|to))?\s+\w{3,}(?:-\w{3,})*-(?:shi|gun|ku|machi|cho)\s+\w{3,}\s+\d+(?:-chome)?(?:\s+|-)\d+-\d+$",
            I | U,
        ),  # oneliner
        # from RWD
        compile(r"^〒?(:?\d+-\d+)\s+\w+\s*\d+$"),
    ]

    def is_of_this_type(self, text: str) -> bool:
        return any(pattern.match(text) for pattern in self.patterns)
