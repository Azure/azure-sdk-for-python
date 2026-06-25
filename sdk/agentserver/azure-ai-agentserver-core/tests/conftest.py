# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Shared fixtures for azure-ai-agentserver-core tests."""
import os

import pytest
import httpx

from azure.ai.agentserver.core import AgentServerHost


def pytest_configure(config):
    config.addinivalue_line("markers", "tracing_e2e: end-to-end tracing tests requiring live Azure resources")


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


@pytest.fixture()
def appinsights_connection_string():
    """Return the Application Insights connection string from the environment.

    Tests marked ``tracing_e2e`` are skipped when the variable is absent
    (e.g. local development without live resources).
    """
    conn_str = os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING")
    if not conn_str:
        pytest.skip("APPLICATIONINSIGHTS_CONNECTION_STRING not set")
    return conn_str


@pytest.fixture()
def appinsights_resource_id():
    """Return the Application Insights ARM resource ID from the environment.

    Needed by ``LogsQueryClient.query_resource()`` to verify spans in App Insights.
    """
    resource_id = os.environ.get("APPLICATIONINSIGHTS_RESOURCE_ID")
    if not resource_id:
        pytest.skip("APPLICATIONINSIGHTS_RESOURCE_ID not set")
    return resource_id


@pytest.fixture()
def logs_query_client():
    """Create a ``LogsQueryClient`` for querying Application Insights.

    In CI the pipeline runs inside ``AzurePowerShell@5`` which authenticates
    via the service connection.  We detect this by checking for
    ``AZURESUBSCRIPTION_TENANT_ID`` and use ``AzurePowerShellCredential``
    directly so the token is issued from the correct tenant.
    Locally we fall back to ``DefaultAzureCredential``.
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
