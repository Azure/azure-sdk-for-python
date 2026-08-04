# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Row 11 × Path A — developer checkpoint write, handler completes within grace.

Row 11 is the **developer-checkpoint-write** contract: an extension of
Row 1 (``store=true, background=true, resilient_background=True``) covering
``yield stream.checkpoint()`` in the one-OutputItem-per-phase pattern.

Path A: the handler runs all phases and reaches a natural terminal within
the grace period. Checkpoints fire at every phase boundary but no crash
occurs, so the final ``response.output`` reflects every phase produced by
the fresh entry — each carrying the lifetime-0 marker ``L0_phase{n}``.

This is the regression-guard happy path; the recovery cutpoints live in
Path B (graceful) and Path C (SIGKILL).

Contract source: ``docs/resilience-contract.md`` § Per-row contracts →
Row 11, Path A (Principle XI: asserts ``response.output`` content, not just
status).
"""

from __future__ import annotations

from collections.abc import Callable

import pytest

from tests.e2e._crash_harness import CrashHarness
from tests.e2e.resilience_contract.conftest import (
    LONG_GRACE_S,
    output_text_markers,
    poll_until_terminal,
    post_and_get_response_id,
)


@pytest.mark.asyncio
@pytest.mark.parametrize("stream", [False, True], ids=["stream=False", "stream=True"])
async def test_row_11_path_a(make_checkpoint_harness: Callable[..., CrashHarness], stream: bool) -> None:
    """Row 11 Path A: all phases checkpoint + complete naturally; output = all L0."""
    harness = make_checkpoint_harness(phases=3, crash_cutpoint=None, shutdown_grace_seconds=LONG_GRACE_S)
    await harness.start()
    try:
        response_id = await post_and_get_response_id(
            harness.client,
            store=True,
            background=True,
            stream=stream,
        )
        terminal = await poll_until_terminal(harness.client, response_id)
        assert terminal["status"] == "completed", terminal
        # Principle XI content-depth: every phase produced by the fresh
        # entry, in order, each tagged with the lifetime-0 marker.
        assert output_text_markers(terminal) == ["L0_phase0", "L0_phase1", "L0_phase2"], terminal
    finally:
        await harness.close()
