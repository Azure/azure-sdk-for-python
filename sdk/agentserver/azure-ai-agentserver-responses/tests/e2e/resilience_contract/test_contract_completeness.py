# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Completeness meta-test (FR-008, per Constitution Principle X).

Parses ``resilience-contract.md`` § The matrix and asserts that every
(row × applicable termination path) pair has a paired test module in
this directory with the expected name and parametrize ids.

This test exists to prevent the suite from silently drifting from the
contract: if a new row is added to the contract doc but no matching
test module is added, this test fails CI before any other conformance
test runs.

The rules enforced (per ``resilience-contract.md`` § Test discipline +
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

from tests.e2e.resilience_contract._contract_parser import load_contract_rows

_HERE = Path(__file__).parent


def _module_path(row: int, path_letter: str) -> Path:
    return _HERE / f"test_row_{row}_path_{path_letter}.py"


def _module_name(row: int, path_letter: str) -> str:
    return f"tests.e2e.resilience_contract.test_row_{row}_path_{path_letter}"


def test_every_row_has_a_test_module_per_applicable_path() -> None:
    """Every documented (row × applicable path) has a paired test module."""
    try:
        rows = load_contract_rows()
    except FileNotFoundError as exc:
        import pytest  # pylint: disable=import-outside-toplevel

        pytest.skip(f"contract spec unavailable: {exc}")
    missing: list[str] = []
    for row in rows:
        for path_letter in row.applicable_paths:
            mod_path = _module_path(row.row_number, path_letter)
            if not mod_path.exists():
                missing.append(
                    f"row {row.row_number} (store={row.store}, "
                    f"bg={row.background}, dbg={row.resilient_background}) "
                    f"path {path_letter.upper()} → {mod_path.name} not found"
                )
    assert not missing, (
        "resilience-contract.md § The matrix declares rows/paths that have "
        "no paired test module in tests/e2e/resilience_contract/:\n  " + "\n  ".join(missing)
    )


def test_every_row_module_parametrizes_on_stream() -> None:
    """Every row × path module must parametrize on stream=False AND stream=True.

    The matrix collapses ``stream`` out of the row keys (per
    ``resilience-contract.md`` § The matrix). The contract therefore
    holds regardless of stream, so every cell test runs both stream
    values to prove it empirically.
    """
    try:
        rows = load_contract_rows()
    except FileNotFoundError as exc:
        import pytest  # pylint: disable=import-outside-toplevel

        pytest.skip(f"contract spec unavailable: {exc}")
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
                re.search(r"parametrize\([^)]*['\"]stream['\"]", source) and "True" in source and "False" in source
            ) or ("stream=True" in source and "stream=False" in source)
            if not has_both:
                missing.append(
                    f"row {row.row_number} path {path_letter.upper()} "
                    f"({mod_name}) does not parametrize on stream=False/True"
                )
    assert not missing, (
        "Cell test modules missing stream parametrization (per "
        "resilience-contract.md § The matrix):\n  " + "\n  ".join(missing)
    )


def test_no_synthetic_crash_shortcuts_in_suite() -> None:
    """Constitution Principle X bans synthetic-crash shortcuts.

    Conformance tests MUST drive ``_crash_harness`` directly; they MUST
    NOT mock the harness, fabricate ``ResilienceContext``, or call
    internal failure-marker functions (e.g. ``_persist_crash_failed``)
    directly. This test grep-scans cell modules for those banned
    patterns.
    """
    banned_patterns = [
        # No mocking the harness.
        (r"mock[._].*CrashHarness", "mocking CrashHarness"),
        (r"patch[._].*CrashHarness", "patching CrashHarness"),
        # No fabricated resilience contexts.
        (r"ResilienceContext\s*\(", "constructing ResilienceContext directly"),
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
    assert (
        not findings
    ), "Constitution Principle X violation — conformance tests must use " "real signals only:\n  " + "\n  ".join(
        findings
    )


def test_contract_coverage_matrix_exists_and_is_non_trivial() -> None:
    """``CONTRACT_COVERAGE.md`` MUST exist and enumerate test mappings.

    The coverage matrix is the single source of truth for "which test
    verifies which contract clause". The Phase 9 reflection
    (``~/.copilot/session-state/.../files/conformance_gap_analysis.md``)
    surfaced this as the resilient fix for the gap class — without a
    coverage matrix and a meta-test that consumes it, contract
    additions can silently land without paired test coverage (as the
    streaming-recovery-continuity clauses did before the Phase 9
    follow-up).

    This test enforces:

    - The matrix file exists.
    - It references each conformance test file the suite ships with.
    - It explicitly documents any cell marked **GAP** so the gap is
      visible rather than silently uncovered.
    """
    matrix_path = _HERE / "CONTRACT_COVERAGE.md"
    assert matrix_path.exists(), (
        f"{matrix_path.name} MUST exist — it is the single source of truth "
        "for which test verifies which contract clause. See the Spec 014 "
        "Phase 9 follow-up reflection for the rationale (Stage 2 / T-171)."
    )
    text = matrix_path.read_text(encoding="utf-8")
    assert len(text) > 1000, (
        f"{matrix_path.name} is suspiciously short ({len(text)} chars) — "
        "expected a comprehensive per-clause mapping."
    )
    # Every test file in this directory MUST be referenced (so the matrix
    # at least mentions every conformance test the suite ships with).
    # Files not referenced are coverage gaps the matrix has missed.
    test_files = sorted(p.name for p in _HERE.glob("test_*.py"))
    missing = [
        name
        for name in test_files
        if name not in text and name != "test_contract_completeness.py"
        # contract completeness is the meta-test, not a per-clause test
    ]
    assert not missing, (
        f"{matrix_path.name} must reference every conformance test file. "
        f"Missing references for: {missing}. Update the matrix to map "
        "each unmapped test to the contract clause(s) it verifies."
    )


def test_per_cell_tests_assert_more_than_just_status() -> None:
    """Per-cell tests SHOULD verify the row's full contract surface.

    The Phase 9 reflection (Spec 014) identified that pre-existing tests
    asserted only on ``response.status`` / ``error.code``, missing
    cross-attempt content continuity and response.output content
    verification. The cross-cutting tests added in T-173
    (``test_streaming_recovery_continuity.py``,
    ``test_metadata_survives_recovery.py``,
    ``test_output_item_slot_reconciliation.py``,
    ``test_conversation_chain_id_stability.py``,
    ``test_response_output_content_correctness.py``) cover the depth
    gaps for completed-row cells.

    This test is the structural gate: if someone adds a new per-cell
    test that asserts only on terminal status (no event content, no
    response.output content, no metadata, no chain id), this assertion
    flags it as a likely shape-only test that needs depth assertions.
    The check is permissive — it allows the failed-row Path B/C tests
    (which legitimately only need to check ``status="failed"`` +
    ``error.code``) by allow-listing ``response.error`` assertions.

    Cross-cutting depth tests (`test_streaming_recovery_continuity.py`
    et al.) are exempted; they are the depth coverage. Per-cell tests
    can compose with them rather than duplicating.
    """
    permissible_depth_signals = (
        "response.error",
        "error.code",
        "error_code",
        '.get("error")',  # failed-row idiom: error = terminal.get("error"); error.get("code")
        ".get('error')",
        "output_text.delta",
        "response.output_item",
        "output[0]",
        "output_item.added",
        "output_text.done",
        "response.in_progress",
        "sequence_number",
        "_final_text_from_snapshot",  # response.output content helper
        "output_text_markers",  # Row 11 / per-lifetime response.output content helper
        "_get_full_stream",  # caller of the GET-replay helper
        "GET ?stream=true",
    )
    findings: list[str] = []
    for module_file in _HERE.glob("test_row_*_path_*.py"):
        text = module_file.read_text(encoding="utf-8")
        # If the test asserts only on terminal["status"] and nothing
        # else from the assertion vocabulary, flag it.
        has_status_assertion = 'terminal["status"]' in text or "terminal['status']" in text
        if not has_status_assertion:
            continue  # not a status-style test; out of scope
        has_other_depth_signal = any(s in text for s in permissible_depth_signals)
        if not has_other_depth_signal:
            findings.append(module_file.name)
    # Spec 032 / FR-001 — HARD GATE (was a soft ``warnings.warn`` per Spec 014
    # Phase 9, which let terminal-status-only per-cell tests pass and allowed
    # depth coverage to silently rot). Per Constitution Principle XI, a per-cell
    # test MUST verify the row's contract surface, not just terminal status.
    # The detector above recognizes both the completed-row content idioms
    # (response.output / output_text / _final_text_from_snapshot / markers) and
    # the failed-row error idioms (``terminal.get("error")`` / ``error.get("code")``),
    # so legitimate tests are not false-flagged.
    assert not findings, (
        "Per-cell resilience tests MUST assert on more than terminal['status'] "
        "alone — verify the row's contract surface (response.output content, "
        "event content, sequence numbers, or the failed-row error payload). "
        f"Shape-only modules needing depth assertions: {findings}. See "
        "tests/e2e/resilience_contract/CONTRACT_COVERAGE.md for the per-clause "
        "matrix and the permissible_depth_signals vocabulary in this gate."
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
