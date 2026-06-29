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
