# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""End-to-end tracing tests using core's AgentServerHost against live Application Insights.

These tests are selected by ``pytest -m tracing_e2e`` via the pipeline's
``TestMarkArgument`` and are skipped when ``APPLICATIONINSIGHTS_CONNECTION_STRING``
is not set (e.g. local development without live resources).

The connection string is picked up automatically from the environment variable
``APPLICATIONINSIGHTS_CONNECTION_STRING`` by ``AgentServerHost.__init__``.

With context-only propagation (no invoke_agent span), these tests verify that
framework-created child spans are properly exported to App Insights.
"""
import time
import uuid
from datetime import timedelta

import pytest
from starlette.requests import Request
from starlette.responses import JSONResponse, Response, StreamingResponse
from starlette.routing import Route
from starlette.testclient import TestClient

from opentelemetry import trace

from azure.ai.agentserver.core import AgentServerHost

pytestmark = pytest.mark.tracing_e2e

# Ingestion delay: App Insights may take a few minutes to make data queryable.
_APPINSIGHTS_POLL_TIMEOUT = 300
_APPINSIGHTS_POLL_INTERVAL = 15


def _flush_provider():
    """Force-flush all span processors so live exporters send data to App Insights.

    ``AgentServerHost.__init__`` calls ``configure_observability()`` which sets up
    the global ``TracerProvider`` with the Azure Monitor exporter.  We just
    flush whatever the current global provider is.
    """
    provider = trace.get_tracer_provider()
    if hasattr(provider, "force_flush"):
        provider.force_flush()


def _poll_appinsights(logs_client, resource_id, query, *, timeout=_APPINSIGHTS_POLL_TIMEOUT):
    """Poll Application Insights until the KQL query returns ≥1 row or timeout.

    Returns the list of rows from the first table, or an empty list on timeout.
    """
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        response = logs_client.query_resource(
            resource_id,
            query,
            timespan=timedelta(minutes=30),
        )
        if response.tables and response.tables[0].rows:
            return response.tables[0].rows
        time.sleep(_APPINSIGHTS_POLL_INTERVAL)
    return []


# ---------------------------------------------------------------------------
# Minimal echo app factories using core's AgentServerHost
# ---------------------------------------------------------------------------

def _make_echo_app():
    """Create an AgentServerHost with a POST /echo route.

    Returns (app, request_ids) where request_ids is a list that collects the
    unique ID assigned to each request (for later App Insights correlation).

    TraceContextMiddleware automatically propagates W3C trace context from
    incoming request headers, so handlers don't need to call request_context().
    """
    request_ids: list[str] = []

    async def echo_handler(request: Request) -> Response:
        req_id = str(uuid.uuid4())
        request_ids.append(req_id)
        body = await request.body()
        resp = Response(content=body, media_type="application/octet-stream")
        resp.headers["x-request-id"] = req_id
        return resp

    routes = [Route("/echo", echo_handler, methods=["POST"])]
    app = AgentServerHost(routes=routes)
    return app, request_ids


def _make_streaming_echo_app():
    """Create a streaming echo app. Returns (app, request_ids)."""
    request_ids: list[str] = []

    async def stream_handler(request: Request) -> StreamingResponse:
        req_id = str(uuid.uuid4())
        request_ids.append(req_id)

        async def generate():
            for chunk in [b"chunk1\n", b"chunk2\n", b"chunk3\n"]:
                yield chunk

        return StreamingResponse(generate(), media_type="application/x-ndjson")

    routes = [Route("/echo", stream_handler, methods=["POST"])]
    app = AgentServerHost(routes=routes)
    return app, request_ids


def _make_echo_app_with_child_span():
    """Create an AgentServerHost whose handler creates a child span.

    Returns (app, request_ids, child_span_ids).  The child span simulates a
    framework creating its own span inside the propagated context.
    ``child_span_ids`` captures the hex span-id of each child so the test can
    query App Insights by that value.

    TraceContextMiddleware propagates context automatically — the child span
    becomes a child of the caller's trace without explicit request_context().
    """
    request_ids: list[str] = []
    child_span_ids: list[str] = []
    child_tracer = trace.get_tracer("test.framework")

    async def echo_handler(request: Request) -> Response:
        req_id = str(uuid.uuid4())
        request_ids.append(req_id)
        with child_tracer.start_as_current_span("framework_child") as child:
            child_span_ids.append(format(child.get_span_context().span_id, "016x"))
            body = await request.body()
            resp = Response(content=body, media_type="application/octet-stream")
            resp.headers["x-request-id"] = req_id
            return resp

    routes = [Route("/echo", echo_handler, methods=["POST"])]
    app = AgentServerHost(routes=routes)
    return app, request_ids, child_span_ids


def _make_failing_echo_app():
    """Create an app whose handler raises an error. Returns (app, request_ids)."""
    request_ids: list[str] = []

    async def fail_handler(request: Request) -> Response:
        req_id = str(uuid.uuid4())
        request_ids.append(req_id)
        try:
            raise ValueError("e2e error test")
        except ValueError:
            resp = JSONResponse({"error": "e2e error test"}, status_code=500)
            resp.headers["x-request-id"] = req_id
            return resp

    routes = [Route("/echo", fail_handler, methods=["POST"])]
    app = AgentServerHost(routes=routes)
    return app, request_ids


# ---------------------------------------------------------------------------
# E2E: Verify spans are ingested into Application Insights
# ---------------------------------------------------------------------------

class TestAppInsightsIngestionE2E:
    """Query Application Insights to confirm spans created inside handlers
    are actually ingested and enriched via TraceContextMiddleware propagation."""

    def test_echo_request_succeeds(
        self,
        appinsights_connection_string,
        appinsights_resource_id,
        logs_query_client,
    ):
        """Verify basic echo request succeeds with context-only propagation."""
        app, request_ids = _make_echo_app()
        client = TestClient(app)
        resp = client.post("/echo", content=b"hello e2e")
        assert resp.status_code == 200
        assert resp.content == b"hello e2e"

    def test_streaming_request_succeeds(
        self,
        appinsights_connection_string,
        appinsights_resource_id,
        logs_query_client,
    ):
        """Verify streaming echo request succeeds with context-only propagation."""
        app, _request_ids = _make_streaming_echo_app()
        client = TestClient(app)
        resp = client.post("/echo", content=b"stream e2e")
        assert resp.status_code == 200

    def test_error_request_returns_500(
        self,
        appinsights_connection_string,
        appinsights_resource_id,
        logs_query_client,
    ):
        """Verify failing request returns 500 with context-only propagation."""
        app, _request_ids = _make_failing_echo_app()
        client = TestClient(app)
        resp = client.post("/echo", content=b"fail e2e")
        assert resp.status_code == 500

    def test_span_parenting_in_appinsights(
        self,
        appinsights_connection_string,
        appinsights_resource_id,
        logs_query_client,
    ):
        """Verify a child span created inside the handler is exported to App Insights.

        With context-only propagation, the child (framework_child, SpanKind.INTERNAL)
        lands in ``dependencies``.  We verify it appears using its locally-captured span-id.
        """
        app, request_ids, child_span_ids = _make_echo_app_with_child_span()
        client = TestClient(app)
        resp = client.post("/echo", content=b"parenting e2e")
        assert resp.status_code == 200
        child_span_id = child_span_ids[-1]
        _flush_provider()

        # Find the child span in the dependencies table using its span-id.
        child_query = (
            "dependencies "
            f"| where id == '{child_span_id}' "
            "| where name == 'framework_child' "
            "| project id, name, operation_Id, operation_ParentId "
            "| take 1"
        )
        child_rows = _poll_appinsights(logs_query_client, appinsights_resource_id, child_query)
        assert len(child_rows) > 0, (
            f"Child framework_child span (id={child_span_id}) not found in "
            f"dependencies table after {_APPINSIGHTS_POLL_TIMEOUT}s"
        )

    def test_span_emitted_without_incoming_trace_context(
        self,
        appinsights_connection_string,
        appinsights_resource_id,
        logs_query_client,
    ):
        """Verify that spans created by downstream frameworks are exported even
        when the incoming request has NO traceparent/tracestate/baggage headers.

        This simulates a direct call (e.g. health check, load balancer probe)
        that does not carry W3C trace context.  The framework (MAF) should still
        be able to create spans that are exported to App Insights as new traces.

        Uses span_id and trace_id to confirm the exact span made it to App Insights.
        """
        span_name = f"NoContext-{uuid.uuid4().hex[:8]}"
        framework_tracer = trace.get_tracer("test.framework.no_context")
        captured_span_id: list[str] = []
        captured_trace_id: list[str] = []

        async def handler(request: Request) -> Response:
            with framework_tracer.start_as_current_span(span_name) as span:
                span_ctx = span.get_span_context()
                captured_span_id.append(format(span_ctx.span_id, "016x"))
                captured_trace_id.append(format(span_ctx.trace_id, "032x"))
                body = await request.body()
            return Response(content=body, media_type="application/octet-stream")

        routes = [Route("/echo", handler, methods=["POST"])]
        app = AgentServerHost(routes=routes)
        client = TestClient(app)

        # Send request with NO traceparent/tracestate/baggage headers
        resp = client.post("/echo", content=b"no context test")
        assert resp.status_code == 200
        _flush_provider()

        span_id = captured_span_id[-1]
        trace_id = captured_trace_id[-1]

        # Query by span_id (mapped to 'id' in App Insights dependencies table)
        # and operation_Id (trace_id) for precise matching
        query = (
            "dependencies "
            f"| where id == '{span_id}' "
            f"| where operation_Id == '{trace_id}' "
            "| project id, name, operation_Id, timestamp "
            "| take 1"
        )
        rows = _poll_appinsights(logs_query_client, appinsights_resource_id, query)
        assert len(rows) > 0, (
            f"Framework span (id={span_id}, trace_id={trace_id}) not found in "
            f"App Insights dependencies table after {_APPINSIGHTS_POLL_TIMEOUT}s. "
            "Spans should be emitted even without incoming trace context."
        )
