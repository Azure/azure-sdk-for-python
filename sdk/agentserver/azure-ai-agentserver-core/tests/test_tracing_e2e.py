# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""End-to-end tracing tests that use an echo agent against live Application Insights.

These tests are selected by ``pytest -m tracing_e2e`` via the pipeline's
``TestMarkArgument`` and are skipped when ``APPLICATIONINSIGHTS_CONNECTION_STRING``
is not set (e.g. local development without live resources).

The connection string is picked up automatically from the environment variable
``APPLICATIONINSIGHTS_CONNECTION_STRING`` by ``AgentServerHost.__init__``.

Each test correlates its specific span in App Insights using the unique
``x-agent-invocation-id`` response header, which is stamped on the span as
``azure.ai.agentserver.invocations.invocation_id`` in customDimensions.

Since the span is created with ``SpanKind.SERVER``, it lands in the ``requests``
table in Application Insights.
"""
import time
from datetime import timedelta

import pytest
from starlette.requests import Request
from starlette.responses import Response, StreamingResponse
from starlette.testclient import TestClient

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider as SdkTracerProvider

from azure.ai.agentserver.invocations import InvocationAgentServerHost

pytestmark = pytest.mark.tracing_e2e

# Ingestion delay: App Insights may take a few minutes to make data queryable.
_APPINSIGHTS_POLL_TIMEOUT = 300
_APPINSIGHTS_POLL_INTERVAL = 15

# KQL attribute key for the invocation ID stamped on each span.
_INV_ID_ATTR = "azure.ai.agentserver.invocations.invocation_id"


# ---------------------------------------------------------------------------
# Ensure an OTel provider is set so tracing is active
# ---------------------------------------------------------------------------

_existing = trace.get_tracer_provider()
if not hasattr(_existing, "force_flush"):
    _MODULE_PROVIDER = SdkTracerProvider()
    trace.set_tracer_provider(_MODULE_PROVIDER)
else:
    _MODULE_PROVIDER = _existing



def _flush_provider():
    """Force-flush all span processors so live exporters send data to App Insights."""
    if hasattr(_MODULE_PROVIDER, "force_flush"):
        _MODULE_PROVIDER.force_flush()


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
# Echo agent factories — connection string comes from env var
# ---------------------------------------------------------------------------

def _make_echo_agent():
    """Create an InvocationAgentServerHost that echoes request body.

    Tracing is configured via ``APPLICATIONINSIGHTS_CONNECTION_STRING`` env var.
    """
    server = InvocationAgentServerHost()

    @server.invoke_handler
    async def handle(request: Request) -> Response:
        body = await request.body()
        return Response(content=body, media_type="application/octet-stream")

    return server


def _make_streaming_echo_agent():
    """Create a streaming echo agent. Connection string from env var."""
    server = InvocationAgentServerHost()

    @server.invoke_handler
    async def handle(request: Request) -> StreamingResponse:
        async def generate():
            for chunk in [b"chunk1\n", b"chunk2\n", b"chunk3\n"]:
                yield chunk

        return StreamingResponse(generate(), media_type="application/x-ndjson")

    return server


def _make_failing_echo_agent():
    """Create an echo agent whose handler raises. Connection string from env var."""
    server = InvocationAgentServerHost()

    @server.invoke_handler
    async def handle(request: Request) -> Response:
        raise ValueError("e2e error test")

    return server


# ---------------------------------------------------------------------------
# E2E: Verify spans are ingested into Application Insights
# ---------------------------------------------------------------------------

class TestAppInsightsIngestionE2E:
    """Query Application Insights ``requests`` table to confirm spans were
    actually ingested, correlating via x-agent-invocation-id."""

    def test_invoke_span_in_appinsights(
        self,
        appinsights_connection_string,
        appinsights_resource_id,
        logs_query_client,
    ):
        """Send an echo request and verify its span appears in App Insights ``requests`` table."""
        server = _make_echo_agent()
        client = TestClient(server)
        resp = client.post("/invocations", content=b"hello e2e")
        assert resp.status_code == 200
        inv_id = resp.headers["x-agent-invocation-id"]
        _flush_provider()

        # SpanKind.SERVER → requests table; invocation_id → customDimensions
        query = (
            "requests "
            f"| where tostring(customDimensions['{_INV_ID_ATTR}']) == '{inv_id}' "
            "| project name, timestamp, duration, success, customDimensions "
            "| take 1"
        )
        rows = _poll_appinsights(logs_query_client, appinsights_resource_id, query)
        assert len(rows) > 0, (
            f"invoke_agent span with invocation_id={inv_id} not found in "
            f"App Insights requests table after {_APPINSIGHTS_POLL_TIMEOUT}s"
        )

    def test_streaming_span_in_appinsights(
        self,
        appinsights_connection_string,
        appinsights_resource_id,
        logs_query_client,
    ):
        """Send a streaming request and verify its span appears in App Insights."""
        server = _make_streaming_echo_agent()
        client = TestClient(server)
        resp = client.post("/invocations", content=b"stream e2e")
        assert resp.status_code == 200
        inv_id = resp.headers["x-agent-invocation-id"]
        _flush_provider()

        query = (
            "requests "
            f"| where tostring(customDimensions['{_INV_ID_ATTR}']) == '{inv_id}' "
            "| take 1"
        )
        rows = _poll_appinsights(logs_query_client, appinsights_resource_id, query)
        assert len(rows) > 0, (
            f"Streaming span with invocation_id={inv_id} not found in App Insights"
        )

    def test_error_span_in_appinsights(
        self,
        appinsights_connection_string,
        appinsights_resource_id,
        logs_query_client,
    ):
        """Send a failing request and verify the error span appears with success=false."""
        server = _make_failing_echo_agent()
        client = TestClient(server)
        resp = client.post("/invocations", content=b"fail e2e")
        inv_id = resp.headers["x-agent-invocation-id"]
        _flush_provider()

        query = (
            "requests "
            f"| where tostring(customDimensions['{_INV_ID_ATTR}']) == '{inv_id}' "
            "| where success == false "
            "| take 1"
        )
        rows = _poll_appinsights(logs_query_client, appinsights_resource_id, query)
        assert len(rows) > 0, (
            f"Error span with invocation_id={inv_id} not found in App Insights"
        )

    def test_genai_attributes_in_appinsights(
        self,
        appinsights_connection_string,
        appinsights_resource_id,
        logs_query_client,
    ):
        """Verify GenAI semantic convention attributes are present on the ingested span."""
        server = _make_echo_agent()
        client = TestClient(server)
        resp = client.post("/invocations", content=b"genai attr e2e")
        inv_id = resp.headers["x-agent-invocation-id"]
        _flush_provider()

        query = (
            "requests "
            f"| where tostring(customDimensions['{_INV_ID_ATTR}']) == '{inv_id}' "
            "| where isnotempty(customDimensions['gen_ai.system']) "
            "| project name, "
            "  genai_system=tostring(customDimensions['gen_ai.system']), "
            "  genai_provider=tostring(customDimensions['gen_ai.provider.name']) "
            "| take 1"
        )
        rows = _poll_appinsights(logs_query_client, appinsights_resource_id, query)
        assert len(rows) > 0, (
            f"Span with invocation_id={inv_id} and gen_ai.system attribute "
            "not found in App Insights"
        )
