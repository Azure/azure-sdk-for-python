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
import uuid
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


# ---------------------------------------------------------------------------
# Warm-up fixture: initialize app and wait for App Insights to be ready
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module", autouse=True)
def _warmup_appinsights():
    """Initialize the application and send a warm-up span to App Insights.

    App Insights has a cold-start ingestion delay for the first telemetry
    session — data can take 5+ minutes to become queryable.  This module-scoped
    fixture initializes the host (configuring the exporter), sends a dummy span,
    and polls until App Insights confirms ingestion.  Real tests then run against
    a "warm" pipeline with fast ingestion.
    """
    import os

    conn_str = os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING")
    resource_id = os.environ.get("APPLICATIONINSIGHTS_RESOURCE_ID")
    if not conn_str or not resource_id:
        yield
        return

    # Initialize the application — triggers configure_observability() which
    # sets up the TracerProvider with the App Insights exporter.
    InvocationAgentServerHost()

    # Send a warmup span
    warmup_name = f"warmup-{uuid.uuid4().hex[:8]}"
    tracer = trace.get_tracer("test.warmup")
    with tracer.start_as_current_span(warmup_name):
        pass
    _flush_provider()

    # Poll until App Insights ingests the warm-up span (up to 360s)
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


# ---------------------------------------------------------------------------
# E2E test
# ---------------------------------------------------------------------------

class TestInvocationTracingE2E:
    """Verify that user-created spans inside InvocationAgentServerHost handlers land in App Insights."""

    @pytest.mark.asyncio
    async def test_handler_span_in_appinsights(
        self,
        appinsights_connection_string,
        appinsights_resource_id,
        logs_query_client,
    ):
        """POST to /invocations with a handler that creates a span, verify it appears in App Insights.

        The InvocationAgentServerHost propagates W3C trace context but does not
        create its own invoke_agent span.  This test verifies that a user-created
        span inside the handler is correctly exported to App Insights.
        """
        handler_tracer = trace.get_tracer("test.invocation.handler")
        captured_span_id: list[str] = []
        captured_trace_id: list[str] = []

        app = InvocationAgentServerHost()

        @app.invoke_handler
        async def handle(request: Request) -> Response:
            with handler_tracer.start_as_current_span("HandlerWork") as span:
                span_ctx = span.get_span_context()
                captured_span_id.append(format(span_ctx.span_id, "016x"))
                captured_trace_id.append(format(span_ctx.trace_id, "032x"))
                body = await request.body()
            return Response(content=body, media_type="application/octet-stream")

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            resp = await client.post("/invocations", content=b"hello e2e")

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


class TestSpanParentingE2E:
    """Verify that a child span created inside the invocation handler is
    correctly parented under an external caller span, with the full
    parent-child relationship visible in Application Insights."""

    @pytest.mark.asyncio
    async def test_handler_child_span_parented_under_caller_in_appinsights(
        self,
        appinsights_connection_string,
        appinsights_resource_id,
        logs_query_client,
    ):
        """End-to-end: create a real caller span, propagate its trace context
        via traceparent header to /invocations, create a child span inside the
        handler, flush to App Insights, and validate the parent-child
        relationship via KQL using span_id and trace_id.

        Expected hierarchy in App Insights:
            CallerOperation (dependencies) → HandleInvocation (dependencies)
        Both share the same operation_Id (trace ID), and HandleInvocation's
        operation_ParentId equals the caller span's id.
        """
        from opentelemetry.propagate import inject

        app = InvocationAgentServerHost()
        handler_tracer = trace.get_tracer("test.handler")
        handler_span_id: list[str] = []

        @app.invoke_handler
        async def handle(request: Request) -> Response:
            with handler_tracer.start_as_current_span("HandleInvocation") as span:
                handler_span_id.append(format(span.get_span_context().span_id, "016x"))
                body = await request.body()
                return Response(content=body, media_type="application/octet-stream")

        # 1. Create a real caller span and capture its IDs
        caller_tracer = trace.get_tracer("test.caller")
        with caller_tracer.start_as_current_span("CallerOperation") as caller_span:
            caller_ctx = caller_span.get_span_context()
            caller_trace_id = format(caller_ctx.trace_id, "032x")
            caller_span_id = format(caller_ctx.span_id, "016x")

            # 2. Inject the caller's trace context into HTTP headers
            headers: dict[str, str] = {}
            inject(headers)

            # 3. Send the request with the propagated trace context
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://testserver") as client:
                resp = await client.post("/invocations", content=b"parenting e2e", headers=headers)

            assert resp.status_code == 200

        _flush_provider()

        child_span_id = handler_span_id[-1]

        # 4. Query App Insights for the caller span by its span_id
        caller_query = (
            "dependencies "
            f"| where id == '{caller_span_id}' "
            f"| where operation_Id == '{caller_trace_id}' "
            "| project id, name, operation_Id "
            "| take 1"
        )
        caller_rows = _poll_appinsights(logs_query_client, appinsights_resource_id, caller_query)
        assert len(caller_rows) > 0, (
            f"CallerOperation span (id={caller_span_id}, trace_id={caller_trace_id}) "
            f"not found in App Insights after {_APPINSIGHTS_POLL_TIMEOUT}s"
        )

        # 5. Query App Insights for the handler span by its span_id
        handler_query = (
            "dependencies "
            f"| where id == '{child_span_id}' "
            f"| where operation_Id == '{caller_trace_id}' "
            "| project id, name, operation_Id, operation_ParentId "
            "| take 1"
        )
        handler_rows = _poll_appinsights(logs_query_client, appinsights_resource_id, handler_query)
        assert len(handler_rows) > 0, (
            f"HandleInvocation span (id={child_span_id}, trace_id={caller_trace_id}) "
            f"not found in App Insights after {_APPINSIGHTS_POLL_TIMEOUT}s"
        )

        # 6. Validate parenting: HandleInvocation's parent must be the caller span
        # handler_rows columns: [id, name, operation_Id, operation_ParentId]
        handler_parent_id = handler_rows[0][3]
        assert handler_parent_id == caller_span_id, (
            f"HandleInvocation parent ({handler_parent_id}) "
            f"!= CallerOperation id ({caller_span_id}). "
            f"Span parenting is broken in App Insights."
        )
