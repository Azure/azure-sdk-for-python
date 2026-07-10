# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Regression test: bg non-stream POST must return in_progress, not completed.

When ``background=True, stream=False``, the POST response must always have
``status: "in_progress"`` (or ``"queued"``).  A handler that yields events
synchronously (no ``await`` between yields) would previously cause the
background task to run to completion — including ``transition_to("completed")``,
provider persistence, and eager eviction — before ``run_background``'s
``await signal.wait()`` resumed, so the POST returned ``"completed"`` instead
of ``"in_progress"``.

The fix adds ``await asyncio.sleep(0)`` after ``response_created_signal.set()``
to yield to the event loop, giving ``run_background`` a chance to capture the
in-progress snapshot before the handler continues.

Regression test for: bg=True, stream=False POST returning "completed".
"""

from __future__ import annotations

from typing import Any

from starlette.testclient import TestClient

from azure.ai.agentserver.responses import ResponsesAgentServerHost
from azure.ai.agentserver.responses.streaming import ResponseEventStream


# ─── Handlers ─────────────────────────────────────────────


def _fast_sync_handler(request: Any, context: Any, cancellation_signal: Any) -> Any:
    """Handler that completes instantly with NO awaits between yields.

    This is the typical pattern when using ResponseEventStream — all
    emit_*() calls are synchronous, so the entire handler runs without
    yielding to the event loop.
    """

    async def _events():
        stream = ResponseEventStream(
            response_id=context.response_id,
            model=getattr(request, "model", None),
        )
        yield stream.emit_created()
        yield stream.emit_in_progress()

        message = stream.add_output_item_message()
        yield message.emit_added()
        text = message.add_text_content()
        yield text.emit_added()
        yield text.emit_delta("Hello!")
        yield text.emit_text_done("Hello!")
        yield text.emit_done()
        yield message.emit_done()

        yield stream.emit_completed()

    return _events()


def _minimal_sync_handler(request: Any, context: Any, cancellation_signal: Any) -> Any:
    """Minimal handler: just created → completed, zero awaits."""

    async def _events():
        stream = ResponseEventStream(
            response_id=context.response_id,
            model=getattr(request, "model", None),
        )
        yield stream.emit_created()
        yield stream.emit_completed()

    return _events()


# ─── Tests ────────────────────────────────────────────────


class TestBgNonStreamPostStatus:
    """Verify POST /responses returns in_progress for bg non-stream requests."""

    def test_post_returns_in_progress_with_fast_sync_handler(self) -> None:
        """POST with bg=True, stream=False must return in_progress even when
        the handler completes instantly with no awaits."""
        app = ResponsesAgentServerHost()
        app.response_handler(_fast_sync_handler)
        client = TestClient(app)

        r = client.post(
            "/responses",
            json={
                "model": "m",
                "input": "hi",
                "stream": False,
                "store": True,
                "background": True,
            },
        )
        assert r.status_code == 200
        body = r.json()
        assert body["status"] in ("in_progress", "queued"), (
            f"Expected in_progress or queued but got {body['status']!r}"
        )

    def test_post_returns_in_progress_with_minimal_handler(self) -> None:
        """Minimal created → completed handler must still return in_progress."""
        app = ResponsesAgentServerHost()
        app.response_handler(_minimal_sync_handler)
        client = TestClient(app)

        r = client.post(
            "/responses",
            json={
                "model": "m",
                "input": "hi",
                "stream": False,
                "store": True,
                "background": True,
            },
        )
        assert r.status_code == 200
        body = r.json()
        assert body["status"] in ("in_progress", "queued"), (
            f"Expected in_progress or queued but got {body['status']!r}"
        )

    def test_post_returns_in_progress_not_completed_after_handler_finishes(self) -> None:
        """Even after the handler fully completes, the POST snapshot must
        still show in_progress — not the terminal status that the bg task
        has already transitioned to."""
        app = ResponsesAgentServerHost()
        app.response_handler(_fast_sync_handler)
        client = TestClient(app)

        r = client.post(
            "/responses",
            json={
                "model": "m",
                "input": "hi",
                "stream": False,
                "store": True,
                "background": True,
            },
        )
        assert r.status_code == 200
        body = r.json()
        # Must NOT be "completed" — the POST response is the initial snapshot
        assert body["status"] != "completed", (
            "POST returned 'completed' — bg task ran to completion before "
            "run_background captured the in_progress snapshot"
        )
        assert body["status"] in ("in_progress", "queued")
