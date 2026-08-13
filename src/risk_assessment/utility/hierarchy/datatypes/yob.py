from datetime import date

from risk_assessment.utility.hierarchy import MaterializedHierarchy


class YOBHierarchy(MaterializedHierarchy):
    def __init__(self) -> None:
        current_year = date.today().year

        all_paths: list[list[str]] = [
            (
                [str(past_year)]
                + [
                    f"{str(past_year - (past_year % interval))}-{str(past_year - (past_year % interval) + interval)}"
                    for interval in [2, 4, 8]
                ]
                + ["*"]
            )
            for past_year in range(current_year - 160, current_year + 1)
        ]

        super().__init__(all_paths)
