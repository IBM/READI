from re import I, Pattern, U, compile

from word2number.w2n import word_to_num

from risk_assessment.classification.identifiers import Identifier


class Age(Identifier):
    def is_of_this_type(self, text: str | int) -> bool:
        int_value: int = 10_000_000

        if isinstance(text, str):
            try:
                int_value = int(text, base=10)

                if text != str(int_value):
                    return False
            except ValueError:
                pass

        elif isinstance(text, int):
            int_value = text

        return 17 < int_value <= 91


class AgeImproved(Identifier):
    SUFFIXES = r"(?:man|woman|male|female|daughter|son|niece|nephew|lady|gentleman)"

    age_pattern_with_gender: list[Pattern[str]] = [
        compile(r"^([0-9]+)\s*yrs\.?\s+" + SUFFIXES, I | U),
        compile(r"^([0-9]+)\s*years\.?\s+" + SUFFIXES, I | U),
        compile(r"^([0-9]+)\s*y/o\.?\s+" + SUFFIXES, I | U),
        compile(r"^([0-9]+)\s*yo\.?\s+" + SUFFIXES, I | U),
    ]

    age_pattern: list[Pattern[str]] = [
        compile(r"^([0-9]+)\s+year old$", I | U),
        compile(r"^([0-9]+)-year old$", I | U),
        compile(r"^([0-9]+)-year-old$", I | U),
        compile(r"^([0-9]+)\s+years\s+of\s+age$", I | U),
        compile(r"^([0-9]+)\s+years old$", I | U),
        compile(r"^([0-9]+)-years old$", I | U),
        compile(r"^([0-9]+)-years-old$", I | U),
        compile(r"^([0-9]+)\s+yrs\.?\s+old$", I | U),
        compile(r"^([0-9]+)-yrs\.?\s+old$", I | U),
        compile(r"^([0-9]+)-yrs-old$", I | U),
        compile(r"^([0-9]+)\s+yr(\.)? old$", I | U),
        compile(r"^([0-9]+)-yr(\.)? old$", I | U),
        compile(r"^([0-9]+)-yr-old$", I | U),
        compile(r"^([0-9]+)\s+yo$", I | U),
        compile(r"^([0-9]+)\s+y/o$", I | U),
        compile(r"^([0-9]+)\s+([0-9]+)/[0-9]+\s+y/?o$", I | U),
        compile(r"^([0-9]+) weeks old$", I | U),
        compile(r"^([0-9]+)weeks old$", I | U),
        compile(r"^([0-9]+)-weeks old$", I | U),
        compile(r"^([0-9]+)-weeks-old$", I | U),
        compile(r"^([0-9]+) months old$", I | U),
        compile(r"^([0-9]+)months old$", I | U),
        compile(r"^([0-9]+)-months old$", I | U),
        compile(r"^([0-9]+)-months-old$", I | U),
        compile(r"^at age\s+([0-9]+)$", I | U),
        compile(r"^at age\s+of\s+([0-9]+)$", I | U),
        compile(r"^at age\s+([0-9]+) and ([0-9]+)$", I | U),
        compile(r"^at age\s+([0-9]+) and ([0-9]+)/[0-9]+$", I | U),
        compile(r"^at the age of ([0-9]+)$", I | U),
        compile(r"^([0-9]+) year and ([0-9]+) month$", I | U),
        compile(r"^([0-9]+) years and ([0-9]+) months$", I | U),
        compile(r"^([0-9]+) yrs and ([0-9]+) month$", I | U),
        compile(r"^([0-9]+)yr and ([0-9]+)mo$", I | U),
        compile(r"^([0-9]+) yrs ([0-9]+)/[0-9]+ mo$", I | U),
        compile(r"^([0-9]+) years ([0-9]+)/[0-9]+ mo$", I | U),
        compile(r"^dob:?\s+([0-9]+)$", I | U),
        compile(r"^dob:?\s+\d{1,2}(?:\s+|-)\d{1,2}(?:\s+|-)\d{4}$", I | U),
        compile(r"^date\s+of\s+birth\s*:\s+([0-9]+)/([0-9]+)/([0-9]+)$", I | U),
        compile(r"^date\s+of\s+birth\s*:\s+([0-9]+)$", I | U),
        compile(r"^dob:\s+[0-9][0-9]-([0-9]+)-([0-9]+)$", I | U),  # DOB: 03-28-1934
        compile(r"^dob:\s+[0-9][0-9]/([0-9]+)/([0-9]+)$", I | U),  # DOB: 03/28/1934
        compile(r"^dob\s+[0-9][0-9]-([0-9]+)-([0-9]+)"),  # DOB 03-28-1934
        compile(r"age:?\s*([1-9][0-9]*)$", I | U),
        compile(r"alive\s+([1-9][0-9]*)$", I | U),
        compile(r"comment:\s*age\s+([1-9][0-9]*)$", I | U),
        compile(r"comments:\s*age\s+([1-9][0-9]*)$", I | U),
        compile(r"comments:\s*died\s+age\s+([1-9][0-9]*)$", I | U),
        compile(r"^died\s+age\s+([0-9]+)$", I | U),
        compile(r"^deceased\s+age\s+([0-9]+)$", I | U),
        compile(r"^deceased\s+([0-9]+)$", I | U),
        compile(r"^died\s+at\s+([0-9]+)$", I | U),
        compile(r"^died\s+([0-9]+)-old\s+age$", I | U),
        compile(r"^died\s+of\s+([\w|'|-]+\s+){1,3}at\s+([0-9]+)$", I | U),
        compile(r"^died\s+of\s+([\w|'|-]+\s+){1,3}at\s+age\s+(of\s+)?([0-9]+)$", I | U),
        compile(r"^passed\s+away\s+at\s+age\s+([0-9]+)$", I | U),
    ]

    def _try_birthday_patterns(self, input: str) -> bool:
        input = input.lower()
        if (input.startswith("on his") or input.startswith("on her")) and input.endswith("birthday"):
            middle_part = input[len("on his") : -len("birthday")].strip()

            return valid_number(middle_part)

        return False

    def _try_word_pattern(self, text: str) -> bool:
        if self._try_birthday_patterns(text):
            return True

        for suffix in ["year old", "years old", "yrs old", "months old", "days old", "weeks old", "-years-old"]:
            if text.endswith(suffix):
                text = text[0 : -len(suffix)]
                if valid_number(text):
                    return True

        return False

    def is_of_this_type(self, text: str) -> bool:
        return (
            any(pattern.match(text) for pattern in self.age_pattern)
            or any(pattern.match(text) for pattern in self.age_pattern_with_gender)
            or self._try_word_pattern(text)
        )


def valid_number(text: str) -> bool:
    try:
        num = word_to_num(text.strip().casefold())

        if type(num) is int:
            return True
    except Exception:
        return False

    return False


# def create_number(text: str) -> int | None:
#     allowedStrings: set[str] = set([
#         "zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety",
#         "hundred", "thousand", "million", "billion", "trillion"
#     ])
#
#     result = 0
#     finalResult = 0
#
#     if text is None or not len(text):
#         return None
#
#     text = text.replace("-", " ")
#     text = text.casefold().replace(" and", " ")
#     splitParts = text.strip().split(r"\s+")
#
#     for string in splitParts:
#         if string not in allowedStrings:
#             return None
#
#     for string in splitParts:
#         if string == "zero":
#             result += 0
#         elif string == "one":
#             result += 1
#         elif string == ("two"):
#             result += 2
#         elif string == ("three"):
#             result += 3
#         elif string == ("four"):
#             result += 4
#         elif string == ("five"):
#             result += 5
#         elif string == ("six"):
#             result += 6
#         elif string == ("seven"):
#             result += 7
#         elif string == ("eight"):
#             result += 8
#         elif string == ("nine"):
#             result += 9
#         elif string == ("ten"):
#             result += 10
#         elif string == ("eleven"):
#             result += 11
#         elif string == ("twelve"):
#             result += 12
#         elif string == ("thirteen"):
#             result += 13
#         elif string == ("fourteen"):
#             result += 14
#         elif string == ("fifteen"):
#             result += 15
#         elif string == ("sixteen"):
#             result += 16
#         elif string == ("seventeen"):
#             result += 17
#         elif string == ("eighteen"):
#             result += 18
#         elif string == ("nineteen"):
#             result += 19
#         elif string == ("twenty"):
#             result += 20
#         elif string == ("thirty"):
#             result += 30
#         elif string == ("forty"):
#             result += 40
#         elif string == ("fifty"):
#             result += 50
#         elif string == ("sixty"):
#             result += 60
#         elif string == ("seventy"):
#             result += 70
#         elif string == ("eighty"):
#             result += 80
#         elif string == ("ninety"):
#             result += 90
#         elif string == ("hundred"):
#             result *= 100
#         elif string == ("thousand"):
#             result *= 1_000
#             finalResult += result
#             result = 0
#         elif string == ("million"):
#             result *= 1_000_000
#             finalResult += result
#             result = 0
#         elif string == ("billion"):
#             result *= 1_000_000_000
#             finalResult += result
#             result = 0
#         elif string == ("trillion"):
#             result *= 1_000_000_000_000
#
#         finalResult += result
#         result = 0
#
#     finalResult += result
#     return finalResult
#
