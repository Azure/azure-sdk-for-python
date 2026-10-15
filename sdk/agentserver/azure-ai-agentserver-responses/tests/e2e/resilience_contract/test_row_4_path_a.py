# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Row 4 × Path A — ``(store=false, ...)`` × ``stream=F/T`` × ``background=F/T``.

Path A: handler completes naturally; no persistence. The response
appears only over the original HTTP connection.

For ``background=False, stream=False``: the POST blocks until terminal.
For ``background=False, stream=True``: SSE delivered live until terminal.
For ``background=True, stream=False``: POST returns in-progress; client
  polls — but with ``store=false`` the response can't be retrieved.
  Today this combination is accepted; the contract is "best-effort".
For ``background=True, stream=True``: in-progress + live SSE on the
  same connection.

EXPECTED: GREEN today; regression guard.

Contract source: ``resilience-contract.md`` § Per-row contracts → Row 4.
"""

from __future__ import annotations

import json
from collections.abc import Callable

import pytest

from tests.e2e._crash_harness import CrashHarness
from tests.e2e.resilience_contract.conftest import LONG_GRACE_S


@pytest.mark.asyncio
@pytest.mark.parametrize("stream", [False, True], ids=["stream=False", "stream=True"])
async def test_row_4_path_a(
    make_harness: Callable[..., CrashHarness],
    stream: bool,
) -> None:
    """Row 4 Path A: store=false handler completes; no persistence required.

    Note: ``background=True`` is parametrized out because the framework
    rejects ``(store=false, background=true)`` with HTTP 400
    ``unsupported_parameter`` ("background=true requires store=true").
    Row 4 is therefore exercised with ``background=False`` only.
    """
    harness = make_harness(
        resilient_background=False,
        handler_sleep_ms=50,
        shutdown_grace_seconds=LONG_GRACE_S,
    )
    await harness.start()
    try:
        body = {
            "model": "conformance-test",
            "input": "hello",
            "store": False,
            "background": False,
            "stream": stream,
        }
        if stream:
            terminal_seen = False
            async with harness.client.stream("POST", "/responses", json=body, timeout=15.0) as resp:
                assert resp.status_code == 200, await resp.aread()
                async for line in resp.aiter_lines():
                    if not line.startswith("data:"):
                        continue
                    try:
                        payload = json.loads(line.removeprefix("data:").strip())
                    except json.JSONDecodeError:
                        continue
                    if payload.get("type", "") in (
                        "response.completed",
                        "response.failed",
                        "response.cancelled",
                    ):
                        terminal_seen = True
                        break
            assert terminal_seen, "no terminal event on row 4 stream"
        else:
            r = await harness.client.post("/responses", json=body, timeout=15.0)
            assert r.status_code == 200, r.text
            data = r.json()
            assert data.get("status") == "completed", data
    finally:
        await harness.close()
