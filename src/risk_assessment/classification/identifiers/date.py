import re
from collections.abc import Callable, Iterable
from datetime import datetime
from re import Match, Pattern

import re2

from risk_assessment.classification.identifiers import Identifier


def _compute_unique_patterns(
    patterns: dict[str, Pattern[str]],
    ampm_patterns: dict[str, Pattern[str]],
    patterns_with_processing: dict[str, tuple[Pattern[str], Callable[[Match[str]], str]]],
) -> str:
    unique_patterns: set[str] = set()

    for pttrns in [patterns, ampm_patterns]:
        for pattern in pttrns.values():
            unique_patterns.add(pattern.pattern)

    for pattern, _ in patterns_with_processing.values():
        unique_patterns.add(pattern.pattern)

    return "|".join(unique_patterns)


class DateTime(Identifier):
    patterns: dict[str, Pattern[str]] = {
        r"%d %b %Y %H:%M:%S %z": re.compile(
            r"^\d{1,2} \w{3} \d{4} \d{1,2}:\d{1,2}:\d{1,2} [+-]?\d{2}\d{2}(?:\d{2}(?:\.\d{6})?)?$", re.I | re.U
        ),
        r"%Y%m%d%H%M": re.compile(r"^\d{4}\d{2}\d{2}\d{2}\d{2}$", re.I | re.U),
        r"%Y.%m.%d": re.compile(r"^\d{4}\.\d{2}\.\d{2}$", re.I | re.U),
        r"%d/%m/%Y": re.compile(r"^\d{1,2}/\d{1,2}/\d{4}$", re.I | re.U),
        r"%m/%d/%Y": re.compile(r"^\d{1,2}/\d{1,2}/\d{4}$", re.I | re.U),
        r"%d.%m.%Y": re.compile(r"^\d{2}\.\d{2}\.\d{4}$", re.I | re.U),
        r"%m.%d.%Y": re.compile(r"^\d{2}\.\d{2}\.\d{4}$", re.I | re.U),
        r"%Y-%m-%d": re.compile(r"^\d{4}-\d{1,2}-\d{1,2}$", re.I | re.U),
        r"%d-%m-%y": re.compile(r"^\d{1,2}-\d{1,2}-\d{2}$", re.I | re.U),
        r"%m-%d-%y": re.compile(r"^\d{1,2}-\d{1,2}-\d{2}$", re.I | re.U),
        r"%d-%m-%Y": re.compile(r"^\d{1,2}-\d{1,2}-\d{4}$", re.I | re.U),
        r"%m-%d-%Y": re.compile(r"^\d{1,2}-\d{1,2}-\d{4}$", re.I | re.U),
        r"%d/%m/%y": re.compile(r"^\d{1,2}/\d{1,2}/\d{2}$", re.I | re.U),
        r"%m/%d/%y": re.compile(r"^\d{1,2}/\d{1,2}/\d{2}$", re.I | re.U),
        r"%d-%m-%Y %H:%M:%S": re.compile(r"^\d{1,2}-\d{1,2}-\d{4} \d{2}:\d{2}:\d{2}$", re.I | re.U),
        r"%m-%d-%Y %H:%M:%S": re.compile(r"^\d{1,2}-\d{1,2}-\d{4} \d{2}:\d{2}:\d{2}$", re.I | re.U),
        r"%d/%m/%Y %H:%M:%S": re.compile(r"^\d{1,2}/\d{1,2}/\d{4} \d{2}:\d{2}:\d{2}$", re.I | re.U),
        r"%m/%d/%Y %H:%M:%S": re.compile(r"^\d{1,2}/\d{1,2}/\d{4} \d{2}:\d{2}:\d{2}$", re.I | re.U),
        r"%b %d, %Y": re.compile(r"^\w{3} \d{1,2}, \d{4}$", re.I | re.U),
        r"%b %d,%Y": re.compile(r"^\w{3} \d{1,2},\d{4}$", re.I | re.U),
        r"%b %d %Y": re.compile(r"^\w{3} \d{1,2} \d{4}$", re.I | re.U),
        r"%b %d, %y": re.compile(r"^\w{3} \d{1,2}, \d{2}$", re.I | re.U),
        r"%b %d,%y": re.compile(r"^\w{3} \d{1,2},\d{2}$", re.I | re.U),
        r"%b %d %y": re.compile(r"^\w{3} \d{1,2} \d{2}$", re.I | re.U),
        r"%B %d, %Y": re.compile(r"^\w{4,} \d{1,2}, \d{4}$", re.I | re.U),
        r"%B %d,%Y": re.compile(r"^\w{4,} \d{1,2},\d{4}$", re.I | re.U),
        r"%B %d %Y": re.compile(r"^\w{4,} \d{1,2} \d{4}$", re.I | re.U),
        r"%B the %d %Y": re.compile(r"^\w{4,} the \d{1}st \d{4}$", re.I | re.U),
        r"%B the %dst %Y": re.compile(r"^\w{4,} the \d{1,2}st \d{4}$", re.I | re.U),
        r"%B the %dnd %Y": re.compile(r"^\w{4,} the \d{1,2}nd \d{4}$", re.I | re.U),
        r"%B the %drd %Y": re.compile(r"^\w{4,} the \d{1,2}rd \d{4}$", re.I | re.U),
        r"%B the %dth %Y": re.compile(r"^\w{4,} the \d{1,2}th \d{4}$", re.I | re.U),
        r"%B the %dst, %Y": re.compile(r"^\w{4,} the \d{1,2}st, \d{4}$", re.I | re.U),
        r"%B the %dnd, %Y": re.compile(r"^\w{4,} the \d{1,2}nd, \d{4}$", re.I | re.U),
        r"%B the %drd, %Y": re.compile(r"^\w{4,} the \d{1,2}rd, \d{4}$", re.I | re.U),
        r"%B the %dth, %Y": re.compile(r"^\w{4,} the \d{1,2}th, \d{4}$", re.I | re.U),
        r"%d %b %y": re.compile(r"^\d{1,2} \w{3} \d{2}$", re.I | re.U),
        r"%d %b %Y": re.compile(r"^\d{1,2} \w{3} \d{4}$", re.I | re.U),
        r"%a, %d %b %Y %H:%M:%S %Z": re.compile(
            r"^\w{3}, \d{1,2} \w{3} \d{4} \d{1,2}:\d{1,2}:\d{1,2} \w{3}$", re.I | re.U
        ),
        r"%d-%B-%Y": re.compile(r"^\d{1,2}-\w{4,}-\d{4}$", re.I | re.U),
        r"%d-%b-%Y": re.compile(r"^\d{1,2}-\w{3}-\d{4}$", re.I | re.U),
        r"%B %dst, %Y": re.compile(r"^\w{4,} \d{1,2}st, \d{4}$", re.I | re.U),
        r"%B %dnd, %Y": re.compile(r"^\w{4,} \d{1,2}nd, \d{4}$", re.I | re.U),
        r"%B %drd, %Y": re.compile(r"^\w{4,} \d{1,2}rd, \d{4}$", re.I | re.U),
        r"%B %dth, %Y": re.compile(r"^\w{4,} \d{1,2}th, \d{4}$", re.I | re.U),
        r"%a %b %d %H:%M:%S %Y": re.compile(r"^\w{3} \w{3} \d{1,2} \d{1,2}:\d{1,2}:\d{1,2} \d{4}$", re.I | re.U),
        r"%a %b %d, %Y": re.compile(r"^\w{3} \w{3} \d{1,2}, \d{4}$", re.I | re.U),
        r"%B of %Y": re.compile(r"^\w{4,} of \d{4}$", re.I | re.U),
        r"%B %Y": re.compile(r"^\w{4,} \d{4}$", re.I | re.U),
        r"%d %B '%y": re.compile(r"^\d{1,2} \w{4,} '\d{2}$", re.I | re.U),
        r"'%y-%B": re.compile(r"^'\d{2}-\w{4,}$", re.I | re.U),
        r"%d %B %Y": re.compile(r"^\d{1,2} \w{4,} \d{4}$", re.I | re.U),
        r"%B %d": re.compile(r"^\w{4,} \d{1,2}$", re.I | re.U),
        r"%B %dst of this year": re.compile(r"^\w{4,} \d{1,2}st of this year$", re.I | re.U),
        r"%B %dnd of this year": re.compile(r"^\w{4,} \d{1,2}nd of this year$", re.I | re.U),
        r"%B %drd of this year": re.compile(r"^\w{4,} \d{1,2}rd of this year$", re.I | re.U),
        r"%B %dth of this year": re.compile(r"^\w{4,} \d{1,2}th of this year$", re.I | re.U),
        r"%Y-%m-%dT%H:%M:%S.%fZ": re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d+Z$", re.I | re.U),
        r"%Y-%m-%dT%H:%M:%S.%f": re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d+$", re.I | re.U),
        r"%Y-%m-%d %H:%M:%S.%f": re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d+$", re.I | re.U),
        r"%Y-%m-%dT%H:%M:%S.%f%z": re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{3}\+\d{2}:\d{2}$", re.I | re.U),
        r"%Y-%m-%d %H:%M:%S": re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$", re.I | re.U),
        r"%Y-%m-%dT%H:%M:%SZ": re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$", re.I | re.U),
        r"%d %b %Y %H:%M:%S": re.compile(r"^\d{2} \w{3} \d{4} \d{1,2}:\d{1,2}:\d{1,2}$", re.I | re.U),
        r"%d %B %Y %H:%M:%S %Z": re.compile(r"^\d{1,2} \w{3,} \d{4} \d{1,2}:\d{1,2}:\d{1,2} \w{3}$", re.I | re.U),
        r"%A %d %B %Y %H:%M:%S %Z": re.compile(
            r"^\w{3,} \d{1,2} \w{3,} \d{4} \d{1,2}:\d{1,2}:\d{1,2} \w{3}$", re.I | re.U
        ),
        r"%Y%b%d": re.compile(r"^\d{4}\w{1,}\d{1,2}\w{1,}\d{1,2}$", re.I | re.U),
        r"%Y年%m月%d": re.compile(r"^\d{4}年\d{1,2}月\d{1,2}$", re.I | re.U),
        r"%Y年%m月%d日": re.compile(r"^\d{4}年\d{1,2}月\d{1,2}日$", re.I | re.U),
        r"%y年": re.compile(r"^\d{2}年$", re.I | re.U),
        r"%y年%m月%d日": re.compile(r"^\d{2}年\d{1,2}月\d{1,2}日$", re.I | re.U),
        r"%y年%m・%d": re.compile(r"^\d{2}年\d{1,2}・\d{1,2}$", re.I | re.U),
        r"%y年%m": re.compile(r"^\d{2}年\d{1,2}$", re.I | re.U),
    }
    ampm_patterns: dict[str, Pattern[str]] = {
        r"%B %d, %Y %I:%M %p": re.compile(r"^\w{4,} \d{1,2}, \d{4} \d{1,2}:\d{1,2} [AP]M$", re.I | re.U),
        r"%a %b %d, %Y %I:%M %p": re.compile(r"^\w{3} \w{3} \d{1,2}, \d{4} \d{1,2}:\d{1,2} [AP]M$", re.I | re.U),
        r"%d/%m/%Y %I:%M %p": re.compile(r"^\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{1,2} [AP]M$", re.I | re.U),
        r"%m/%d/%Y %I:%M %p": re.compile(r"^\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{1,2} [AP]M$", re.I | re.U),
        r"%d/%m/%Y %I:%M:%S %p": re.compile(r"^\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{1,2}:\d{1,2} [AP]M$", re.I | re.U),
        r"%m/%d/%Y %I:%M:%S %p": re.compile(r"^\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{1,2}:\d{1,2} [AP]M$", re.I | re.U),
        r"%b %d, %Y %I:%M %p": re.compile(r"^\w{3} \d{1,2}, \d{4} \d{1,2}:\d{1,2} [AP]M$", re.I | re.U),
        r"%d/%m/%Y at %I:%M %p": re.compile(r"^\d{1,2}/\d{1,2}/\d{4} at \d{1,2}:\d{1,2} [AP]M$", re.I | re.U),
        r"%m/%d/%Y at %I:%M %p": re.compile(r"^\d{1,2}/\d{1,2}/\d{4} at \d{1,2}:\d{1,2} [AP]M$", re.I | re.U),
        r"%I:%M %p": re.compile(r"^\d{1,2}:\d{1,2} [AP]M$", re.I | re.U),
        r"%d/%m/%y at %I:%M %p": re.compile(r"^\d{1,2}/\d{1,2}/\d{2} at \d{1,2}:\d{1,2} [AP]M$", re.I | re.U),
        r"%m/%d/%y at %I:%M %p": re.compile(r"^\d{1,2}/\d{1,2}/\d{2} at \d{1,2}:\d{1,2} [AP]M$", re.I | re.U),
        r"%d/%m/%y at %I:%M%p": re.compile(r"^\d{1,2}/\d{1,2}/\d{2} at \d{1,2}:\d{1,2}[AP]M$", re.I | re.U),
        r"%m/%d/%y at %I:%M%p": re.compile(r"^\d{1,2}/\d{1,2}/\d{2} at \d{1,2}:\d{1,2}[AP]M$", re.I | re.U),
        r"%B %d at %I%p": re.compile(r"^\w{4,} \d{1,2} at \d{1,2}[AP]M$", re.I | re.U),
        r"%d/%m/%Y,%I:%M %p": re.compile(r"^\d{1,2}/\d{1,2}/\d{4},\d{1,2}:\d{1,2} [AP]M$", re.I | re.U),
        r"%m/%d/%Y,%I:%M %p": re.compile(r"^\d{1,2}/\d{1,2}/\d{4},\d{1,2}:\d{1,2} [AP]M$", re.I | re.U),
        r"%Y/%m/%d %I:%M:%S %p %Z": re.compile(
            r"^\d{4}/\d{1,2}/\d{1,2} \d{1,2}:\d{1,2}:\d{1,2} [AP]M GMT[+-]\d{1,2}$", re.I | re.U
        ),
    }
    patterns_with_processing: dict[str, tuple[Pattern[str], Callable[[Match[str]], str]]] = {
        r"%Y/%m/%d %I:%M:%S %p %Z": (
            re.compile(r"^(\d{4}/\d{1,2}/\d{1,2} \d{1,2}:\d{1,2}:\d{1,2} [AP]M (?:\w{3}))[\+-]\d+$", re.I | re.U),
            lambda m: m.group(1),
        ),
    }
    unique_patterns: set[str] = {
        r"^\d{1,2} \w{3} \d{4} \d{1,2}:\d{1,2}:\d{1,2} [+-]?\d{2}\d{2}(?:\d{2}(?:\.\d{6})?)?$",
        r"^\d{4}\d{2}\d{2}\d{2}\d{2}$",
        r"^\d{4}\.\d{2}\.\d{2}$",
        r"^\d{1,2}/\d{1,2}/\d{4}$",
        r"^\d{2}\.\d{2}\.\d{4}$",
        r"^\d{4}-\d{1,2}-\d{1,2}$",
        r"^\d{1,2}-\d{1,2}-\d{2}$",
        r"^\d{1,2}-\d{1,2}-\d{4}$",
        r"^\d{1,2}/\d{1,2}/\d{2}$",
        r"^\d{1,2}-\d{1,2}-\d{4} \d{2}:\d{2}:\d{2}$",
        r"^\d{1,2}/\d{1,2}/\d{4} \d{2}:\d{2}:\d{2}$",
        r"^\w{3} \d{1,2}, \d{4}$",
        r"^\w{3} \d{1,2},\d{4}$",
        r"^\w{3} \d{1,2} \d{4}$",
        r"^\w{3} \d{1,2}, \d{2}$",
        r"^\w{3} \d{1,2},\d{2}$",
        r"^\w{3} \d{1,2} \d{2}$",
        r"^\w{4,} \d{1,2}, \d{4}$",
        r"^\w{4,} \d{1,2},\d{4}$",
        r"^\w{4,} \d{1,2} \d{4}$",
        r"^\w{4,} the \d{1}st \d{4}$",
        r"^\w{4,} the \d{1,2}st \d{4}$",
        r"^\w{4,} the \d{1,2}nd \d{4}$",
        r"^\w{4,} the \d{1,2}rd \d{4}$",
        r"^\w{4,} the \d{1,2}th \d{4}$",
        r"^\w{4,} the \d{1,2}st, \d{4}$",
        r"^\w{4,} the \d{1,2}nd, \d{4}$",
        r"^\w{4,} the \d{1,2}rd, \d{4}$",
        r"^\w{4,} the \d{1,2}th, \d{4}$",
        r"^\d{1,2} \w{3} \d{2}$",
        r"^\d{1,2} \w{3} \d{4}$",
        r"^\w{3}, \d{1,2} \w{3} \d{4} \d{1,2}:\d{1,2}:\d{1,2} \w{3}$",
        r"^\d{1,2}-\w{4,}-\d{4}$",
        r"^\d{1,2}-\w{3}-\d{4}$",
        r"^\w{4,} \d{1,2}st, \d{4}$",
        r"^\w{4,} \d{1,2}nd, \d{4}$",
        r"^\w{4,} \d{1,2}rd, \d{4}$",
        r"^\w{4,} \d{1,2}th, \d{4}$",
        r"^\w{3} \w{3} \d{1,2} \d{1,2}:\d{1,2}:\d{1,2} \d{4}$",
        r"^\w{3} \w{3} \d{1,2}, \d{4}$",
        r"^\w{4,} of \d{4}$",
        r"^\w{4,} \d{4}$",
        r"^\d{1,2} \w{4,} '\d{2}$",
        r"^'\d{2}-\w{4,}$",
        r"^\d{1,2} \w{4,} \d{4}$",
        r"^\w{4,} \d{1,2}$",
        r"^\w{4,} \d{1,2}st of this year$",
        r"^\w{4,} \d{1,2}nd of this year$",
        r"^\w{4,} \d{1,2}rd of this year$",
        r"^\w{4,} \d{1,2}th of this year$",
        r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d+Z$",
        r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d+$",
        r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d+$",
        r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{3}\+\d{2}:\d{2}$",
        r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$",
        r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$",
        r"^\d{2} \w{3} \d{4} \d{1,2}:\d{1,2}:\d{1,2}$",
        r"^\d{1,2} \w{3,} \d{4} \d{1,2}:\d{1,2}:\d{1,2} \w{3}$",
        r"^\w{3,} \d{1,2} \w{3,} \d{4} \d{1,2}:\d{1,2}:\d{1,2} \w{3}$",
        r"^\d{4}\w{1,}\d{1,2}\w{1,}\d{1,2}$",
        r"^\d{4}年\d{1,2}月\d{1,2}$",
        r"^\d{4}年\d{1,2}月\d{1,2}日$",
        r"^\w{4,} \d{1,2}, \d{4} \d{1,2}:\d{1,2} [AP]M$",
        r"^\w{3} \w{3} \d{1,2}, \d{4} \d{1,2}:\d{1,2} [AP]M$",
        r"^\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{1,2} [AP]M$",
        r"^\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{1,2}:\d{1,2} [AP]M$",
        r"^\w{3} \d{1,2}, \d{4} \d{1,2}:\d{1,2} [AP]M$",
        r"^\d{1,2}/\d{1,2}/\d{4} at \d{1,2}:\d{1,2} [AP]M$",
        r"^\d{1,2}:\d{1,2} [AP]M$",
        r"^\d{1,2}/\d{1,2}/\d{2} at \d{1,2}:\d{1,2} [AP]M$",
        r"^\d{1,2}/\d{1,2}/\d{2} at \d{1,2}:\d{1,2}[AP]M$",
        r"^\w{4,} \d{1,2} at \d{1,2}[AP]M$",
        r"^\d{1,2}/\d{1,2}/\d{4},\d{1,2}:\d{1,2} [AP]M$",
        r"^\d{4}/\d{1,2}/\d{1,2} \d{1,2}:\d{1,2}:\d{1,2} [AP]M GMT[+-]\d{1,2}$",
    }

    options = re2.Options()
    options.case_sensitive = False
    combined_pattern = re2.compile(_compute_unique_patterns(patterns, ampm_patterns, patterns_with_processing), options)

    formats: set[str] = {
        r"%d %b %Y %H:%M:%S %z",
        r"%Y%m%d%H%M",
        r"%Y.%m.%d",
        r"%d/%m/%Y",
        r"%m/%d/%Y",
        r"%d.%m.%Y",
        r"%m.%d.%Y",
        r"%Y-%m-%d",
        r"%d-%m-%y",
        r"%m-%d-%y",
        r"%d-%m-%Y",
        r"%m-%d-%Y",
        r"%d/%m/%y",
        r"%m/%d/%y",
        r"%d-%m-%Y %H:%M:%S",
        r"%m-%d-%Y %H:%M:%S",
        r"%d/%m/%Y %H:%M:%S",
        r"%m/%d/%Y %H:%M:%S",
        r"%b %d, %Y",
        r"%b %d,%Y",
        r"%b %d %Y",
        r"%b %d, %y",
        r"%b %d,%y",
        r"%b %d %y",
        r"%B %d, %Y",
        r"%B %d,%Y",
        r"%B %d %Y",
        r"%B the %d %Y",
        r"%B the %dst %Y",
        r"%B the %dnd %Y",
        r"%B the %drd %Y",
        r"%B the %dth %Y",
        r"%B the %dst, %Y",
        r"%B the %dnd, %Y",
        r"%B the %drd, %Y",
        r"%B the %dth, %Y",
        r"%d %b %y",
        r"%d %b %Y",
        r"%a, %d %b %Y %H:%M:%S %Z",
        r"%d-%B-%Y",
        r"%d-%b-%Y",
        r"%B %dst, %Y",
        r"%B %dnd, %Y",
        r"%B %drd, %Y",
        r"%B %dth, %Y",
        r"%a %b %d %H:%M:%S %Y",
        r"%a %b %d, %Y",
        r"%B of %Y",
        r"%B %Y",
        r"%d %B '%y",
        r"'%y-%B",
        r"%d %B %Y",
        r"%B %d",
        r"%B %dst of this year",
        r"%B %dnd of this year",
        r"%B %drd of this year",
        r"%B %dth of this year",
        r"%Y-%m-%dT%H:%M:%S.%fZ",
        r"%Y-%m-%dT%H:%M:%S.%f",
        r"%Y-%m-%d %H:%M:%S.%f",
        r"%Y-%m-%dT%H:%M:%S.%f%z",
        r"%Y-%m-%d %H:%M:%S",
        r"%Y-%m-%dT%H:%M:%SZ",
        r"%d %b %Y %H:%M:%S",
        r"%d %B %Y %H:%M:%S %Z",
        r"%A %d %B %Y %H:%M:%S %Z",
        r"%Y%b%d",
        r"%Y年%m月%d",
        r"%Y年%m月%d日",
        r"%B %d, %Y %I:%M %p",
        r"%a %b %d, %Y %I:%M %p",
        r"%d/%m/%Y %I:%M %p",
        r"%m/%d/%Y %I:%M %p",
        r"%d/%m/%Y %I:%M:%S %p",
        r"%m/%d/%Y %I:%M:%S %p",
        r"%b %d, %Y %I:%M %p",
        r"%d/%m/%Y at %I:%M %p",
        r"%m/%d/%Y at %I:%M %p",
        r"%I:%M %p",
        r"%d/%m/%y at %I:%M %p",
        r"%m/%d/%y at %I:%M %p",
        r"%d/%m/%y at %I:%M%p",
        r"%m/%d/%y at %I:%M%p",
        r"%B %d at %I%p",
        r"%d/%m/%Y,%I:%M %p",
        r"%m/%d/%Y,%I:%M %p",
        r"%Y/%m/%d %I:%M:%S %p %Z",
    }

    def __init__(self, fast: bool = False) -> None:
        super().__init__()
        self.fast = fast

    def is_of_this_type(self, text: str) -> bool:
        if self.fast:
            return _match_pattern(self.combined_pattern, self.formats, text) or _match_patterns_with_code(
                self.patterns_with_processing.items(), text
            )

        return (
            _match_patterns(self.patterns.items(), text)
            or _match_patterns(self.ampm_patterns.items(), text)
            or _match_patterns_with_code(self.patterns_with_processing.items(), text)
        )


def _match_patterns_with_code(
    patterns: Iterable[tuple[str, tuple[Pattern[str], Callable[[Match[str]], str]]]], text: str
) -> bool:
    text = _convert_to_all_english(text)

    for format, (pattern, code) in patterns:
        matcher = pattern.match(text)

        if matcher:
            if _match_format(format, code(matcher)):
                return True
    return False


def _convert_to_all_english(text: str) -> str:
    return text.replace("午後", "PM").replace("午前", "AM")  # Japanese


def _match_format(format: str, text: str) -> bool:
    try:
        obj = datetime.strptime(text, format)
        return obj is not None
    except ValueError:
        return False


def _match_patterns(patterns: Iterable[tuple[str, Pattern[str]]], text: str) -> bool:
    text = _convert_to_all_english(text)

    return any(_match_format(format, text) for format, pattern in patterns if pattern.match(text))


def _match_pattern(pattern: Pattern[str], formats: set[str], text: str) -> bool:
    text = _convert_to_all_english(text)

    if pattern.match(text):
        for format in formats:
            try:
                obj = datetime.strptime(text, format)
                return obj is not None
            except ValueError:
                continue

    return False
