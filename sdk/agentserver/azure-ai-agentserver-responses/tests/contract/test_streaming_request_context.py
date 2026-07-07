# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Contract test: the platform request context is available inside streaming handlers.

For streaming requests the registered handler does not run during
``handle_create``; it runs lazily while Starlette iterates the
``StreamingResponse`` body.  The request context bound in ``handle_create`` is
reset in its ``finally`` block before that iteration begins, so the streaming
body must re-establish the platform context itself.  Otherwise
``get_request_context()`` returns the empty context inside any streaming
handler and the per-request ``x-agent-foundry-call-id`` / ``x-agent-user-id``
cannot be forwarded on raw outbound 1P calls (protocol 2.0.0).

Regression test for: request context not re-established for the streaming body.
"""

from __future__ import annotations

from typing import Any

from starlette.testclient import TestClient

from azure.ai.agentserver.core import get_request_context
from azure.ai.agentserver.responses import ResponsesAgentServerHost
from azure.ai.agentserver.responses.store._memory import InMemoryResponseProvider
from azure.ai.agentserver.responses.streaming import ResponseEventStream


def _build_capturing_client(captured: dict[str, Any]) -> TestClient:
    def _capturing_handler(request: Any, context: Any, cancellation_signal: Any) -> Any:
        async def _events():
            # This runs while Starlette iterates the streaming body, AFTER
            # handle_create returned and reset its own request context.
            rc = get_request_context()
            captured["call_id"] = rc.call_id
            captured["user_id"] = rc.user_id
            captured["session_id"] = rc.session_id

            stream = ResponseEventStream(
                response_id=context.response_id, model=getattr(request, "model", None)
            )
            yield stream.emit_created()
            yield stream.emit_completed()

        return _events()

    app = ResponsesAgentServerHost(store=InMemoryResponseProvider())
    app.response_handler(_capturing_handler)
    return TestClient(app)


class TestStreamingRequestContext:
    """The platform context must be visible inside streaming handler bodies."""

    def test_streaming_handler_sees_call_id_and_user_id(self) -> None:
        captured: dict[str, Any] = {}
        client = _build_capturing_client(captured)

        headers = {
            "x-agent-user-id": "user_123",
            "x-agent-foundry-call-id": "call_456",
        }
        with client.stream(
            "POST",
            "/responses",
            json={"model": "m", "input": "hi", "stream": True, "store": False},
            headers=headers,
        ) as r:
            assert r.status_code == 200
            # Force the SSE body to iterate fully so the handler runs.
            for _ in r.iter_lines():
                pass

        assert captured.get("call_id") == "call_456"
        assert captured.get("user_id") == "user_123"

    def test_streaming_handler_without_headers_sees_empty_context(self) -> None:
        captured: dict[str, Any] = {}
        client = _build_capturing_client(captured)

        with client.stream(
            "POST",
            "/responses",
            json={"model": "m", "input": "hi", "stream": True, "store": False},
        ) as r:
            assert r.status_code == 200
            for _ in r.iter_lines():
                pass

        # No identity headers → context fields are None (but the handler still ran).
        assert "call_id" in captured
        assert captured.get("call_id") is None
        assert captured.get("user_id") is None
