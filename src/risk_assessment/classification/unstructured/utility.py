from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from risk_assessment.classification.unstructured import Entity


def entity_to_text(entity: Entity, text: str) -> str:
    return f"[{text[entity.start : entity.end]} -> {entity.entity_type}@[{','.join(src for src in entity.source)}]]"


class AnnotationWriter:
    def __init__(self, file_name: str | Path, with_source: bool = True) -> None:
        self.with_source = with_source
        try:
            if isinstance(file_name, str):
                self._file_reference = open(file_name, "w")
            elif isinstance(file_name, Path):
                self._file_reference = file_name.open("w")
            else:
                raise ValueError(f"file_name is expected to be either a str or a Path, {type(file_name)} found")
        except OSError as e:
            print(f"Unable to open {file_name} because of {e}")
            raise e

    def __enter__(self) -> AnnotationWriter:
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self._file_reference.close()

    def write(self, doc_id: str, entities: list[Entity]) -> None:
        self._file_reference.write(
            json.dumps(
                {
                    "document_id": doc_id,
                    "entities": [self._marshal_entity(entity) for entity in sorted(entities, key=lambda x: x.start)],
                }
            )
        )
        self._file_reference.write("\n")

    def _marshal_entity(self, entity: Entity) -> dict[str, Any]:
        response: dict[str, Any] = {
            "span": {
                "begin": entity.start,
                "end": entity.end,
            },
            "type": entity.entity_type,
            "confidence": entity.confidence,
            "pos_tags": ",".join(entity.pos_tags),
        }

        if self.with_source:
            response["source"] = ",".join(entity.source)

        return response
