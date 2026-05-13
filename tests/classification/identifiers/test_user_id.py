import json
from pathlib import Path

from risk_assessment.classification.identifiers.user_id import UniqueIDIdentifier


def test_unique_ids():
    identifier = UniqueIDIdentifier()

    with (Path(__file__).parent / "data" / "unique_id.json").open() as input:
        for id in json.load(input):
            assert identifier.is_of_this_type(id), id
