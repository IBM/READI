import pytest

from risk_assessment.classification.identifiers import IP, URI
from risk_assessment.classification.unstructured.aggregator import Aggregator, AggregatorConfiguration
from risk_assessment.classification.unstructured.drl import DRLEntityExtractor
from risk_assessment.classification.unstructured.spacy import SpacyEntityExtractor


@pytest.mark.xfail(reason="Old version of the pipeline")
def test_overall_pipeline():
    spacy = SpacyEntityExtractor("en_core_web_sm")

    drl = DRLEntityExtractor(identifiers=[URI(), IP()], type_mapping={"PersonName": "PERSON"})

    aggregator = Aggregator(
        AggregatorConfiguration(
            prune_negative_scores=True, weights={"SPACY": {"CARDINAL": -1, "ORG": -1}, "DRL": {"URI": 100}}
        )
    )

    text = """This is a nice text from John Meyer, who is a good friend of Mary O'Donnel.
    He shared his email address with her, and now he is receiving spam from https://www.goodguys.com.
    This is a bad URL as it is hosted at 127.0.0.1 """

    spacy_entities = spacy.extract(text)
    drl_entities = drl.extract(text)

    entities = aggregator.aggregate([drl_entities, spacy_entities], text)

    assert spacy_entities
    assert drl_entities
    assert entities

    assert len(entities) <= len(spacy_entities) + len(drl_entities)
