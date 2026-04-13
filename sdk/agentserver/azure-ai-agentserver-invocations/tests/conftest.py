# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Shared fixtures and factory functions for invocations tests."""
import json
import os
from typing import Any

import pytest
from httpx import ASGITransport, AsyncClient
from starlette.requests import Request
from starlette.responses import JSONResponse, Response, StreamingResponse

from azure.ai.agentserver.invocations import InvocationAgentServerHost


def pytest_configure(config):
    config.addinivalue_line("markers", "tracing_e2e: end-to-end tracing tests against live Application Insights")


# ---------------------------------------------------------------------------
# E2E tracing fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def appinsights_connection_string():
    """Return APPLICATIONINSIGHTS_CONNECTION_STRING or skip the test."""
    cs = os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING")
    if not cs:
        pytest.skip("APPLICATIONINSIGHTS_CONNECTION_STRING not set")
    return cs


@pytest.fixture()
def appinsights_resource_id():
    """Return the App Insights resource ID provisioned by test-resources.bicep."""
    rid = os.environ.get("APPLICATIONINSIGHTS_RESOURCE_ID")
    if not rid:
        pytest.skip("APPLICATIONINSIGHTS_RESOURCE_ID not set")
    return rid


@pytest.fixture()
def logs_query_client():
    """Create a ``LogsQueryClient`` for querying Application Insights.

    In CI the pipeline runs inside ``AzurePowerShell@5`` — use
    ``AzurePowerShellCredential`` directly to get a token from the correct
    tenant.  Locally fall back to ``DefaultAzureCredential``.
    """
    from azure.monitor.query import LogsQueryClient

    if os.environ.get("AZURESUBSCRIPTION_TENANT_ID"):
        from azure.identity import AzurePowerShellCredential

        credential = AzurePowerShellCredential(
            tenant_id=os.environ["AZURESUBSCRIPTION_TENANT_ID"],
        )
    else:
        from azure.identity import DefaultAzureCredential

        credential = DefaultAzureCredential()
    return LogsQueryClient(credential)


# ---------------------------------------------------------------------------
# Sample OpenAPI spec used by several tests
# ---------------------------------------------------------------------------

SAMPLE_OPENAPI_SPEC: dict[str, Any] = {
    "openapi": "3.0.0",
    "info": {"title": "Echo Agent", "version": "1.0.0"},
    "paths": {
        "/invocations": {
            "post": {
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["message"],
                                "properties": {
                                    "message": {"type": "string"},
                                },
                            }
                        }
                    },
                },
                "responses": {
                    "200": {
                        "description": "OK",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "reply": {"type": "string"},
                                    },
                                }
                            }
                        },
                    }
                },
            }
        }
    },
}


# ---------------------------------------------------------------------------
# Factory functions
# ---------------------------------------------------------------------------


def _make_echo_agent(**kwargs: Any) -> InvocationAgentServerHost:
    """Create an InvocationAgentServerHost whose invoke handler echoes the request body."""
    app = InvocationAgentServerHost(**kwargs)

    @app.invoke_handler
    async def handle(request: Request) -> Response:
        body = await request.body()
        return Response(content=body, media_type="application/octet-stream")

    return app


def _make_streaming_agent(**kwargs: Any) -> InvocationAgentServerHost:
    """Create an InvocationAgentServerHost whose invoke handler returns 3 JSON chunks."""
    app = InvocationAgentServerHost(**kwargs)

    @app.invoke_handler
    async def handle(request: Request) -> StreamingResponse:
        async def generate():
            for i in range(3):
                yield json.dumps({"chunk": i}) + "\n"

        return StreamingResponse(generate(), media_type="application/x-ndjson")

    return app


def _make_async_storage_agent(**kwargs: Any) -> InvocationAgentServerHost:
    """Create an InvocationAgentServerHost with get/cancel handlers and in-memory store."""
    app = InvocationAgentServerHost(**kwargs)
    store: dict[str, Any] = {}

    @app.invoke_handler
    async def handle(request: Request) -> Response:
        inv_id = request.state.invocation_id
        body = await request.body()
        store[inv_id] = body
        return Response(content=body, media_type="application/octet-stream")

    @app.get_invocation_handler
    async def get_handler(request: Request) -> Response:
        inv_id = request.path_params["invocation_id"]
        if inv_id not in store:
            return JSONResponse(
                {"error": {"code": "not_found", "message": "Not found"}},
                status_code=404,
            )
        return Response(content=store[inv_id], media_type="application/octet-stream")

    @app.cancel_invocation_handler
    async def cancel_handler(request: Request) -> Response:
        inv_id = request.path_params["invocation_id"]
        if inv_id not in store:
            return JSONResponse(
                {"error": {"code": "not_found", "message": "Not found"}},
                status_code=404,
            )
        del store[inv_id]
        return JSONResponse({"status": "cancelled"})

    return app


def _make_validated_agent() -> InvocationAgentServerHost:
    """Create an InvocationAgentServerHost with OpenAPI spec."""
    app = InvocationAgentServerHost(openapi_spec=SAMPLE_OPENAPI_SPEC)

    @app.invoke_handler
    async def handle(request: Request) -> Response:
        data = await request.json()
        return JSONResponse({"reply": f"echo: {data['message']}"})

    return app


def _make_failing_agent(**kwargs: Any) -> InvocationAgentServerHost:
    """Create an InvocationAgentServerHost whose handler raises ValueError."""
    app = InvocationAgentServerHost(**kwargs)

    @app.invoke_handler
    async def handle(request: Request) -> Response:
        raise ValueError("something went wrong")

    return app


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def echo_client():
    app = _make_echo_agent()
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://testserver")


@pytest.fixture()
def streaming_client():
    app = _make_streaming_agent()
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://testserver")


@pytest.fixture()
def async_storage_server():
    return _make_async_storage_agent()


@pytest.fixture()
def async_storage_client(async_storage_server):
    transport = ASGITransport(app=async_storage_server)
    return AsyncClient(transport=transport, base_url="http://testserver")


@pytest.fixture()
def validated_client():
    app = _make_validated_agent()
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://testserver")


@pytest.fixture()
def no_spec_client():
    app = _make_echo_agent()
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://testserver")


@pytest.fixture()
def failing_client():
    app = _make_failing_agent()
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://testserver")
