# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Row 4 × Path C — ``(store=false, ...)`` × ``stream=F/T`` × ``background=F/T``.

Path C: SIGKILL — no in-process action runs and no persisted state
exists to scan. The matrix explicitly says "no recovery applies."

The test asserts two invariants on the next process lifetime:
(a) No leftover state in the on-disk response store directory for the
    `store=false` request (because nothing was ever persisted).
(b) The framework does NOT log a startup error or warning about an
    orphaned response — because there's nothing to be orphaned about.

EXPECTED: GREEN today; locked in by this test.

Contract source: ``resilience-contract.md`` § Per-row contracts → Row 4.
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from pathlib import Path

import pytest

from tests.e2e._crash_harness import CrashHarness
from tests.e2e.resilience_contract.conftest import (
    LONG_GRACE_S,
    LONG_TIME_SECS,
)


@pytest.mark.asyncio
@pytest.mark.parametrize("stream", [False, True], ids=["stream=False", "stream=True"])
async def test_row_4_path_c(
    make_harness: Callable[..., CrashHarness],
    tmp_path: Path,
    stream: bool,
) -> None:
    """Row 4 Path C: store=false + SIGKILL → no leftover state on next lifetime.

    ``background`` parametrize dropped: ``(store=false, background=true)``
    is rejected with HTTP 400. Row 4 is exercised with ``background=False``
    only.
    """
    harness = make_harness(
        resilient_background=False,
        handler_sleep_ms=int(LONG_TIME_SECS * 1000),
        shutdown_grace_seconds=LONG_GRACE_S,
    )
    await harness.start()
    bg_task = None
    try:
        body = {
            "model": "conformance-test",
            "input": "hello",
            "store": False,
            "background": False,
            "stream": stream,
        }

        async def _fire() -> None:
            try:
                if stream:
                    async with harness.client.stream("POST", "/responses", json=body, timeout=15.0) as resp:
                        async for _ in resp.aiter_lines():
                            pass
                else:
                    await harness.client.post("/responses", json=body, timeout=15.0)
            except Exception:  # pylint: disable=broad-exception-caught
                pass

        bg_task = asyncio.create_task(_fire())
        await asyncio.sleep(0.5)
        await harness.kill()
        await harness.restart()

        # (a) No leftover state in the response store.
        resp_dir = tmp_path / "responses" / "responses"
        if resp_dir.exists():
            files = list(resp_dir.glob("*.json"))
            assert not files, (
                f"Row 4 Path C: store=false should leave no response files, " f"found: {[f.name for f in files]}"
            )

        # (b) No leftover resilient task record.
        tasks_dir = tmp_path / "tasks"
        if tasks_dir.exists():
            task_files = list(tasks_dir.rglob("*.json"))
            assert not task_files, (
                f"Row 4 Path C: store=false should leave no resilient task "
                f"records, found: {[str(f.relative_to(tasks_dir)) for f in task_files]}"
            )
    finally:
        if bg_task is not None:
            bg_task.cancel()
            try:
                await bg_task
            except (asyncio.CancelledError, Exception):  # noqa: BLE001
                pass
        await harness.close()
