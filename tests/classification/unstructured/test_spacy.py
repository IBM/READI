from risk_assessment.classification.unstructured.spacy import SpacyEntityExtractor
from risk_assessment.classification.unstructured.utility import entity_to_text


def test_spacy_extractor_basic():
    text = """Ireland (/ˈaɪərlənd/ (listen) YRE-lənd; Irish: Éire [ˈeːɾʲə] (listen); Ulster-Scots: Airlann [ˈɑːrlən]) is an island in the North Atlantic Ocean, in north-western Europe. It is separated from Great Britain to its east by the North Channel, the Irish Sea, and St George's Channel. Ireland is the second-largest island of the British Isles, the third-largest in Europe, and the twentieth-largest on Earth.[8]

Geopolitically, Ireland is divided between the Republic of Ireland (officially named Ireland), which covers five-sixths of the island, and Northern Ireland, which is part of the United Kingdom. As of 2022, the population of the entire island is just over 7 million, with 5.1 million living in the Republic of Ireland and 1.9 million in Northern Ireland, ranking it the second-most populous island in Europe after Great Britain.[5]

The geography of Ireland comprises relatively low-lying mountains surrounding a central plain, with several navigable rivers extending inland. Its lush vegetation is a product of its mild but changeable climate which is free of extremes in temperature. Much of Ireland was woodland until the end of the Middle Ages. Today, woodland makes up about 10% of the island, compared with a European average of over 33%,[9] and most of it is non-native conifer plantations.[10][11] There are twenty-six extant land mammal species native to Ireland.[12] The Irish climate is influenced by the Atlantic Ocean and thus very moderate,[13] and winters are milder than expected for such a northerly area, although summers are cooler than those in continental Europe. Rainfall and cloud cover are abundant.

Gaelic Ireland had emerged by the 1st century AD. The island was Christianised from the 5th century onwards. Following the 12th century Anglo-Norman invasion, England claimed sovereignty. However, English rule did not extend over the whole island until the 16th–17th century Tudor conquest, which led to colonisation by settlers from Britain. In the 1690s, a system of Protestant English rule was designed to materially disadvantage the Catholic majority and Protestant dissenters, and was extended during the 18th century. With the Acts of Union in 1801, Ireland became a part of the United Kingdom. A war of independence in the early 20th century was followed by the partition of the island, thus creating the Irish Free State, which became increasingly sovereign over the following decades, and Northern Ireland, which remained a part of the United Kingdom. Northern Ireland saw much civil unrest from the late 1960s until the 1990s. This subsided following the Good Friday Agreement in 1998. In 1973, the Republic of Ireland joined the European Economic Community while the United Kingdom, and Northern Ireland, as part of it, did the same. In 2020, the United Kingdom, Northern Ireland included, left what was by then the European Union (EU).

Irish culture has had a significant influence on other cultures, especially in the field of literature. Alongside mainstream Western culture, a strong indigenous culture exists, as expressed through Gaelic games, Irish music, Irish language, and Irish dance. The island's culture shares many features with that of Great Britain, including the English language, and sports such as association football, rugby, horse racing, golf, and boxing.
"""
    entities = SpacyEntityExtractor("en_core_web_sm").extract(text)

    assert entities
    assert len({entity.entity_type for entity in entities}) == 10

    assert 100 >= len(entities) >= 85, {entity_to_text(entity, text) for entity in entities}
