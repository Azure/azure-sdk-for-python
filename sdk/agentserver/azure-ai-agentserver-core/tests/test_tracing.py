# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for tracing configuration — not invocation spans (those live in the invocations package)."""
import contextlib
import os
from unittest import mock

from azure.ai.agentserver.core import AgentServerHost
from azure.ai.agentserver.core._config import (
    resolve_agent_name,
    resolve_agent_version,
    resolve_appinsights_connection_string,
)
from azure.ai.agentserver.core._constants import Constants


# ------------------------------------------------------------------ #
# Tracing enabled / disabled
# ------------------------------------------------------------------ #


class TestTracingToggle:
    """Tracing is enabled when App Insights or OTLP endpoint is configured."""

    def test_tracing_disabled_when_no_endpoints(self) -> None:
        env = os.environ.copy()
        env.pop(Constants.APPLICATIONINSIGHTS_CONNECTION_STRING, None)
        env.pop(Constants.OTEL_EXPORTER_OTLP_ENDPOINT, None)
        with mock.patch.dict(os.environ, env, clear=True):
            agent = AgentServerHost()
            assert agent.tracing is None

    def test_tracing_enabled_via_appinsights_env_var(self) -> None:
        with mock.patch.dict(os.environ, {Constants.APPLICATIONINSIGHTS_CONNECTION_STRING: "InstrumentationKey=test"}):
            with mock.patch(
                "azure.ai.agentserver.core._tracing.TracingHelper.__init__",
                return_value=None,
            ):
                agent = AgentServerHost()
                assert agent.tracing is not None

    def test_tracing_enabled_via_otlp_env_var(self) -> None:
        with mock.patch.dict(os.environ, {Constants.OTEL_EXPORTER_OTLP_ENDPOINT: "http://localhost:4318"}):
            with mock.patch(
                "azure.ai.agentserver.core._tracing.TracingHelper.__init__",
                return_value=None,
            ):
                agent = AgentServerHost()
                assert agent.tracing is not None

    def test_tracing_enabled_via_constructor_connection_string(self) -> None:
        with mock.patch(
            "azure.ai.agentserver.core._tracing.TracingHelper.__init__",
            return_value=None,
        ):
            agent = AgentServerHost(applicationinsights_connection_string="InstrumentationKey=ctor")
            assert agent.tracing is not None


# ------------------------------------------------------------------ #
# Application Insights connection string resolution
# ------------------------------------------------------------------ #


class TestAppInsightsConnectionString:
    """Tests for resolve_appinsights_connection_string()."""

    def test_explicit_wins(self) -> None:
        assert resolve_appinsights_connection_string("InstrumentationKey=abc") == "InstrumentationKey=abc"

    def test_env_var(self) -> None:
        with mock.patch.dict(
            os.environ,
            {Constants.APPLICATIONINSIGHTS_CONNECTION_STRING: "InstrumentationKey=env"},
        ):
            assert resolve_appinsights_connection_string(None) == "InstrumentationKey=env"

    def test_none_when_unset(self) -> None:
        env = os.environ.copy()
        env.pop(Constants.APPLICATIONINSIGHTS_CONNECTION_STRING, None)
        with mock.patch.dict(os.environ, env, clear=True):
            assert resolve_appinsights_connection_string(None) is None

    def test_explicit_overrides_env_var(self) -> None:
        with mock.patch.dict(
            os.environ,
            {Constants.APPLICATIONINSIGHTS_CONNECTION_STRING: "InstrumentationKey=env"},
        ):
            result = resolve_appinsights_connection_string("InstrumentationKey=explicit")
            assert result == "InstrumentationKey=explicit"


# ------------------------------------------------------------------ #
# _setup_azure_monitor (mocked)
# ------------------------------------------------------------------ #


class TestSetupAzureMonitor:
    """Verify _setup_azure_monitor calls the right helpers."""

    @staticmethod
    def _tracing_mocks() -> contextlib.ExitStack:
        """Enter the common set of mocks needed to instantiate TracingHelper."""
        stack = contextlib.ExitStack()
        stack.enter_context(mock.patch("azure.ai.agentserver.core._tracing._HAS_OTEL", True))
        stack.enter_context(mock.patch("azure.ai.agentserver.core._tracing.trace", create=True))
        stack.enter_context(
            mock.patch("azure.ai.agentserver.core._tracing.TraceContextTextMapPropagator", create=True)
        )
        stack.enter_context(
            mock.patch("azure.ai.agentserver.core._tracing._ensure_trace_provider", return_value=mock.MagicMock())
        )
        return stack

    def test_setup_azure_monitor_called_when_conn_str_provided(self) -> None:
        with self._tracing_mocks():
            with mock.patch(
                "azure.ai.agentserver.core._tracing.TracingHelper._setup_azure_monitor"
            ) as mock_setup:
                with mock.patch("azure.ai.agentserver.core._tracing.TracingHelper._setup_otlp_export"):
                    from azure.ai.agentserver.core._tracing import TracingHelper
                    TracingHelper(connection_string="InstrumentationKey=test")
                    # _setup_azure_monitor receives (connection_string, resource, trace_provider)
                    mock_setup.assert_called_once()
                    args = mock_setup.call_args[0]
                    assert args[0] == "InstrumentationKey=test"

    def test_setup_azure_monitor_not_called_when_no_conn_str(self) -> None:
        with self._tracing_mocks():
            with mock.patch(
                "azure.ai.agentserver.core._tracing.TracingHelper._setup_azure_monitor"
            ) as mock_setup:
                with mock.patch("azure.ai.agentserver.core._tracing.TracingHelper._setup_otlp_export"):
                    from azure.ai.agentserver.core._tracing import TracingHelper
                    TracingHelper(connection_string=None)
                    mock_setup.assert_not_called()


# ------------------------------------------------------------------ #
# Constructor passes / skips connection string
# ------------------------------------------------------------------ #


class TestConstructorConnectionString:
    """Verify AgentServerHost forwards the connection string to TracingHelper."""

    def test_constructor_passes_connection_string(self) -> None:
        with mock.patch(
            "azure.ai.agentserver.core._tracing.TracingHelper.__init__",
            return_value=None,
        ) as mock_init:
            AgentServerHost(
                applicationinsights_connection_string="InstrumentationKey=ctor",
            )
            mock_init.assert_called_once_with(connection_string="InstrumentationKey=ctor")


# ------------------------------------------------------------------ #
# Agent name / version resolution with new env vars
# ------------------------------------------------------------------ #


class TestAgentIdentityResolution:
    """Tests for resolve_agent_name() and resolve_agent_version()."""

    def test_agent_name_from_env(self) -> None:
        with mock.patch.dict(os.environ, {Constants.FOUNDRY_AGENT_NAME: "my-agent"}):
            assert resolve_agent_name() == "my-agent"

    def test_agent_name_default_empty(self) -> None:
        env = os.environ.copy()
        env.pop(Constants.FOUNDRY_AGENT_NAME, None)
        with mock.patch.dict(os.environ, env, clear=True):
            assert resolve_agent_name() == ""

    def test_agent_version_from_env(self) -> None:
        with mock.patch.dict(os.environ, {Constants.FOUNDRY_AGENT_VERSION: "2.0"}):
            assert resolve_agent_version() == "2.0"

    def test_agent_version_default_empty(self) -> None:
        env = os.environ.copy()
        env.pop(Constants.FOUNDRY_AGENT_VERSION, None)
        with mock.patch.dict(os.environ, env, clear=True):
            assert resolve_agent_version() == ""



