"""Network identifier for detecting IP addresses and URIs.

This module provides identifiers for recognizing IPv4 addresses, IPv6 addresses,
IP addresses (both versions), and URIs/URLs.
"""

from ipaddress import AddressValueError, IPv4Address, IPv6Address
from logging import getLogger
from pathlib import Path
from typing import Final
from urllib.parse import quote, urlparse

from risk_assessment.classification.identifiers import Identifier


def _valid_characters(text: str | None) -> bool:
    """Check if text contains only valid URL-encoded characters.

    Args:
        text: The text to check.

    Returns:
        True if text is None, empty, or contains only valid URL characters, False otherwise.
    """
    if text is not None:
        if len(text):
            return quote(text) == text

    return True


def _load_known_schemas() -> list[str]:
    """Load known URI schemes from data file.

    Returns:
        List of known URI scheme names.
    """
    with (Path(__file__).parent / "data" / "common" / "uri-schemes-1.csv").open("r") as input:
        return [line.split(",")[0] for line in input if len(line.strip())]


KNOWN_SCHEMAS: Final[list[str]] = _load_known_schemas()


def _valid_scheme(text: str) -> bool:
    """Check if text is a valid and known URI scheme.

    Args:
        text: The scheme to check.

    Returns:
        True if scheme is valid and in the known schemes list, False otherwise.
    """
    return quote(text) == text and text in KNOWN_SCHEMAS


def _valid_ipv6_hostname(text: str) -> bool:
    """Check if text is a valid IPv6 address.

    Args:
        text: The text to check.

    Returns:
        True if text is a valid IPv6 address, False otherwise.
    """
    try:
        if IPv6Address(text) is not None:
            return True
    except AddressValueError:
        pass
    return False


def _valid_hostname(text: str | None) -> bool:
    """Check if text is a valid hostname.

    Args:
        text: The hostname to check.

    Returns:
        True if hostname is None, contains valid characters, or is a valid IPv6 address.
    """
    if text is None or _valid_characters(text):
        return True
    else:
        return _valid_ipv6_hostname(text)


class IPv4(Identifier):
    """Identifier for IPv4 addresses.

    Example:
        >>> identifier = IPv4()
        >>> identifier.is_of_this_type("192.168.1.1")
        True
        >>> identifier.is_of_this_type("256.1.1.1")
        False
    """

    def is_of_this_type(self, text: str) -> bool:
        """Check if text is a valid IPv4 address.

        Args:
            text: The text to check.

        Returns:
            True if text is a valid IPv4 address, False otherwise.
        """
        try:
            if IPv4Address(text) is not None:
                return True
        except AddressValueError:
            pass

        return False


class IPv6(Identifier):
    """Identifier for IPv6 addresses.

    Example:
        >>> identifier = IPv6()
        >>> identifier.is_of_this_type("2001:0db8:85a3:0000:0000:8a2e:0370:7334")
        True
        >>> identifier.is_of_this_type("::1")
        True
    """

    def is_of_this_type(self, text: str, allow_double_colon: bool = True) -> bool:
        """Check if text is a valid IPv6 address.

        Args:
            text: The text to check.
            allow_double_colon: If False, reject "::" notation. Defaults to True.

        Returns:
            True if text is a valid IPv6 address, False otherwise.
        """
        try:
            if IPv6Address(text) is not None:
                if text == "::" and not allow_double_colon:
                    return False
                return True
        except AddressValueError:
            pass

        return False


class IP(Identifier):
    """Identifier for IP addresses (both IPv4 and IPv6).

    Example:
        >>> identifier = IP()
        >>> identifier.is_of_this_type("192.168.1.1")
        True
        >>> identifier.is_of_this_type("2001:0db8::1")
        True
    """

    _ipv4 = IPv4()
    _ipv6 = IPv6()

    def __init__(self, allow_double_colon: bool = True) -> None:
        """Initialize the IP identifier.

        Args:
            allow_double_colon: If False, reject "::" notation in IPv6. Defaults to True.
        """
        super().__init__()
        self.allow_double_colon: bool = allow_double_colon

    def is_of_this_type(self, text: str) -> bool:
        """Check if text is a valid IP address (IPv4 or IPv6).

        Args:
            text: The text to check.

        Returns:
            True if text is a valid IPv4 or IPv6 address, False otherwise.
        """
        return IP._ipv4.is_of_this_type(text) or IP._ipv6.is_of_this_type(text, self.allow_double_colon)


class URI(Identifier):
    """Identifier for URIs and URLs.

    Validates URIs by checking scheme, hostname, and path components.
    Also handles common patterns like "www." and "mail." prefixes.

    Example:
        >>> identifier = URI()
        >>> identifier.is_of_this_type("https://example.com/path")
        True
        >>> identifier.is_of_this_type("www.example.com")
        True
        >>> identifier.is_of_this_type("ftp://files.example.org")
        True
    """

    logger = getLogger(__name__)

    def is_of_this_type(self, text: str) -> bool:
        """Check if text is a valid URI.

        Args:
            text: The text to check.

        Returns:
            True if text is a valid URI with known scheme and valid components, False otherwise.
        """
        if len(text.strip()) != len(text):
            return False
        try:
            result = urlparse(text)

            if result is not None:
                if result.scheme and _valid_scheme(result.scheme):
                    if _valid_hostname(result.hostname):
                        if _valid_characters(result.path):
                            return True
                else:
                    if text.startswith("www.") or text.startswith("mail."):
                        return self.is_of_this_type(f"http://{text}")

        except Exception:
            return False

        return False
