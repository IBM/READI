from importlib.resources import files
from pathlib import Path

import pandas as pd  # type: ignore

from risk_assessment.masking import cleanse_dataframe_field


def test_cleanse():
    res = files(__package__) / "data" / "data.csv"
    with res.open() as iostream:
        data = pd.read_csv(iostream, header=None)

    data_folder = Path(__file__).parent / "data" / "markers"

    cleansed = cleanse_dataframe_field(data, 3, data_folder, r"markers-{}.json")

    assert cleansed is not None
    assert len(cleansed) == len(data)


def test_cleanse_with_headers():
    res = files(__package__).joinpath("data/data_with_headers.csv")
    with res.open() as iostream:
        data = pd.read_csv(iostream)

    data_folder = str(Path(Path(Path(__file__).parent, "data"), "markers").absolute())

    cleansed = cleanse_dataframe_field(data, "text", data_folder, r"markers-{}.json")

    assert cleansed is not None
    assert len(cleansed) == len(data)
