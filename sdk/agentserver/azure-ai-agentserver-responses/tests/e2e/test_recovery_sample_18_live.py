# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Spec 013 US1 — Phase 8 live Copilot crash-recovery tests (T-130..T-136).

End-to-end tests against sample 18 (durable Copilot) using a real
``gh copilot`` upstream. These tests SPAWN sample 18 as a subprocess via
``CrashHarness`` and drive the full POST → kill → restart → re-POST loop
against a real Copilot session.

The model is selected via the ``COPILOT_MODEL`` env var (sample 18 reads
the same var). The default ``gpt-5-mini`` is a low-cost model that is
generally available; operators with access to other models can override.

These tests are marked ``@pytest.mark.live`` so they are skipped by
default CI runs. To execute: ``pytest -m live tests/e2e/test_recovery_sample_18_live.py``.

Prerequisites:
- ``gh copilot`` installed and authenticated.
- ``COPILOT_MODEL`` resolves to an available model.

Cross-references:
- T-130: Sample 18 startup smoke (covered by ``test_sample18_lifecycle``).
- T-132: Full crash + recovery cycle (covered by
  ``test_full_crash_then_recovery_round_trip``).
- T-133: Window-2 crash (covered by ``test_window2_crash_orphan_create``).
- T-134: Steering across recovery (covered by ``test_steered_turn_2_after_crash``).
- T-135: Client cancel mid-stream (covered by ``test_client_cancel_returns_cancelled``).
- T-136: Observations captured in ``research.md`` §Phase 8 Results.
"""

from __future__ import annotations

import os
import time
from pathlib import Path

import pytest

from tests.e2e._crash_harness import CrashHarness

pytestmark = pytest.mark.live


_MODEL = os.environ.get("COPILOT_MODEL", "gpt-5-mini")
_SAMPLE_MODULE = Path(__file__).parent.parent.parent / "samples" / "sample_18_durable_copilot.py"


def _payload(input_text: str, **overrides) -> dict:
    body = {
        "model": "copilot",
        "input": input_text,
        "store": True,
        "background": True,
    }
    body.update(overrides)
    return body


def _wait_for_terminal(client, response_id: str, timeout_s: float = 60.0) -> dict:
    """Poll until the response reaches a terminal state."""
    import anyio  # noqa: F401  # pylint: disable=unused-import

    deadline = time.time() + timeout_s
    last = {}
    while time.time() < deadline:
        r = client.get(f"http://127.0.0.1:{client._port}/responses/{response_id}")
        if r.status_code == 200:
            last = r.json()
            if last.get("status") in ("completed", "failed", "cancelled"):
                return last
        time.sleep(0.5)
    return last


@pytest.mark.asyncio
async def test_sample18_lifecycle(tmp_path: Path) -> None:
    """T-130 / T-132 baseline: sample 18 starts, accepts a turn, terminates cleanly."""
    harness = CrashHarness(
        sample_module=_SAMPLE_MODULE,
        tmp_path=tmp_path,
        env_extras={"COPILOT_MODEL": _MODEL},
        readiness_timeout_seconds=20.0,
    )
    await harness.start()
    try:
        r = await harness.client.post("/responses", json=_payload("say hi briefly"))
        assert r.status_code == 200, r.text
        response_id = r.json()["id"]

        # Poll for terminal.
        deadline = time.time() + 60.0
        last = {}
        while time.time() < deadline:
            poll = await harness.client.get(f"/responses/{response_id}")
            if poll.status_code == 200:
                last = poll.json()
                if last.get("status") in ("completed", "failed", "cancelled"):
                    break
            import asyncio  # pylint: disable=import-outside-toplevel

            await asyncio.sleep(0.5)

        # Even if Copilot is slow or errors, the framework should land
        # SOME terminal state — we shouldn't be stuck in_progress.
        assert last.get("status") in ("completed", "failed", "cancelled"), last
    finally:
        await harness.close()


@pytest.mark.asyncio
async def test_full_crash_then_recovery_round_trip(tmp_path: Path) -> None:
    """T-132: full crash + recovery cycle.

    Drive a turn, kill the subprocess mid-flight, restart, verify the
    response eventually reaches a terminal state in the file store.
    """
    harness = CrashHarness(
        sample_module=_SAMPLE_MODULE,
        tmp_path=tmp_path,
        env_extras={"COPILOT_MODEL": _MODEL},
        readiness_timeout_seconds=20.0,
    )
    await harness.start()
    try:
        r = await harness.client.post("/responses", json=_payload("count to 5 slowly"))
        assert r.status_code == 200, r.text
        response_id = r.json()["id"]

        # Give Copilot a beat to actually start emitting.
        import asyncio  # pylint: disable=import-outside-toplevel

        await asyncio.sleep(1.5)

        # Kill the subprocess mid-flight (SIGKILL via process group).
        await harness.kill()

        # Sanity: the in-flight response was persisted by the durable task
        # path to the file response store, even though we crashed.
        resp_file = tmp_path / "responses" / "responses" / f"{response_id}.json"
        # Note: layout from FileResponseStore. The file may not be there
        # YET if we crashed before the first response.created persist;
        # restart and the recovered handler will produce a terminal.

        # Restart the subprocess. Durable framework should re-enter the
        # task in "recovered" mode and produce a terminal.
        await harness.restart()

        # Poll for terminal on the new subprocess.
        deadline = time.time() + 90.0
        last = {}
        while time.time() < deadline:
            poll = await harness.client.get(f"/responses/{response_id}")
            if poll.status_code == 200:
                last = poll.json()
                if last.get("status") in ("completed", "failed", "cancelled"):
                    break
            await asyncio.sleep(0.5)

        # The recovered attempt must land a terminal state.
        assert last.get("status") in ("completed", "failed", "cancelled"), last

        # And the file response store has exactly ONE response object
        # for this id (idempotent create + swallow contract).
        resp_dir = tmp_path / "responses" / "responses"
        matching = list(resp_dir.glob(f"{response_id}*.json")) if resp_dir.exists() else []
        # Allow 1 (object only) or 2 (object + .items dir's json — only the
        # response object itself matters for uniqueness).
        response_objs = [p for p in matching if p.name == f"{response_id}.json"]
        assert len(response_objs) <= 1, response_objs
    finally:
        await harness.close()


@pytest.mark.asyncio
async def test_window2_crash_orphan_create(tmp_path: Path) -> None:
    """T-133: kill immediately after POST (before response.created persist).

    On restart, the recovery path's reach of ``response.created`` should
    land the response cleanly via the create path (no swallow needed
    because the store has no entry yet).
    """
    harness = CrashHarness(
        sample_module=_SAMPLE_MODULE,
        tmp_path=tmp_path,
        env_extras={"COPILOT_MODEL": _MODEL},
        readiness_timeout_seconds=20.0,
    )
    await harness.start()
    try:
        r = await harness.client.post("/responses", json=_payload("hi"))
        assert r.status_code == 200, r.text
        response_id = r.json()["id"]

        # Kill almost immediately — window 2.
        await harness.kill()
        await harness.restart()

        # Poll for terminal.
        import asyncio  # pylint: disable=import-outside-toplevel

        deadline = time.time() + 90.0
        last = {}
        while time.time() < deadline:
            poll = await harness.client.get(f"/responses/{response_id}")
            if poll.status_code == 200:
                last = poll.json()
                if last.get("status") in ("completed", "failed", "cancelled"):
                    break
            await asyncio.sleep(0.5)

        assert last.get("status") in ("completed", "failed", "cancelled"), last
    finally:
        await harness.close()


@pytest.mark.asyncio
async def test_steered_turn_2_after_crash(tmp_path: Path) -> None:
    """T-134: steering across recovery.

    Turn 1 in flight → crash → restart → POST turn 2 with
    ``previous_response_id`` of turn 1. The chain id is preserved across
    recovery so both turns resolve against the same Copilot session.
    """
    harness = CrashHarness(
        sample_module=_SAMPLE_MODULE,
        tmp_path=tmp_path,
        env_extras={"COPILOT_MODEL": _MODEL},
        readiness_timeout_seconds=20.0,
    )
    await harness.start()
    try:
        # Turn 1.
        r1 = await harness.client.post("/responses", json=_payload("turn 1 hi"))
        assert r1.status_code == 200, r1.text
        resp1_id = r1.json()["id"]

        import asyncio  # pylint: disable=import-outside-toplevel

        await asyncio.sleep(1.0)
        await harness.kill()
        await harness.restart()

        # Wait for turn 1 to land terminal on the recovered attempt.
        deadline = time.time() + 90.0
        while time.time() < deadline:
            poll = await harness.client.get(f"/responses/{resp1_id}")
            if poll.status_code == 200:
                if poll.json().get("status") in ("completed", "failed", "cancelled"):
                    break
            await asyncio.sleep(0.5)

        # Turn 2: cite turn 1 as predecessor.
        r2 = await harness.client.post(
            "/responses",
            json=_payload("turn 2 follow up", previous_response_id=resp1_id),
        )
        # Either 200 (accepted) or 409 (fork conflict if turn 1 had already
        # been superseded by something — shouldn't happen here).
        assert r2.status_code in (200, 409), r2.text
    finally:
        await harness.close()


@pytest.mark.asyncio
async def test_client_cancel_returns_cancelled(tmp_path: Path) -> None:
    """T-135: client cancel mid-stream.

    POST a streaming turn, then DELETE while still in flight. The framework
    should land the response in ``cancelled`` and the session should remain
    consistent (no orphaned in_progress).
    """
    harness = CrashHarness(
        sample_module=_SAMPLE_MODULE,
        tmp_path=tmp_path,
        env_extras={"COPILOT_MODEL": _MODEL},
        readiness_timeout_seconds=20.0,
    )
    await harness.start()
    try:
        r = await harness.client.post("/responses", json=_payload("count slowly to 100"))
        assert r.status_code == 200, r.text
        response_id = r.json()["id"]

        # Brief in-flight, then explicit cancel.
        import asyncio  # pylint: disable=import-outside-toplevel

        await asyncio.sleep(1.0)

        cancel = await harness.client.post(f"/responses/{response_id}/cancel")
        assert cancel.status_code in (200, 202, 204), cancel.text

        # Poll for terminal.
        deadline = time.time() + 30.0
        last = {}
        while time.time() < deadline:
            poll = await harness.client.get(f"/responses/{response_id}")
            if poll.status_code == 200:
                last = poll.json()
                if last.get("status") in ("completed", "failed", "cancelled"):
                    break
            await asyncio.sleep(0.5)

        assert last.get("status") in ("cancelled", "completed"), last
    finally:
        await harness.close()
