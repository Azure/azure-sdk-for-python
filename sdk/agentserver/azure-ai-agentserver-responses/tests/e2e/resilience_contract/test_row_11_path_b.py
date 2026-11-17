# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Row 11 × Path B — developer checkpoint write, graceful shutdown at a cutpoint.

Row 11 extends Row 1 (``store=true, background=true, resilient_background=True``)
with the ``yield stream.checkpoint()`` write point. Path B drives a real
SIGTERM with a deliberately-short grace period while the handler is parked at
a checkpoint cutpoint. The handler observes ``context.shutdown``, calls
``await context.exit_for_recovery()`` (the unified recovery primitive), and
the framework leaves the response ``in_progress`` for next-lifetime recovery.
On restart the handler resumes from the checkpointed snapshot.

The recovered ``response.output`` content is identical to Path C for the same
cutpoint — the disposition (graceful defer vs abrupt kill) differs but the
checkpoint contract's recovery outcome does not:

- **C1 — ``after_checkpoint:1``**: phase 1 checkpointed before shutdown →
  recovery resumes at phase 2 → ``[L0_phase0, L0_phase1, L1_phase2]``.
- **C3 — ``before_checkpoint:1``**: phase 1 emitted but not checkpointed →
  recovery re-runs phase 1 → ``[L0_phase0, L1_phase1, L1_phase2]``.

Contract source: ``docs/resilience-contract.md`` § Per-row contracts →
Row 11, Path B.
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable

import pytest

from tests.e2e._crash_harness import CrashHarness
from tests.e2e.resilience_contract.conftest import (
    SHORT_GRACE_S,
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
async def test_row_11_path_b(
    make_checkpoint_harness: Callable[..., CrashHarness],
    stream: bool,
    cutpoint: str,
    expected_markers: list[str],
) -> None:
    """Row 11 Path B: graceful shutdown at a cutpoint → exit_for_recovery → recovery."""
    harness = make_checkpoint_harness(
        phases=3,
        crash_cutpoint=cutpoint,
        shutdown_grace_seconds=SHORT_GRACE_S,
    )
    await harness.start()
    try:
        response_id = await post_and_get_response_id(
            harness.client,
            store=True,
            background=True,
            stream=stream,
        )
        # Let the handler reach and park at the cutpoint before SIGTERM.
        await asyncio.sleep(1.0)

        # SIGTERM with short grace. The parked handler observes shutdown and
        # calls exit_for_recovery() → deferral. If it can't defer within
        # grace the harness falls back to SIGKILL (Path C is the documented
        # Path-B-failure fallback, which recovers identically).
        await harness.terminate(wait_seconds=SHORT_GRACE_S + 2.0)
        await harness.restart()

        terminal = await poll_until_terminal(harness.client, response_id, timeout_seconds=30.0)
        assert terminal["status"] == "completed", terminal
        assert output_text_markers(terminal) == expected_markers, terminal
    finally:
        await harness.close()
