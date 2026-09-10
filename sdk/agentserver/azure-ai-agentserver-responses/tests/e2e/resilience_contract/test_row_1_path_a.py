# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Row 1 × Path A — ``(store=true, bg=true, resilient_bg=True)`` × ``stream=F/T``.

Path A: handler completes within the configured grace period (the
"happy path"). No framework recovery involvement; the response
transitions to ``completed`` naturally.

EXPECTED: GREEN today; regression guard.

Contract source: ``sdk/agentserver/specs/resilience-contract.md``
§ Per-row contracts → Row 1, Path A.
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
async def test_row_1_path_a(make_harness: Callable[..., CrashHarness], stream: bool) -> None:
    """Row 1 Path A: resilient+bg handler completes naturally within grace."""
    harness = make_harness(
        resilient_background=True,
        handler_sleep_ms=50,
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
        terminal = await poll_until_terminal(harness.client, response_id)
        assert terminal["status"] == "completed", terminal
        # Spec 032 / FR-001 depth: the polled response.output is the contract
        # surface — assert it reflects the fresh (lifetime-0) handler's content,
        # not just a terminal status. The conformance handler tags its final
        # text ``L0_done|…``.
        markers = output_text_markers(terminal)
        assert markers, f"Row 1 Path A response.output must carry content; got: {terminal.get('output')!r}"
        assert markers[-1].startswith(
            "L0_done"
        ), f"Row 1 Path A response.output must reflect the fresh handler (L0_done…); got: {markers!r}"
    finally:
        await harness.close()
