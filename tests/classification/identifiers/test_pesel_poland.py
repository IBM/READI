from risk_assessment.classification.identifiers import PESELPoland


def test_PESELPoland():
    identifier = PESELPoland()

    assert not identifier.is_of_this_type("12111678904"), "12111678904"
    assert identifier.is_of_this_type("12111678908"), "12111678908"


def test_PESELPoland_centuries():
    identifier = PESELPoland()

    assert identifier.is_of_this_type("12111678908"), "12111678908"  # 1900-1999
    assert identifier.is_of_this_type("12911678902"), "12911678902"  # 1800-1899
    assert identifier.is_of_this_type("12311678904"), "12311678904"  # 2000-2099
    assert identifier.is_of_this_type("12711678906"), "12711678906"  # 2200-2299
    assert identifier.is_of_this_type("12511678900"), "12511678900"  # 2100-2199
