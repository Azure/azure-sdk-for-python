# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Row 1 × Path C with a request-carried ``agent_reference`` (hosted-shaped input).

**Why this test exists (conformance gap closure).**

The hosted gateway injects an ``agent_reference`` onto every request, which the
library normalizes into an :class:`AgentReference` *model* (a Mapping, but NOT
``json.dumps``-serializable). That model flows into the resilient-task input
(``_start_resilient_background`` -> ``start_resilient`` -> ``_split_runtime_refs``).
If it is persisted un-normalized, the core resilient ``create_and_start`` ->
``_resolve_input_storage`` size check raises
``TypeError: Object of type AgentReference is not JSON serializable`` and the
whole resilient start **silently falls back to a non-resilient ``asyncio.create_task``**
— so no resilient task exists and crash recovery never happens.

Every other resilience test sends NO ``agent_reference`` (so
``_normalize_agent_reference`` returns the ``{}`` sentinel, which is trivially
serializable) or a plain string — so none of them exercised the model form and
the bug shipped invisibly. This test mirrors the hosted condition: it puts an
``agent_reference`` on the request and then crashes (Path C). Because resilient
start is **provider-agnostic**, the bug reproduces locally: if the model leaks
into the resilient input, the resilient task is never created, the SIGKILL'd
non-resilient task is lost, and recovery never reaches ``completed`` — failing
this test. With the fix (normalize model -> dict before persisting) the resilient
task is created and recovery completes.

Contract source: ``resilience-contract.md`` § Per-row contracts → Row 1.
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable

import pytest

from tests.e2e._crash_harness import CrashHarness
from tests.e2e.resilience_contract.conftest import (
    LONG_GRACE_S,
    LONG_TIME_SECS,
    poll_until_terminal,
    post_and_get_response_id,
)

# A realistic hosted-shaped agent_reference. The library normalizes this dict
# into an AgentReference MODEL (not a plain dict) on the way in, reproducing the
# exact value the hosted gateway injects.
_AGENT_REFERENCE = {
    "type": "agent_reference",
    "name": "resilience-conformance-agent",
    "version": "1",
}


@pytest.mark.asyncio
@pytest.mark.parametrize("stream", [False, True], ids=["stream=False", "stream=True"])
async def test_row_1_path_c_recovers_with_agent_reference(
    make_harness: Callable[..., CrashHarness], stream: bool
) -> None:
    """A resilient bg request carrying an ``agent_reference`` MUST still start a
    resilient task and recover after SIGKILL.

    Regression guard for the hosted ``AgentReference is not JSON serializable``
    resilient-start failure that silently degraded resilient background responses to
    non-resilient ``asyncio.create_task`` (no crash recovery).
    """
    harness = make_harness(
        resilient_background=True,
        handler_sleep_ms=int(LONG_TIME_SECS * 1000),
        shutdown_grace_seconds=LONG_GRACE_S,
    )
    await harness.start()
    try:
        response_id = await post_and_get_response_id(
            harness.client,
            store=True,
            background=True,
            stream=stream,
            extra={"agent_reference": _AGENT_REFERENCE},
        )
        # Let the handler begin before the SIGKILL.
        await asyncio.sleep(0.5)

        await harness.kill()
        await harness.restart()

        # If agent_reference broke resilient start, the SIGKILL'd asyncio fallback
        # left no resilient record -> this never reaches "completed".
        terminal = await poll_until_terminal(
            harness.client,
            response_id,
            timeout_seconds=30.0,
        )
        assert terminal["status"] == "completed", terminal
    finally:
        await harness.close()
