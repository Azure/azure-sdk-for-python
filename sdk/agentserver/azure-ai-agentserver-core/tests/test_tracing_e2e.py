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
