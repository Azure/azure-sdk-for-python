# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""End-to-end tracing test for InvocationAgentServerHost against live Application Insights.

This test verifies that InvocationAgentServerHost automatically creates traced
spans when handling /invocations requests, and that those spans are ingested
into Application Insights with the correct invocation ID attribute.

Selected by ``pytest -m tracing_e2e`` and skipped when
``APPLICATIONINSIGHTS_CONNECTION_STRING`` is not set.
"""
import time
from datetime import timedelta

import pytest
from httpx import ASGITransport, AsyncClient
from starlette.requests import Request
from starlette.responses import Response

from opentelemetry import trace

from azure.ai.agentserver.invocations import InvocationAgentServerHost

pytestmark = pytest.mark.tracing_e2e

_APPINSIGHTS_POLL_TIMEOUT = 300
_APPINSIGHTS_POLL_INTERVAL = 15

# Attribute key that InvocationAgentServerHost stamps on each span.
_INVOCATION_ID_ATTR = "azure.ai.agentserver.invocations.invocation_id"


def _flush_provider():
    """Force-flush the global TracerProvider so exporters send data."""
    provider = trace.get_tracer_provider()
    if hasattr(provider, "force_flush"):
        provider.force_flush()


def _poll_appinsights(logs_client, resource_id, query, *, timeout=_APPINSIGHTS_POLL_TIMEOUT):
    """Poll Application Insights until the KQL query returns >= 1 row or timeout."""
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
# E2E test
# ---------------------------------------------------------------------------

class TestInvocationTracingE2E:
    """Verify InvocationAgentServerHost auto-creates traced spans that land in App Insights."""

    @pytest.mark.asyncio
    async def test_invocation_span_in_appinsights(
        self,
        appinsights_connection_string,
        appinsights_resource_id,
        logs_query_client,
    ):
        """POST to /invocations and verify the span appears in App Insights requests table."""
        app = InvocationAgentServerHost()

        @app.invoke_handler
        async def handle(request: Request) -> Response:
            body = await request.body()
            return Response(content=body, media_type="application/octet-stream")

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            resp = await client.post("/invocations", content=b"hello e2e")

        assert resp.status_code == 200
        invocation_id = resp.headers.get("x-agent-invocation-id")
        assert invocation_id, "Expected x-agent-invocation-id in response headers"
        _flush_provider()

        query = (
            "requests "
            f"| where tostring(customDimensions['{_INVOCATION_ID_ATTR}']) == '{invocation_id}' "
            "| project name, timestamp, duration, success, customDimensions "
            "| take 1"
        )
        rows = _poll_appinsights(logs_query_client, appinsights_resource_id, query)
        assert len(rows) > 0, (
            f"invoke_agent span with invocation_id={invocation_id} not found in "
            f"App Insights requests table after {_APPINSIGHTS_POLL_TIMEOUT}s"
        )
