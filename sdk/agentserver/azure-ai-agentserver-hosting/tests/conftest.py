# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Shared fixtures for azure-ai-agentserver-hosting tests."""
import pytest
import httpx

from azure.ai.agentserver.hosting import AgentServer


@pytest.fixture()
def agent() -> AgentServer:
    """Create a bare AgentServer with no protocol routes.

    Tracing is disabled to avoid requiring opentelemetry in the test env.
    """
    return AgentServer()


@pytest.fixture()
def client(agent: AgentServer) -> httpx.AsyncClient:
    """Create an httpx.AsyncClient bound to the AgentServer's ASGI app."""
    return httpx.AsyncClient(
        transport=httpx.ASGITransport(app=agent.app),
        base_url="http://testserver",
    )
