# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Live e2e tests for the ``durable_copilot`` invocations sample.

These tests spawn the sample as a subprocess via :class:`CrashHarness`
and drive it via real HTTP. They require:

- The github-copilot-sdk installed (``pip install github-copilot-sdk``).
- The Copilot CLI installed and authenticated (``gh auth login`` +
  a github copilot subscription).

The tests are gated behind ``@pytest.mark.live`` AND skip at runtime
if the prerequisites aren't detected — that way ``-m "not live"``
selection is the canonical way to opt out, but a developer running
``-m live`` on a box without Copilot won't get scary errors.

Scope: minimum cells that exercise the streaming primitive end-to-end
through the sample. We do NOT replicate the 14-cell
``sample_18_invocation_patterns`` matrix here — that suite is already
exercised by ``azure-ai-agentserver-responses``; this file proves
the invocations sample is wired correctly.
"""

from __future__ import annotations

import asyncio
import importlib.util
import json
import os
import shutil
from pathlib import Path

import pytest

from ._crash_harness import CrashHarness

pytestmark = pytest.mark.live


def _missing_copilot_reason() -> str | None:
    """Return a non-None skip reason if the sample's deps aren't available."""
    if importlib.util.find_spec("copilot") is None:
        return "github-copilot-sdk not installed (pip install github-copilot-sdk)"
    if shutil.which("gh") is None and shutil.which("copilot") is None:
        return "neither 'gh' nor 'copilot' CLI is on PATH"
    return None


_SKIP_REASON = _missing_copilot_reason()


_SAMPLES_DIR = Path(__file__).resolve().parent.parent.parent / "samples"


def _harness(tmp_path: Path) -> CrashHarness:
    """Build a harness wired to the durable_copilot sample.

    Spawns ``python -m durable_copilot.app`` with the samples directory
    on PYTHONPATH and ``AGENTSERVER_DURABLE_ROOT`` rooted at
    ``tmp_path / "tasks"`` so the durable provider is isolated per
    test.
    """
    env_extras = {
        "PYTHONPATH": (f"{_SAMPLES_DIR}{os.pathsep}{os.environ.get('PYTHONPATH', '')}").rstrip(os.pathsep),
        # Do NOT override HOME — the Copilot CLI needs to find its auth
        # config under the real user's $HOME. We accept a per-test bleed
        # in ~/.durable-sessions/copilot-invocations; each test uses a
        # different ``agent_session_id`` so they don't collide.
    }
    return CrashHarness(
        sample_module="durable_copilot.app",
        tmp_path=tmp_path,
        env_extras=env_extras,
        readiness_timeout_seconds=20.0,
    )


@pytest.mark.skipif(_SKIP_REASON is not None, reason=_SKIP_REASON or "")
@pytest.mark.asyncio
async def test_sample_starts_and_responds_to_invocation(tmp_path: Path) -> None:
    """Smoke test — the sample boots and a basic POST returns 202."""
    async with _harness(tmp_path) as harness:
        resp = await harness.client.post(
            "/invocations?agent_session_id=live-copilot-1",
            json={"message": "Reply with exactly the word PONG."},
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code in (200, 202), f"unexpected status {resp.status_code}: {resp.text}"
        body = resp.json()
        # InvocationAgentServerHost stamps invocation_id on either the
        # response header or the body; both shapes are acceptable for
        # this smoke test.
        inv_id = body.get("invocation_id") or resp.headers.get("x-agent-invocation-id")
        assert inv_id, f"no invocation_id surfaced: body={body} headers={dict(resp.headers)}"


@pytest.mark.skipif(_SKIP_REASON is not None, reason=_SKIP_REASON or "")
@pytest.mark.asyncio
async def test_sse_stream_emits_text_deltas(tmp_path: Path) -> None:
    """POST with ``Accept: text/event-stream`` streams text_delta events.

    Validates  gaps 1 (streaming=True wired) + 2 (delta forwarded)
    end-to-end against a real Copilot session.
    """
    async with _harness(tmp_path) as harness:
        async with harness.client.stream(
            "POST",
            "/invocations?agent_session_id=live-copilot-sse",
            json={"message": "Count from 1 to 3, one number per line."},
            headers={
                "Content-Type": "application/json",
                "Accept": "text/event-stream",
            },
            timeout=120.0,
        ) as resp:
            assert resp.status_code == 200, await resp.aread()
            saw_text_delta = False
            saw_session_idle = False
            seen_types: list[str] = []
            async for line in resp.aiter_lines():
                if not line.startswith("data:"):
                    continue
                try:
                    payload = json.loads(line[len("data:") :].strip())
                except json.JSONDecodeError:
                    continue
                t = payload.get("type")
                if t:
                    seen_types.append(t)
                if t == "text_delta":
                    saw_text_delta = True
                if t == "session_idle":
                    saw_session_idle = True
                # Break the moment we have what we need. After idle
                # the stream stays open (task suspended) so iterating
                # would block until httpx timeout.
                if saw_text_delta and saw_session_idle:
                    break
                # Also break on idle alone — if no deltas arrived by
                # idle, none will (gap 2 regression).
                if saw_session_idle:
                    break
            assert saw_text_delta, f"no text_delta event in stream —  gap 2 regression? " f"types_seen={seen_types}"
            assert saw_session_idle, f"no session_idle event —  gap 3 regression? " f"types_seen={seen_types}"


@pytest.mark.skipif(_SKIP_REASON is not None, reason=_SKIP_REASON or "")
@pytest.mark.asyncio
async def test_poll_after_completion_returns_snapshot(tmp_path: Path) -> None:
    """GET /invocations/<id> returns the post-completion snapshot."""
    async with _harness(tmp_path) as harness:
        resp = await harness.client.post(
            "/invocations?agent_session_id=live-copilot-poll",
            json={"message": "Reply with the single word DONE."},
            headers={"Content-Type": "application/json"},
            timeout=120.0,
        )
        assert resp.status_code in (200, 202)
        inv_id = resp.json().get("invocation_id") or resp.headers.get("x-agent-invocation-id")
        assert inv_id

        # Poll until status is no longer "queued"/"running"/"streaming".
        deadline = asyncio.get_event_loop().time() + 60.0
        snapshot = None
        while asyncio.get_event_loop().time() < deadline:
            get = await harness.client.get(f"/invocations/{inv_id}")
            if get.status_code != 200:
                await asyncio.sleep(0.5)
                continue
            snapshot = get.json()
            if snapshot.get("status") in ("completed", "superseded", "cancelled"):
                break
            await asyncio.sleep(1.0)
        assert snapshot is not None, "never got a snapshot"
        assert snapshot.get("status") in (
            "completed",
            "superseded",
            "cancelled",
        ), f"task never reached terminal status: {snapshot}"
