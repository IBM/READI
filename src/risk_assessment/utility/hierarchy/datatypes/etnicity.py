from risk_assessment.utility.hierarchy import MaterializedHierarchy


class EtnicityHierarchy(MaterializedHierarchy):
    def __init__(self) -> None:
        super().__init__(
            [
                ["White", "*"],
                ["Asian-Pac-Islander", "*"],
                ["Amer-Indian-Eskimo", "*"],
                ["Other", "*"],
                ["Black", "*"],
            ]
        )
