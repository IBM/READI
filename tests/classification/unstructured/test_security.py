import re

import pytest
from nltk.tokenize import WordPunctTokenizer

from risk_assessment.classification.identifiers import IP, Phone, RegexIdentifier, RegexIdentifierWithSpan
from risk_assessment.classification.unstructured.aggregator import Aggregator, AggregatorConfiguration
from risk_assessment.classification.unstructured.drl import DRLEntityExtractor
from risk_assessment.classification.unstructured.spacy import SpacyEntityExtractor
from risk_assessment.classification.unstructured.stanza_ner import STANZAEntityExtractor


@pytest.mark.skip
def test_deidentify_playbook():
    text = """My name is Adrian, this my text with ip 239.217.64.23, 123.217.74.23 and ticket id SOCP123329
My name is Bob and I'm an analyst at Microsoft!
I'm an analyst named Charlie. You can contact me at (123)-456-7890. I live at Foobar street
Please block 124.398.74.23 from your systems.
Set stronger access privileges for the user user_user1name and inform other administrators to do the same.
Please whitelist ip address219.217.64.43
If this activity was expected, finetune your QRadar rules.
Make sure no data has been illegitimately stored on Microsoft Cloud
Please check the role if internal Host "108.5.174.233"
URL seems suspicious as per Apache platforms ,kindly verify it's reputation if it is malicious it should be blocked .""".split(
        "\n"
    )

    known_entities: list[set[str]] = [
        {"Adrian", "239.217.64.23", "123.217.74.23", "SOCP123329"},
        {"Bob", "Microsoft"},
        {"Charlie", "(123)-456-7890", "Foobar street"},
        # {"Charlie", "(123)-456-7890", "Foobar"},
        {"124.398.74.23"},
        {"user_user1name"},
        # {"user user_user1name"},
        {"219.217.64.43"},
        {"QRadar"},
        {"Microsoft Cloud"},
        {"108.5.174.233"},
        {"Apache"},
    ]

    assert len(text) == len(known_entities)

    for text_line, line_entities in zip(text, known_entities):
        for entity in line_entities:
            assert entity in text_line

    spacy = SpacyEntityExtractor("en_core_web_sm")
    stanza_extractor = STANZAEntityExtractor()

    dpt = DRLEntityExtractor(
        identifiers=[
            # Name(),
            IP(),
            RegexIdentifier("TICKET_ID", [re.compile(r"SOCP\d+")]),
            RegexIdentifierWithSpan("USERNAME", [re.compile(r"user\s([a-z10-9_]{3,})")]),
            Phone(),
        ],
        tokenizer=WordPunctTokenizer(),
        max_shinglet_length=8,
    )
    extractor = Aggregator(
        AggregatorConfiguration(
            prioritize_inclusion=True,
            weights={
                "Phone": {"DRL": 1000},
                "FAC": {"STANZA": 1000},
                "ORG": {"STANZA": 1000},
            },
        ),
    )

    for sentence, expected_entities in zip(text, known_entities):
        spacy_entities = spacy.extract(sentence)
        dpt_entities = dpt.extract(sentence)
        stanza_entities = stanza_extractor.extract(sentence)

        detected_entities = extractor.aggregate(
            [spacy_entities, dpt_entities, stanza_entities],
            sentence,
        )

        assert detected_entities is not None

        if len(detected_entities) == 0 and len(expected_entities) == 0:
            """worked"""
            continue

        detected_text: set[str] = {sentence[e.start : e.end] for e in detected_entities}

        assert len(detected_entities) == len(detected_text)

        true_positive = detected_text & expected_entities
        false_negative = expected_entities - detected_text
        false_positive = detected_text - expected_entities

        assert 0 == len(false_positive), false_positive
        assert 0 == len(false_negative), false_negative

        assert len(true_positive) == len(expected_entities)
