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

import asyncio
import json
from importlib.metadata import requires
from pathlib import Path
from typing import Any
from urllib.parse import quote, unquote

import httpx
from openai import AsyncOpenAI, AsyncStream
import pytest
from packaging.requirements import Requirement
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
from azure.ai.agentserver.responses.hosting._observability import InMemoryCreateSpanHook


def test_original_subject_and_snapshot_core_dependency_floor() -> None:
    requirements = (Requirement(value) for value in requires("azure-ai-agentserver-responses") or [])
    core = next(value for value in requirements if value.name == "azure-ai-agentserver-core")
    assert "2.4.0b1" in core.specifier
    assert "2.3.0" not in core.specifier
    assert "2.3.0b2" not in core.specifier
    assert "2.3.0b1" not in core.specifier
    assert callable(FoundryAgentRequestContext.model_attribution_headers)


@pytest.mark.parametrize("value", ["malformed", 'oid="one", oid="two"', 'unknown="value"'])
def test_malformed_original_subject_ends_span_without_running_handler(value: str) -> None:
    hook = InMemoryCreateSpanHook()
    app = ResponsesAgentServerHost(options=ResponsesServerOptions(create_span_hook=hook), configure_observability=None)

    async def handler(_request: Any, _context: Any, _cancellation_signal: Any) -> Any:
        pytest.fail("Malformed attribution must not reach a handler.")

    app.response_handler(handler)
    response = TestClient(app).post(
        "/responses",
        json={"model": "test", "input": "hi", "store": False},
        headers={"x-ms-original-subject": value},
    )
    assert response.status_code == 400
    assert response.headers["x-platform-error-source"] == "platform"
    assert len(hook.spans) == 1
    assert hook.spans[0].error is not None
    assert get_request_context().original_subject is None


@pytest.mark.asyncio
async def test_model_sdk_extra_headers_preserve_the_dictionary_and_independent_json_header() -> None:
    observed: list[httpx.Request] = []

    def receive(request: httpx.Request) -> httpx.Response:
        observed.append(request)
        return httpx.Response(
            200,
            json={
                "id": "resp_test",
                "object": "response",
                "created_at": 0,
                "status": "completed",
                "model": "test",
                "output": [],
            },
        )

    subject_value = 'oid="original-oid", tid="original-tid", idtype="user"'
    token = set_request_context(
        FoundryAgentRequestContext(
            original_subject=FoundryOriginalSubject.from_headers({"x-ms-original-subject": subject_value}),
            call_id="call-current",
            user_id="different-state-key",
        )
    )
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
                extra_headers=get_request_context().model_attribution_headers(
                    {
                        "x-example-context": independent_json,
                        "X-MS-Foundry-Baggage": "application=example,Foundry.Original_Subject=stale",
                        "X-MS-Original-Subject": "stale",
                    }
                ),
            )
        assert response.id == "resp_test"
    finally:
        reset_request_context(token)

    assert len(observed) == 1
    assert not any(name.lower().startswith("x-ms-original-subject") for name in observed[0].headers)
    baggage = observed[0].headers["x-ms-foundry-baggage"].split(",")
    assert baggage[1] == "application=example"
    assert unquote(baggage[0].split("=", 1)[1]) == subject_value
    assert len(baggage) == 2
    assert observed[0].headers["x-agent-foundry-call-id"] == "call-current"
    assert observed[0].headers["x-example-context"] == independent_json
    assert observed[0].headers["authorization"] == "Bearer test-model-key"
    assert "x-agent-user-id" not in observed[0].headers
    assert get_request_context().original_subject is None


@pytest.mark.asyncio
@pytest.mark.parametrize("stream", [False, True])
async def test_reused_model_sdk_isolates_concurrent_invocations_streams_and_retries(stream: bool) -> None:
    observed: list[tuple[str, dict[str, str]]] = []
    attempts: dict[str, int] = {}
    arrivals: set[str] = set()
    concurrent = asyncio.Event()

    async def receive(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        invocation = body["input"]
        observed.append((invocation, dict(request.headers)))
        attempts[invocation] = attempts.get(invocation, 0) + 1
        if attempts[invocation] == 1:
            if invocation != "without-subject":
                arrivals.add(invocation)
                if len(arrivals) == 3:
                    concurrent.set()
                await asyncio.wait_for(concurrent.wait(), timeout=5)
            return httpx.Response(
                503,
                headers={"retry-after-ms": "1"},
                json={"error": {"message": "Retry this synthetic request.", "type": "server_error"}},
            )
        response = {
            "id": "resp_test",
            "object": "response",
            "created_at": 0,
            "status": "completed",
            "model": "test",
            "output": [],
        }
        if stream:
            event = {"type": "response.completed", "sequence_number": 0, "response": response}
            return httpx.Response(
                200,
                headers={"content-type": "text/event-stream"},
                content=f"event: response.completed\ndata: {json.dumps(event)}\n\n",
            )
        return httpx.Response(200, json=response)

    existing = {
        "X-MS-Original-Subject": "stale",
        "X-MS-Original-Subject-Oid": "stale",
        "X-MS-Original-Subject-Tid": "stale",
        "X-MS-Original-Subject-Idtype": "stale",
        "X-AGENT-FOUNDRY-CALL-ID": "stale-call",
        "X-MS-Foundry-Baggage": (
            "foundry.agent.name=example,Foundry.Original_Subject;stale=1,foundry.original_subject.oid=stale"
        ),
        "x-example-context": json.dumps({"application_id": "example"}),
    }
    original_headers = existing.copy()
    parent = get_request_context()
    http_client: Any = httpx.AsyncClient(
        transport=httpx.MockTransport(receive), headers={"x-transport-default": "unchanged"}
    )
    transport_defaults = dict(http_client.headers)
    async with AsyncOpenAI(
        api_key="test-model-key",
        base_url="https://model.test",
        max_retries=1,
        organization="test-organization",
        project="test-project",
        default_headers={"x-shared-client": "unchanged"},
        http_client=http_client,
    ) as client:
        client_defaults = dict(client.default_headers)
        authentication = dict(client.auth_headers)

        async def invoke(invocation: str, subject: FoundryOriginalSubject | None) -> None:
            context = FoundryAgentRequestContext(
                original_subject=subject, call_id=f"call-{invocation}", user_id="independent-state-key"
            )
            token = set_request_context(context)
            try:
                await asyncio.sleep(0)
                result = await client.responses.create(
                    model="test",
                    input=invocation,
                    stream=stream,
                    extra_headers=get_request_context().model_attribution_headers(existing),
                )
                if stream:
                    assert isinstance(result, AsyncStream)
                    events = [event async for event in result]
                    assert len(events) == 1
                    event = events[0]
                    assert event.type == "response.completed"
                    assert event.response.id == "resp_test"
                else:
                    assert not isinstance(result, AsyncStream)
                    assert result.id == "resp_test"
                assert get_request_context() is context
            finally:
                reset_request_context(token)

        subjects = {
            f"invocation-{index}": FoundryOriginalSubject(oid=f'subject-{index}%2C+;/\\"', tid="tenant", idtype=idtype)
            for index, idtype in enumerate(("user", "app", "future"))
        }
        await asyncio.gather(*(invoke(invocation, subject) for invocation, subject in subjects.items()))
        await invoke("without-subject", None)
        assert dict(client.default_headers) == client_defaults
        assert dict(client.auth_headers) == authentication
        assert dict(http_client.headers) == transport_defaults

    assert get_request_context() is parent
    assert existing == original_headers
    assert attempts == {**dict.fromkeys(subjects, 2), "without-subject": 2}
    for invocation, headers in observed:
        assert headers["authorization"] == authentication["Authorization"]
        assert headers["x-shared-client"] == "unchanged"
        assert headers["x-transport-default"] == "unchanged"
        assert headers["x-example-context"] == existing["x-example-context"]
        assert "x-agent-user-id" not in headers
        assert not any(name.lower().startswith("x-ms-original-subject") for name in headers)
        if invocation == "without-subject":
            assert "x-agent-foundry-call-id" not in headers
            assert headers["x-ms-foundry-baggage"] == "foundry.agent.name=example"
        else:
            assert headers["x-agent-foundry-call-id"] == f"call-{invocation}"
            members = headers["x-ms-foundry-baggage"].split(",")
            assert members[1] == "foundry.agent.name=example"
            assert len(members) == 2
            assert members[0].startswith("foundry.original_subject=")
            index = invocation.removeprefix("invocation-")
            expected = rf'oid="subject-{index}%2C+;/\\\"", tid="tenant", idtype="{subjects[invocation].idtype}"'
            assert unquote(members[0].split("=", 1)[1]) == expected


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
    def test_original_subject_survives_handler_rebinding(self, stream: bool, stored: bool, tmp_path: Path) -> None:
        captured: dict[str, Any] = {}
        client = _build_capturing_client(captured, resilient=stored, storage_dir=tmp_path / "store" if stored else None)
        subject = {
            "x-ms-original-subject": 'oid="original-oid", tid="original-tid", idtype="user"',
        }
        response = client.post(
            "/responses",
            json={"model": "m", "input": "hi", "stream": stream, "store": stored},
            headers={**subject, "x-agent-foundry-call-id": "call-current", "x-agent-user-id": "state-key"},
        )
        assert response.status_code == 200
        assert captured["model_headers"] == {
            "x-agent-foundry-call-id": "call-current",
            "x-ms-foundry-baggage": "foundry.original_subject=" + quote(subject["x-ms-original-subject"], safe=""),
        }
        assert (
            unquote(captured["model_headers"]["x-ms-foundry-baggage"].split("=", 1)[1])
            == subject["x-ms-original-subject"]
        )
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
