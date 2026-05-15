"""ICD (International Classification of Diseases) code identifiers.

This module provides identifiers for detecting ICD-9, ICD-10, ICD-11 codes,
UMLS medical terms, and general medical codes and terms.
"""

import csv
from pathlib import Path

import pandas as pd

from risk_assessment.classification.identifiers import Identifier


class ICDv9(Identifier):
    """Identifier for ICD-9 (International Classification of Diseases, 9th Revision) codes.

    Loads ICD-9 codes and terms from a CSV file and validates text against them.
    Can optionally match both codes and their associated medical terms.

    Attributes:
        with_terms: If True, matches both codes and medical terms; if False, only codes.
        codes: Set of valid ICD-9 codes.
        names: Set of valid ICD-9 medical term names (short and full names).
        min_length: Minimum length of any code or term.
        max_length: Maximum length of any code or term.

    Example:
        >>> identifier = ICDv9(with_terms=False)
        >>> identifier.is_of_this_type("250.00")  # Diabetes code
        True
        >>> identifier = ICDv9(with_terms=True)
        >>> identifier.is_of_this_type("diabetes mellitus")
        True
    """

    def __init__(self, with_terms: bool = False) -> None:
        """Initialize the ICD-9 identifier.

        Args:
            with_terms: If True, match both codes and medical terms. Defaults to False.
        """
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
        """Check if text is a valid ICD-9 medical term name.

        Args:
            text: The text to check.

        Returns:
            True if the text matches a known ICD-9 term name, False otherwise.
        """
        return text.casefold() in self.names

    def is_valid_code(self, text: str) -> bool:
        """Check if text is a valid ICD-9 code.

        Args:
            text: The text to check.

        Returns:
            True if the text matches a known ICD-9 code, False otherwise.
        """
        return text in self.codes

    def is_within_bounds(self, text: str) -> bool:
        """Check if text length is within valid bounds for ICD-9 codes/terms.

        Args:
            text: The text to check.

        Returns:
            True if text length is between min_length and max_length, False otherwise.
        """
        return self.min_length <= len(text) <= self.max_length

    def is_of_this_type(self, text: str) -> bool:
        """Check if text is a valid ICD-9 code or term.

        Args:
            text: The text to check.

        Returns:
            True if text is a valid ICD-9 code, or (if with_terms is True) a valid term name.
        """
        if self.is_within_bounds(text):
            if self.is_valid_code(text) or (self.with_terms and self.is_valid_name(text)):
                return True
        return False


class ICDv10(Identifier):
    """Identifier for ICD-10 (International Classification of Diseases, 10th Revision) codes.

    Loads ICD-10 codes and terms from a CSV file and validates text against them.
    Can optionally match both codes and their associated medical terms.

    Attributes:
        with_terms: If True, matches both codes and medical terms; if False, only codes.
        codes: Set of valid ICD-10 codes.
        names: Set of valid ICD-10 medical term names.
        min_length: Minimum length of any code or term.
        max_length: Maximum length of any code or term.

    Example:
        >>> identifier = ICDv10(with_terms=False)
        >>> identifier.is_of_this_type("E11.9")  # Type 2 diabetes code
        True
    """

    def __init__(self, with_terms: bool = False) -> None:
        """Initialize the ICD-10 identifier.

        Args:
            with_terms: If True, match both codes and medical terms. Defaults to False.
        """
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
        """Check if text is a valid ICD-10 medical term name.

        Args:
            text: The text to check.

        Returns:
            True if the text matches a known ICD-10 term name, False otherwise.
        """
        return text.casefold() in self.names

    def is_valid_code(self, text: str) -> bool:
        """Check if text is a valid ICD-10 code.

        Args:
            text: The text to check.

        Returns:
            True if the text matches a known ICD-10 code, False otherwise.
        """
        return text in self.codes

    def is_within_bounds(self, text: str) -> bool:
        """Check if text length is within valid bounds for ICD-10 codes/terms.

        Args:
            text: The text to check.

        Returns:
            True if text length is between min_length and max_length, False otherwise.
        """
        return self.min_length <= len(text) <= self.max_length

    def is_of_this_type(self, text: str) -> bool:
        """Check if text is a valid ICD-10 code or term.

        Args:
            text: The text to check.

        Returns:
            True if text is a valid ICD-10 code, or (if with_terms is True) a valid term name.
        """
        if self.is_within_bounds(text):
            if self.is_valid_code(text) or (self.with_terms and self.is_valid_name(text)):
                return True
        return False


class ICDv11(Identifier):
    """Identifier for ICD-11 (International Classification of Diseases, 11th Revision) codes.

    Loads ICD-11 codes and terms from a CSV file and validates text against them.
    Can optionally match both codes and their associated medical terms.
    Skips certain chapters (X, V, 24, 23, 22) during loading.

    Attributes:
        with_terms: If True, matches both codes and medical terms; if False, only codes.
        codes: Set of valid ICD-11 codes.
        names: Set of valid ICD-11 medical term descriptions.
        min_length: Minimum length of any code or term.
        max_length: Maximum length of any code or term.

    Example:
        >>> identifier = ICDv11(with_terms=False)
        >>> identifier.is_of_this_type("5A11")  # ICD-11 code
        True
    """

    def __init__(self, with_terms: bool = False) -> None:
        """Initialize the ICD-11 identifier.

        Skips chapters X, V, 24, 23, 22 during data loading.

        Args:
            with_terms: If True, match both codes and medical terms. Defaults to False.
        """
        self.with_terms = with_terms
        self.codes = set()
        self.names = set()

        self.min_length = 10000
        self.max_length = 0

        with (Path(__file__).parent / "data" / "en" / "ICDv11.csv").open("r") as io_stream:
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
        """Check if text is a valid ICD-11 medical term description.

        Args:
            text: The text to check.

        Returns:
            True if the text matches a known ICD-11 term description, False otherwise.
        """
        return text.casefold() in self.names

    def is_valid_code(self, text: str) -> bool:
        """Check if text is a valid ICD-11 code.

        Args:
            text: The text to check.

        Returns:
            True if the text matches a known ICD-11 code, False otherwise.
        """
        return text in self.codes

    def is_within_bounds(self, text: str) -> bool:
        """Check if text length is within valid bounds for ICD-11 codes/terms.

        Args:
            text: The text to check.

        Returns:
            True if text length is between min_length and max_length, False otherwise.
        """
        return self.min_length <= len(text) <= self.max_length

    def is_of_this_type(self, text: str) -> bool:
        """Check if text is a valid ICD-11 code or term.

        Args:
            text: The text to check.

        Returns:
            True if text is a valid ICD-11 code, or (if with_terms is True) a valid term description.
        """
        if self.is_within_bounds(text):
            if self.is_valid_code(text) or (self.with_terms and self.is_valid_name(text)):
                return True
        return False


class UMLS(Identifier):
    """Identifier for UMLS (Unified Medical Language System) medical terms.

    Loads UMLS terms from a parquet file and validates text against them.
    UMLS is a comprehensive medical terminology system that integrates multiple
    medical vocabularies and standards.

    Attributes:
        umls_array: Set of valid UMLS medical terms.

    Example:
        >>> identifier = UMLS()
        >>> identifier.is_of_this_type("hypertension")
        True
    """

    def __init__(self) -> None:
        """Initialize the UMLS identifier by loading terms from parquet file."""
        umls_terms = pd.read_parquet(Path(__file__).parent.joinpath("data/en/umls_terms.parquet").as_posix())
        self.umls_array = set(umls_terms["Terms"].tolist())

    def is_of_this_type(self, text: str) -> bool:
        """Check if text is a valid UMLS medical term.

        Args:
            text: The text to check.

        Returns:
            True if the text matches a known UMLS term, False otherwise.
        """
        if text in self.umls_array:
            return True
        return False


class MedicalCode(Identifier):
    """Identifier for any medical code across ICD-9, ICD-10, and ICD-11.

    Combines all three ICD versions to identify medical codes without matching
    their associated medical terms.

    Attributes:
        icd11: ICDv11 identifier instance (codes only).
        icd10: ICDv10 identifier instance (codes only).
        icd9: ICDv9 identifier instance (codes only).

    Example:
        >>> identifier = MedicalCode()
        >>> identifier.is_of_this_type("E11.9")  # ICD-10 code
        True
        >>> identifier.is_of_this_type("250.00")  # ICD-9 code
        True
    """

    def __init__(self) -> None:
        """Initialize the MedicalCode identifier with all ICD versions."""
        self.icd11 = ICDv11(False)
        self.icd10 = ICDv10(False)
        self.icd9 = ICDv9(False)

    def is_of_this_type(self, text: str) -> bool:
        """Check if text is a valid medical code from any ICD version.

        Args:
            text: The text to check.

        Returns:
            True if text matches any ICD-9, ICD-10, or ICD-11 code, False otherwise.
        """
        return any(
            [self.icd11.is_of_this_type(text), self.icd10.is_of_this_type(text), self.icd9.is_of_this_type(text)]
        )


class MedicalTerm(Identifier):
    """Identifier for medical terms from UMLS and ICD classifications.

    Can identify medical terms from UMLS only, or from UMLS combined with
    ICD-9, ICD-10, and ICD-11 term descriptions.

    Attributes:
        icd11: ICDv11 identifier instance (with terms).
        icd10: ICDv10 identifier instance (with terms).
        icd9: ICDv9 identifier instance (with terms).
        umls: UMLS identifier instance.
        umls_only: If True, only check UMLS terms; if False, check all sources.

    Example:
        >>> identifier = MedicalTerm(umls_only=True)
        >>> identifier.is_of_this_type("hypertension")
        True
        >>> identifier = MedicalTerm(umls_only=False)
        >>> identifier.is_of_this_type("diabetes mellitus")
        True
    """

    def __init__(self, umls_only: bool = False) -> None:
        """Initialize the MedicalTerm identifier.

        Args:
            umls_only: If True, only match UMLS terms. If False, match UMLS and all ICD terms.
                Defaults to True.
        """
        self.icd11 = ICDv11(True)
        self.icd10 = ICDv10(True)
        self.icd9 = ICDv9(True)
        self.umls: Identifier
        try:
            self.umls = UMLS()
        except Exception:
            # Fallback to a no-op identifier if UMLS initialization fails
            # (e.g., missing data files, permission errors, corrupted data)
            class AlwaysFalse(Identifier):
                def is_of_this_type(self, text: str) -> bool:
                    return False

            self.umls = AlwaysFalse()
        self.umls_only = umls_only

    def is_of_this_type(self, text: str) -> bool:
        """Check if text is a valid medical term.

        Args:
            text: The text to check.

        Returns:
            True if text matches UMLS terms (and optionally ICD terms), False otherwise.
        """
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
