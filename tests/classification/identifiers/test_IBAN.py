from risk_assessment.classification.identifiers import IBAN


def test_random(faker):
    identifier = IBAN()

    for _ in range(100):
        iban = faker.iban()

        assert identifier.is_of_this_type(iban), iban


def test_known_valid():
    valid = [
        "AD1400080001001234567890",  # Andorra
        "AE460090000000123456789",  # Arab Emirates
        "AL35202111090000000001234567",  # Albania
        "AT483200000012345864",  # Austria
        "AZ96AZEJ00000000001234567890",  # Azerbaijan
        "BE71096123456769",  # Belgium
        "BG18RZBB91550123456789",  # Bulgaria
        "BH02CITI00001077181611",  # Bahrain
        "BR1500000000000010932840814P2",  # Brazil
        "BY13NBRB3600900000002Z00AB00",  # Belarus
        "CH5604835012345678009",  # Switzerland
        "CR23015108410026012345",  # Costa Rica
        "CY21002001950000357001234567",  # Cyprus
        "CZ5508000000001234567899",  # Czech Republic
        "DK9520000123456789",  # Denmark
        "DO22ACAU00000000000123456789",  # Dominican Republic
        "EE471000001020145685",  # Estonia
        "EG800002000156789012345180002",  # Egypt
        "ES7921000813610123456789",  # Spain
        "FI1410093000123458",  # Finland
        "FO9264600123456789",  # Faroe Islands
        "FR7630006000011234567890189",  # France
        "GB33BUKB20201555555555",  # Great Britain
        "GE60NB0000000123456789",  # Georgia
        "GI04BARC000001234567890",  # Gibraltar
        "GL8964710123456789",  # Greenland
        "GR9608100010000001234567890",  # Greece
        "GT20AGRO00000000001234567890",  # Guatamala
        "HR1723600001101234565",  # Croatia
        "HU93116000060000000012345676",  # Hungary
        "IE64IRCE92050112345678",  # Ireland
        "IL170108000000012612345",  # Israel
        "IQ20CBIQ861800101010500",  # Iraq
        "IS750001121234563108962099",  # Iceland
        "IT60X0542811101000000123456",  # Italy
        "JO71CBJO0000000000001234567890",  # Jordan
        "KW81CBKU0000000000001234560101",  # Kuwait
        "KZ563190000012344567",  # Kazakhtan
        "LB92000700000000123123456123",  # Lebanon
        "LC14BOSL123456789012345678901234",  # Saint Lucia
        "LI7408806123456789012",  # Liechtenstein
        "LT601010012345678901",  # Lithuania
        "LU120010001234567891",  # Luxemburg
        "LV97HABA0012345678910",  # Latvia
        "MC5810096180790123456789085",  # Monaco
        "MD21EX000000000001234567",  # Moldova
        "ME25505000012345678951",  # Montenegro
        "MK07250120000058984",  # Macedonia
        "MR1300020001010000123456753",  # Mauritania
        "MT31MALT01100000000000000000123",  # Malta
        "MU43BOMM0101123456789101000MUR",  # Mauritius
        "NL02ABNA0123456789",  # Netherlands
        "NO8330001234567",  # Norway
        "PK36SCBL0000001123456702",  # Pakistan
        "PL10105000997603123456789123",  # Poland
        "PS92PALS000000000400123456702",  # Palestine
        "PT50002700000001234567833",  # Portugal
        "QA54QNBA000000000000693123456",  # Qatar
        "RO09BCYP0000001234567890",  # Romania
        "RS35105008123123123173",  # Serbia
        "SA4420000001234567891234",  # Saudi Arabia
        "SC52BAHL01031234567890123456USD",  # Seychelles
        "SE7280000810340009783242",  # Sweden
        "SI56192001234567892",  # Slovenia
        "SK8975000000000012345671",  # Slovakia
        "SM76P0854009812123456789123",  # San Marino
        "ST23000200000289355710148",  # Sao Tome and Principe
        "TL380010012345678910106",  # East Timor
        "TL380080012345678910157",  # East Timor,
        "TN5904018104004942712345",  # Tunisia
        "TR320010009999901234567890",  # Turkey
        "UA903052992990004149123456789",  # Ukraine
        "VA59001123000012345678",  # Vatican
        "VG21PACG0000000123456789",  # Virgin Islands
        "XK051212012345678906",  # Kosovo
    ]

    identifier = IBAN()

    for iban in valid:
        assert identifier.is_of_this_type(iban), iban


def test_known_invalid():
    identifier = IBAN()

    invalid = [
        "AL3520211109000000000123467",
        "AD14000800010012345678901",
        "BH02CTI00001077181611",
        "14703500735207SIJUOLAA.FI10",
        "147035007352072818193024211010-9151810",
        "FI14703500735207SIJUOLAA.FI10",
        "FI147035007352072818193024211010-9151810",
    ]

    for iban in invalid:
        assert not identifier.is_of_this_type(iban), iban


def test_positive():
    identifier = IBAN()

    assert identifier.is_of_this_type("GB82 WEST 1234 5698 7654 32"), "GB82 WEST 1234 5698 7654 32"
    assert identifier.is_of_this_type("IE71WZXH31864186813343"), "IE71WZXH31864186813343"


def test_negative():
    identifier = IBAN()

    assert not identifier.is_of_this_type("GR98"), "GR98"


def test_italy():
    identifier = IBAN()

    assert identifier.is_of_this_type("IT60X0542811101000000123456"), "IT60X0542811101000000123456"
    assert not identifier.is_of_this_type("IT50X0542811101000000123456"), "IT50X0542811101000000123456"
    assert not identifier.is_of_this_type("IT600542811101000000123456"), "IT600542811101000000123456"
    assert not identifier.is_of_this_type("IT60X054281101000000123456"), "IT60X054281101000000123456"
    assert not identifier.is_of_this_type("IT60X05428111101000000123456"), "IT60X05428111101000000123456"

    assert identifier.is_of_this_type("IT17L0311168870000000003654"), "IT17L0311168870000000003654"


def test_great_britain():
    identifier = IBAN()

    assert identifier.is_of_this_type("GB33BUKB20201555555555"), "GB33BUKB20201555555555"
    assert not identifier.is_of_this_type("GB23BUKB20201555555555"), "GB23BUKB20201555555555"
    assert not identifier.is_of_this_type("NL33BUKB20201555555555"), "NL33BUKB20201555555555"
    assert not identifier.is_of_this_type("GB33BKB20201555555555"), "GB33BKB20201555555555"
    assert not identifier.is_of_this_type("GB33BUKB2020155555555"), "GB33BUKB2020155555555"


def test_greece():
    identifier = IBAN()

    assert identifier.is_of_this_type("GR1601101250000000012300695"), "GR1601101250000000012300695"
    assert not identifier.is_of_this_type("GB23BUKB20201555555555"), "GB23BUKB20201555555555"
    assert not identifier.is_of_this_type("NL33BUKB20201555555555"), "NL33BUKB20201555555555"
    assert not identifier.is_of_this_type("GB33BKB20201555555555"), "GB33BKB20201555555555"
    assert not identifier.is_of_this_type("GB33BUKB2020155555555"), "GB33BUKB2020155555555"


def test_from_pile():
    identifier = IBAN()

    assert identifier.is_of_this_type("HR2623400091111064242")
    assert not identifier.is_of_this_type("HR2623400091111064242\n")

    assert not identifier.is_of_this_type("HR2623400091111064242\nBIC-")
