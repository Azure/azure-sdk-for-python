"""Sample 18 invocation pattern p06 — foreground + streamed.

Pattern: ``(store=true, background=false, stream=True)``.

Foreground streaming: the client receives SSE events over the live HTTP
connection. Per the Responses API behaviour contract (Rules B17 + B11):

- The client MUST keep the connection open until the terminal event
  arrives — closing the connection early is a cancellation that
  transitions the response to ``status: "cancelled"`` (B17).
- For ``store=true``, the terminal response is retrievable via GET
  regardless of how it terminated (B17).

Paths covered:

- **Path A** — natural completion through the live stream
  (server emits ``response.completed``; client reads it before closing).
- **Path B** — SIGTERM short grace mid-stream → server's in-process
  shutdown handler writes a failed terminal; GET-reconnect sees
  ``response.failed``.
- **Path C** — SIGKILL mid-stream → next-lifetime recovery scanner
  writes the failed terminal via the bookkeeping task; GET-reconnect
  sees ``response.failed``.
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable

import pytest

from tests.e2e._crash_harness import CrashHarness
from tests.e2e.sample_18_invocation_patterns.conftest import (
    SLOW_PROMPT,
    LONG_GRACE_S,
    SHORT_GRACE_S,
    TERMINAL_POLL_BUDGET_S,
    poll_until_terminal,
    post_and_get_response_id,
    post_stream_to_terminal,
    reconnect_stream_and_collect_events,
)

pytestmark = pytest.mark.live


def _terminal_in(events: list[dict]) -> dict | None:
    for ev in events:
        t = ev.get("type", "")
        if t in (
            "response.completed",
            "response.failed",
            "response.cancelled",
        ):
            return ev
    return None


@pytest.mark.asyncio
async def test_p06_path_a_natural_completion(
    make_harness: Callable[..., CrashHarness],
) -> None:
    """p06 Path A: foreground streamed POST completes via the live stream.

    Holds the stream open until the server emits the terminal event —
    a foreground stream's terminal is delivered on the live wire, not
    via a separate poll. Per B17, closing the stream early would be a
    cancellation; the test would then incorrectly observe a cancelled
    terminal instead of the natural completion it's exercising.
    """
    harness = make_harness(
        shutdown_grace_seconds=LONG_GRACE_S,
    )
    await harness.start()
    try:
        response_id, events = await post_stream_to_terminal(
            harness.client,
            store=True,
            model="copilot",
            input_text="say hi briefly",
            timeout_seconds=TERMINAL_POLL_BUDGET_S,
        )
        terminal_event = _terminal_in(events)
        assert terminal_event is not None, f"No terminal in live stream events: {[e.get('type') for e in events]}"
        assert terminal_event.get("type") == "response.completed", terminal_event
        # GET retrieval after natural completion should also see completed.
        terminal = await poll_until_terminal(
            harness.client,
            response_id,
            timeout_seconds=TERMINAL_POLL_BUDGET_S,
        )
        assert terminal["status"] == "completed", terminal
    finally:
        await harness.close()


@pytest.mark.asyncio
async def test_p06_path_b_graceful_marks_failed(
    make_harness: Callable[..., CrashHarness],
) -> None:
    """p06 Path B: graceful shutdown → failed terminal; GET sees it.

    Drives the stream in a background task (so the connection stays
    open while the handler is producing) and concurrently triggers
    SIGTERM with a short grace. The server's shutdown handler must
    finalise the response as ``failed`` (per B11 + the in-process
    shutdown contract) before the grace window expires.

    Per spec Endpoint 3 Rule B2: SSE replay via ``GET ?stream=true``
    is rejected with HTTP 400 for foreground responses
    (``background=false``); the polled JSON GET is the canonical way
    to retrieve the terminal state.
    """
    harness = make_harness(
        shutdown_grace_seconds=SHORT_GRACE_S,
    )
    await harness.start()
    try:
        response_id_ready = asyncio.Event()
        captured_response_id: dict[str, str | None] = {"value": None}

        async def _consume() -> None:
            try:
                # We need response_id quickly so we can issue the
                # SIGTERM. The helper captures it from the first
                # response.created event.
                import json as _json

                body = {
                    "model": "copilot",
                    "input": SLOW_PROMPT,
                    "store": True,
                    "background": False,
                    "stream": True,
                }
                async with harness.client.stream(
                    "POST", "/responses", json=body, timeout=TERMINAL_POLL_BUDGET_S
                ) as resp:
                    if resp.status_code != 200:
                        return
                    async for line in resp.aiter_lines():
                        if not line.startswith("data:"):
                            continue
                        try:
                            payload = _json.loads(line.removeprefix("data:").strip())
                        except _json.JSONDecodeError:
                            continue
                        if captured_response_id["value"] is None:
                            rid = (payload.get("response") or {}).get("id")
                            if rid:
                                captured_response_id["value"] = rid
                                response_id_ready.set()
                        if payload.get("type", "") in (
                            "response.completed",
                            "response.failed",
                            "response.cancelled",
                        ):
                            break
            except Exception:  # pylint: disable=broad-exception-caught
                pass

        consumer = asyncio.create_task(_consume())
        try:
            await asyncio.wait_for(response_id_ready.wait(), timeout=10.0)
        except asyncio.TimeoutError:
            consumer.cancel()
            raise AssertionError("Server did not emit response.created within 10s")

        response_id = captured_response_id["value"]
        assert response_id is not None

        await harness.terminate(wait_seconds=SHORT_GRACE_S + 2.0)
        # Consumer's stream will error or finish — drain it cleanly.
        try:
            await asyncio.wait_for(asyncio.shield(consumer), timeout=5.0)
        except (asyncio.TimeoutError, Exception):  # pylint: disable=broad-exception-caught
            consumer.cancel()
        await harness.restart()

        # Per B11 + the shutdown contract, response.status == "failed".
        terminal = await poll_until_terminal(
            harness.client,
            response_id,
            timeout_seconds=TERMINAL_POLL_BUDGET_S,
        )
        assert terminal["status"] == "failed", terminal
    finally:
        await harness.close()


@pytest.mark.asyncio
async def test_p06_path_c_sigkill_marks_failed(
    make_harness: Callable[..., CrashHarness],
) -> None:
    """p06 Path C: SIGKILL → next-lifetime marks failed.

    SIGKILL takes the process down with no graceful shutdown window,
    so the connection is dropped abruptly from the OS. The
    next-lifetime recovery scanner picks up the bookkeeping task and
    writes the ``response.failed`` terminal with
    ``error.code=server_error``.
    Polled JSON GET after the restart returns the failed terminal.

    Per spec Endpoint 3 Rule B2, foreground responses do not support
    SSE replay (``GET ?stream=true`` returns 400). Only the JSON GET
    is asserted here.
    """
    harness = make_harness(
        shutdown_grace_seconds=LONG_GRACE_S,
    )
    await harness.start()
    try:
        response_id_ready = asyncio.Event()
        captured_response_id: dict[str, str | None] = {"value": None}

        async def _consume() -> None:
            try:
                import json as _json

                body = {
                    "model": "copilot",
                    "input": SLOW_PROMPT,
                    "store": True,
                    "background": False,
                    "stream": True,
                }
                async with harness.client.stream(
                    "POST", "/responses", json=body, timeout=TERMINAL_POLL_BUDGET_S
                ) as resp:
                    if resp.status_code != 200:
                        return
                    async for line in resp.aiter_lines():
                        if not line.startswith("data:"):
                            continue
                        try:
                            payload = _json.loads(line.removeprefix("data:").strip())
                        except _json.JSONDecodeError:
                            continue
                        if captured_response_id["value"] is None:
                            rid = (payload.get("response") or {}).get("id")
                            if rid:
                                captured_response_id["value"] = rid
                                response_id_ready.set()
                        if payload.get("type", "") in (
                            "response.completed",
                            "response.failed",
                            "response.cancelled",
                        ):
                            break
            except Exception:  # pylint: disable=broad-exception-caught
                pass

        consumer = asyncio.create_task(_consume())
        try:
            await asyncio.wait_for(response_id_ready.wait(), timeout=10.0)
        except asyncio.TimeoutError:
            consumer.cancel()
            raise AssertionError("Server did not emit response.created within 10s")

        response_id = captured_response_id["value"]
        assert response_id is not None

        await harness.kill()
        # Consumer's connection died with the process — give it a moment
        # to wind down, then bail.
        try:
            await asyncio.wait_for(asyncio.shield(consumer), timeout=2.0)
        except (asyncio.TimeoutError, Exception):  # pylint: disable=broad-exception-caught
            consumer.cancel()
        await harness.restart()

        terminal = await poll_until_terminal(
            harness.client,
            response_id,
            timeout_seconds=TERMINAL_POLL_BUDGET_S,
        )
        assert terminal["status"] == "failed", terminal
        error = terminal.get("error") or {}
        assert error.get("code") == "server_error", terminal
        # SOT ResponseError is {code, message} only — the internal
        # shutdown_reason is not leaked to the customer payload.
        assert "additionalInfo" not in error, terminal
    finally:
        await harness.close()
