import re

from nltk.tokenize import (
    TreebankWordTokenizer,
    WordPunctTokenizer,
)

from risk_assessment.classification.identifiers import (
    City,
    Country,
    Email,
    Name,
    Phone,
    RegexIdentifier,
    RegexIdentifierWithSpan,
)
from risk_assessment.classification.identifiers.network import IP
from risk_assessment.classification.unstructured.drl import (
    DRLEntityExtractor,
    ImprovedDRLEntityExtractor,
    _generate_shinglets,
)


def test_extractor_with_custom_name():
    data = "My name is John Doe and this is my email: john.doe@gmail.com"

    extractor0 = DRLEntityExtractor(
        identifiers=[
            Name(),
            Email(),
        ],
    )

    for e in extractor0.extract(data):
        assert e.source == frozenset(["DRL"])

    extractor1 = DRLEntityExtractor(
        identifiers=[
            Name(),
            Email(),
        ],
        name="DRL_treebank",
    )

    for e in extractor1.extract(data):
        assert e.source == frozenset({"DRL_treebank"})

    extractor2 = DRLEntityExtractor(
        identifiers=[
            Name(),
            Email(),
        ],
        tokenizer=WordPunctTokenizer(),
        name="DRL_word",
    )

    for e in extractor2.extract(data):
        assert e.source == frozenset(["DRL_word"])


def test_shinglet_generator():
    spans: list[tuple[int, int]] = [(0, 1), (1, 5), (5, 10)]

    shinglets = list(_generate_shinglets(spans))

    assert len(shinglets) == 6


def test_shinglet_generator_with_min():
    spans: list[tuple[int, int]] = [(0, 1), (1, 5), (5, 10)]

    shinglets = list(_generate_shinglets(spans, min_length=2))

    assert len(shinglets) == 3


def test_shinglet_generator_with_examples():
    spans: list[tuple[int, int]] = [(0, 1), (1, 5), (5, 10), (10, 11)]

    expected = [
        (0, 1),
        (0, 5),
        (0, 10),
        (0, 11),
        (1, 5),
        (1, 10),
        (1, 11),
        (5, 10),
        (5, 11),
        (10, 11),
    ]

    generated = list(_generate_shinglets(spans, max_length=5))

    assert len(generated) == len(expected)

    assert 0 == len(set(generated) - set(expected))

    for e, g in zip(expected, generated):
        assert e == g


def test_drl_extractor_basic():
    extractor = DRLEntityExtractor(
        identifiers=[
            City(),
            Country(),
            Name(),
        ],
    )

    entities = extractor.extract("""Ireland (/ˈaɪərlənd/ (listen) YRE-lənd; Irish: Éire [ˈeːɾʲə] (listen); Ulster-Scots: Airlann [ˈɑːrlən]) is an island in the North Atlantic Ocean, in north-western Europe. It is separated from Great Britain to its east by the North Channel, the Irish Sea, and St George's Channel. Ireland is the second-largest island of the British Isles, the third-largest in Europe, and the twentieth-largest on Earth.[8]

Geopolitically, Ireland is divided between the Republic of Ireland (officially named Ireland), which covers five-sixths of the island, and Northern Ireland, which is part of the United Kingdom. As of 2022, the population of the entire island is just over 7 million, with 5.1 million living in the Republic of Ireland and 1.9 million in Northern Ireland, ranking it the second-most populous island in Europe after Great Britain.[5]

The geography of Ireland comprises relatively low-lying mountains surrounding a central plain, with several navigable rivers extending inland. Its lush vegetation is a product of its mild but changeable climate which is free of extremes in temperature. Much of Ireland was woodland until the end of the Middle Ages. Today, woodland makes up about 10% of the island, compared with a European average of over 33%,[9] and most of it is non-native conifer plantations.[10][11] There are twenty-six extant land mammal species native to Ireland.[12] The Irish climate is influenced by the Atlantic Ocean and thus very moderate,[13] and winters are milder than expected for such a northerly area, although summers are cooler than those in continental Europe. Rainfall and cloud cover are abundant.

Gaelic Ireland had emerged by the 1st century AD. The island was Christianised from the 5th century onwards. Following the 12th century Anglo-Norman invasion, England claimed sovereignty. However, English rule did not extend over the whole island until the 16th–17th century Tudor conquest, which led to colonisation by settlers from Britain. In the 1690s, a system of Protestant English rule was designed to materially disadvantage the Catholic majority and Protestant dissenters, and was extended during the 18th century. With the Acts of Union in 1801, Ireland became a part of the United Kingdom. A war of independence in the early 20th century was followed by the partition of the island, thus creating the Irish Free State, which became increasingly sovereign over the following decades, and Northern Ireland, which remained a part of the United Kingdom. Northern Ireland saw much civil unrest from the late 1960s until the 1990s. This subsided following the Good Friday Agreement in 1998. In 1973, the Republic of Ireland joined the European Economic Community while the United Kingdom, and Northern Ireland, as part of it, did the same. In 2020, the United Kingdom, Northern Ireland included, left what was by then the European Union (EU).

Irish culture has had a significant influence on other cultures, especially in the field of literature. Alongside mainstream Western culture, a strong indigenous culture exists, as expressed through Gaelic games, Irish music, Irish language, and Irish dance. The island's culture shares many features with that of Great Britain, including the English language, and sports such as association football, rugby, horse racing, golf, and boxing.""")

    assert entities is not None
    assert len(entities) == 110

    assert len({entity.entity_type for entity in entities}) == 3


def test_from_secBU():
    text = "I'm an analyst named Charlie. You can contact me at (123)-456-7890. I live at Foobar street"

    extractor = DRLEntityExtractor(
        identifiers=[
            IP(),
            RegexIdentifier("TICKET_ID", [re.compile(r"SOCP\d+")]),
            RegexIdentifier("USERNAME", [re.compile(r"user ([:alnum:]{3,})")]),
            Phone(),
        ],
        tokenizer=WordPunctTokenizer(),
        max_shinglet_length=8,
    )

    entities = extractor.extract(text)

    assert len(entities) == 1, entities


def test_weird_pattern():
    text = "Set stronger access privileges for the user user_user1name and inform other administrators to do the same."

    extractor = DRLEntityExtractor(
        identifiers=[
            IP(),
            RegexIdentifier("TICKET_ID", [re.compile(r"SOCP\d+")]),
            RegexIdentifierWithSpan("USERNAME", [re.compile(r"user\s([a-z10-9_]{3,})")]),
            Phone(),
        ],
        tokenizer=WordPunctTokenizer(),
        max_shinglet_length=8,
    )

    entities = extractor.extract(text)

    assert len(entities) == 1


def test_improved_drl():
    text = "I'm an analyst named Charlie.You can contact me at...(123)-456-7890. I live at Foobar street"

    extractor = ImprovedDRLEntityExtractor(
        identifiers=[
            Phone(),
        ],
        tokenizer_list=[WordPunctTokenizer(), TreebankWordTokenizer()],
        max_shinglet_length=8,
    )

    entities = extractor.extract(text)

    assert len(entities) == 1, entities


def test_improved_drl_issue_with_merge():
    text = """Enable secret password z9M!@YkF@( for privileged mode!
Username lisa.rowe secret !#2UcNzWv
!
interface GigabitEthernet0/0
 ip address 192.137.119.100 255.255.255.0
 ipv6 address c056:4cc3:6f52:8528:798b:6fb4:9d53:d09e
!
interface GigabitEthernet0/1
 ip address 98.204.207.135 255.255.255.0
 ipv6 address aba2:3a20:4a2a:b44c:abfa:e101:8802:5cbe"""

    extractor = ImprovedDRLEntityExtractor(
        identifiers=[
            IP(),
        ],
        tokenizer_list=[WordPunctTokenizer(), TreebankWordTokenizer()],
        max_shinglet_length=15,
    )

    entities = extractor.extract(text)

    assert len(entities) == 6


def test_degenerate_example():
    text = " \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n "

    extractor = ImprovedDRLEntityExtractor(
        identifiers=[
            IP(),
        ],
        tokenizer_list=[WordPunctTokenizer(), TreebankWordTokenizer()],
        max_shinglet_length=15,
    )

    expected_empy = extractor.extract(text)

    assert len(expected_empy) == 0
