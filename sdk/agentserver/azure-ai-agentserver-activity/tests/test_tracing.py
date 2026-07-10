# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tracing and baggage tests for the activity protocol host."""

import pytest
from starlette.responses import JSONResponse

from azure.ai.agentserver.activity import ActivityAgentServerHost

# opentelemetry-api is a runtime dependency and opentelemetry-sdk is a test
# dependency, so both are always importable in the test environment.
from opentelemetry import trace
from opentelemetry.baggage import get_baggage
from opentelemetry.propagate import inject
from opentelemetry.sdk.trace import TracerProvider as SdkTracerProvider


@pytest.fixture(autouse=True)
def _ensure_real_tracer_provider():
    """Ensure tests run with a real tracer provider (not no-op)."""
    existing = trace.get_tracer_provider()
    if not hasattr(existing, "add_span_processor"):
        trace.set_tracer_provider(SdkTracerProvider())


@pytest.mark.asyncio
async def test_activity_sets_baggage_values_per_request(asgi_client):
    async def handle(_request):
        return JSONResponse(
            {
                "session": get_baggage("azure.ai.agentserver.session_id") or "",
                "conversation": get_baggage("azure.ai.agentserver.conversation_id") or "",
            }
        )

    app = ActivityAgentServerHost(request_handler=handle, configure_observability=None)
    async with asgi_client(app) as client:
        resp = await client.post(
            "/activity/messages?agent_session_id=session-from-query",
            json={"type": "message", "text": "hello", "conversation": {"id": "conv-42"}},
            headers={"Authorization": "Bearer test-token"},
        )

    assert resp.status_code == 200
    body = resp.json()
    assert body["session"] == "session-from-query"
    assert body["conversation"] == "conv-42"


@pytest.mark.asyncio
async def test_traceparent_is_propagated_to_handler_child_span(asgi_client):
    handler_tracer = trace.get_tracer("test.activity.handler")

    observed = {"trace_id": "", "parent_span_id": ""}

    async def handle(_request):
        with handler_tracer.start_as_current_span("activity_handler_child") as span:
            observed["trace_id"] = format(span.context.trace_id, "032x")
            observed["parent_span_id"] = format(span.parent.span_id, "016x") if span.parent else ""
        return JSONResponse({"ok": True})

    app = ActivityAgentServerHost(request_handler=handle, configure_observability=None)

    caller_tracer = trace.get_tracer("test.activity.caller")
    with caller_tracer.start_as_current_span("CallerOperation") as caller_span:
        caller_trace_id = format(caller_span.context.trace_id, "032x")
        caller_span_id = format(caller_span.context.span_id, "016x")
        headers = {
            "Authorization": "Bearer test-token",
            "x-agent-session-id": "session-123",
        }
        inject(headers)

        async with asgi_client(app) as client:
            resp = await client.post(
                "/activity/messages",
                json={"type": "message", "text": "hello"},
                headers=headers,
            )

    assert resp.status_code == 200
    assert observed["trace_id"] == caller_trace_id
    # The handler span should be in the incoming trace; parent may be the
    # framework request span (if middleware creates one) or the caller span.
    assert observed["parent_span_id"]
    assert observed["parent_span_id"] != "0000000000000000"
