import sys

import pytest

from risk_assessment.classification.identifiers import IP, IPv4, IPv6


def test_invalid():
    identifier = IP()

    assert not identifier.is_of_this_type("a.b.0.1")

    assert not identifier.is_of_this_type("1111.2.3.4")  # each prefix of IP address should be <= 255
    assert not identifier.is_of_this_type(".2.3.4")


def test_valid():
    identifier = IP()

    assert identifier.is_of_this_type("1.2.3.4"), "Fails IP v4"
    assert identifier.is_of_this_type("::"), "Fails IP v6"


def test_valid_no_double_colon_allowed():
    identifier = IP(allow_double_colon=False)

    assert not identifier.is_of_this_type("::")


def test_ipv4():
    identifier = IPv4()

    assert identifier.is_of_this_type("1.2.3.4")


@pytest.mark.skipif(sys.version_info < (3, 9), reason="requires python3.9 or higher")
def test_ipv6_second_take():
    valid = [
        r"fe80::7:8%eth0",
    ]

    identifier = IPv6()

    for ip in valid:
        assert identifier.is_of_this_type(ip), ip


def test_ipv6():
    identifier = IPv6()

    valid = [
        r"1:2:3:4:5:6:7:8",
        r"1::",
        r"1::8",
        r"1::7:8",
        r"1::6:7:8",
        r"1::5:6:7:8",
        r"1::4:5:6:7:8",
        r"1::3:4:5:6:7:8",
        r"::255.255.255.255",
        r"::ffff:255.255.255.255",
        r"::FFFF:255.255.255.255",
        r"::ffff:0:255.255.255.255",
        r"::FFFF:0:255.255.255.255",
        r"::AABB:0:255.255.255.255",
        r"2001:db8:3:4::192.0.2.33",
        r"64:ff9b::192.0.2.33",
        r"::a8dc:58:194.33.160.31",
    ]

    for ip in valid:
        assert identifier.is_of_this_type(ip), ip
