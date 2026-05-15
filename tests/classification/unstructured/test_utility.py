import json
from pathlib import Path

import pytest

from risk_assessment.classification.unstructured import Entity
from risk_assessment.classification.unstructured.utility import AnnotationWriter


def test_dumping_of_entities(tmp_path: Path) -> None:
    f = tmp_path / "output.txt"
    with AnnotationWriter(f) as writer:
        for i in range(10):
            writer.write(f"foo{i}", [Entity(i, i + 10, "type", frozenset(["FOO"]))])

    assert f.exists()


def test_validation_of_file(tmp_path: Path) -> None:
    f = tmp_path / "output.txt"
    with AnnotationWriter(f) as writer:
        for i in range(10):
            writer.write(f"foo{i}", [Entity(i, i + 10, "type", frozenset(["FOO"]))])

    assert f.exists()

    with f.open("r") as input:
        lines = input.readlines()

        assert len(lines) == 10

        for line in lines:
            data = json.loads(line)
            assert "document_id" in data
            assert len(data) == 2
            assert len(data["entities"][0]) == 5


def test_validation_of_file_with_no_sources(tmp_path: Path) -> None:
    f = tmp_path / "output.txt"
    with AnnotationWriter(f, with_source=False) as writer:
        for i in range(10):
            writer.write(f"foo{i}", [Entity(i, i + 10, "type", frozenset(["FOO"]))])

    assert f.exists()

    with f.open("r") as input:
        lines = input.readlines()

        assert len(lines) == 10

        for line in lines:
            data = json.loads(line)
            assert "document_id" in data
            assert len(data) == 2
            assert len(data["entities"][0]) == 4
