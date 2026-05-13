from risk_assessment.classification.identifiers import LanguageBasedDictionaryIdentifier


def test_expansion():
    identifier = LanguageBasedDictionaryIdentifier("FOOBAR", {"en": ["Gear"]}, False)

    assert identifier.is_of_this_type("gear"), "gear"
    assert identifier.is_of_this_type_with_language("gear", "en"), "gear in french"
    assert identifier.is_of_this_type_with_language("Engrenage", "fr"), "gear in french"
