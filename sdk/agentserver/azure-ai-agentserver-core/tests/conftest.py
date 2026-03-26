# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Shared fixtures for azure-ai-agentserver-core tests."""
import pytest
import httpx

from azure.ai.agentserver.core import AgentHost


@pytest.fixture()
def agent() -> AgentHost:
    """Create a bare AgentHost with no protocol routes.

    Tracing is disabled to avoid requiring opentelemetry in the test env.
    """
    return AgentHost()


@pytest.fixture()
def client(agent: AgentHost) -> httpx.AsyncClient:
    """Create an httpx.AsyncClient bound to the AgentHost's ASGI app."""
    return httpx.AsyncClient(
        transport=httpx.ASGITransport(app=agent.app),
        base_url="http://testserver",
    )
