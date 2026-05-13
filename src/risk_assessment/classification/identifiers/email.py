import re

from risk_assessment.classification.identifiers import Identifier


class Email(Identifier):
    pattern = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$")

    def is_of_this_type(self, text: str) -> bool:
        m = self.pattern.match(text)

        if m:
            return True
        return False
