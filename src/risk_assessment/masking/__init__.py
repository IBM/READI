"""Text masking utilities for applying de-identification transformations to DataFrames.

This module provides tools for replacing detected entities in free-text fields
of a pandas DataFrame with anonymized substitutes.  The transformation policy
maps entity types (e.g. ``"Email"``, ``"CreditCardNumber"``) to callables
from :mod:`risk_assessment.masking.actions`.

Typical usage::

    from risk_assessment.masking import cleanse_dataframe_field
    from risk_assessment.masking.actions import tagging_factory, format_preserving_redact

    policy = {
        "Email": tagging_factory(),
        "CreditCardNumber": format_preserving_redact,
    }
    cleansed_df = cleanse_dataframe_field(df, "notes", "./nlp_reports/", transformations=policy)
"""

import json
import logging
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pandas import DataFrame

from risk_assessment.masking.actions import format_preserving_redact, no_action, tagging_factory

logger = logging.getLogger(__file__)


@dataclass
class NLPReport:
    """Parsed NLP report produced by an entity-extraction pipeline.

    Attributes:
        extracted_text: The original text that was analysed.
        entities: List of detected entities, each represented as
            ``[annotation_text, begin, end, entity_type]``.
    """

    extracted_text: str
    entities: list[list[Any]]


def _load_entities(path: str | Path) -> NLPReport:
    with open(path) as input:
        return NLPReport(**json.load(input))


def _default_transformation_policy() -> dict[str, Callable[[str, str], str]]:
    return {
        "IpAddress": format_preserving_redact,
        "Port": format_preserving_redact,
        "DateOfBirth": tagging_factory(),
        "CreditCardNumber": format_preserving_redact,
        "URL": tagging_factory(),
        "ANP": no_action,
    }


def cleanse_dataframe_field(
    data: DataFrame,
    field_name: Any,
    nlp_report_directory: str | Path,
    nlp_report_file_pattern: str = r"mytext-{}.json",
    transformations: dict[str, Callable[[str, str], str]] = _default_transformation_policy(),
    default: Callable[[str, str], str] = tagging_factory(),
) -> DataFrame:
    """Apply entity masking to a text column of a DataFrame using pre-generated NLP reports.

    For each row, loads the corresponding NLP report from ``nlp_report_directory``,
    verifies the text matches, then replaces every detected entity span using the
    appropriate transformation from ``transformations`` (or ``default`` if the
    entity type is not in the policy).  Replacements are applied in reverse span
    order to preserve character offsets.

    Args:
        data: The DataFrame to modify in-place.
        field_name: Column name of the free-text field to cleanse.
        nlp_report_directory: Directory containing one JSON NLP report per row.
        nlp_report_file_pattern: ``str.format``-style pattern for the report
            filename.  ``{}`` is substituted with ``index + 1``.
            Defaults to ``"mytext-{}.json"``.
        transformations: Mapping from entity type string to a
            ``(entity_type, entity_text) -> replacement_text`` callable.
            Defaults to a built-in policy covering common entity types.
        default: Fallback transformation for entity types not in
            ``transformations``.  Defaults to :func:`~risk_assessment.masking.actions.tagging_factory`.

    Returns:
        The modified DataFrame (also mutated in-place).

    Raises:
        ValueError: If the NLP report's extracted text does not match the
            DataFrame cell value, or if an entity span does not match the
            annotation text.
    """
    for index in data.index:
        logger.info("Processing %s", index)
        report = _load_entities(Path(nlp_report_directory) / Path(nlp_report_file_pattern.format(index + 1)))

        row = data.iloc[[index]]
        field = row[field_name]
        text = field[index]

        if report.extracted_text != text:
            raise ValueError(f"{report.extracted_text} -> {text}")

        for [annotation_text, begin, end, entity_type] in sorted(report.entities, key=lambda t: t[1], reverse=True):
            entity_text = text[begin:end]

            if entity_text != annotation_text:
                raise ValueError("Entity and text span strings do not match")

            transformed_text = (transformations[entity_type] if entity_type in transformations else default)(
                entity_type, entity_text
            )

            text = text[0:begin] + transformed_text + text[end:]

        data.at[index, field_name] = text

    return data
