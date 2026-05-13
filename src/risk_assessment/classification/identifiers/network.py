import importlib.resources
from ipaddress import AddressValueError, IPv4Address, IPv6Address
from logging import getLogger
from typing import Final
from urllib.parse import quote, urlparse

from risk_assessment.classification.identifiers import Identifier


def _valid_characters(text: str | None) -> bool:
    if text is not None:
        if len(text):
            return quote(text) == text

    return True


def _load_known_schemas() -> list[str]:
    ref = importlib.resources.files(__package__).joinpath("data/common/uri-schemes-1.csv")
    with ref.open("r") as input:
        return [line.split(",")[0] for line in input if len(line.strip())]


KNOWN_SCHEMAS: Final[list[str]] = _load_known_schemas()


def _valid_scheme(text: str) -> bool:
    return quote(text) == text and text in KNOWN_SCHEMAS


def _valid_ipv6_hostname(text: str) -> bool:
    try:
        if IPv6Address(text) is not None:
            return True
    except AddressValueError:
        pass
    return False


def _valid_hostname(text: str | None) -> bool:
    if text is None or _valid_characters(text):
        return True
    else:
        return _valid_ipv6_hostname(text)


class IPv4(Identifier):
    def is_of_this_type(self, text: str) -> bool:
        try:
            if IPv4Address(text) is not None:
                return True
        except AddressValueError:
            pass

        return False


class IPv6(Identifier):
    def is_of_this_type(self, text: str, allow_double_colon: bool = True) -> bool:
        try:
            if IPv6Address(text) is not None:
                if text == "::" and not allow_double_colon:
                    return False
                return True
        except AddressValueError:
            pass

        return False


class IP(Identifier):
    _ipv4 = IPv4()
    _ipv6 = IPv6()

    def __init__(self, allow_double_colon: bool = True) -> None:
        super().__init__()
        self.allow_double_colon: bool = allow_double_colon

    def is_of_this_type(self, text: str) -> bool:
        return IP._ipv4.is_of_this_type(text) or IP._ipv6.is_of_this_type(text, self.allow_double_colon)


class URI(Identifier):
    logger = getLogger(__name__)

    def is_of_this_type(self, text: str) -> bool:
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
