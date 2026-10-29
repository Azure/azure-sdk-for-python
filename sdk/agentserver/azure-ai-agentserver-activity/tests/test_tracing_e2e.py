# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""End-to-end tracing test for ActivityAgentServerHost against live Application Insights.

This test verifies that ``ActivityAgentServerHost`` propagates trace context on
``POST /activity/messages`` requests and that spans created inside an activity
handler are ingested into Application Insights with the correct trace/span
identifiers.

Selected by ``pytest -m tracing_e2e`` and skipped when
``APPLICATIONINSIGHTS_CONNECTION_STRING`` is not set.
"""
import os
import time
import uuid
from datetime import timedelta

import pytest
from starlette.responses import JSONResponse

from opentelemetry import trace

from azure.ai.agentserver.activity import ActivityAgentServerHost

pytestmark = pytest.mark.tracing_e2e

_APPINSIGHTS_POLL_TIMEOUT = 300
_APPINSIGHTS_POLL_INTERVAL = 15


def _flush_provider():
    """Force-flush the global TracerProvider so exporters send data."""
    provider = trace.get_tracer_provider()
    if hasattr(provider, "force_flush"):
        provider.force_flush()


def _poll_appinsights(logs_client, resource_id, query, *, timeout=_APPINSIGHTS_POLL_TIMEOUT):
    """Poll Application Insights until the KQL query returns >= 1 row or timeout."""
    from azure.core.exceptions import ServiceRequestError

    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            response = logs_client.query_resource(
                resource_id,
                query,
                timespan=timedelta(minutes=30),
            )
        except ServiceRequestError:
            # Transient network issues (DNS, connection reset) — retry after interval
            time.sleep(_APPINSIGHTS_POLL_INTERVAL)
            continue
        if response.tables and response.tables[0].rows:
            return response.tables[0].rows
        time.sleep(_APPINSIGHTS_POLL_INTERVAL)
    return []


@pytest.fixture(scope="module", autouse=True)
def _warmup_appinsights():
    """Initialize the application and wait for App Insights to be queryable.

    App Insights has a cold-start ingestion delay for the first telemetry
    session. This module-scoped fixture initializes the host (configuring the
    exporter), sends a dummy span, and polls until ingestion is confirmed so the
    real tests run against a warm pipeline.
    """
    conn_str = os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING")
    resource_id = os.environ.get("APPLICATIONINSIGHTS_RESOURCE_ID")
    if not conn_str or not resource_id:
        yield
        return

    # Initialize the host — triggers configure_observability() which sets up the
    # TracerProvider with the App Insights exporter.
    async def _noop(_request):
        return JSONResponse({"ok": True})

    ActivityAgentServerHost(request_handler=_noop)

    warmup_name = f"warmup-{uuid.uuid4().hex[:8]}"
    tracer = trace.get_tracer("test.warmup")
    with tracer.start_as_current_span(warmup_name):
        pass
    _flush_provider()

    from azure.monitor.query import LogsQueryClient

    if os.environ.get("AZURESUBSCRIPTION_TENANT_ID"):
        from azure.identity import AzurePowerShellCredential

        credential = AzurePowerShellCredential(tenant_id=os.environ["AZURESUBSCRIPTION_TENANT_ID"])
    else:
        from azure.identity import DefaultAzureCredential

        credential = DefaultAzureCredential()

    client = LogsQueryClient(credential)
    query = f"dependencies | where name == '{warmup_name}' | take 1"
    _poll_appinsights(client, resource_id, query, timeout=360)
    yield


class TestActivityTracingE2E:
    """Verify that user-created spans inside ActivityAgentServerHost handlers land in App Insights."""

    @pytest.mark.asyncio
    async def test_handler_span_in_appinsights(
        self,
        asgi_client,
        appinsights_connection_string,
        appinsights_resource_id,
        logs_query_client,
    ):
        """POST to /activity/messages with a handler that creates a span, verify it appears in App Insights."""
        handler_tracer = trace.get_tracer("test.activity.handler")
        captured_span_id: list[str] = []
        captured_trace_id: list[str] = []

        async def _handler(_request):
            with handler_tracer.start_as_current_span("HandlerWork") as span:
                span_ctx = span.get_span_context()
                captured_span_id.append(format(span_ctx.span_id, "016x"))
                captured_trace_id.append(format(span_ctx.trace_id, "032x"))
            return JSONResponse({"ok": True})

        app = ActivityAgentServerHost(request_handler=_handler)
        async with asgi_client(app) as client:
            resp = await client.post(
                "/activity/messages",
                json={"type": "message", "text": "hello e2e"},
                headers={"Authorization": "Bearer test-token"},
            )

        assert resp.status_code == 200
        _flush_provider()

        span_id = captured_span_id[-1]
        trace_id = captured_trace_id[-1]

        query = (
            "dependencies "
            f"| where id == '{span_id}' "
            f"| where operation_Id == '{trace_id}' "
            "| project id, name, operation_Id, timestamp "
            "| take 1"
        )
        rows = _poll_appinsights(logs_query_client, appinsights_resource_id, query)
        assert len(rows) > 0, (
            f"Handler span (id={span_id}, trace_id={trace_id}) not found in "
            f"App Insights dependencies table after {_APPINSIGHTS_POLL_TIMEOUT}s"
        )
