# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Centralized resilient-dispatch decisions (Spec 033 §3.3 / FR-006).

The row/disposition mapping for the resilience matrix is decided in exactly one
place here, rather than being re-derived inline at each call site. Call sites
consume :func:`decide_disposition` (and :func:`classify_row`) instead of
re-implementing the ``"re-invoke" if … else "mark-failed"`` rule.
"""

from __future__ import annotations

# The two resilient-recovery dispositions carried on the durable task input
# (``ResilientResponseInput.disposition``) and read by the recovery scanner.
DISPOSITION_REINVOKE = "re-invoke"
DISPOSITION_MARK_FAILED = "mark-failed"


def decide_disposition(
    *,
    background: bool,
    resilient_tasks_enabled: bool,
    store: bool,
) -> str:
    """Return the resilient-recovery disposition for a response.

    The single decision site (Spec 033 FR-006). With resilient tasks enabled, a
    stored background response is **re-invoked** (Row 1) and stored foreground
    work is **marked failed** (Row 3). When the switch is disabled (Row 2), no
    task manager exists, so the returned fallback value is not persisted or
    applied by a recovery scanner.

    :keyword background: The request's ``background`` flag.
    :paramtype background: bool
    :keyword resilient_tasks_enabled: Whether resilient tasks are enabled for the process.
    :paramtype resilient_tasks_enabled: bool
    :keyword store: The request's ``store`` flag.
    :paramtype store: bool
    :returns: ``DISPOSITION_REINVOKE`` or ``DISPOSITION_MARK_FAILED``.
    :rtype: str
    """
    if background and resilient_tasks_enabled and store:
        return DISPOSITION_REINVOKE
    return DISPOSITION_MARK_FAILED


def classify_row(
    *,
    store: bool,
    background: bool,
    resilient_tasks_enabled: bool,
) -> int:
    """Return the resilience-matrix row number (1-4) for a response.

    Row 1: ``store + background + resilient_tasks_enabled`` (full recovery).
    Row 2: ``store + background`` with resilient tasks disabled (non-durable).
    Row 3: ``store`` foreground (mark-failed).
    Row 4: ``store=false`` (no resilient state; no recovery).

    :keyword store: The request's ``store`` flag.
    :paramtype store: bool
    :keyword background: The request's ``background`` flag.
    :paramtype background: bool
    :keyword resilient_tasks_enabled: Whether resilient tasks are enabled for the process.
    :paramtype resilient_tasks_enabled: bool
    :returns: The matrix row number (1-4).
    :rtype: int
    """
    if not store:
        return 4
    if not background:
        return 3
    return 1 if resilient_tasks_enabled else 2
