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
# E2E test
# ---------------------------------------------------------------------------

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
        relationship via KQL.

        Expected hierarchy in App Insights:
            CallerOperation (dependencies) → HandleInvocation (dependencies)
        Both share the same operation_Id (trace ID), and HandleInvocation's
        operation_ParentId equals the caller span's id.
        """
        from opentelemetry.propagate import inject

        app = InvocationAgentServerHost()
        handler_tracer = trace.get_tracer("test.handler")

        @app.invoke_handler
        async def handle(request: Request) -> Response:
            with handler_tracer.start_as_current_span("HandleInvocation"):
                body = await request.body()
                return Response(content=body, media_type="application/octet-stream")

        # 1. Create a real caller span
        caller_tracer = trace.get_tracer("test.caller")
        with caller_tracer.start_as_current_span("CallerOperation") as caller_span:
            caller_trace_id = format(caller_span.context.trace_id, "032x")
            caller_span_id = format(caller_span.context.span_id, "016x")

            # 2. Inject the caller's trace context into HTTP headers
            headers: dict[str, str] = {}
            inject(headers)

            # 3. Send the request with the propagated trace context
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://testserver") as client:
                resp = await client.post("/invocations", content=b"parenting e2e", headers=headers)

            assert resp.status_code == 200

        _flush_provider()

        # 4. Query App Insights for both spans in this trace
        query = (
            "dependencies "
            f"| where operation_Id == '{caller_trace_id}' "
            "| where name in ('CallerOperation', 'HandleInvocation') "
            "| project name, id, operation_ParentId, operation_Id "
        )
        rows = _poll_appinsights(logs_query_client, appinsights_resource_id, query)
        assert len(rows) >= 2, (
            f"Expected at least 2 spans (CallerOperation + HandleInvocation) "
            f"in trace {caller_trace_id}, but found {len(rows)} after "
            f"{_APPINSIGHTS_POLL_TIMEOUT}s"
        )

        # Build a lookup by span name
        columns = {name: idx for idx, name in enumerate(["name", "id", "operation_ParentId", "operation_Id"])}
        span_by_name = {}
        for row in rows:
            span_name = row[columns["name"]]
            span_by_name[span_name] = row

        assert "CallerOperation" in span_by_name, (
            f"CallerOperation span not found. Found: {[r[columns['name']] for r in rows]}"
        )
        assert "HandleInvocation" in span_by_name, (
            f"HandleInvocation span not found. Found: {[r[columns['name']] for r in rows]}"
        )

        caller_row = span_by_name["CallerOperation"]
        handler_row = span_by_name["HandleInvocation"]

        # HandleInvocation's parent must be the caller span
        assert handler_row[columns["operation_ParentId"]] == caller_row[columns["id"]], (
            f"HandleInvocation parent ({handler_row[columns['operation_ParentId']]}) "
            f"!= CallerOperation id ({caller_row[columns['id']]}). "
            f"Span parenting is broken in App Insights."
        )
