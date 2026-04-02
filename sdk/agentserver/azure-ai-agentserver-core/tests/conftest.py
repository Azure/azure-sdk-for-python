# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Shared fixtures for azure-ai-agentserver-core tests."""
import pytest
import httpx

from azure.ai.agentserver.core import AgentServerHost


@pytest.fixture()
def agent() -> AgentServerHost:
    """Create a bare AgentServerHost with no protocol routes.

    Tracing is disabled to avoid requiring opentelemetry in the test env.
    """
    return AgentServerHost()


@pytest.fixture()
def client(agent: AgentServerHost) -> httpx.AsyncClient:
    """Create an httpx.AsyncClient bound to the AgentServerHost's ASGI app."""
    return httpx.AsyncClient(
        transport=httpx.ASGITransport(app=agent),
        base_url="http://testserver",
    )
