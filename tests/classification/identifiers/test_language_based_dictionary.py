from unittest.mock import patch

import risk_assessment.classification.identifiers as identifiers_module


def test_expansion():
    identifier = identifiers_module.LanguageBasedDictionaryIdentifier("FOOBAR", {"en": ["Gear"]}, False)

    def fake_enrich(ident, language):
        ident.add_language(language, ["Engrenage"])

    assert identifier.is_of_this_type("gear"), "gear"
    assert identifier.is_of_this_type_with_language("gear", "en"), "gear in english"
    with patch.object(identifiers_module, "_enrich_with_language", side_effect=fake_enrich):
        assert identifier.is_of_this_type_with_language("Engrenage", "fr"), "gear in french"
