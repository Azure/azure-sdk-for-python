# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Row 1 × Path A — ``(store=true, bg=true, durable_bg=True)`` × ``stream=F/T``.

Path A: handler completes within the configured grace period (the
"happy path"). No framework recovery involvement; the response
transitions to ``completed`` naturally.

EXPECTED: GREEN today; regression guard.

Contract source: ``sdk/agentserver/specs/durability-contract.md``
§ Per-row contracts → Row 1, Path A.
"""

from __future__ import annotations

from collections.abc import Callable

import pytest

from tests.e2e._crash_harness import CrashHarness
from tests.e2e.durability_contract.conftest import (
    LONG_GRACE_S,
    poll_until_terminal,
    post_and_get_response_id,
)


@pytest.mark.asyncio
@pytest.mark.parametrize("stream", [False, True], ids=["stream=False", "stream=True"])
async def test_row_1_path_a(make_harness: Callable[..., CrashHarness], stream: bool) -> None:
    """Row 1 Path A: durable+bg handler completes naturally within grace."""
    harness = make_harness(
        durable_background=True,
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
    finally:
        await harness.close()
