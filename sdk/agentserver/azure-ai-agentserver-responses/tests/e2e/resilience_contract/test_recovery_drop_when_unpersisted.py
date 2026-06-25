# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Spec 026 FR-026-4/5/6 — recovery drops an unpersisted response.

Real-signal conformance (Constitution Principle X): a resilient background
handler is SIGKILLed **before** it emits ``response.created`` (before the
framework persists the response). On restart the recovery scan reclaims
the task, but the responses layer MUST drop it — no re-invocation, no
terminal — because the original ``POST`` returned no response id a client
could fetch.

Scoped to the non-streaming background path. The drop **gate** is shared
code that runs on the recovered-entry path *before* the stream-vs-non-stream
dispatch (FR-026-7, verified by code position), but the never-persisted
precondition is only deterministically reproducible for ``stream=False``:
the bg+streaming path persists the response early at ``POST`` (so a
reconnecting client can replay), so a pre-create crash there leaves the
response *persisted* and recovery correctly re-invokes instead of dropping.
"""

from __future__ import annotations

import asyncio
from pathlib import Path

import httpx
import pytest

from tests.e2e._crash_harness import CrashHarness

_DROP_HANDLER = "tests.e2e.resilience_contract._drop_handler"


async def _fire_post(base_url: str, body: dict) -> None:
    """Fire the POST that starts the handler. For a pre-create crash the
    stream never resolves (stream=True) or the bg snapshot returns while the
    response is still unpersisted (stream=False) — either way we don't depend
    on its result; the handler's marker file drives the assertions."""
    try:
        async with httpx.AsyncClient(base_url=base_url, timeout=15.0) as c:
            await c.post("/responses", json=body)
    except Exception:  # pylint: disable=broad-exception-caught
        pass  # crash / cancel / hang are all expected


async def _wait_marker_lines(marker: Path, n: int, timeout: float = 20.0) -> str:
    """Wait until the marker file has at least ``n`` lines; return the
    response_id from the first line."""
    deadline = asyncio.get_event_loop().time() + timeout
    while asyncio.get_event_loop().time() < deadline:
        if marker.exists():
            lines = marker.read_text(encoding="utf-8").strip().splitlines()
            if len(lines) >= n:
                return lines[0].split("\t")[1]
        await asyncio.sleep(0.1)
    raise AssertionError(
        f"marker file never reached {n} line(s): " f"{marker.read_text() if marker.exists() else '<missing>'}"
    )


@pytest.mark.asyncio
async def test_recovery_drop_when_unpersisted(tmp_path: Path) -> None:
    """A non-streaming resilient background response crashed before
    ``create_response`` is dropped on recovery (not re-invoked, GET 404).

    Scoped to ``stream=False``: that is where the never-persisted window is
    deterministically reproducible. The bg+**streaming** path persists the
    response early (at POST, so a reconnecting client can replay), so a
    pre-create crash there leaves the response *persisted* and recovery
    correctly re-invokes rather than drops. The drop **gate** itself is the
    same code for both modes — it runs on the shared recovered-entry path
    *before* the stream-vs-non-stream dispatch (verified by code position);
    this test exercises it via the mode that can actually reach the
    definitively-absent precondition.
    """
    stream = False
    marker = tmp_path / "drop_marker.txt"
    harness = CrashHarness(
        sample_module=_DROP_HANDLER,
        tmp_path=tmp_path,
        readiness_timeout_seconds=15.0,
        env_extras={
            "CONFORMANCE_DROP_MARKER_FILE": str(marker),
            # Long pre-create sleep: the handler sits here (task record exists,
            # response NOT yet persisted) until we SIGKILL it.
            "CONFORMANCE_PRE_CREATE_SLEEP_MS": "60000",
            "AGENTSERVER_SHUTDOWN_GRACE_SECONDS": "10",
            "LOGLEVEL": "WARNING",
        },
    )
    await harness.start()
    try:
        body = {
            "model": "conformance-test",
            "input": "hi",
            "store": True,
            "background": True,
            "stream": stream,
        }
        post_task = asyncio.create_task(_fire_post(harness.base_url, body))

        # Handler entered → exactly one invocation, sitting in the pre-create
        # sleep. The resilient task record exists; the response is NOT persisted.
        response_id = await _wait_marker_lines(marker, 1, timeout=20.0)

        # SIGKILL before create_response — the real crash in the pre-create window.
        await harness.kill()
        post_task.cancel()

        # Restart: the cold-start recovery scan reclaims the stale task.
        await harness.restart()
        # Give the scan time to reclaim + drop + settle.
        await asyncio.sleep(8.0)

        # FR-026-4/7: the handler MUST NOT have been re-invoked — the marker
        # file still has exactly one line (the crashed lifetime).
        lines = marker.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 1, (
            "recovery MUST drop an unpersisted response (no re-invocation), "
            f"for stream={stream}; marker lines: {lines}"
        )

        # The response was never resiliently created — GET MUST be not-found.
        async with httpx.AsyncClient(base_url=harness.base_url, timeout=10.0) as c:
            r = await c.get(f"/responses/{response_id}")
            assert r.status_code == 404, (
                f"unpersisted+dropped response must be 404, got {r.status_code} " f"for stream={stream}"
            )
    finally:
        await harness.close()
