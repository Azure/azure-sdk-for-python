# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Live e2e tests for the ``resilient_research`` invocations sample.

These tests spawn the sample as a subprocess via :class:`CrashHarness`
and drive it via real HTTP. They require:

- A reachable Azure AI Foundry endpoint
  (``FOUNDRY_PROJECT_ENDPOINT``).
- A model deployment usable by the sample's ``responses.create`` call
  (``AZURE_AI_MODEL_DEPLOYMENT_NAME`` if not the default
  ``gpt-4.1-mini``).
- An identity that ``DefaultAzureCredential`` can resolve (``az
  login`` in dev).

Gated behind ``@pytest.mark.live`` AND skips at runtime if the env
prerequisites aren't present.

Scope: validates the streaming primitive end-to-end through the
sample:

- POST + Accept SSE returns a live stream of ``type=token`` deltas
  with monotonic ``sequence_number``.
- GET + Accept SSE + ``?last_event_id=N`` skips events whose
  sequence_number <= N.
- Crash mid-stream + restart preserves monotonic sequence numbers
  across the boundary (the recovered handler bumps off
  ``stream.last_cursor()``).

To keep the live runtime tractable we override the sample's phase
plan via env vars so a single test run completes in ~30-60 s rather
than ~45 min: ``NUM_PHASES=2``, ``CALLS_PER_PHASE=1``,
``TARGET_OUTPUT_TOKENS=80``, cooldowns zeroed.
"""

from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path

import pytest

from ._crash_harness import CrashHarness

pytestmark = [
    pytest.mark.live,
    # CrashHarness uses POSIX process-group signals (os.killpg / os.getpgid),
    # absent on Windows — skip there like the other POSIX-only tests.
    pytest.mark.skipif(
        not hasattr(os, "fork"),
        reason="CrashHarness uses POSIX process-group signals (os.killpg)",
    ),
]


def _missing_env_reason() -> str | None:
    if not os.environ.get("FOUNDRY_PROJECT_ENDPOINT"):
        return "FOUNDRY_PROJECT_ENDPOINT not set"
    return None


_SKIP_REASON = _missing_env_reason()


_SAMPLES_DIR = Path(__file__).resolve().parent.parent.parent / "samples"


def _harness(tmp_path: Path, *, num_phases: int = 2) -> CrashHarness:
    """Build a harness wired to the resilient_research sample.

    Overrides the sample's phase plan to a fast configuration so the
    live test completes in <60 s.
    """
    env_extras = {
        "PYTHONPATH": (f"{_SAMPLES_DIR}{os.pathsep}{os.environ.get('PYTHONPATH', '')}").rstrip(os.pathsep),
        "HOME": str(tmp_path / "home"),
        "AGENTSERVER_STREAMS_DIR": str(tmp_path / "streams"),
        "NUM_PHASES": str(num_phases),
        "CALLS_PER_PHASE": "1",
        "TARGET_OUTPUT_TOKENS": "80",
        "INTRA_PHASE_COOLDOWN_SEC": "0",
        "INTER_PHASE_COOLDOWN_SEC": "0",
        # Force AzureCliCredential when AZURE_AI_CREDENTIAL=cli is set
        # in the parent (e.g. dev box with conflicting MSI). The
        # default behavior — DefaultAzureCredential's full chain — is
        # what hosted deployments use.
        "AZURE_AI_CREDENTIAL": os.environ.get("AZURE_AI_CREDENTIAL", ""),
    }
    # Don't isolate $HOME if the parent enabled AZURE_AI_CREDENTIAL=cli —
    # AzureCliCredential needs the real user's az login cache.
    if env_extras["AZURE_AI_CREDENTIAL"] == "cli":
        del env_extras["HOME"]
    else:
        (tmp_path / "home").mkdir(parents=True, exist_ok=True)
    (tmp_path / "streams").mkdir(parents=True, exist_ok=True)
    return CrashHarness(
        sample_module="resilient_research.app",
        tmp_path=tmp_path,
        env_extras=env_extras,
        readiness_timeout_seconds=20.0,
    )


def _parse_sse_payloads(line_iter):
    """Yield decoded ``data:`` payloads from an SSE line iterator."""
    for line in line_iter:
        if line.startswith("data:"):
            try:
                yield json.loads(line[len("data:") :].strip())
            except json.JSONDecodeError:
                continue


@pytest.mark.skipif(_SKIP_REASON is not None, reason=_SKIP_REASON or "")
@pytest.mark.asyncio
async def test_post_sse_streams_tokens_with_monotonic_sequence(tmp_path: Path) -> None:
    """POST + Accept SSE streams token events with monotonic sequence_number."""
    async with _harness(tmp_path) as harness:
        seqs: list[int] = []
        saw_run_start = False
        saw_token = False
        saw_run_complete = False
        async with harness.client.stream(
            "POST",
            "/invocations?agent_session_id=live-research-sse",
            json={"topic": "the future of small language models"},
            headers={
                "Content-Type": "application/json",
                "Accept": "text/event-stream",
            },
            timeout=180.0,
        ) as resp:
            assert resp.status_code == 200, await resp.aread()
            buffered: list[str] = []
            async for line in resp.aiter_lines():
                buffered.append(line)
            for payload in _parse_sse_payloads(buffered):
                seq = payload.get("sequence_number")
                if seq is not None:
                    seqs.append(seq)
                t = payload.get("type")
                if t == "run_start":
                    saw_run_start = True
                elif t == "token":
                    saw_token = True
                elif t == "run_complete":
                    saw_run_complete = True

        assert saw_run_start, f"never saw run_start; seqs={seqs}"
        assert saw_token, f"never saw any token events; seqs={seqs}"
        assert saw_run_complete, f"never saw run_complete; seqs={seqs}"
        assert seqs == sorted(seqs), f"sequence_numbers out of order: {seqs}"
        assert seqs == list(range(seqs[0], seqs[-1] + 1)), f"gap in sequence_numbers: {seqs}"


@pytest.mark.skipif(_SKIP_REASON is not None, reason=_SKIP_REASON or "")
@pytest.mark.asyncio
async def test_get_sse_with_last_event_id_skips_seen_events(tmp_path: Path) -> None:
    """GET + Accept SSE + ?last_event_id=N skips events with seq <= N."""
    async with _harness(tmp_path) as harness:
        # Start a turn (non-SSE POST so we can drive the stream from GET).
        post = await harness.client.post(
            "/invocations?agent_session_id=live-research-getsse",
            json={"topic": "the history of the printing press"},
            headers={"Content-Type": "application/json"},
        )
        assert post.status_code in (200, 202)
        inv_id = post.json().get("invocation_id") or post.headers.get("x-agent-invocation-id")
        assert inv_id

        # First GET — read enough events to capture some sequence numbers.
        first_seqs: list[int] = []
        async with harness.client.stream(
            "GET",
            f"/invocations/{inv_id}",
            headers={"Accept": "text/event-stream"},
            timeout=120.0,
        ) as resp:
            assert resp.status_code == 200
            async for line in resp.aiter_lines():
                if line.startswith("data:"):
                    try:
                        payload = json.loads(line[len("data:") :].strip())
                    except json.JSONDecodeError:
                        continue
                    seq = payload.get("sequence_number")
                    if seq is not None:
                        first_seqs.append(seq)
                    if len(first_seqs) >= 3 or payload.get("type") == "run_complete":
                        break
        assert len(first_seqs) >= 2, f"first GET produced too few events: {first_seqs}"

        skip_cursor = first_seqs[0]
        # Second GET with ?last_event_id=<first seq> — every event we
        # see must have sequence_number > skip_cursor.
        second_seqs: list[int] = []
        async with harness.client.stream(
            "GET",
            f"/invocations/{inv_id}?last_event_id={skip_cursor}",
            headers={"Accept": "text/event-stream"},
            timeout=120.0,
        ) as resp:
            assert resp.status_code == 200
            async for line in resp.aiter_lines():
                if line.startswith("data:"):
                    try:
                        payload = json.loads(line[len("data:") :].strip())
                    except json.JSONDecodeError:
                        continue
                    seq = payload.get("sequence_number")
                    if seq is not None:
                        second_seqs.append(seq)
                    if payload.get("type") in ("run_complete", "done", "superseded"):
                        break
        # All observed events must be strictly after skip_cursor.
        for s in second_seqs:
            assert s > skip_cursor, f"event with seq={s} survived ?last_event_id={skip_cursor}"


@pytest.mark.skipif(_SKIP_REASON is not None, reason=_SKIP_REASON or "")
@pytest.mark.asyncio
async def test_crash_recovery_preserves_monotonic_sequence(tmp_path: Path) -> None:
    """SIGKILL mid-run + restart: post-recovery seq strictly > pre-crash seq.

    Validates that the file-backed replay backing rehydrates
    ``last_cursor()`` correctly so the recovered handler doesn't
    re-use sequence numbers.
    """
    harness = _harness(tmp_path, num_phases=3)
    await harness.start()
    inv_id = None
    try:
        post = await harness.client.post(
            "/invocations?agent_session_id=live-research-crash",
            json={"topic": "renewable energy storage technologies"},
            headers={"Content-Type": "application/json"},
        )
        assert post.status_code in (200, 202)
        inv_id = post.json().get("invocation_id") or post.headers.get("x-agent-invocation-id")
        assert inv_id

        # Watch the stream until we see at least one phase_end (so
        # ``completed_phases`` is >0 on recovery → handler emits the
        # type=recovered marker per agent.py line ~219); then SIGKILL.
        pre_crash_seqs: list[int] = []
        saw_phase_end = False
        async with harness.client.stream(
            "GET",
            f"/invocations/{inv_id}",
            headers={"Accept": "text/event-stream"},
            timeout=180.0,
        ) as resp:
            assert resp.status_code == 200
            async for line in resp.aiter_lines():
                if line.startswith("data:"):
                    try:
                        payload = json.loads(line[len("data:") :].strip())
                    except json.JSONDecodeError:
                        continue
                    seq = payload.get("sequence_number")
                    if seq is not None:
                        pre_crash_seqs.append(seq)
                    if payload.get("type") == "phase_end":
                        saw_phase_end = True
                        # Drain a couple more events to make the
                        # sequence-number gap interesting, then break.
                        if len(pre_crash_seqs) >= 6:
                            break
        assert saw_phase_end, f"never saw phase_end before crash budget exhausted: {pre_crash_seqs}"
        assert len(pre_crash_seqs) >= 3, f"didn't see enough events before crash: {pre_crash_seqs}"
        last_pre = pre_crash_seqs[-1]

        # SIGKILL + restart same tmp_path: state survives, handler
        # re-enters with entry_mode=recovered, last_cursor returns the
        # max seq that hit disk.
        await harness.kill()
        await harness.restart()

        # Reconnect and read until terminal; collect post-crash seqs.
        post_crash_seqs: list[int] = []
        saw_recovered = False
        async with harness.client.stream(
            "GET",
            f"/invocations/{inv_id}",
            headers={"Accept": "text/event-stream"},
            timeout=180.0,
        ) as resp:
            assert resp.status_code == 200
            async for line in resp.aiter_lines():
                if line.startswith("data:"):
                    try:
                        payload = json.loads(line[len("data:") :].strip())
                    except json.JSONDecodeError:
                        continue
                    seq = payload.get("sequence_number")
                    t = payload.get("type")
                    if t == "recovered":
                        saw_recovered = True
                    if seq is not None:
                        post_crash_seqs.append(seq)
                    if t in ("run_complete", "done", "superseded"):
                        break

        assert saw_recovered, "post-restart stream never carried a type=recovered marker"
        # The post-restart stream replays everything from disk, then
        # live-tails the new events. The crash boundary is wherever
        # the largest pre-crash seq sits. Every seq > last_pre must
        # come from the post-crash lifetime and must be strictly
        # greater than last_pre.
        post_only = [s for s in post_crash_seqs if s > last_pre]
        assert post_only, f"no post-crash events after last_pre={last_pre}; " f"post_crash_seqs={post_crash_seqs}"
        assert post_only == sorted(post_only)
        assert post_only[0] == last_pre + 1, (
            f"sequence gap at crash boundary: last_pre={last_pre} " f"first_post_crash={post_only[0]}"
        )
    finally:
        await harness.close()
