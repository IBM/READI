import csv
from pathlib import Path

import pandas as pd

from risk_assessment.classification.identifiers import Identifier


class ICDv9(Identifier):
    def __init__(self, with_terms: bool = False) -> None:
        self.with_terms = with_terms
        self.codes = set()
        self.names = set()

        self.min_length = 10000
        self.max_length = 0

        with (Path(__file__).parent / "data" / "en" / "ICDList.csv").open("r") as io_stream:
            reader = csv.reader(io_stream, delimiter=";")

            for record in reader:
                if len(record) != 7:
                    continue

                [code, short_name, full_name, chapter_code, chapter_name, category_code, category_name] = record

                self.codes.add(code)
                self.names.add(short_name.casefold())
                self.names.add(full_name.casefold())

                if self.min_length > len(code):
                    self.min_length = len(code)
                if self.min_length > len(short_name):
                    self.min_length = len(short_name)
                if self.min_length > len(full_name):
                    self.min_length = len(full_name)
                if self.max_length < len(code):
                    self.max_length = len(code)
                if self.max_length < len(short_name):
                    self.max_length = len(short_name)
                if self.max_length < len(full_name):
                    self.max_length = len(full_name)

    def is_valid_name(self, text: str) -> bool:
        return text.casefold() in self.names

    def is_valid_code(self, text: str) -> bool:
        return text in self.codes

    def is_within_bounds(self, text: str) -> bool:
        return self.min_length <= len(text) <= self.max_length

    def is_of_this_type(self, text: str) -> bool:
        if self.is_within_bounds(text):
            if self.is_valid_code(text) or (self.with_terms and self.is_valid_name(text)):
                return True
        return False


class ICDv10(Identifier):
    def __init__(self, with_terms: bool = False) -> None:
        self.with_terms = with_terms
        self.codes = set()
        self.names = set()

        self.min_length = 10000
        self.max_length = 0

        with (Path(__file__).parent / "data" / "en" / "ICDv10.csv").open("r") as io_stream:
            reader = csv.reader(io_stream)

            for record in reader:
                if len(record) != 6:
                    continue

                [code, full_name, category_code, category_name, chapter_code, chapter_name] = record

                self.codes.add(code)
                self.names.add(full_name.casefold())

                if self.min_length > len(code):
                    self.min_length = len(code)
                if self.min_length > len(full_name):
                    self.min_length = len(full_name)
                if self.max_length < len(code):
                    self.max_length = len(code)
                if self.max_length < len(full_name):
                    self.max_length = len(full_name)

    def is_valid_name(self, text: str) -> bool:
        return text.casefold() in self.names

    def is_valid_code(self, text: str) -> bool:
        return text in self.codes

    def is_within_bounds(self, text: str) -> bool:
        return self.min_length <= len(text) <= self.max_length

    def is_of_this_type(self, text: str) -> bool:
        if self.is_within_bounds(text):
            if self.is_valid_code(text) or (self.with_terms and self.is_valid_name(text)):
                return True
        return False


class ICDv11(Identifier):
    def __init__(self, with_terms: bool = False) -> None:
        """
        skip chapters:
        - X, V, 24, 23, 22
        """
        self.with_terms = with_terms
        self.codes = set()
        self.names = set()

        self.min_length = 10000
        self.max_length = 0

        with (Path(__file__) / "data" / "en" / "ICDv11.csv").open("r") as io_stream:
            reader = csv.reader(io_stream)
            next(reader)  # discard header

            for record in reader:
                if len(record) != 3:
                    continue

                [_, code, description] = record

                self.codes.add(code)
                self.names.add(description.casefold())

                if self.min_length > len(code):
                    self.min_length = len(code)
                if self.min_length > len(description):
                    self.min_length = len(description)
                if self.max_length < len(code):
                    self.max_length = len(code)
                if self.max_length < len(description):
                    self.max_length = len(description)

    def is_valid_name(self, text: str) -> bool:
        return text.casefold() in self.names

    def is_valid_code(self, text: str) -> bool:
        return text in self.codes

    def is_within_bounds(self, text: str) -> bool:
        return self.min_length <= len(text) <= self.max_length

    def is_of_this_type(self, text: str) -> bool:
        if self.is_within_bounds(text):
            if self.is_valid_code(text) or (self.with_terms and self.is_valid_name(text)):
                return True
        return False


class UMLS(Identifier):
    def __init__(self) -> None:
        umls_terms = pd.read_parquet(Path(__file__).parent.joinpath("data/en/umls_terms.parquet").as_posix())
        self.umls_array = set(umls_terms["Terms"].tolist())

    def is_of_this_type(self, text: str) -> bool:
        if text in self.umls_array:
            return True
        return False


class MedicalCode(Identifier):
    def __init__(self) -> None:
        self.icd11 = ICDv11(False)
        self.icd10 = ICDv10(False)
        self.icd9 = ICDv9(False)

    def is_of_this_type(self, text: str) -> bool:
        return any(
            [self.icd11.is_of_this_type(text), self.icd10.is_of_this_type(text), self.icd9.is_of_this_type(text)]
        )


class MedicalTerm(Identifier):
    def __init__(self, umls_only: bool = True) -> None:
        self.icd11 = ICDv11(True)
        self.icd10 = ICDv10(True)
        self.icd9 = ICDv9(True)
        self.umls = UMLS()
        self.umls_only = umls_only

    def is_of_this_type(self, text: str) -> bool:
        if self.umls_only:
            return self.umls.is_of_this_type(text)

        return any(
            [
                self.umls.is_of_this_type(text),
                self.icd11.is_of_this_type(text),
                self.icd10.is_of_this_type(text),
                self.icd9.is_of_this_type(text),
            ]
        )
