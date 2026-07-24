# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Root conftest — ensures the project root is on sys.path so that
``from tests._helpers import …`` works regardless of how pytest is invoked."""

import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

_PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "tracing_e2e: end-to-end tracing tests against live Application Insights",
    )


@pytest.fixture(autouse=True, scope="session")
def _prevent_distro_setup(request):
    """Prevent microsoft-opentelemetry distro from contaminating global OTel
    state during tests.  Without this, CI environments that have the distro
    installed and APPLICATIONINSIGHTS_CONNECTION_STRING set would trigger
    ``use_microsoft_opentelemetry()`` on the first server construction,
    installing a global TracerProvider that breaks later traceparent-
    propagation tests.

    When running E2E tracing tests (``-m tracing_e2e``), the real distro
    export is needed so spans actually reach Application Insights."""
    mark_expression = request.config.getoption("-m", default="")
    # Only enable the real distro when the marker expression actually *selects*
    # the E2E suite. A plain substring check would also match exclusions like
    # ``-m "not tracing_e2e"`` (or a parenthesized ``-m "not (tracing_e2e)"``)
    # and wrongly leave the real distro enabled for ordinary tests,
    # contaminating global OpenTelemetry state.
    normalized = mark_expression.replace(" ", "").replace("(", "").replace(")", "")
    selects_e2e = "tracing_e2e" in normalized and "nottracing_e2e" not in normalized
    if selects_e2e:
        yield
    else:
        with patch("azure.ai.agentserver.core._tracing._setup_distro_export", create=True):
            yield


# ---------------------------------------------------------------------------
# E2E tracing fixtures (used by test_tracing_e2e.py, selected via -m tracing_e2e)
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
