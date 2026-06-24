# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Centralized durable-dispatch decisions (Spec 033 §3.3 / FR-006).

The row/disposition mapping for the durability matrix is decided in exactly one
place here, rather than being re-derived inline at each call site. Call sites
consume :func:`decide_disposition` (and :func:`classify_row`) instead of
re-implementing the ``"re-invoke" if … else "mark-failed"`` rule.
"""

from __future__ import annotations

# The two durable-recovery dispositions stamped into the ``_responses``
# framework metadata namespace and read by the recovery scanner.
DISPOSITION_REINVOKE = "re-invoke"
DISPOSITION_MARK_FAILED = "mark-failed"


def decide_disposition(
    *,
    background: bool,
    durable_background: bool,
    store: bool,
) -> str:
    """Return the durable-recovery disposition for a response.

    The single decision site (Spec 033 FR-006). A response is **re-invoked** on
    crash recovery only when it is a stored, background response running under
    ``durable_background`` (durability matrix Row 1); every other durable row
    (Row 2 ``durable_background=False``, Row 3 foreground+store) is **marked
    failed** on recovery — the handler is not re-run.

    :keyword background: The request's ``background`` flag.
    :paramtype background: bool
    :keyword durable_background: The deployment's ``durable_background`` option.
    :paramtype durable_background: bool
    :keyword store: The request's ``store`` flag.
    :paramtype store: bool
    :returns: ``DISPOSITION_REINVOKE`` or ``DISPOSITION_MARK_FAILED``.
    :rtype: str
    """
    if background and durable_background and store:
        return DISPOSITION_REINVOKE
    return DISPOSITION_MARK_FAILED


def classify_row(
    *,
    store: bool,
    background: bool,
    durable_background: bool,
) -> int:
    """Return the durability-matrix row number (1-4) for a response.

    Row 1: ``store + background + durable_background`` (full recovery).
    Row 2: ``store + background`` without ``durable_background`` (mark-failed).
    Row 3: ``store`` foreground (mark-failed).
    Row 4: ``store=false`` (no durable state; no recovery).

    :keyword store: The request's ``store`` flag.
    :paramtype store: bool
    :keyword background: The request's ``background`` flag.
    :paramtype background: bool
    :keyword durable_background: The deployment's ``durable_background`` option.
    :paramtype durable_background: bool
    :returns: The matrix row number (1-4).
    :rtype: int
    """
    if not store:
        return 4
    if not background:
        return 3
    return 1 if durable_background else 2
