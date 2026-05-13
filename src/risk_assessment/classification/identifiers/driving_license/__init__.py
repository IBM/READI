from risk_assessment.classification.identifiers import Identifier
from risk_assessment.classification.identifiers.driving_license.japan import (
    JapanDrivingLicense,
)


class DrivingLicense(Identifier):
    def __init__(self) -> None:
        self.identifiers = [
            JapanDrivingLicense(),
        ]

    def is_of_this_type(self, text: str) -> bool:
        return any(identifier.is_of_this_type(text) for identifier in self.identifiers)
