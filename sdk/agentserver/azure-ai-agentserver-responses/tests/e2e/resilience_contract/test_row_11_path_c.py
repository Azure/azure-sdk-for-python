# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Row 11 × Path C — developer checkpoint write, SIGKILL mid-handler.

Row 11 extends Row 1 (``store=true, background=true, resilient_background=True``)
with the ``yield stream.checkpoint()`` write point. Path C drives a real
SIGKILL (via ``_crash_harness``) at a deterministic cutpoint, then restarts
and asserts recovery resumes from the checkpointed snapshot — proving the
central guarantee of the one-OutputItem-per-phase pattern.

The crash signal is timed against the **persisted** ``output`` length (a
checkpoint persists the phases completed so far), so the cutpoint is
deterministic rather than clock-raced:

- **C1 — ``after_checkpoint:1``**: phase 1's checkpoint has persisted
  (2 items) when we SIGKILL. Recovery resumes at phase 2, so phases 0–1
  survive with their lifetime-0 markers and only phase 2 re-runs as
  lifetime-1 → ``[L0_phase0, L0_phase1, L1_phase2]``. No data loss, no
  duplication.
- **C3 — ``before_checkpoint:1``**: phase 1's item was emitted but its
  checkpoint never ran (only phase 0 is persisted, 1 item) when we SIGKILL.
  Recovery resumes at phase 1, so phase 1 re-runs as lifetime-1 →
  ``[L0_phase0, L1_phase1, L1_phase2]``. This is the central guarantee:
  an un-checkpointed phase is re-run, not lost or duplicated.

(C2 "checkpoint crashes mid-write" is NOT a deterministic cutpoint with the
``FileResponseStore`` provider — ``update_response`` commits the envelope via
an atomic ``os.replace``, so a mid-write crash exposes either the prior or
the newly-committed snapshot, never a torn one. The provider-atomicity
limitation is documented in the contract matrix; no torn-write recovery is
asserted. C4/C5 are unit-tested in ``tests/unit/test_checkpoint.py``.)

Contract source: ``docs/resilience-contract.md`` § Per-row contracts →
Row 11, Path C.
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable

import pytest

from tests.e2e._crash_harness import CrashHarness
from tests.e2e.resilience_contract.conftest import (
    LONG_GRACE_S,
    output_text_markers,
    poll_until_terminal,
    post_and_get_response_id,
)

# (cutpoint, expected post-recovery markers)
_CUTPOINTS = [
    ("after_checkpoint:1", ["L0_phase0", "L0_phase1", "L1_phase2"]),
    ("before_checkpoint:1", ["L0_phase0", "L1_phase1", "L1_phase2"]),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("stream", [False, True], ids=["stream=False", "stream=True"])
@pytest.mark.parametrize(
    "cutpoint, expected_markers",
    _CUTPOINTS,
    ids=["C1=after_checkpoint", "C3=before_checkpoint"],
)
async def test_row_11_path_c(
    make_checkpoint_harness: Callable[..., CrashHarness],
    stream: bool,
    cutpoint: str,
    expected_markers: list[str],
) -> None:
    """Row 11 Path C: SIGKILL at a checkpoint cutpoint → recovery resumes correctly."""
    harness = make_checkpoint_harness(
        phases=3,
        crash_cutpoint=cutpoint,
        shutdown_grace_seconds=LONG_GRACE_S,
    )
    await harness.start()
    try:
        response_id = await post_and_get_response_id(
            harness.client,
            store=True,
            background=True,
            stream=stream,
        )
        # The handler emits phases up to the cutpoint as fast as it can, then
        # parks forever at the cutpoint pause (it cannot advance further on
        # the fresh entry). A fixed margin guarantees it has reached and is
        # parked at the cutpoint, so the SIGKILL lands at the intended
        # checkpoint boundary deterministically.
        await asyncio.sleep(1.0)

        await harness.kill()
        await harness.restart()

        terminal = await poll_until_terminal(harness.client, response_id, timeout_seconds=30.0)
        assert terminal["status"] == "completed", terminal
        # Principle XI content-depth: per-lifetime markers make the
        # resume-point (and absence of loss/duplication) directly visible.
        assert output_text_markers(terminal) == expected_markers, terminal
    finally:
        await harness.close()
