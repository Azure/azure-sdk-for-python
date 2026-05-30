#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Sample 18 crash + recovery + replay demo.

Runs sample 18 in streaming mode with a real Copilot upstream, waits for
a handful of text deltas to arrive, SIGKILLs the subprocess mid-stream,
restarts, reconnects via GET ?stream=true&starting_after=N to resume from
the last event seen, then after the response completes does a final
GET ?stream=true&starting_after=0 to grab the full replay.

Writes three raw SSE streams to a temp directory:

  stream_1_initial.sse     — bytes received before the crash
  stream_2_resumed.sse     — bytes received on GET-reconnect starting_after=N
  stream_3_full_replay.sse — bytes received on GET-reconnect starting_after=0

Plus a summary.json with the response_id, sequence numbers, byte counts,
and timing.

Usage: python sample_18_crash_recovery_demo.py
       (run from repo root or anywhere — paths resolve from this file)
"""

from __future__ import annotations

import asyncio
import json
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

import httpx

# Add the responses package root to sys.path so we can reuse CrashHarness.
_RESPONSES_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_RESPONSES_DIR))

from tests.e2e._crash_harness import CrashHarness  # noqa: E402


_SAMPLE = _RESPONSES_DIR / "samples" / "sample_18_durable_copilot.py"
# A prompt that takes Copilot a noticeable amount of time (several
# minutes) — counting/enumeration with descriptions is a reliable choice.
_PROMPT = (
    "Count from 1 to 50. For each number, write one sentence describing "
    "something interesting about that number (its mathematical properties, "
    "historical significance, cultural meaning — be creative). Put a blank "
    "line between each entry. Take your time and be thoughtful about each "
    "number. This will be a long response and that is intentional."
)
# Stop the initial stream after seeing this many text.delta events,
# then immediately crash. With sample 18 now listening to
# AssistantMessageDeltaData (real incremental tokens), we should see many
# small deltas as Copilot generates the response — stop after 5 so the
# response is still mid-generation when SIGKILL hits.
_DELTAS_BEFORE_CRASH = 5
# Cap the initial wait. Copilot can take 30-90s to start streaming a
# long response — be generous.
_INITIAL_WAIT_BUDGET_S = 300.0
# Cap the recovery + final replay phases. Recovery includes the
# upstream Copilot reattach which can add 30-60s.
_RECOVERY_BUDGET_S = 300.0
_REPLAY_BUDGET_S = 60.0


def _ts() -> str:
    return time.strftime("%H:%M:%S", time.localtime())


async def _capture_initial(
    harness: CrashHarness,
    out: Path,
) -> tuple[str, int]:
    """POST a streaming response; capture bytes; stop after a few deltas.

    Returns (response_id, highest_sequence_number_seen).
    """
    body = {
        "model": "copilot",
        "input": _PROMPT,
        "store": True,
        "background": True,
        "stream": True,
    }
    response_id = ""
    delta_count = 0
    max_seq = -1
    long_timeout = httpx.Timeout(
        connect=10.0, read=_INITIAL_WAIT_BUDGET_S, write=10.0, pool=10.0
    )

    print(f"[{_ts()}] POST /responses (stream=true, bg=true, store=true)")
    with out.open("wb") as fh:
        async with harness.client.stream(
            "POST", "/responses", json=body, timeout=long_timeout
        ) as resp:
            assert resp.status_code == 200, f"POST failed: {resp.status_code}"
            buf = bytearray()
            async for chunk in resp.aiter_bytes():
                fh.write(chunk)
                fh.flush()
                buf.extend(chunk)
                done_parsing = False
                while b"\n\n" in buf and not done_parsing:
                    raw, _, rest = buf.partition(b"\n\n")
                    buf = bytearray(rest)
                    for line in raw.split(b"\n"):
                        if not line.startswith(b"data:"):
                            continue
                        try:
                            payload = json.loads(line[5:].strip())
                        except json.JSONDecodeError:
                            continue
                        seq = payload.get("sequence_number")
                        if isinstance(seq, int) and seq > max_seq:
                            max_seq = seq
                        t = payload.get("type", "")
                        if not response_id:
                            rid = payload.get("response", {}).get("id")
                            if rid:
                                response_id = rid
                                print(
                                    f"[{_ts()}] captured response_id={response_id}"
                                )
                        if "output_text.delta" in t:
                            delta_count += 1
                            print(
                                f"[{_ts()}] delta {delta_count} (seq={seq})"
                            )
                            if delta_count >= _DELTAS_BEFORE_CRASH:
                                done_parsing = True
                                break
                if done_parsing:
                    return response_id, max_seq
    return response_id, max_seq


async def _capture_resumed(
    harness: CrashHarness,
    response_id: str,
    starting_after: int,
    out: Path,
) -> int:
    """Reconnect via GET ?stream=true&starting_after=N; capture bytes to terminal.

    Returns highest sequence number seen.
    """
    print(
        f"[{_ts()}] GET /responses/{response_id}?stream=true&starting_after={starting_after}"
    )
    max_seq = starting_after
    terminal = False
    deadline = time.monotonic() + _RECOVERY_BUDGET_S
    long_timeout = httpx.Timeout(
        connect=10.0, read=_RECOVERY_BUDGET_S, write=10.0, pool=10.0
    )
    with out.open("wb") as fh:
        async with harness.client.stream(
            "GET",
            f"/responses/{response_id}",
            params={"stream": "true", "starting_after": str(starting_after)},
            timeout=long_timeout,
        ) as resp:
            assert resp.status_code == 200, (
                f"GET reconnect failed: {resp.status_code} "
                f"{(await resp.aread()).decode('utf-8', errors='replace')}"
            )
            buf = bytearray()
            async for chunk in resp.aiter_bytes():
                fh.write(chunk)
                fh.flush()
                buf.extend(chunk)
                while b"\n\n" in buf:
                    raw, _, rest = buf.partition(b"\n\n")
                    buf = bytearray(rest)
                    for line in raw.split(b"\n"):
                        if not line.startswith(b"data:"):
                            continue
                        try:
                            payload = json.loads(line[5:].strip())
                        except json.JSONDecodeError:
                            continue
                        seq = payload.get("sequence_number")
                        if isinstance(seq, int) and seq > max_seq:
                            max_seq = seq
                        t = payload.get("type", "")
                        if t in (
                            "response.completed",
                            "response.failed",
                            "response.cancelled",
                        ):
                            terminal = True
                            print(
                                f"[{_ts()}] resumed stream terminal: {t} (seq={seq})"
                            )
                if terminal:
                    return max_seq
                if time.monotonic() > deadline:
                    print(
                        f"[{_ts()}] WARN: recovery budget exhausted, "
                        f"max_seq={max_seq}"
                    )
                    return max_seq
    return max_seq


async def _capture_full_replay(
    harness: CrashHarness,
    response_id: str,
    out: Path,
) -> int:
    """Final GET ?stream=true&starting_after=0 — capture the full event log."""
    print(
        f"[{_ts()}] GET /responses/{response_id}?stream=true&starting_after=0  (full replay)"
    )
    max_seq = -1
    deadline = time.monotonic() + _REPLAY_BUDGET_S
    long_timeout = httpx.Timeout(
        connect=10.0, read=_REPLAY_BUDGET_S, write=10.0, pool=10.0
    )
    with out.open("wb") as fh:
        async with harness.client.stream(
            "GET",
            f"/responses/{response_id}",
            params={"stream": "true", "starting_after": "0"},
            timeout=long_timeout,
        ) as resp:
            assert resp.status_code == 200, (
                f"GET full replay failed: {resp.status_code} "
                f"{(await resp.aread()).decode('utf-8', errors='replace')}"
            )
            buf = bytearray()
            async for chunk in resp.aiter_bytes():
                fh.write(chunk)
                fh.flush()
                buf.extend(chunk)
                while b"\n\n" in buf:
                    raw, _, rest = buf.partition(b"\n\n")
                    buf = bytearray(rest)
                    for line in raw.split(b"\n"):
                        if not line.startswith(b"data:"):
                            continue
                        try:
                            payload = json.loads(line[5:].strip())
                        except json.JSONDecodeError:
                            continue
                        seq = payload.get("sequence_number")
                        if isinstance(seq, int) and seq > max_seq:
                            max_seq = seq
                if time.monotonic() > deadline:
                    print(
                        f"[{_ts()}] WARN: replay budget exhausted, max_seq={max_seq}"
                    )
                    return max_seq
    return max_seq


async def _run(out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    stream_1 = out_dir / "stream_1_initial.sse"
    stream_2 = out_dir / "stream_2_resumed.sse"
    stream_3 = out_dir / "stream_3_full_replay.sse"
    summary_path = out_dir / "summary.json"

    summary: dict[str, Any] = {
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "prompt": _PROMPT,
        "out_dir": str(out_dir),
    }

    harness = CrashHarness(
        sample_module=str(_SAMPLE),
        tmp_path=out_dir / "harness_state",
        env_extras={
            "AGENTSERVER_SHUTDOWN_GRACE_SECONDS": "60",
            "AGENTSERVER_GRACEFUL_SHUTDOWN_TIMEOUT_SECONDS": "60",
            "LOGLEVEL": "WARNING",
        },
        readiness_timeout_seconds=30.0,
    )

    try:
        print(f"[{_ts()}] starting sample 18 subprocess (lifetime 1)")
        await harness.start()

        response_id, last_seq = await _capture_initial(harness, stream_1)
        summary["response_id"] = response_id
        summary["initial_stream_max_seq"] = last_seq
        summary["initial_stream_bytes"] = stream_1.stat().st_size
        if not response_id:
            print("ERROR: never captured a response id; aborting")
            summary["error"] = "no_response_id"
            summary_path.write_text(json.dumps(summary, indent=2))
            return

        # Crash the subprocess mid-stream.
        print(f"[{_ts()}] SIGKILL subprocess (lifetime 1)")
        await harness.kill()

        # Bring it back up.
        print(f"[{_ts()}] restart subprocess (lifetime 2)")
        await harness.restart()
        # Give it a beat for the recovery scanner to reclaim the task.
        await asyncio.sleep(1.0)

        resumed_max_seq = await _capture_resumed(
            harness, response_id, last_seq, stream_2
        )
        summary["resumed_stream_max_seq"] = resumed_max_seq
        summary["resumed_stream_bytes"] = stream_2.stat().st_size

        # Give the response a beat to settle in the store.
        await asyncio.sleep(0.5)

        full_max_seq = await _capture_full_replay(harness, response_id, stream_3)
        summary["full_replay_max_seq"] = full_max_seq
        summary["full_replay_bytes"] = stream_3.stat().st_size

    finally:
        try:
            await harness.close()
        except Exception:  # pylint: disable=broad-exception-caught
            pass

    summary["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    summary_path.write_text(json.dumps(summary, indent=2))
    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(json.dumps(summary, indent=2))
    print()
    print(f"Outputs at: {out_dir}")
    print(f"  {stream_1}")
    print(f"  {stream_2}")
    print(f"  {stream_3}")
    print(f"  {summary_path}")


def main() -> None:
    base = Path(tempfile.gettempdir()) / f"sample18_crash_demo_{int(time.time())}"
    asyncio.run(_run(base))


if __name__ == "__main__":
    main()
