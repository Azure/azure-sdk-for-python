"""Unit tests for `.github/skills/_shared/schema_validator.py`.

The validator is pure-Python (no `azure.*` imports, no network). These tests
cover:

* valid single-type schema
* valid classify-and-route schema
* unknown ``baseAnalyzerId`` rejected (catches the `prebuilt-documentAnalyzer`
  typo class observed in the CU-Tools investigation)
* missing ``fieldSchema`` on non-classifier
* classify-route schemas reject top-level ``fieldSchema``
* purity guard: validator source contains no ``azure``/``requests``/``urllib``
  imports
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_SKILL_SHARED_DIR = (
    Path(__file__).resolve().parent.parent / ".github" / "skills" / "_shared"
)


def _load_validator():
    spec = importlib.util.spec_from_file_location(
        "_skill_schema_validator", _SKILL_SHARED_DIR / "schema_validator.py"
    )
    assert spec and spec.loader, "could not load schema_validator.py"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


sv = _load_validator()


def test_valid_single_type_schema():
    ok, errors = sv.validate_schema(
        {
            "baseAnalyzerId": "prebuilt-document",
            "fieldSchema": {
                "fields": {
                    "invoiceNumber": {
                        "type": "string",
                        "method": "extract",
                        "description": "Invoice number printed at the top right.",
                    }
                }
            },
        }
    )
    assert ok, errors
    assert errors == []


def test_valid_classify_route_schema():
    ok, errors = sv.validate_schema(
        {
            "baseAnalyzerId": "prebuilt-document",
            "config": {
                "enableSegment": True,
                "contentCategories": {
                    "invoice": {
                        "description": "Pages whose top heading is 'Invoice'.",
                        "analyzerId": "invoice_extractor_v1",
                    },
                    "bank_statement": {
                        "description": "Pages whose top heading is 'Bank Statement'.",
                        "analyzerId": "bank_statement_extractor_v1",
                    },
                },
            },
        }
    )
    assert ok, errors


def test_rejects_unknown_base_analyzer_id():
    ok, errors = sv.validate_schema(
        {
            "baseAnalyzerId": "prebuilt-documentAnalyzer",
            "fieldSchema": {"fields": {"x": {"type": "string"}}},
        }
    )
    assert not ok
    assert any("baseAnalyzerId" in e for e in errors)
    assert any("prebuilt-documentAnalyzer" in e for e in errors)


def test_rejects_missing_field_schema_on_non_classifier():
    ok, errors = sv.validate_schema({"baseAnalyzerId": "prebuilt-document"})
    assert not ok
    assert any("fieldSchema" in e for e in errors)


def test_classify_route_rejects_top_level_field_schema():
    ok, errors = sv.validate_schema(
        {
            "baseAnalyzerId": "prebuilt-document",
            "fieldSchema": {"fields": {"x": {"type": "string"}}},
            "config": {
                "enableSegment": True,
                "contentCategories": {
                    "invoice": {"description": "d", "analyzerId": "a"},
                },
            },
        }
    )
    assert not ok
    assert any("fieldSchema" in e and "inner" in e for e in errors)


def test_classify_route_requires_enable_segment_true():
    ok, errors = sv.validate_schema(
        {
            "baseAnalyzerId": "prebuilt-document",
            "config": {
                "contentCategories": {
                    "invoice": {"description": "d", "analyzerId": "a"},
                }
            },
        }
    )
    assert not ok
    assert any("enableSegment" in e for e in errors)


def test_validate_schema_file_missing(tmp_path):
    ok, errors = sv.validate_schema_file(tmp_path / "does_not_exist.json")
    assert not ok
    assert any("not found" in e for e in errors)


def test_validate_schema_file_invalid_json(tmp_path):
    p = tmp_path / "broken.json"
    p.write_text("{ this is not json", encoding="utf-8")
    ok, errors = sv.validate_schema_file(p)
    assert not ok
    assert any("not valid JSON" in e for e in errors)


def test_purity_guard_no_forbidden_imports():
    source = (_SKILL_SHARED_DIR / "schema_validator.py").read_text(encoding="utf-8")
    for forbidden in ("import azure", "from azure", "import requests", "import urllib"):
        assert forbidden not in source, (
            f"schema_validator.py must not contain {forbidden!r}; "
            "see _shared/README.md for rules"
        )


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
