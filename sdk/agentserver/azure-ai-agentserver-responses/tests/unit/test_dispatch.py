# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Unit tests for centralized resilient-dispatch decisions (Spec 033 FR-006)."""

from __future__ import annotations

import re
from pathlib import Path

from azure.ai.agentserver.responses.hosting._dispatch import (
    DISPOSITION_MARK_FAILED,
    DISPOSITION_REINVOKE,
    classify_row,
    decide_disposition,
)


def test_decide_disposition_truth_table() -> None:
    # Row 1: stored background under resilient_background → re-invoke.
    assert decide_disposition(background=True, resilient_background=True, store=True) == DISPOSITION_REINVOKE
    # Row 2: stored background WITHOUT resilient_background → mark-failed.
    assert decide_disposition(background=True, resilient_background=False, store=True) == DISPOSITION_MARK_FAILED
    # Row 3: foreground + store → mark-failed.
    assert decide_disposition(background=False, resilient_background=True, store=True) == DISPOSITION_MARK_FAILED
    # No store → mark-failed (Row 4 has no resilient task anyway).
    assert decide_disposition(background=True, resilient_background=True, store=False) == DISPOSITION_MARK_FAILED


def test_classify_row() -> None:
    assert classify_row(store=True, background=True, resilient_background=True) == 1
    assert classify_row(store=True, background=True, resilient_background=False) == 2
    assert classify_row(store=True, background=False, resilient_background=True) == 3
    assert classify_row(store=False, background=True, resilient_background=True) == 4


def test_disposition_not_re_derived_inline_outside_dispatch() -> None:
    """FR-006 grep-gate: the ``"re-invoke" if … else "mark-failed"`` decision
    appears only in ``_dispatch.py``, never re-derived inline elsewhere."""
    hosting = Path(__file__).resolve().parents[2] / "azure" / "ai" / "agentserver" / "responses" / "hosting"
    pattern = re.compile(r'["\']re-invoke["\']\s+if\b')
    offenders = []
    for py in hosting.glob("*.py"):
        if py.name == "_dispatch.py":
            continue
        if pattern.search(py.read_text(encoding="utf-8")):
            offenders.append(py.name)
    assert not offenders, f"inline disposition derivation must move to _dispatch.decide_disposition: {offenders}"
