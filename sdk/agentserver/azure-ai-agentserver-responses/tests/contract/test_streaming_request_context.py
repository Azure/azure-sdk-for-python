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

import json
from pathlib import Path
from typing import Any

import httpx
from openai import AsyncOpenAI
import pytest
from starlette.testclient import TestClient

from azure.ai.agentserver.core import (
    FoundryAgentRequestContext,
    FoundryOriginalSubject,
    get_request_context,
    reset_request_context,
    set_request_context,
)
from azure.ai.agentserver.responses import ResponsesAgentServerHost, ResponsesServerOptions
from azure.ai.agentserver.responses.store._file import FileResponseStore
from azure.ai.agentserver.responses.store._memory import InMemoryResponseProvider
from azure.ai.agentserver.responses.streaming import ResponseEventStream


@pytest.mark.asyncio
async def test_model_sdk_extra_headers_preserve_the_dictionary_and_independent_json_header() -> None:
    observed: list[httpx.Request] = []

    def receive(request: httpx.Request) -> httpx.Response:
        observed.append(request)
        return httpx.Response(200, json={
            "id": "resp_test",
            "object": "response",
            "created_at": 0,
            "status": "completed",
            "model": "test",
            "output": [],
        })

    subject_value = 'oid="original-oid", tid="original-tid", idtype="user"'
    token = set_request_context(FoundryAgentRequestContext(
        original_subject=FoundryOriginalSubject.from_headers({"x-ms-original-subject": subject_value}),
        call_id="call-current",
        user_id="different-state-key",
    ))
    independent_json = json.dumps({"application_id": "example"}, separators=(",", ":"), ensure_ascii=True)
    try:
        async with AsyncOpenAI(
            api_key="test-model-key",
            base_url="https://model.test",
            http_client=httpx.AsyncClient(transport=httpx.MockTransport(receive)),
        ) as client:
            response = await client.responses.create(
                model="test",
                input="Hello",
                extra_headers={"x-example-context": independent_json, **get_request_context().model_attribution_headers()},
            )
        assert response.id == "resp_test"
    finally:
        reset_request_context(token)

    assert len(observed) == 1
    assert observed[0].headers["x-ms-original-subject"] == subject_value
    assert observed[0].headers["x-agent-foundry-call-id"] == "call-current"
    assert observed[0].headers["x-example-context"] == independent_json
    assert observed[0].headers["authorization"] == "Bearer test-model-key"
    assert "x-agent-user-id" not in observed[0].headers
    assert "x-ms-original-subject-oid" not in observed[0].headers
    assert get_request_context().original_subject is None


def _build_capturing_client(
    captured: dict[str, Any],
    *,
    resilient: bool = False,
    storage_dir: Path | None = None,
) -> TestClient:
    async def _capturing_handler(request: Any, context: Any, cancellation_signal: Any) -> Any:
        # An async-generator handler: its body does not execute until Starlette
        # iterates the streaming response, AFTER handle_create returned and reset
        # its own request context. The framework re-establishes the platform
        # context inside the streaming body iterator, so it is visible here.
        rc = get_request_context()
        captured["call_id"] = rc.call_id
        captured["user_id"] = rc.user_id
        captured["session_id"] = rc.session_id
        captured["model_headers"] = rc.model_attribution_headers()
        captured["platform_headers"] = rc.platform_headers()

        stream = ResponseEventStream(response_id=context.response_id, model=getattr(request, "model", None))
        yield stream.emit_created()
        yield stream.emit_completed()

    app = ResponsesAgentServerHost(
        options=ResponsesServerOptions(resilient_background=resilient),
        store=FileResponseStore(storage_dir) if storage_dir is not None else InMemoryResponseProvider(),
    )
    app.response_handler(_capturing_handler)
    return TestClient(app)


class TestStreamingRequestContext:
    """The platform context must be visible inside streaming handler bodies."""

    @pytest.mark.parametrize("stream", [False, True])
    @pytest.mark.parametrize("stored", [False, True])
    def test_original_subject_survives_handler_rebinding(
        self, stream: bool, stored: bool, tmp_path: Path
    ) -> None:
        captured: dict[str, Any] = {}
        client = _build_capturing_client(
            captured, resilient=stored, storage_dir=tmp_path / "store" if stored else None
        )
        subject = {
            "x-ms-original-subject": 'oid="original-oid", tid="original-tid", idtype="user"',
        }
        response = client.post(
            "/responses",
            json={"model": "m", "input": "hi", "stream": stream, "store": stored},
            headers={**subject, "x-agent-foundry-call-id": "call-current", "x-agent-user-id": "state-key"},
        )
        assert response.status_code == 200
        assert captured["model_headers"] == {**subject, "x-agent-foundry-call-id": "call-current"}
        assert captured["platform_headers"] == {"x-agent-foundry-call-id": "call-current"}
        assert captured["user_id"] == "state-key"
        assert get_request_context().original_subject is None

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

    def test_stored_sync_handler_sees_call_id_and_user_id(self, tmp_path: Path) -> None:
        captured: dict[str, Any] = {}
        client = _build_capturing_client(captured, resilient=True, storage_dir=tmp_path / "sync")

        r = client.post(
            "/responses",
            json={
                "model": "m",
                "input": "hi",
                "stream": False,
                "store": True,
                "agent_session_id": "session_789",
            },
            headers={
                "x-agent-user-id": "user_123",
                "x-agent-foundry-call-id": "call_456",
            },
        )

        assert r.status_code == 200
        assert captured.get("call_id") == "call_456"
        assert captured.get("user_id") == "user_123"
        assert captured.get("session_id") == "session_789"

    def test_stored_streaming_handler_sees_call_id_and_user_id(self, tmp_path: Path) -> None:
        captured: dict[str, Any] = {}
        client = _build_capturing_client(captured, resilient=True, storage_dir=tmp_path / "stream")

        with client.stream(
            "POST",
            "/responses",
            json={
                "model": "m",
                "input": "hi",
                "stream": True,
                "store": True,
                "agent_session_id": "session_789",
            },
            headers={
                "x-agent-user-id": "user_123",
                "x-agent-foundry-call-id": "call_456",
            },
        ) as r:
            assert r.status_code == 200
            for _ in r.iter_lines():
                pass

        assert captured.get("call_id") == "call_456"
        assert captured.get("user_id") == "user_123"
        assert captured.get("session_id") == "session_789"
