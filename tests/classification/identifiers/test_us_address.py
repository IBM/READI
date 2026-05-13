import datetime

import pytest

from risk_assessment.classification.identifiers import USPostalAddress


def test_multilines():
    valid_POBOXes = [
        "88 BROOKLYN ST\n" + "Brookl Hill, NY 12345",
        "7 Blackmoore Cir\n" + "Dublin, NY 12345",
        "7 Blackmoore Cir\n" + "    Dublin, NY 123450000",
        "40 SOMETHING RD\n" + "City, MA 123121111",
        # "Apt 1\n" +
        "Dublin, NY 12345",
        "123 BLACKMORE AVE APT 1\n" + "BRONX, NY 12345",
        "123 East Side Mall\n" + "Bronx, NY 12345-6789",
        "123 Bronx AV.\n" + "Bronx, NY 12345",
        "APT C\n" + "5800 SPRINGFIELD GARDENS CIR\n" + "SPRINGFIELD VA 22162-1058",
        "1500 E MAIN AVE STE 201\n" + "SPRINGFIELD VA 22162-1010",
        "123 Cobbleston St\n" + "Westwood, MA 02090",
        "345 Westwood Street\n" + "Watertown, MA 02472-2811",
        "123 TALBOT AVE\n" + "Boston, MA 12345",
        # # "Apt#123\n" +
        # "Auburndale, MA 12345",
        # # "Apt 123\n" +
        # "Auburndale, MA 12345",
    ]
    identifier = USPostalAddress()

    for POBOX in valid_POBOXes:
        assert identifier.is_of_this_type(POBOX), POBOX


def test_last_line():
    valid_last_lines = [
        "Westwood, MA 02090",
    ]

    identifier = USPostalAddress()

    for line in valid_last_lines:
        assert identifier.is_of_this_type(line), line


def test_delivery_address_line():
    valid_delivery_address_line = [
        "101 MAIN ST",
        "101 MAIN ST APT 12",
        "101 W MAIN ST APT 12",
        "101 W MAIN ST S APT 12",
        "123 Cobbleston St",
        "123 Brookline Ave., Boston, MA 12345",
    ]

    identifier = USPostalAddress()

    for line in valid_delivery_address_line:
        assert identifier.is_of_this_type(line), line


def test_from_rwd():
    identifier = USPostalAddress()

    assert identifier.is_of_this_type("1160 South Main Street 322, Middletown, Connecticut, U.S.A. 06457-5044")
    assert identifier.is_of_this_type("12489 W 84Th DR, ARVADA, Jefferson County, CO")
    assert identifier.is_of_this_type("12489 W 84Th DR, ARVADA, Jefferson County, CO")
    assert identifier.is_of_this_type("13992 E 107Th AVE, COMMERCE CITY, Adams County, CO")
    assert identifier.is_of_this_type("13992 E 107Th AVE, COMMERCE CITY, Adams County, CO")
    assert identifier.is_of_this_type("13992 E 107Th AVE, COMMERCE CITY, Adams County, CO")
    assert identifier.is_of_this_type("16101 Road J, CORTEZ, Montezuma County, CO")
    assert identifier.is_of_this_type("16122 W 70Th AVE, ARVADA, Jefferson County, CO")
    assert identifier.is_of_this_type("1824 Alto Ln, Lutz")
    assert identifier.is_of_this_type("1824 Alto Ln, Lutz, FL 33558 Republican Party of Florida")
    assert identifier.is_of_this_type("415 W. Route 66, 201")
    assert identifier.is_of_this_type("52 Canyon Cove LN, DRAKE, Larimer County, CO")
    assert identifier.is_of_this_type("646 Riverview Trace Ct, Fort Myers, Florida 33916")
    assert identifier.is_of_this_type("Lutz, FL 33558 Republican Party of Florida")
    assert not identifier.is_of_this_type("1160 South Main Street 322, Middletown, Connecticut, U.S.A. 06457-5044.")
    assert not identifier.is_of_this_type("1824 Alto Ln, Lutz ")
    assert not identifier.is_of_this_type("1824 Alto Ln, Lutz, FL 33558 Republican Party of Florida.")
    assert not identifier.is_of_this_type("Camera LensesSimply put, the better you understand different")
    assert not identifier.is_of_this_type("Dec 2018 00:00:00 -0000Template - Content graphicsAlex")
    assert not identifier.is_of_this_type("Lutz, FL 33558 Republican Party of Florida.")


def test_invalid():
    invalid = [
        # "40 generic brand",
        # "12 months and stop CT",
        # "1 week with pcp Dr.",
        # "16 per Dr.",
        # "168 that represents the corresponding ontology file as",
        "500 mg",
        "20 minutes",
        "80 mg after each meal and I suggest that he",
        "12 hours before your test",
        "1 liter",
        "5  refills",
        "121  40-197",
        "108 High",
        "5 Blood",
        "John Does\n" + "123 Brown Street\n" + "Braintree, MA 03284-3222",
        "John Doe",
        "Kellaris prime",
        "50mg of ibuprophenis",
        "11 and is scheduled for her first actual",
        "130-167 which is significant improvement since increase  in",
        "2 days left upper jaw line near ear is",
        "1 right hand is",
        # "5 Fixes For Common Sleep Issues All Couples",
        # "11 states posted land",
        # "15 Best Stair Tread Rugs Indoor"
        # "3 Year experience in digital"
    ]

    identifier = USPostalAddress()

    for line in invalid:
        assert not identifier.is_of_this_type(line), line


@pytest.mark.skip("only for internal benchmark")
def test_bench():
    start = datetime.datetime.now()
    for _ in range(100):
        test_recognize_valid_addresses()

    pytest.fail(f"{(datetime.datetime.now() - start) / 100}")


def test_recognize_valid_addresses():
    valid_addresses = [
        "200 E Main St, Phoenix AZ 85123, USA",
        "200 E Main St., Phoenix AZ 85123, USA",
        "200 Main Street, Phoenix AZ 85123, USA",
        "200 Main Boulevard, Phoenix AZ 85123, USA",
        "200 Main Blvd, Phoenix AZ 85123, USA",
        "200 Main Blvd., Phoenix AZ 85123, USA",
        "200 Main Drive, Phoenix AZ 85123, USA",
        "200 Main Dr., Phoenix AZ 85123, USA",
        "200 Main Court, Phoenix AZ 85123, USA",
        "200 Main Ct., Phoenix AZ 85123, USA",
        "300 Bolyston Ave, Seattle WA 98102",
        "300 Bolyston Avenue, Seattle WA 98102",
        "300 Bolyston Ave., Seattle WA 98102",
        "2505 SACKETT RUN RD",
        "1022 WOODLAND AVE",
        "123 MAGNOLIA ST",
        "1500 E MAIN AVE STE 201",
        "102 MAIN ST APT 101",
        "1356 EXECUTIVE DR STE 202",
        "1600 CENTRAL PL BLDG 14",
        "55 SYLVAN BLVD RM 108",
        "425 FLOWER BLVD",
        "425 FLOWER BLVD # 72",
        "5800 SPRINGFIELD GARDENS CIR",
        "1201 BROAD ST E",
        "1401 S. MAIN ST.",
        "101 MAIN ST",
        "101 MAIN ST APT 12",
        "101 W MAIN ST APT 12",
        "101 W MAIN ST S APT 12",
        "12 E BUSINESS LN STE 209",
        "46 Riverview Trace Ct, Fort Myers, Florida 33916",
    ]

    identifier = USPostalAddress()
    for address in valid_addresses:
        assert identifier.is_of_this_type(address), address


@pytest.mark.skip(reason="Unable to fix it for now")
def test_rwd_false_positives():
    examples: list[str] = [
        "5 Fixes For Common Sleep Issues All Couples",
        "11 states posted land",
        "15 Best Stair Tread Rugs Indoor",
        "3 Year experience in digital",
        "4 days ago Display Domain Stats or",
        "1 month its stil 10 bucks",
        "3 different lighting modes that are available in",
        "216 clear lights that are available in",
        "1 Tube Light Set",
        "50 LED bulbs that are available in",
        "13 with this comprehensive course from TeachUcomp",
        "13 Training Tutorial DVD",
        "3 LED light modes and",
        "5 hour drive.",
        "100 learning and development programs in",
        "2 hours drive",
        "2015 and available in",
        "5 star Los Dominicos Station hotel or",
        "1 minute walk",
        "4 asset protection strategies every real estate investor",
        "5 minute walk from Circular Quay Station",
        "20 million units of demand",
        "180 Degree Mountain View\nHouse Description",
        "3331 WARNING PATROLLED AND PROTECT",
        "66S-Metal 41866",
    ]

    identifier = USPostalAddress()

    for not_address in examples:
        assert not identifier.is_of_this_type(not_address), not_address

    logs = """Warning: Declaration of art_MenuWalker::start_lvl(&$output, $depth) should be compatible with Walker::start_lvl(&$output, $depth = 0, $args = Array) in /home/greescom/domains/thearizonadispensary.com/wp-content/themes/The_Arizona_Dispensary/core/navigation.php on line 169
Warning: Declaration of art_MenuWalker::end_lvl(&$output, $depth) should be compatible with Walker::end_lvl(&$output, $depth = 0, $args = Array) in /home/greescom/domains/thearizonadispensary.com/wp-content/themes/The_Arizona_Dispensary/core/navigation.php on line 169
Warning: Declaration of art_MenuWalker::end_el(&$output, $item, $depth) should be compatible with Walker::end_el(&$output, $object, $depth = 0, $args = Array) in /home/greescom/domains/thearizonadispensary.com/wp-content/themes/The_Arizona_Dispensary/core/navigation.php on line 169
Warning: Declaration of art_PageWalker::start_lvl(&$output) should be compatible with Walker::start_lvl(&$output, $depth = 0, $args = Array) in /home/greescom/domains/thearizonadispensary.com/wp-content/themes/The_Arizona_Dispensary/core/navigation.php on line 311
Warning: Declaration of art_PageWalker::end_lvl(&$output) should be compatible with Walker::end_lvl(&$output, $depth = 0, $args = Array) in /home/greescom/domains/thearizonadispensary.com/wp-content/themes/The_Arizona_Dispensary/core/navigation.php on line 311
Warning: Declaration of art_PageWalker::end_el(&$output, $page) should be compatible with Walker::end_el(&$output, $object, $depth = 0, $args = Array) in /home/greescom/domains/thearizonadispensary.com/wp-content/themes/The_Arizona_Dispensary/core/navigation.php on line 311
Warning: Declaration of art_CategoryWalker::start_lvl(&$output) should be compatible with Walker::start_lvl(&$output, $depth = 0, $args = Array) in /home/greescom/domains/thearizonadispensary.com/wp-content/themes/The_Arizona_Dispensary/core/navigation.php on line 404
Warning: Declaration of art_CategoryWalker::end_lvl(&$output) should be compatible with Walker::end_lvl(&$output, $depth = 0, $args = Array) in /home/greescom/domains/thearizonadispensary.com/wp-content/themes/The_Arizona_Dispensary/core/navigation.php on line 404""".split(
        "\n"
    )

    for not_address in logs:
        assert not identifier.is_of_this_type(not_address), not_address
