# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Shared fixtures for the durability-contract conformance suite (Spec 014).

Per Constitution Principle X, every cell test in this package MUST use
the real ``CrashHarness`` to spawn the test handler subprocess and drive
real signals. These fixtures encapsulate the SIGTERM-long-grace / SIGTERM-
short-grace / SIGKILL mechanisms used by Path A / Path B / Path C
respectively.

Fixtures:

- ``conformance_handler_module`` — the importable path to ``_test_handler``.
- ``make_harness`` — factory for constructing ``CrashHarness`` with the
  per-row configuration (durable_background, store_disabled, handler
  sleep, grace).
- ``LONG_TIME_SECS`` / ``SHORT_GRACE_S`` constants — exposed as module
  attributes so cell tests can reference them directly.

Timing constants are chosen to be wide enough that CI clock skew (~50ms
worst case) cannot induce flake — handler sleeps for ``LONG_TIME_SECS=5``
seconds while Path B sets grace to ``SHORT_GRACE_S=1`` second. The 5x
gap is the deterministic margin.
"""

from __future__ import annotations

import asyncio
import os
from collections.abc import AsyncIterator, Callable
from pathlib import Path
from typing import Any

import httpx
import pytest

from tests.e2e._crash_harness import CrashHarness

# ── Timing constants ─────────────────────────────────────────────────

# How long the test handler sleeps (interruptibly). Path A sets grace
# > this; Path B sets grace < this. 5s is wide enough to avoid CI flake.
LONG_TIME_SECS: float = 5.0

# Path B grace period — short enough to force grace exhaustion. The
# ResponseOptions.shutdown_grace_period_seconds is an integer ≥ 1, so
# we use 1 second. With LONG_TIME_SECS=5 the 4-second gap is the
# deterministic margin.
SHORT_GRACE_S: int = 1

# Path A grace period — long enough that the handler completes naturally
# before grace expires. With the default _SLEEP_MS=50 in the handler,
# 10 seconds is plenty.
LONG_GRACE_S: int = 10


_TEST_HANDLER_MODULE = "tests.e2e.durability_contract._test_handler"


@pytest.fixture
def conformance_handler_module() -> str:
    """Importable module path for the conformance test handler."""
    return _TEST_HANDLER_MODULE


@pytest.fixture
def make_harness(tmp_path: Path) -> Callable[..., CrashHarness]:
    """Factory for constructing a ``CrashHarness`` with per-row configuration.

    Returns a callable that takes:

    - ``durable_background`` (bool, default True) — server option.
    - ``store_disabled`` (bool, default False) — server option.
    - ``handler_sleep_ms`` (int, default 50) — handler sleep before
      emitting completion.
    - ``shutdown_grace_seconds`` (int, default LONG_GRACE_S) — server's
      in-process shutdown grace period.
    - ``readiness_timeout`` (float, default 15.0) — how long to wait for
      the subprocess to bind its port.

    Returns: an unstarted ``CrashHarness``. Caller must ``await
    harness.start()`` and ``await harness.close()`` (or use it as an
    async context manager).
    """

    def _factory(
        *,
        durable_background: bool = True,
        store_disabled: bool = False,
        handler_sleep_ms: int = 50,
        pre_sleep_deltas: int = 0,
        emit_metadata_watermark: bool = False,
        shutdown_grace_seconds: int = LONG_GRACE_S,
        readiness_timeout: float = 15.0,
    ) -> CrashHarness:
        env = {
            "CONFORMANCE_DURABLE_BACKGROUND": "true" if durable_background else "false",
            "CONFORMANCE_STORE_DISABLED": "true" if store_disabled else "false",
            "CONFORMANCE_HANDLER_SLEEP_MS": str(handler_sleep_ms),
            "CONFORMANCE_PRE_SLEEP_DELTAS": str(pre_sleep_deltas),
            "CONFORMANCE_EMIT_METADATA_WATERMARK": ("true" if emit_metadata_watermark else "false"),
            "AGENTSERVER_SHUTDOWN_GRACE_SECONDS": str(shutdown_grace_seconds),
            # Force Hypercorn to cancel in-flight connections after the
            # responses-layer grace so foreground responses (Row 3) get
            # their cancellation_signal set BEFORE Hypercorn waits its
            # default 30s for handler completion. Without this, a
            # SIGTERM-short-grace test would always see the foreground
            # handler complete naturally and ``GET`` returns
            # ``status="completed"`` instead of the expected ``failed``.
            "AGENTSERVER_GRACEFUL_SHUTDOWN_TIMEOUT_SECONDS": str(shutdown_grace_seconds),
            # Quiet the responses package's own logging during conformance
            # runs so test output stays focused on failures.
            "LOGLEVEL": os.environ.get("LOGLEVEL", "WARNING"),
        }
        return CrashHarness(
            sample_module=_TEST_HANDLER_MODULE,
            tmp_path=tmp_path,
            readiness_timeout_seconds=readiness_timeout,
            env_extras=env,
        )

    return _factory


# ── Helper: poll until terminal ───────────────────────────────────────


async def poll_until_terminal(
    client: httpx.AsyncClient,
    response_id: str,
    *,
    timeout_seconds: float = 30.0,
) -> dict[str, Any]:
    """Poll ``GET /responses/{id}`` until terminal or timeout.

    Returns the final response body. Raises ``TimeoutError`` if the
    response did not reach terminal within the timeout.
    """
    deadline = asyncio.get_event_loop().time() + timeout_seconds
    last: dict[str, Any] = {}
    while asyncio.get_event_loop().time() < deadline:
        try:
            r = await client.get(f"/responses/{response_id}")
        except httpx.RequestError:
            await asyncio.sleep(0.1)
            continue
        if r.status_code == 200:
            last = r.json()
            if last.get("status") in ("completed", "failed", "cancelled"):
                return last
        await asyncio.sleep(0.1)
    raise TimeoutError(
        f"Response {response_id} did not reach terminal within " f"{timeout_seconds}s. Last seen: {last}"
    )


async def post_and_get_response_id(
    client: httpx.AsyncClient,
    *,
    store: bool,
    background: bool,
    stream: bool,
    model: str = "conformance-test",
    input_text: str = "hello",
    extra: dict[str, Any] | None = None,
) -> str:
    """POST a response request with the given flags and return the response id.

    Handles all four combinations of (background, stream):

    - ``bg=True, stream=False``: response body is in-progress snapshot.
    - ``bg=True, stream=True``: response body is SSE; parse response.created.
    - ``bg=False, stream=False``: response body is the terminal.
    - ``bg=False, stream=True``: response body is SSE delivered live; we
      parse response.created from it.

    For tests that need the post-POST behavior beyond the id (e.g. to
    keep streaming or to capture the terminal snapshot), use the lower-
    level client methods directly.
    """
    body: dict[str, Any] = {
        "model": model,
        "input": input_text,
        "store": store,
        "background": background,
        "stream": stream,
    }
    if extra:
        body.update(extra)

    if not stream:
        r = await client.post("/responses", json=body)
        r.raise_for_status()
        return r.json()["id"]

    # Streaming POST — parse the first response.created event for the id.
    import json

    async with client.stream("POST", "/responses", json=body) as resp:
        if resp.status_code != 200:
            text = (await resp.aread()).decode("utf-8", errors="replace")
            raise httpx.HTTPStatusError(
                f"POST /responses returned {resp.status_code}: {text}",
                request=resp.request,
                response=resp,
            )
        async for line in resp.aiter_lines():
            if not line.startswith("data:"):
                continue
            try:
                payload = json.loads(line.removeprefix("data:").strip())
            except json.JSONDecodeError:
                continue
            event_type = payload.get("type", "")
            if "response.created" in event_type:
                rid = payload.get("response", {}).get("id")
                if rid:
                    return rid
    raise RuntimeError("POST /responses streamed without yielding a response.created event")


async def post_stream_to_terminal(
    client: httpx.AsyncClient,
    *,
    store: bool,
    model: str = "conformance-test",
    input_text: str = "hello",
    extra: dict[str, Any] | None = None,
    timeout_seconds: float = 120.0,
) -> tuple[str, list[dict[str, Any]]]:
    """POST a foreground+stream request and consume the SSE to terminal.

    Unlike :func:`post_and_get_response_id`, this helper keeps the
    streaming POST connection OPEN until a terminal event arrives or
    the timeout fires, mirroring how a real foreground+stream client
    would behave. Closing the connection early triggers the spec's
    Rule B17 (connection termination = cancellation), which is correct
    for cancellation tests but wrong for natural-completion or server-
    shutdown tests where the server is expected to drive the terminal.

    Returns ``(response_id, events)`` where ``events`` is the list of
    payload dicts parsed from each ``data:`` line (in order). The
    response id is extracted from the first ``response.created`` event.
    Raises ``RuntimeError`` if no ``response.created`` is observed.

    :param client: An httpx async client bound to the server base URL.
    :param store: Forwarded into the request body.
    :param model: Forwarded into the request body.
    :param input_text: Forwarded into the request body.
    :param extra: Optional additional body fields.
    :param timeout_seconds: Upper bound on the streaming read.
    """
    import json

    body: dict[str, Any] = {
        "model": model,
        "input": input_text,
        "store": store,
        "background": False,
        "stream": True,
    }
    if extra:
        body.update(extra)

    response_id: str | None = None
    events: list[dict[str, Any]] = []

    async with client.stream("POST", "/responses", json=body, timeout=timeout_seconds) as resp:
        if resp.status_code != 200:
            text = (await resp.aread()).decode("utf-8", errors="replace")
            raise httpx.HTTPStatusError(
                f"POST /responses returned {resp.status_code}: {text}",
                request=resp.request,
                response=resp,
            )
        async for line in resp.aiter_lines():
            if not line.startswith("data:"):
                continue
            try:
                payload = json.loads(line.removeprefix("data:").strip())
            except json.JSONDecodeError:
                continue
            events.append(payload)
            if response_id is None:
                rid = (payload.get("response") or {}).get("id")
                if rid:
                    response_id = rid
            event_type = payload.get("type", "")
            if event_type in (
                "response.completed",
                "response.failed",
                "response.cancelled",
            ):
                break
    if response_id is None:
        raise RuntimeError("POST /responses streamed without yielding a response.created event")
    return response_id, events


async def reconnect_stream_and_collect_events(
    client: httpx.AsyncClient,
    response_id: str,
    *,
    starting_after: int | None = None,
    timeout_seconds: float = 30.0,
) -> list[dict[str, Any]]:
    """Reconnect to a streamed response via GET ?stream=true and collect events.

    Returns the list of parsed event payloads in the order they arrive,
    stopping when the response reaches a terminal event (``response.completed``,
    ``response.failed``, ``response.cancelled``) or when the timeout expires.

    This is the client-side of the streaming sub-contract (per
    ``durability-contract.md`` § Streaming sub-contract): the client uses
    ``starting_after=<last_seen_event_id>`` to skip events it already
    has and expects the server to deliver a ``response.in_progress``
    reset event on recovery before continuation.
    """
    import json

    params: dict[str, Any] = {"stream": "true"}
    if starting_after is not None:
        params["starting_after"] = str(starting_after)
    events: list[dict[str, Any]] = []
    async with client.stream(
        "GET",
        f"/responses/{response_id}",
        params=params,
        timeout=timeout_seconds,
    ) as resp:
        if resp.status_code != 200:
            text = (await resp.aread()).decode("utf-8", errors="replace")
            raise httpx.HTTPStatusError(
                f"GET /responses/{response_id}?stream=true returned " f"{resp.status_code}: {text}",
                request=resp.request,
                response=resp,
            )
        async for line in resp.aiter_lines():
            if not line.startswith("data:"):
                continue
            try:
                payload = json.loads(line.removeprefix("data:").strip())
            except json.JSONDecodeError:
                continue
            events.append(payload)
            event_type = payload.get("type", "")
            if event_type in (
                "response.completed",
                "response.failed",
                "response.cancelled",
            ):
                break
    return events


async def post_foreground_and_discover_id(
    client: httpx.AsyncClient,
    tmp_path: Path,
    *,
    stream: bool,
    model: str = "conformance-test",
    input_text: str = "hello",
) -> tuple[str, "asyncio.Task[Any]"]:
    """For row 3 (``bg=False``): fire the POST async, discover the response id.

    Foreground responses don't return their id until terminal, so for
    Path B / Path C tests (which crash mid-handler) we can't await the
    POST. This helper:

    - For ``stream=True``: opens a streaming POST and parses
      ``response.created`` from the first SSE event in a background task.
    - For ``stream=False``: fires the POST as a background task and
      polls the on-disk response store at
      ``tmp_path/responses/responses/`` to discover the just-created
      response id.

    Returns ``(response_id, background_task)``. The caller is
    responsible for cancelling the background task in a ``finally``
    block so it doesn't leak.
    """
    import asyncio
    import json

    body = {
        "model": model,
        "input": input_text,
        "store": True,
        "background": False,
        "stream": stream,
    }

    if stream:
        # Streamed foreground — parse first response.created event.
        loop = asyncio.get_event_loop()
        ready: asyncio.Future[str] = loop.create_future()

        async def _runner() -> None:
            try:
                async with client.stream("POST", "/responses", json=body) as resp:
                    if resp.status_code != 200:
                        text = (await resp.aread()).decode("utf-8", errors="replace")
                        if not ready.done():
                            ready.set_exception(RuntimeError(f"POST failed {resp.status_code}: {text}"))
                        return
                    async for line in resp.aiter_lines():
                        if not line.startswith("data:"):
                            continue
                        try:
                            payload = json.loads(line.removeprefix("data:").strip())
                        except json.JSONDecodeError:
                            continue
                        if "response.created" in payload.get("type", ""):
                            rid = payload.get("response", {}).get("id")
                            if rid and not ready.done():
                                ready.set_result(rid)
                                # Keep iterating so the server keeps the
                                # request alive until something else kills
                                # the connection.
            except Exception as exc:  # pylint: disable=broad-exception-caught
                if not ready.done():
                    ready.set_exception(exc)

        task = asyncio.create_task(_runner())
        try:
            response_id = await asyncio.wait_for(ready, timeout=5.0)
        except (TimeoutError, asyncio.TimeoutError) as exc:
            task.cancel()
            raise RuntimeError("Foreground+stream POST did not emit response.created within 5s") from exc
        return response_id, task

    # Non-streaming foreground — pre-allocate the id and pass it in the body
    # so the test can poll on the known id immediately. The foreground
    # non-stream pipeline does NOT persist the response object until the
    # handler emits the terminal event (via _persist_and_resolve_terminal),
    # so polling the store directory for a new file would race against the
    # handler's sleep + the SIGTERM in Path B / C — the file never appears
    # before crash. Pre-allocating the id sidesteps that race entirely.
    from azure.ai.agentserver.responses._id_generator import (  # pylint: disable=import-outside-toplevel
        IdGenerator,
    )

    response_id = IdGenerator.new_response_id()
    body_with_id = {**body, "response_id": response_id}

    async def _runner_polled() -> None:
        try:
            await client.post("/responses", json=body_with_id, timeout=120.0)
        except Exception:  # pylint: disable=broad-exception-caught
            pass  # Crash / disconnect is expected in Path B/C tests.

    task = asyncio.create_task(_runner_polled())
    # Give the server a tick to start the handler before returning so the
    # caller's subsequent SIGTERM lands while the handler is mid-sleep.
    await asyncio.sleep(0.1)
    return response_id, task
