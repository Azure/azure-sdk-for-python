# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Shared fixtures for activity protocol tests."""

import pytest
from httpx import ASGITransport, AsyncClient
from starlette.responses import JSONResponse, Response

from azure.ai.agentserver.activity import ActivityAgentServerHost


def pytest_configure(config):
    config.addinivalue_line("markers", "tracing_e2e: end-to-end tracing tests against live Application Insights")


@pytest.fixture
async def activity_client():
    async def on_message(request) -> Response:
        activity = request.state.activity
        return JSONResponse({"type": "message", "text": f"echo:{activity.get('text', '')}"})

    app = ActivityAgentServerHost.from_request_handler(on_message, configure_observability=None)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client
