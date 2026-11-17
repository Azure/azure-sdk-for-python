# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Row 3 × Path A — ``(store=true, bg=false)`` × ``stream=F/T``.

Path A: foreground handler completes within grace, returning the
terminal directly to the client.

EXPECTED: GREEN today; regression guard.

Contract source: ``resilience-contract.md`` § Per-row contracts → Row 3.
"""

from __future__ import annotations

from collections.abc import Callable

import pytest

from tests.e2e._crash_harness import CrashHarness
from tests.e2e.resilience_contract.conftest import LONG_GRACE_S


@pytest.mark.asyncio
@pytest.mark.parametrize("stream", [False, True], ids=["stream=False", "stream=True"])
async def test_row_3_path_a(make_harness: Callable[..., CrashHarness], stream: bool) -> None:
    """Row 3 Path A: foreground handler completes naturally on the HTTP connection."""
    harness = make_harness(
        resilient_background=True,  # resilient_background is "any" for row 3
        handler_sleep_ms=50,
        shutdown_grace_seconds=LONG_GRACE_S,
    )
    await harness.start()
    try:
        body = {
            "model": "conformance-test",
            "input": "hello",
            "store": True,
            "background": False,
            "stream": stream,
        }
        if stream:
            # Streamed foreground — read until terminal event.
            import json

            terminal_seen = False
            terminal_type = ""
            async with harness.client.stream("POST", "/responses", json=body, timeout=15.0) as resp:
                assert resp.status_code == 200, await resp.aread()
                async for line in resp.aiter_lines():
                    if not line.startswith("data:"):
                        continue
                    try:
                        payload = json.loads(line.removeprefix("data:").strip())
                    except json.JSONDecodeError:
                        continue
                    etype = payload.get("type", "")
                    if etype in (
                        "response.completed",
                        "response.failed",
                        "response.cancelled",
                    ):
                        terminal_seen = True
                        terminal_type = etype
                        break
            assert terminal_seen, "no terminal event observed on foreground stream"
            assert terminal_type == "response.completed", terminal_type
        else:
            r = await harness.client.post("/responses", json=body, timeout=15.0)
            assert r.status_code == 200, r.text
            data = r.json()
            assert data["status"] == "completed", data
    finally:
        await harness.close()
