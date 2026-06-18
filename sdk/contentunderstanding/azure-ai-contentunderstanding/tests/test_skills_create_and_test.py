# cspell:ignore capsys
"""Unit tests for the single-analyzer ``create_and_test.py`` script.

Covers the dev-plan §Test Plan items for the helper script:

* ``--help`` exits 0 (argparse smoke).
* An invalid schema returns exit code 2 **before** building the Azure client
  (validator runs first; no service call is made).
* ``summarize()`` flattens nested ``valueArray`` / ``valueObject`` fields to
  leaf-row paths (``parent[].child``, ``parent.child``) instead of producing
  a single aggregate ``n/a`` row.
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
    / "cu-sdk-author-analyzer"
    / "scripts"
    / "create_and_test.py"
)


def _load_script():
    spec = importlib.util.spec_from_file_location(
        "_skill_create_and_test", _SCRIPT_PATH
    )
    assert spec and spec.loader, "could not load create_and_test.py"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


script = _load_script()


# ---------------------------------------------------------------------------
# --help
# ---------------------------------------------------------------------------


def test_help_exits_zero_and_lists_flags(capsys):
    with pytest.raises(SystemExit) as exc:
        script.main(["--help"])
    assert exc.value.code == 0
    out = capsys.readouterr().out
    for flag in ("--schema", "--input", "--output", "--analyzer-id", "--iterations", "--ephemeral"):
        assert flag in out, f"--help output missing {flag}"


# ---------------------------------------------------------------------------
# Invalid schema aborts with exit 2 before any client is built
# ---------------------------------------------------------------------------


def test_invalid_schema_exits_2_without_building_client(tmp_path, monkeypatch, capsys):
    bad_schema = tmp_path / "bad.json"
    bad_schema.write_text(
        json.dumps({"baseAnalyzerId": "prebuilt-documentAnalyzer"}),  # typo
        encoding="utf-8",
    )
    fake_input = tmp_path / "doc.pdf"
    fake_input.write_bytes(b"%PDF-1.4 stub")
    out_dir = tmp_path / "out"

    def _explode():
        raise AssertionError("_build_client must not be called when validation fails")

    monkeypatch.setattr(script, "_build_client", _explode)

    rc = script.main(
        [
            "--schema", str(bad_schema),
            "--input", str(fake_input),
            "--output", str(out_dir),
        ]
    )
    assert rc == 2
    err = capsys.readouterr().err
    assert "[VALIDATE]" in err
    assert "baseAnalyzerId" in err


# ---------------------------------------------------------------------------
# summarize() leaf-row rendering
# ---------------------------------------------------------------------------


def _scalar(value, conf):
    return {"type": "string", "valueString": value, "confidence": conf}


def _number(value, conf):
    return {"type": "number", "valueNumber": value, "confidence": conf}


def _array_of_objects(items):
    return {"type": "array", "valueArray": items}


def _object(obj):
    return {"type": "object", "valueObject": obj}


def test_summarize_flattens_nested_array_and_object_fields():
    doc = {
        "contents": [
            {
                "fields": {
                    "invoiceNumber": _scalar("INV-100", 0.95),
                    "lineItems": _array_of_objects(
                        [
                            _object(
                                {
                                    "itemCode": _scalar("A123", 0.80),
                                    "amount": _number(60.0, 0.92),
                                }
                            ),
                            _object(
                                {
                                    "itemCode": _scalar("B456", 0.70),
                                    "amount": _number(30.0, 0.90),
                                }
                            ),
                        ]
                    ),
                    "address": _object(
                        {
                            "street": _scalar("123 Main St", 0.88),
                        }
                    ),
                }
            }
        ]
    }

    out = script.summarize([("docX", doc)])

    # Leaf rows present.
    assert "lineItems[].itemCode" in out
    assert "lineItems[].amount" in out
    assert "address.street" in out
    assert "invoiceNumber" in out

    # The old aggregate-only behaviour would emit a `lineItems` row with `n/a`
    # confidence and no children. The new behaviour must not emit a bare
    # `lineItems` row.
    for line in out.splitlines():
        stripped = line.strip()
        assert not (stripped.startswith("lineItems ") or stripped.startswith("address "))

    # Lowest-confidence list should rank the 0.70 leaf at the top.
    assert "0.700" in out
    assert "lineItems[].itemCode" in out.split("lowest-confidence")[-1]
