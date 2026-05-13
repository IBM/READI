import re

from risk_assessment.classification.identifiers import (
    Identifier,
    RegexIdentifier,
    RegexIdentifierWithSpan,
)


class Phone(Identifier):
    def __init__(self) -> None:
        self.supported_phone_types: list[Identifier] = [
            USPhone(),
            PhoneNumber(),
            MissingOnes(),
        ]

    def is_of_this_type(self, text: str) -> bool:
        return any(identifier.is_of_this_type(text) for identifier in self.supported_phone_types)


class MissingOnes(RegexIdentifier):
    def __init__(self) -> None:
        super().__init__(
            "Phone",
            [
                re.compile(r"^\d{3} \d{4} \d{4}$", re.U),
                re.compile(r"^\d{5} \d{3} ?\d{3}$", re.U),
                re.compile(r"^\d{4}\.\d{3}\.\d{3}$", re.U),
                re.compile(r"^\d{4}-\d{3}-\d{3}$", re.U),
                re.compile(r"^\d{4} \d{3} \d{3}$", re.U),
                re.compile(r"^\d{4}[ \.-]\d{4}$", re.U),
                re.compile(r"^\d{2}\.\d{4}\.\d{4}$", re.U),
                re.compile(r"^\(\d{2}\) ?\d{4} ?\d{4}$", re.U),
                re.compile(r"^\(\d{2}\)-\d{4}-\d{4}$", re.U),
                re.compile(r"^\(\d{2}\)\.\d{4}\.\d{4}$", re.U),
                re.compile(r"^\(\d{2}\) \d{4} \d{4}$", re.U),
                re.compile(r"^\(\d{3,4}\) ?\d{3,4} ?\d{4}$", re.U),
                re.compile(r"^\(\d{5}\) ?\d{3} ?\d{3,4}$", re.U),
                re.compile(r"^\d{4} \d{7}$", re.U),
                re.compile(r"^\d{2} \d{4} \d{4}$", re.U),
                re.compile(r"^\d{2}-\d{4}-\d{4}$", re.U),
                re.compile(r"^\d{4} \d{3} \d{4}$", re.U),
                re.compile(r"^\+\d{2,3} ?\(0\) ?\d{2} ?\d{4} ?\d{4}$", re.U),
                re.compile(r"^\+\d{2}-\d{3}-\d{3}-\d{3}$", re.U),
                re.compile(r"^\+\d{2}\(0\)\d{3} \d{7}$", re.U),
                re.compile(r"^\+\d{2}\(0\)\d{3}\d{6}$", re.U),
                re.compile(r"^\+\d{2}\(0\)\d{2} ?\d{7}$", re.U),
                re.compile(r"^\+\d{2}\(0\)\d{4} ?\d{6}$", re.U),
                re.compile(r"^\+\d{2}\(0\)\d{4} ?\d{3} ?\d{3}$", re.U),
                re.compile(r"^\+\d{2}\.\d\.\d{4}\.\d{4}$", re.U),
                re.compile(r"^\+\d{2}-\d-\d{4}-\d{4}$", re.U),
                re.compile(r"^\+\d{2} \d \d{4} \d{4}$", re.U),
                re.compile(r"^\+\d{4} \d{4} ?\d{4}$", re.U),
                re.compile(r"^\+\d{2}\.\d{3}\.\d{3}\.\d{3}$", re.U),
                re.compile(r"^\+\d{4} \d{7}$", re.U),
                re.compile(r"^\+\d{6} \d{3} ?\d{3}$", re.U),
                re.compile(r"^\+?1 \(\d{3}\) \d{3}-\d{4}$"),
                re.compile(r"^\+\d{2} ?\d{3} ?\d{3} ?\d{3}$"),
                re.compile(r"^\d{8}$"),
            ],
        )


class USPhone(RegexIdentifier):
    def __init__(self) -> None:
        super().__init__(
            "Phone",
            [
                re.compile(r"^\(\d{3}\)-\d{3}-\d{4}$"),
                re.compile(r"^\d{3}-\d{3}-\d{4}$"),
            ],
        )


_PREFIXES: str = r"(?:(?:Pgr|Ph|[Pp]hone|Fax|Contact):?\s+#?)?"
_EXTENSION: str = r"(?:\s*x\d{3,5})?"


class PhoneNumber(RegexIdentifierWithSpan):
    def __init__(self) -> None:
        super().__init__(
            "Phone",
            [
                re.compile(r"^" + _PREFIXES + r"(\(\d{3}\)[- ]?\d{3}[- ]?\d{4}" + _EXTENSION + r")$"),
                re.compile(
                    r"^" + _PREFIXES + r"((?:\+|00)\d{2}[- ]?\(?\d{3}\)?[- ]?\d{3}[- ]?\d{4}" + _EXTENSION + r")$"
                ),
                re.compile(r"^" + _PREFIXES + r"((?:\+|00)\d{3}[- ]?\d{2}[- ]?\d{3}[- ]?\d{4}" + _EXTENSION + r")$"),
                re.compile(
                    r"^" + _PREFIXES + r"((?:\+|00)\d{3}[- ]?\(?\d{3}\)?[- ]?\d{3}[- ]?\d{4}" + _EXTENSION + r")$"
                ),
                re.compile(r"^" + _PREFIXES + r"(\(?\d{3}\)?[- ]\d{4,5}" + _EXTENSION + r")$"),
                re.compile(r"^" + _PREFIXES + r"(\d{3}-\d{3}-\d{4}" + _EXTENSION + r")$"),
                re.compile(
                    r"^" + _PREFIXES + r"(\d{3}[- ]?(?:\d{2}[- ]?){2}\d{3}" + _EXTENSION + r")$"
                ),  # italy mobile
                re.compile(r"^" + _PREFIXES + r"(0\d{2}[ ]?\d{8}" + _EXTENSION + r")$"),  # uk
                re.compile(r"^" + _PREFIXES + r"(\(\+\d{2,3}\)0\d{10}" + _EXTENSION + r")$"),  # uk
                re.compile(r"^" + _PREFIXES + r"(\+44\(0\)\d{3} \d{3} \d{4}" + _EXTENSION + r")$"),  # uk
                re.compile(
                    r"^" + _PREFIXES + r"((?:\+|00)\d{2,3}[ -]?\(\d{3}\)[ -]?\d{4}[ -]?\d{4}" + _EXTENSION + r")$"
                ),  # US
                re.compile(r"^" + _PREFIXES + r"(\d{3}[- ]?\d{4}" + _EXTENSION + r")$"),  # US
                re.compile(r"^" + _PREFIXES + r"(\(\d{3}\)[- ]\d{3}[- ]?\d{4}" + _EXTENSION + r")$"),  # US
                re.compile(r"^" + _PREFIXES + r"(\d{3}[- ]\d{3}[- ]?\d{4}" + _EXTENSION + r")$"),  # US
                re.compile(r"^" + _PREFIXES + r"((?:\+|00)1[- ]\d{3}[- ]\d{3}[- ]?\d{4}" + _EXTENSION + r")$"),  # US
                re.compile(r"^" + _PREFIXES + r"(1[- ]\d{3}[- ]\d{3}[- ]?\d{4}" + _EXTENSION + r")$"),  # US
                re.compile(r"^" + _PREFIXES + r"(\d{3}[- ]\d{3}[- ]\d{3}[- ]?\d{4}" + _EXTENSION + r")$"),  # US
                re.compile(
                    r"^" + _PREFIXES + r"((?:\+|00)\d{2,3}[- ]\d{3}(?:[- ]\d{2}){3}" + _EXTENSION + r")$"
                ),  # Unknown
                re.compile(
                    r"^" + _PREFIXES + r"((?:\+|00)\d{1,3}\.\d{3}\.\d{3}\.\d{4}" + _EXTENSION + r")$"
                ),  # Unknown
                re.compile(r"^" + _PREFIXES + r"(\d{3}\.\d{3}\.\d{4}" + _EXTENSION + r")$"),  # French
            ],
        )

    def get_span_length_required_to_check(self) -> int:
        return len("Contact: ") + 5

    def is_of_this_type_with_span(self, text: str) -> tuple[bool, tuple[int, int] | None]:
        return super().is_of_this_type_with_span(text)

    def is_of_this_type(self, text: str) -> bool:
        return self.is_of_this_type_with_span(text)[0]
