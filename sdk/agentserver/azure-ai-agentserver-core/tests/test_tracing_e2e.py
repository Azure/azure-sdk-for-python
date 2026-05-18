# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""End-to-end tracing tests using core's AgentServerHost against live Application Insights.

These tests are selected by ``pytest -m tracing_e2e`` via the pipeline's
``TestMarkArgument`` and are skipped when ``APPLICATIONINSIGHTS_CONNECTION_STRING``
is not set (e.g. local development without live resources).

The connection string is picked up automatically from the environment variable
``APPLICATIONINSIGHTS_CONNECTION_STRING`` by ``AgentServerHost.__init__``.

Each test correlates its specific span in App Insights using a unique request ID
stamped as ``gen_ai.response.id`` in customDimensions.

Since the span is created with ``SpanKind.SERVER``, it lands in the ``requests``
table in Application Insights.
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

# KQL attribute key for the response/request ID stamped on each span.
_RESPONSE_ID_ATTR = "gen_ai.response.id"


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
# Minimal echo app factories using core's AgentServerHost + request_span()
# ---------------------------------------------------------------------------

def _make_echo_app():
    """Create an AgentServerHost with a POST /echo route that creates a traced span.

    Returns (app, request_ids) where request_ids is a list that collects the
    unique ID assigned to each request (for later App Insights correlation).
    """
    request_ids: list[str] = []

    async def echo_handler(request: Request) -> Response:
        req_id = str(uuid.uuid4())
        request_ids.append(req_id)
        with app.request_span(dict(request.headers), req_id, "invoke_agent"):
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
        with app.request_span(dict(request.headers), req_id, "invoke_agent"):
            async def generate():
                for chunk in [b"chunk1\n", b"chunk2\n", b"chunk3\n"]:
                    yield chunk

            return StreamingResponse(generate(), media_type="application/x-ndjson")

    routes = [Route("/echo", stream_handler, methods=["POST"])]
    app = AgentServerHost(routes=routes)
    return app, request_ids


def _make_echo_app_with_child_span():
    """Create an AgentServerHost whose handler creates a child span inside request_span.

    Returns (app, request_ids, child_span_ids).  The child span simulates a
    framework creating its own span inside the invoke_agent span context.
    ``child_span_ids`` captures the hex span-id of each child so the test can
    query App Insights by that value.
    """
    request_ids: list[str] = []
    child_span_ids: list[str] = []
    child_tracer = trace.get_tracer("test.framework")

    async def echo_handler(request: Request) -> Response:
        req_id = str(uuid.uuid4())
        request_ids.append(req_id)
        with app.request_span(dict(request.headers), req_id, "invoke_agent"):
            with child_tracer.start_as_current_span("framework_child") as child:
                child_span_ids.append(format(child.context.span_id, "016x"))
                body = await request.body()
                resp = Response(content=body, media_type="application/octet-stream")
                resp.headers["x-request-id"] = req_id
                return resp

    routes = [Route("/echo", echo_handler, methods=["POST"])]
    app = AgentServerHost(routes=routes)
    return app, request_ids, child_span_ids


def _make_failing_echo_app():
    """Create an app whose handler raises inside request_span. Returns (app, request_ids)."""
    request_ids: list[str] = []

    async def fail_handler(request: Request) -> Response:
        req_id = str(uuid.uuid4())
        request_ids.append(req_id)
        try:
            with app.request_span(dict(request.headers), req_id, "invoke_agent") as span:
                raise ValueError("e2e error test")
        except ValueError:
            span.set_status(trace.StatusCode.ERROR, "e2e error test")
            span.record_exception(ValueError("e2e error test"))
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
    """Query Application Insights ``requests`` table to confirm spans were
    actually ingested, correlating via gen_ai.response.id."""

    def test_invoke_span_in_appinsights(
        self,
        appinsights_connection_string,
        appinsights_resource_id,
        logs_query_client,
    ):
        """Send an echo request and verify its span appears in App Insights ``requests`` table."""
        app, request_ids = _make_echo_app()
        client = TestClient(app)
        resp = client.post("/echo", content=b"hello e2e")
        assert resp.status_code == 200
        req_id = request_ids[-1]
        _flush_provider()

        query = (
            "requests "
            f"| where tostring(customDimensions['{_RESPONSE_ID_ATTR}']) == '{req_id}' "
            "| project name, timestamp, duration, success, customDimensions "
            "| take 1"
        )
        rows = _poll_appinsights(logs_query_client, appinsights_resource_id, query)
        assert len(rows) > 0, (
            f"invoke_agent span with response_id={req_id} not found in "
            f"App Insights requests table after {_APPINSIGHTS_POLL_TIMEOUT}s"
        )

    def test_streaming_span_in_appinsights(
        self,
        appinsights_connection_string,
        appinsights_resource_id,
        logs_query_client,
    ):
        """Send a streaming request and verify its span appears in App Insights."""
        app, request_ids = _make_streaming_echo_app()
        client = TestClient(app)
        resp = client.post("/echo", content=b"stream e2e")
        assert resp.status_code == 200
        req_id = request_ids[-1]
        _flush_provider()

        query = (
            "requests "
            f"| where tostring(customDimensions['{_RESPONSE_ID_ATTR}']) == '{req_id}' "
            "| take 1"
        )
        rows = _poll_appinsights(logs_query_client, appinsights_resource_id, query)
        assert len(rows) > 0, (
            f"Streaming span with response_id={req_id} not found in App Insights"
        )

    def test_error_span_in_appinsights(
        self,
        appinsights_connection_string,
        appinsights_resource_id,
        logs_query_client,
    ):
        """Send a failing request and verify the error span appears with success=false."""
        app, request_ids = _make_failing_echo_app()
        client = TestClient(app)
        resp = client.post("/echo", content=b"fail e2e")
        req_id = request_ids[-1]
        _flush_provider()

        query = (
            "requests "
            f"| where tostring(customDimensions['{_RESPONSE_ID_ATTR}']) == '{req_id}' "
            "| where success == false "
            "| take 1"
        )
        rows = _poll_appinsights(logs_query_client, appinsights_resource_id, query)
        assert len(rows) > 0, (
            f"Error span with response_id={req_id} not found in App Insights"
        )

    def test_genai_attributes_in_appinsights(
        self,
        appinsights_connection_string,
        appinsights_resource_id,
        logs_query_client,
    ):
        """Verify GenAI semantic convention attributes are present on the ingested span."""
        app, request_ids = _make_echo_app()
        client = TestClient(app)
        resp = client.post("/echo", content=b"genai attr e2e")
        req_id = request_ids[-1]
        _flush_provider()

        query = (
            "requests "
            f"| where tostring(customDimensions['{_RESPONSE_ID_ATTR}']) == '{req_id}' "
            "| where isnotempty(customDimensions['gen_ai.system']) "
            "| project name, "
            "  genai_system=tostring(customDimensions['gen_ai.system']), "
            "  genai_provider=tostring(customDimensions['gen_ai.provider.name']) "
            "| take 1"
        )
        rows = _poll_appinsights(logs_query_client, appinsights_resource_id, query)
        assert len(rows) > 0, (
            f"Span with response_id={req_id} and gen_ai.system attribute "
            "not found in App Insights"
        )

    def test_span_parenting_in_appinsights(
        self,
        appinsights_connection_string,
        appinsights_resource_id,
        logs_query_client,
    ):
        """Verify a child span created inside request_span is parented correctly in App Insights.

        The parent (invoke_agent, SpanKind.SERVER) lands in ``requests``.
        The child (framework_child, SpanKind.INTERNAL) lands in ``dependencies``.
        We capture the child's span-id locally, use it to find the child row in
        ``dependencies``, then follow its ``operation_ParentId`` back to the
        parent row in ``requests``.
        """
        app, request_ids, child_span_ids = _make_echo_app_with_child_span()
        client = TestClient(app)
        resp = client.post("/echo", content=b"parenting e2e")
        assert resp.status_code == 200
        req_id = request_ids[-1]
        child_span_id = child_span_ids[-1]
        _flush_provider()

        # Step 1: Find the child span in the dependencies table using its span-id.
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

        operation_id = child_rows[0][2]       # operation_Id column
        child_parent_id = child_rows[0][3]    # operation_ParentId column

        # Step 2: Find the parent span in the requests table using the child's operation_ParentId.
        parent_query = (
            "requests "
            f"| where id == '{child_parent_id}' "
            f"| where operation_Id == '{operation_id}' "
            "| project id, name, operation_Id "
            "| take 1"
        )
        parent_rows = _poll_appinsights(logs_query_client, appinsights_resource_id, parent_query)
        assert len(parent_rows) > 0, (
            f"Parent span (id={child_parent_id}) referenced by child's "
            f"operation_ParentId not found in requests table"
        )

        assert parent_rows[0][1] == "invoke_agent", (
            f"Expected parent span name 'invoke_agent', got '{parent_rows[0][1]}'"
        )
