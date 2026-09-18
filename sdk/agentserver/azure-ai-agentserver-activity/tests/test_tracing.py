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


# --------------------------------------------------------------------------- #
#
# The Foundry trace-list query only discovers an operation when a single span
# carries BOTH the agent identity (name / version / id) AND the project id.
# The activity host emits a root ``invoke_agent`` span that supplies both and
# parents the M365 SDK's ``agents.*`` child spans into the same trace.
# --------------------------------------------------------------------------- #

from opentelemetry.sdk.trace.export import (  # noqa: E402
    SimpleSpanProcessor,
    SpanExporter,
    SpanExportResult,
)


class _CollectorExporter(SpanExporter):
    """In-memory span collector for tests."""

    def __init__(self):
        self.spans = []

    def export(self, spans):
        self.spans.extend(spans)
        return SpanExportResult.SUCCESS

    def shutdown(self):
        return True

    def force_flush(self, timeout_millis=30000):
        return True


@pytest.fixture
def span_collector():
    """Attach an in-memory collector to the active global tracer provider.

    OpenTelemetry only honors ``set_tracer_provider`` once per process, so the
    collector is attached to whatever real provider is active (created by the
    autouse ``_ensure_real_tracer_provider`` fixture) rather than replacing it.
    """
    provider = trace.get_tracer_provider()
    if not hasattr(provider, "add_span_processor"):
        provider = SdkTracerProvider()
        trace.set_tracer_provider(provider)
    collector = _CollectorExporter()
    provider.add_span_processor(SimpleSpanProcessor(collector))
    return collector


@pytest.fixture
def _foundry_env(monkeypatch):
    """Populate the Foundry platform environment the host reads at construction."""
    monkeypatch.setenv("FOUNDRY_AGENT_NAME", "echo")
    monkeypatch.setenv("FOUNDRY_AGENT_VERSION", "3")
    monkeypatch.setenv(
        "FOUNDRY_PROJECT_ARM_ID",
        "/subscriptions/sub/resourceGroups/rg/providers/"
        "Microsoft.CognitiveServices/accounts/acct/projects/proj",
    )


def _find_invoke_span(collector):
    for span in collector.spans:
        if span.name == "invoke_agent":
            return span
    return None


@pytest.mark.asyncio
async def test_invoke_agent_span_carries_identity_project_and_response_id(
    asgi_client, span_collector, _foundry_env
):
    """The invoke_agent span carries agent identity, project id, and a per-turn
    response id together — the full set the trace list needs on one span. These
    are set inline (not left to the shared stack) so they are guaranteed present."""

    async def handle(_request):
        return JSONResponse({"ok": True})

    app = ActivityAgentServerHost(request_handler=handle, configure_observability=None)
    async with asgi_client(app) as client:
        resp = await client.post(
            "/activity/messages?agent_session_id=session-abc",
            json={"type": "message", "text": "hi", "id": "act-9", "conversation": {"id": "conv-9"}},
            headers={"Authorization": "Bearer test-token"},
        )

    assert resp.status_code == 200

    span = _find_invoke_span(span_collector)
    assert span is not None, "expected an invoke_agent span"
    attrs = dict(span.attributes)
    assert attrs["gen_ai.operation.name"] == "invoke_agent"
    assert attrs["gen_ai.system"] == "activity"
    # The trace list keys each turn on the response id; for an activity turn that
    # is the activity id.
    assert attrs["azure.ai.agentserver.response_id"] == "act-9"
    # Identity + project must be on the SAME span for the turn to appear.
    assert attrs["gen_ai.agent.name"] == "echo"
    assert attrs["gen_ai.agent.version"] == "3"
    assert attrs["gen_ai.agent.id"] == "echo:3"
    assert attrs["microsoft.foundry.project.id"].endswith("/projects/proj")
    assert attrs["gen_ai.conversation.id"] == "conv-9"
    assert attrs["microsoft.session.id"] == "session-abc"


@pytest.mark.asyncio
async def test_invoke_agent_span_omits_blank_attributes(asgi_client, span_collector, monkeypatch):
    """Without the platform environment variables, identity/project are omitted
    (not emitted as blanks); the operation name and response id are still set."""
    # Ensure a Foundry-configured dev/CI environment does not populate the
    # identity/project config and defeat the assertions below.
    for _var in (
        "FOUNDRY_AGENT_NAME",
        "FOUNDRY_AGENT_VERSION",
        "FOUNDRY_AGENT_ID",
        "FOUNDRY_PROJECT_ENDPOINT",
        "FOUNDRY_PROJECT_ARM_ID",
    ):
        monkeypatch.delenv(_var, raising=False)

    async def handle(_request):
        return JSONResponse({"ok": True})

    app = ActivityAgentServerHost(request_handler=handle, configure_observability=None)
    async with asgi_client(app) as client:
        resp = await client.post(
            "/activity/messages",
            json={"type": "message", "text": "hi", "id": "act-123"},
            headers={"Authorization": "Bearer test-token"},
        )

    assert resp.status_code == 200
    span = _find_invoke_span(span_collector)
    assert span is not None
    attrs = dict(span.attributes)
    assert attrs["gen_ai.operation.name"] == "invoke_agent"
    assert attrs["gen_ai.system"] == "activity"
    assert attrs["azure.ai.agentserver.response_id"] == "act-123"
    assert "gen_ai.agent.name" not in attrs
    assert "microsoft.foundry.project.id" not in attrs


@pytest.mark.asyncio
async def test_handler_child_spans_share_invoke_agent_trace(asgi_client, span_collector):
    """Child spans created inside the handler join the invoke_agent trace."""
    handler_tracer = trace.get_tracer("test.activity.child")
    observed = {"trace_id": ""}

    async def handle(_request):
        with handler_tracer.start_as_current_span("agents.turn") as span:
            observed["trace_id"] = format(span.context.trace_id, "032x")
        return JSONResponse({"ok": True})

    app = ActivityAgentServerHost(request_handler=handle, configure_observability=None)
    async with asgi_client(app) as client:
        resp = await client.post(
            "/activity/messages?agent_session_id=session-xyz",
            json={"type": "message", "text": "hi"},
            headers={"Authorization": "Bearer test-token"},
        )

    assert resp.status_code == 200
    span = _find_invoke_span(span_collector)
    assert span is not None
    root_trace_id = format(span.context.trace_id, "032x")
    assert observed["trace_id"] == root_trace_id


