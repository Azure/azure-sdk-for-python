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


# ---------------------------------------------------------------------------
# _version_sort_key — pure key extractor
# ---------------------------------------------------------------------------


def test_version_sort_key_bare_alias_returns_group_zero():
    key = router._version_sort_key("invoice", "invoice")
    assert key == (0, 0, "")


def test_version_sort_key_v_prefixed_numeric_returns_group_one():
    v9 = router._version_sort_key("invoice_v9", "invoice")
    v10 = router._version_sort_key("invoice_v10", "invoice")
    assert v9 == (1, 9, "")
    assert v10 == (1, 10, "")
    # The whole point of the fix.
    assert v10 > v9, "v10 must sort higher than v9 by numeric version"


def test_version_sort_key_bare_numeric_returns_group_one():
    """`<alias>_<N>` (no `v` prefix) is also a numeric version."""
    assert router._version_sort_key("invoice_42", "invoice") == (1, 42, "")


def test_version_sort_key_non_numeric_suffix_returns_group_two():
    assert router._version_sort_key("invoice_draft", "invoice") == (2, 0, "draft")


# ---------------------------------------------------------------------------
# _discover_inner_from_dir — filesystem-touching resolution
# ---------------------------------------------------------------------------


def _outer_with_aliases(*aliases):
    """Build an outer classifier schema whose category_i has analyzerId=aliases[i].

    ``None`` in the list produces a category with no ``analyzerId`` at all
    (classification-only bucket).
    """
    categories = {}
    for i, alias in enumerate(aliases):
        entry = {"description": f"d{i}"}
        if alias is not None:
            entry["analyzerId"] = alias
        categories[f"cat_{i}"] = entry
    return {
        "baseAnalyzerId": "prebuilt-document",
        "config": {"enableSegment": True, "contentCategories": categories},
    }


def test_discover_inner_from_dir_resolves_exact_match_stem(tmp_path):
    (tmp_path / "invoice.json").write_text("{}")
    (tmp_path / "bank_statement.json").write_text("{}")

    resolved = router._discover_inner_from_dir(
        _outer_with_aliases("invoice", "bank_statement"), tmp_path
    )

    assert resolved == {
        "invoice": tmp_path / "invoice.json",
        "bank_statement": tmp_path / "bank_statement.json",
    }


def test_discover_inner_from_dir_picks_natural_version_max_not_alphabetical(tmp_path):
    """Regression: the previous impl did ``sorted(schema_dir.glob("*.json"))``
    and took the last element as "newest". But ``'1' < '9'`` char-by-char,
    so ``invoice_v10.json`` sorted BEFORE ``invoice_v9.json`` and
    "alphabetical last" silently picked v9 — the older schema. Copilot
    flagged this on the sibling .NET PR (azure-sdk-for-net#60394); the
    natural version sort fix brings all four languages back in lockstep.
    """
    for name in ("invoice_v1", "invoice_v2", "invoice_v9", "invoice_v10"):
        (tmp_path / f"{name}.json").write_text("{}")

    resolved = router._discover_inner_from_dir(
        _outer_with_aliases("invoice"), tmp_path
    )

    assert resolved == {"invoice": tmp_path / "invoice_v10.json"}, (
        "v10 must beat v9 (natural version order, not alphabetical)"
    )


def test_discover_inner_from_dir_prefers_versioned_over_bare_alias(tmp_path):
    """A bare ``<alias>.json`` is group 0 (baseline); any versioned file
    is group 1 or 2 and beats the baseline as "newer".
    """
    (tmp_path / "invoice.json").write_text("{}")
    (tmp_path / "invoice_v1.json").write_text("{}")

    resolved = router._discover_inner_from_dir(
        _outer_with_aliases("invoice"), tmp_path
    )

    assert resolved == {"invoice": tmp_path / "invoice_v1.json"}


def test_discover_inner_from_dir_skips_prebuilt_aliases(tmp_path):
    """``prebuilt-invoice`` is a service alias; no local file required."""
    (tmp_path / "invoice.json").write_text("{}")

    resolved = router._discover_inner_from_dir(
        _outer_with_aliases("invoice", "prebuilt-invoice"), tmp_path
    )

    assert list(resolved) == ["invoice"]


def test_discover_inner_from_dir_skips_categories_without_analyzer_id(tmp_path):
    """A category without ``analyzerId`` is a classification-only bucket."""
    (tmp_path / "invoice.json").write_text("{}")

    resolved = router._discover_inner_from_dir(
        _outer_with_aliases("invoice", None), tmp_path
    )

    assert list(resolved) == ["invoice"]


def test_discover_inner_from_dir_missing_aliases_raises(tmp_path):
    """Every unresolved alias must appear in the SystemExit message."""
    (tmp_path / "invoice.json").write_text("{}")

    with pytest.raises(SystemExit) as excinfo:
        router._discover_inner_from_dir(
            _outer_with_aliases("invoice", "bank_statement", "loan_application"),
            tmp_path,
        )

    msg = str(excinfo.value)
    assert "bank_statement" in msg
    assert "loan_application" in msg


def test_discover_inner_from_dir_unrelated_json_files_ignored(tmp_path):
    (tmp_path / "invoice.json").write_text("{}")
    (tmp_path / "notes.json").write_text("{}")
    (tmp_path / "settings.json").write_text("{}")

    resolved = router._discover_inner_from_dir(
        _outer_with_aliases("invoice"), tmp_path
    )

    assert resolved == {"invoice": tmp_path / "invoice.json"}


def test_discover_inner_from_dir_non_existent_dir_raises(tmp_path):
    missing = tmp_path / "definitely-not-there"
    with pytest.raises(SystemExit) as excinfo:
        router._discover_inner_from_dir(_outer_with_aliases("invoice"), missing)
    assert "--schema-dir is not a directory" in str(excinfo.value)


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
