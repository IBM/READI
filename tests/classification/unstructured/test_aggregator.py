import json

import pytest
from pytest import fail

from risk_assessment.classification.unstructured import Entity
from risk_assessment.classification.unstructured.aggregator import Aggregator, AggregatorConfiguration


def test_validate_empty_list() -> None:
    aggregator = Aggregator()

    entities = aggregator.aggregate([], "")

    assert entities is not None
    assert len(entities) == 0


def test_composition_filtering():
    aggregator = Aggregator()

    entities = [
        Entity(0, 0, "BAR", frozenset(["BAR"])),
        Entity(0, 0, "FOO", frozenset(["FOO"])),
    ]
    merged = aggregator.compose_source_for_best_type(entities, "FOO")

    assert merged
    assert len(merged) == 1


def test_composition_merging():
    aggregator = Aggregator()

    entities = [
        Entity(0, 0, "FOO", frozenset(["BAR"])),
        Entity(0, 0, "FOO", frozenset(["FOO"])),
    ]
    merged = aggregator.compose_source_for_best_type(entities, "FOO")

    assert merged
    assert len(merged) == 2


def test_filter_required_only() -> None:
    entities = [
        Entity(0, 1, "FOO", frozenset(["_"])),
        Entity(10, 12, "BAR", frozenset(["_"])),
    ]
    text = "THIS IS NOT RELEVANT FOR THIS CASE, BUT LET'S MAKE IT LONG"
    no_filter = AggregatorConfiguration(to_report_only=None)
    with_filter = AggregatorConfiguration(to_report_only={"FOO"})

    assert len(Aggregator(no_filter).aggregate([entities], text)) == 2
    assert len(Aggregator(with_filter).aggregate([entities], text)) == 1


def test_remove_repetition() -> None:
    aggregator: Aggregator = Aggregator(AggregatorConfiguration())

    uniques = aggregator.remove_repetition(
        [
            Entity(5, 6, "D", frozenset(["D"])),
            Entity(0, 1, "A", frozenset(["A"])),
            Entity(0, 1, "A", frozenset(["A"])),
            Entity(3, 9, "B", frozenset(["B"])),
            Entity(3, 9, "B", frozenset(["B"])),
        ]
    )

    assert len(uniques) == 3


def test_check_weights():
    entities: list[list[Entity]] = [
        [Entity(start=0, end=4, entity_type="NAME", source=frozenset(["UPI"]))],
        [Entity(start=0, end=11, entity_type="PERSON", source=frozenset(["EISM"]))],
    ]

    weights = json.loads("""{
                "weights": {
                    "SYSIBM_PERSON_REFERENCE": {
                        "EISM": 0.5,
                        "DRL-ANNOTATOR": 0.3,
                        "GUARDIUM-ANNOTATOR": 0.3,
                        "FOO": 0.3
                    },
                    "NAME":{
                            "UPI": 50
                    }
                },
                "thresholds": {}
                }""")

    aggregator = Aggregator(AggregatorConfiguration(**weights))

    merged = aggregator.aggregate(entities, "John Meyers lives in Montana")

    assert merged
    assert len(merged) == 2


def test_silly_with_fake_UPI_invert_not_merged():
    aggregator = Aggregator(AggregatorConfiguration(merge_entities=False))

    entities = aggregator.aggregate(
        [
            [Entity(0, len("John Meyers"), "PERSON", frozenset(["EISM"]))],
            [Entity(0, len("John"), "PERSON", frozenset(["UPI"]))],
        ],
        "John Meyers",
    )

    assert entities
    assert len(entities) == 2, entities


def test_silly_with_fake_UPI_invert():
    aggregator = Aggregator(AggregatorConfiguration(merge_entities=True))

    entities = aggregator.aggregate(
        [
            [Entity(0, len("John Meyers"), "PERSON", frozenset(["EISM"]))],
            [Entity(0, len("John"), "PERSON", frozenset(["UPI"]))],
        ],
        "John Meyers",
    )

    assert entities
    assert len(entities) == 1, entities


def test_silly_with_fake_UPI():
    aggregator = Aggregator(AggregatorConfiguration(merge_entities=True))

    merged = aggregator.aggregate(
        [
            [Entity(0, len("John"), "PERSON", frozenset(["EISM"]))],
            [Entity(0, len("John Meyers"), "PERSON", frozenset(["UPI"]))],
        ],
        "John Meyers",
    )

    assert merged
    assert merged
    assert len(merged) == 1


def test_included_are_merged_when_type_is_consistent():
    aggregator = Aggregator(AggregatorConfiguration(merge_entities=True))

    entities = aggregator.aggregate(
        [
            [Entity(1, 1 + len("ohn"), "FOO", frozenset(["EISM"]))],
            [Entity(0, len("John Meyers"), "FOO", frozenset(["EISM"]))],
        ],
        "John Meyers",
    )

    assert entities
    assert len(entities) == 1

    assert entities[0].source == frozenset(["EISM"])
    assert entities[0].entity_type == "FOO"


def test_overlapping_are_merged_directly():
    aggregator = Aggregator(AggregatorConfiguration())

    entities = aggregator.aggregate(
        [
            [Entity(0, len("John"), "FOO", frozenset(["EISM"]))],
            [Entity(0, len("John"), "FOO", frozenset(["EISM"]))],
        ],
        "John Meyers lives in Montana",
    )

    assert entities
    assert len(entities) == 1
    assert entities[0].source == frozenset(["EISM"])
    assert entities[0].entity_type == "FOO"


def test_included_entities_are_generalized_to_the_including_type():
    aggregator = Aggregator(AggregatorConfiguration(merge_entities=True))

    entities = aggregator.aggregate(
        [
            [Entity(0, 5, "BAR", frozenset(["EISM"]))],
            [Entity(1, 3, "BAR", frozenset(["EISM"]))],
        ],
        "BAR",
    )

    assert entities
    assert len(entities) == 1
    assert entities[0].entity_type == "BAR"
    assert entities[0].source == frozenset({"EISM"})


def test_removal_of_null_scores():
    aggregator = Aggregator(
        AggregatorConfiguration(
            weights={"FOO": {"DRL": 0.0}},
            default_weight=1.0,
        ),
    )

    entities = aggregator.aggregate(
        [
            [Entity(0, len("FOO"), "FOO", frozenset(["DRL"]))],
            [Entity(len("FOO "), len("FOO ") + len("JOHN"), "FOO", frozenset(["EISM"]))],
        ],
        "FOO JOHN",
    )

    assert entities

    assert len(entities) == 1
    assert entities[0].entity_type == "FOO"
    assert entities[0].source == frozenset({"EISM"})


def test_dropping_of_unreliable_annotations():
    aggregator = Aggregator(
        AggregatorConfiguration(
            weights={
                "FOO": {
                    "RISKY": -1.0,
                },
            },
        ),
    )

    aggregated = aggregator.aggregate(
        [
            [Entity(0, len("email@json.com"), "FOO", frozenset(["EISM"]))],
            [Entity(0, len("email@json.com."), "FOO", frozenset(["RISKY"]))],
        ],
        "email@json.com",
    )

    assert aggregated
    assert len(aggregated) == 1
    assert aggregated[0].entity_type == "FOO"
    assert aggregated[0].source == frozenset({"EISM"})
    assert aggregated[0].end == len("email@json.com")


def test_split_and_merge_entity_list():
    aggregator = Aggregator()

    # empty entity list
    entity_list_0: list[Entity] = []
    merged_entity_list_0 = aggregator.split_and_merge(entity_list_0)
    assert entity_list_0 == merged_entity_list_0

    # entity list has only one entity
    entity_list_1 = [Entity(150, 157, "PERSON", frozenset(["EISM"]))]
    merged_entity_list_1 = aggregator.split_and_merge(entity_list_1)

    assert entity_list_1 == merged_entity_list_1


def test_threshold_for_cleaning():
    aggregator = Aggregator(
        AggregatorConfiguration(
            weights={
                "Person": {
                    "FOO_1": 400.0,
                    "FOO_2": 400.0,
                    "BAR": 500.0,
                },
            },
            thresholds={
                "Person": 900.0,
            },
        ),
    )

    text = "John Doe is a nice person"

    merged = aggregator.aggregate(
        [
            [Entity(0, len("John Doe"), "Person", frozenset(["BAR"]))],
            [Entity(0, len(text), "Person", frozenset(["FOO_1"]))],
            [Entity(0, len(text), "Person", frozenset(["FOO_2"]))],
        ],
        text,
    )

    assert len(merged) == 1

    merged_2 = aggregator.aggregate(
        [
            [Entity(0, len("John Doe"), "Person", frozenset(["BAR"]))],
        ],
        text,
    )

    assert len(merged_2) == 0


def test_aggregation_different_tokenizers():
    weights: dict[str, dict[str, float]] = {
        "Person": {"STANZA": 1000, "SPACY": 500},
        "FAC": {"SPACY": -1, "STANZA": -1},
        "Phone": {"DRL": 1000},
        "URI": {"DRL": 400},
        "Date": {"DRL": 1000, "STANZA": 500, "SPACY": 500},
        "DayOfTheWeek": {"DRL": -1},
        "Email": {"DRL": 1000},
        "IBAN": {"DRL": 1000},
        "Location": {"SPACY": 500, "STANZA": 500},
        "PhoneNumber": {"DRL": 1000},
        "CreditCard": {"DRL": 1000},
        "CARDINAL": {"SPACY": -1, "STANZA": -1},
        "WORK_OF_ART": {"SPACY": -1, "STANZA": -1},
        "ORDINAL": {"SPACY": -1, "STANZA": -1},
        "LAW": {"SPACY": -1, "STANZA": -1},
        "QUANTITY": {"SPACY": -1, "STANZA": -1},
        "MONEY": {"SPACY": -1, "STANZA": -1},
        "NORP": {"SPACY": -1, "STANZA": -1},
        "EVENT": {"SPACY": -1, "STANZA": -1},
        "PRODUCT": {"SPACY": -1, "STANZA": -1},
        "PERCENT": {"SPACY": -1, "STANZA": -1},
        "LANGUAGE": {"SPACY": -1, "STANZA": -1},
        "ZipCode": {"DRL": 1200},
        "UKPostCode": {"DRL": 1200},
    }

    data = "my email is: john.doe@ie.ibm.com"

    entities1 = [Entity(len("my_email is: "), len(data), "Email", frozenset(["DRL"]))]
    entities2 = [Entity(len("my_email is: "), len(data), "URI", frozenset(["STANZA"]))]
    entities3 = [
        Entity(len("my_email is: john"), len("my_email is: john.doe"), "NAME", frozenset(["SPACY"])),
        Entity(len("my_email is: john.doe"), len(data), "URI", frozenset(["Spacy"])),
    ]

    configuration = AggregatorConfiguration(
        prioritize_inclusion=True, prune_negative_scores=True, weights=weights, merge_entities=True
    )
    aggregator = Aggregator(configuration=configuration)
    aggregated = aggregator.aggregate([entities1, entities2, entities3], data)

    assert aggregated is not None
    assert len(aggregated) == 1, [data[e.start : e.end] for e in aggregated]


def test_pos_new_version():
    text = """The median household income in New Buffalo, Michigan 49117 is\n$40,676."""

    entities = [
        [
            Entity(
                len("The median household income in "),
                len("The median household income in New Buffalo, Michigan 49117 is"),
                "ADDRESS",
                frozenset(["FOO"]),
            )
        ],
        [
            Entity(
                len("The median household income in New Buffalo, Michigan 49117 "),
                len("The median household income in New Buffalo, Michigan 49117 is"),
                "",
                frozenset(["BAR"]),
                frozenset(["VERB"]),
            )
        ],
    ]

    aggregator = Aggregator(
        AggregatorConfiguration(
            validate_part_of_speech=True,
        ),
    )

    filtered = aggregator.aggregate(entities, text)

    assert len(filtered) == 1


@pytest.mark.skip()
def test_weird_rw_example():
    configuration = AggregatorConfiguration(
        prioritize_inclusion=False,
        weights={
            "ZipCode": {"DRL": 1200},
            "UKPostCode": {"DRL": 1200},
            "USPostalAddress": {"DRL": 1200},
            "Person": {"STANZA": 1000, "SPACY": 450, "SPACY_ML": 450},
            "Phone": {"DRL": 1000},
            "URI": {"DRL": 400},
            "SSN": {"DRL": 1200},
            "NationalIdentity": {"DRL": 1200},
            "Date": {"DRL": 1000, "STANZA": 500, "SPACY": 500},
            "Email": {"DRL": 2000},
            "IBAN": {"DRL": 4000},
            "Location": {"SPACY": 500, "STANZA": 500},
            "PhoneNumber": {"DRL": 1000},
            "CreditCard": {"DRL": 1000},
            "LOC": {"SPACY": 1000, "STANZA": 1000},
            "CARDINAL": {"SPACY": -1, "STANZA": -1},
            "WORK_OF_ART": {"SPACY": -1, "STANZA": -1},
            "ORDINAL": {"SPACY": -1, "STANZA": -1},
            "LAW": {"SPACY": -1, "STANZA": -1},
            "QUANTITY": {"SPACY": -1, "STANZA": -1},
            "MONEY": {"SPACY": -1, "STANZA": -1},
            "EVENT": {"SPACY": -1, "STANZA": -1},
            "PRODUCT": {"SPACY": -1, "STANZA": -1},
            "PERCENT": {"SPACY": -1, "STANZA": -1},
            "LANGUAGE": {"SPACY": -1, "STANZA": -1},
            "MISC": {"SPACY_ML": -1},
            "FAC": {"SPACY": -1, "STANZA": -1},
        },
        thresholds={
            "Person": 900.0,
        },
    )
    aggregator = Aggregator(configuration)

    text = "Courtney Diazhttps://plus.google.com/116772881542245481974noreply@blogger.comBlogger5125tag:blogger.com,1999:blog-5522637171272631985.post-23565846884882250562016-09-13T12:41:02.296+10:002016-09-13T12:41:02.296+10:00Courtney, beautiful work!!"

    entities = [
        [Entity(0, 224, "Person", frozenset(["SPACY_ML"]))],
        [Entity(0, 225, "Person", frozenset(["SPACY"]))],
        [Entity(0, 8, "Person", frozenset(["STANZA"]))],
        [
            Entity(142, 158, "CreditCard", frozenset(["DRL"])),
            Entity(158, 168, "Date", frozenset(["DRL"])),
            Entity(187, 210, "Date", frozenset(["DRL"])),
            Entity(158, 181, "Date", frozenset(["DRL"])),
            Entity(187, 197, "Date", frozenset(["DRL"])),
            Entity(88, 92, "URI", frozenset(["DRL"])),
            Entity(13, 58, "URI", frozenset(["DRL"])),
            Entity(13, 36, "URI", frozenset(["DRL"])),
            Entity(13, 26, "URI", frozenset(["DRL"])),
            Entity(13, 49, "URI", frozenset(["DRL"])),
            Entity(13, 59, "URI", frozenset(["DRL"])),
            Entity(13, 37, "URI", frozenset(["DRL"])),
            Entity(13, 21, "URI", frozenset(["DRL"])),
            Entity(52, 77, "Email", frozenset(["DRL"])),
            Entity(13, 32, "URI", frozenset(["DRL"])),
            Entity(88, 100, "URI", frozenset(["DRL"])),
            Entity(42, 77, "Email", frozenset(["DRL"])),
            Entity(37, 77, "Email", frozenset(["DRL"])),
            Entity(13, 33, "URI", frozenset(["DRL"])),
            Entity(13, 45, "URI", frozenset(["DRL"])),
            Entity(54, 77, "Email", frozenset(["DRL"])),
            Entity(88, 103, "URI", frozenset(["DRL"])),
            Entity(39, 77, "Email", frozenset(["DRL"])),
            Entity(62, 77, "Email", frozenset(["DRL"])),
            Entity(13, 47, "URI", frozenset(["DRL"])),
            Entity(45, 77, "Email", frozenset(["DRL"])),
            Entity(13, 54, "URI", frozenset(["DRL"])),
            Entity(58, 77, "Email", frozenset(["DRL"])),
            Entity(88, 99, "URI", frozenset(["DRL"])),
            Entity(13, 42, "URI", frozenset(["DRL"])),
            Entity(13, 65, "URI", frozenset(["DRL"])),
            Entity(13, 25, "URI", frozenset(["DRL"])),
        ],
    ]
    merged = aggregator.aggregate(entities, text)

    fail("\n".join(f"{text[e.start : e.end]} {e.entity_type} {e.start} {e.end} {e.source}" for e in merged))


def test_confidence_score():
    aggregator = Aggregator(
        AggregatorConfiguration(
            to_report_only={"Person", "Location"},
            weights={
                "Person": {
                    "FOO_1": 450.0,
                    "FOO_2": 400.0,
                    "BAR": 500.0,
                },
                "Location": {
                    "FOO_1": 100.0,
                    "FOO_2": 400.0,
                    "BAR": 500.0,
                },
            },
            thresholds={
                "Person": 100.0,
            },
        ),
    )

    text = "John Doe is a nice person"

    merged = aggregator.aggregate(
        [
            [Entity(0, len("John"), "Person", frozenset(["BAR"]))],
            [Entity(len("John "), len("John ") + len("Doe"), "Person", frozenset(["BAR"]))],
            [Entity(len("John "), len("John ") + len("Doe"), "Location", frozenset(["FOO_1"]))],
        ],
        text,
    )

    assert len(merged) == 2
    assert merged[0].confidence == 1.0
    assert merged[1].confidence == 0.8


def test_pos_not_lost():
    aggregator = Aggregator(
        AggregatorConfiguration(
            validate_part_of_speech=True,
            prioritize_inclusion=False,
        )
    )

    text = "this is simple text"

    merged = aggregator.aggregate(
        [
            [Entity(len("this "), len("this is"), "", frozenset(["foo"]), frozenset(["VERB"]))],
            [Entity(len("this "), len("this is"), "NAME", frozenset(["foo"]))],
        ],
        text,
    )

    assert len(merged) == 0
