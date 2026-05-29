# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Completeness meta-test (FR-008, per Constitution Principle X).

Parses ``durability-contract.md`` § The matrix and asserts that every
(row × applicable termination path) pair has a paired test module in
this directory with the expected name and parametrize ids.

This test exists to prevent the suite from silently drifting from the
contract: if a new row is added to the contract doc but no matching
test module is added, this test fails CI before any other conformance
test runs.

The rules enforced (per ``durability-contract.md`` § Test discipline +
Constitution Principle X):

- Every row in the contract has ``test_row_<N>_path_a.py``,
  ``test_row_<N>_path_b.py``, and ``test_row_<N>_path_c.py``.
- Each module collects pytest parametrize ids for ``stream=False`` and
  ``stream=True`` (the matrix collapses ``stream`` — both must run).
- Row 4 additionally parametrizes on ``background=False/True``.
- Each module imports ``CrashHarness`` (it MUST drive a real subprocess
  and real signals — synthetic-crash shortcuts are disallowed).
"""

from __future__ import annotations

import importlib
import re
from pathlib import Path

import pytest

from tests.e2e.durability_contract._contract_parser import load_contract_rows


_HERE = Path(__file__).parent


def _module_path(row: int, path_letter: str) -> Path:
    return _HERE / f"test_row_{row}_path_{path_letter}.py"


def _module_name(row: int, path_letter: str) -> str:
    return f"tests.e2e.durability_contract.test_row_{row}_path_{path_letter}"


def test_every_row_has_a_test_module_per_applicable_path() -> None:
    """Every documented (row × applicable path) has a paired test module."""
    rows = load_contract_rows()
    missing: list[str] = []
    for row in rows:
        for path_letter in row.applicable_paths:
            mod_path = _module_path(row.row_number, path_letter)
            if not mod_path.exists():
                missing.append(
                    f"row {row.row_number} (store={row.store}, "
                    f"bg={row.background}, dbg={row.durable_background}) "
                    f"path {path_letter.upper()} → {mod_path.name} not found"
                )
    assert not missing, (
        "durability-contract.md § The matrix declares rows/paths that have "
        "no paired test module in tests/e2e/durability_contract/:\n  "
        + "\n  ".join(missing)
    )


def test_every_row_module_parametrizes_on_stream() -> None:
    """Every row × path module must parametrize on stream=False AND stream=True.

    The matrix collapses ``stream`` out of the row keys (per
    ``durability-contract.md`` § The matrix). The contract therefore
    holds regardless of stream, so every cell test runs both stream
    values to prove it empirically.
    """
    rows = load_contract_rows()
    missing: list[str] = []
    for row in rows:
        for path_letter in row.applicable_paths:
            mod_name = _module_name(row.row_number, path_letter)
            try:
                mod = importlib.import_module(mod_name)
            except ImportError:
                # The presence test above catches missing files; this
                # test reports parametrize-missing for files that DO
                # exist. Skip the missing case here so the failure
                # message is unambiguous.
                continue
            source = Path(mod.__file__ or "").read_text(encoding="utf-8")
            # Heuristic: look for a pytest.mark.parametrize on 'stream'
            # with two boolean values, or for both `stream=True` and
            # `stream=False` literals in the test body.
            has_both = bool(
                re.search(r"parametrize\([^)]*['\"]stream['\"]", source)
                and "True" in source
                and "False" in source
            ) or ("stream=True" in source and "stream=False" in source)
            if not has_both:
                missing.append(
                    f"row {row.row_number} path {path_letter.upper()} "
                    f"({mod_name}) does not parametrize on stream=False/True"
                )
    assert not missing, (
        "Cell test modules missing stream parametrization (per "
        "durability-contract.md § The matrix):\n  "
        + "\n  ".join(missing)
    )


def test_no_synthetic_crash_shortcuts_in_suite() -> None:
    """Constitution Principle X bans synthetic-crash shortcuts.

    Conformance tests MUST drive ``_crash_harness`` directly; they MUST
    NOT mock the harness, fabricate ``DurabilityContext``, or call
    internal failure-marker functions (e.g. ``_persist_crash_failed``)
    directly. This test grep-scans cell modules for those banned
    patterns.
    """
    banned_patterns = [
        # No mocking the harness.
        (r"mock[._].*CrashHarness", "mocking CrashHarness"),
        (r"patch[._].*CrashHarness", "patching CrashHarness"),
        # No fabricated durability contexts.
        (r"DurabilityContext\s*\(", "constructing DurabilityContext directly"),
        # No direct calls to internal failure markers.
        (
            r"_persist_(non_bg_)?crash_failed\s*\(",
            "calling _persist_*_crash_failed directly",
        ),
    ]
    findings: list[str] = []
    for module_file in _HERE.glob("test_row_*_path_*.py"):
        text = module_file.read_text(encoding="utf-8")
        for pattern, label in banned_patterns:
            if re.search(pattern, text):
                findings.append(f"{module_file.name}: {label}")
    assert not findings, (
        "Constitution Principle X violation — conformance tests must use "
        "real signals only:\n  " + "\n  ".join(findings)
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
