"""Unit tests for the classify-and-route router script.

Specifically:

* missing ``--inner-schema`` for a referenced category aborts with the right
  message
* category-aware fill-rate denominator is correct (the CU-Tools exporter bug
  must NOT regress: a category with 3 segments and full fill must report
  100%, not 50% just because another category has segments too).
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
_SCRIPT_PATH = (
    _HERE.parent
    / ".github"
    / "skills"
    / "cu-sdk-author-analyzer-classify-route"
    / "scripts"
    / "create_and_test_router.py"
)


def _load_router():
    spec = importlib.util.spec_from_file_location(
        "_skill_create_and_test_router", _SCRIPT_PATH
    )
    assert spec and spec.loader, "could not load router script"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


router = _load_router()


def _segment(category: str, fields: dict) -> dict:
    return {"category": category, "fields": fields}


def _f(value, confidence):
    return {"valueString": value, "confidence": confidence}


def test_summarize_routed_uses_per_category_denominator():
    """Three invoice segments (all filled) must report 100%, not be diluted
    by other categories' segments.
    """

    results = [
        (
            "packet_a",
            {
                "contents": [
                    _segment("invoice", {"InvoiceNumber": _f("INV-1", 0.9)}),
                    _segment("invoice", {"InvoiceNumber": _f("INV-2", 0.91)}),
                    _segment("invoice", {"InvoiceNumber": _f("INV-3", 0.92)}),
                    _segment("bank_statement", {"AccountNumber": _f("12345", 0.8)}),
                ]
            },
        ),
    ]

    text = router.summarize_routed(results)

    # Invoice: 3 segments, 3 filled → 100%
    assert "category: invoice  (3 segments)" in text
    assert "InvoiceNumber                  100.0%" in text
    # Bank statement: 1 segment, 1 filled → 100%, not 25%.
    assert "category: bank_statement  (1 segments)" in text
    assert "AccountNumber                  100.0%" in text
    # 33%/25% (packet-wide denominator) must NOT appear.
    assert "33.3%" not in text
    assert "25.0%" not in text


def test_summarize_routed_reports_zero_fill_for_missing_field_in_some_segments():
    """Two invoice segments, only one has TotalAmount → 50% fill."""

    results = [
        (
            "packet",
            {
                "contents": [
                    _segment(
                        "invoice",
                        {
                            "InvoiceNumber": _f("INV-1", 0.9),
                            "TotalAmount": _f("$100", 0.7),
                        },
                    ),
                    _segment("invoice", {"InvoiceNumber": _f("INV-2", 0.91)}),
                ]
            },
        ),
    ]

    text = router.summarize_routed(results)
    assert "category: invoice  (2 segments)" in text
    assert "InvoiceNumber                  100.0%" in text
    assert "TotalAmount                     50.0%" in text


def test_wire_inner_ids_errors_on_missing_alias():
    outer = {
        "baseAnalyzerId": "prebuilt-document",
        "config": {
            "enableSegment": True,
            "contentCategories": {
                "invoice": {"description": "d", "analyzerId": "invoice"},
                "loan": {"description": "d", "analyzerId": "loan_application"},
            },
        },
    }
    # Only invoice alias supplied; loan_application missing.
    patched, errors = router._wire_inner_ids(outer, {"invoice": "real-invoice-id"})
    assert any("loan_application" in e for e in errors)


def test_wire_inner_ids_errors_on_extra_inner():
    outer = {
        "baseAnalyzerId": "prebuilt-document",
        "config": {
            "enableSegment": True,
            "contentCategories": {
                "invoice": {"description": "d", "analyzerId": "invoice"},
            },
        },
    }
    patched, errors = router._wire_inner_ids(
        outer, {"invoice": "real-invoice-id", "extra": "unused-id"}
    )
    assert any("extra" in e and "no category" in e for e in errors)


def test_wire_inner_ids_passes_through_prebuilt_analyzer_ids():
    """Categories routed at a service prebuilt (e.g. ``prebuilt-invoice``) must
    skip alias resolution and be left untouched. No --inner-schema needed."""
    outer = {
        "baseAnalyzerId": "prebuilt-document",
        "config": {
            "enableSegment": True,
            "omitContent": True,
            "contentCategories": {
                "invoice": {"description": "d", "analyzerId": "prebuilt-invoice"},
                "receipt": {"description": "d", "analyzerId": "prebuilt-receipt"},
                "custom_loan": {"description": "d", "analyzerId": "loan_application"},
            },
        },
    }
    patched, errors = router._wire_inner_ids(
        outer, {"loan_application": "real-loan-id"}
    )
    assert errors == []
    cats = patched["config"]["contentCategories"]
    # prebuilts unchanged
    assert cats["invoice"]["analyzerId"] == "prebuilt-invoice"
    assert cats["receipt"]["analyzerId"] == "prebuilt-receipt"
    # custom alias resolved
    assert cats["custom_loan"]["analyzerId"] == "real-loan-id"


def test_parse_inner_arg():
    parsed = router._parse_inner_arg(["invoice=/tmp/inv.json", "bank=/tmp/b.json"])
    assert parsed == {"invoice": Path("/tmp/inv.json"), "bank": Path("/tmp/b.json")}


def test_parse_inner_arg_rejects_missing_equals():
    with pytest.raises(SystemExit):
        router._parse_inner_arg(["invoice/tmp/inv.json"])


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
