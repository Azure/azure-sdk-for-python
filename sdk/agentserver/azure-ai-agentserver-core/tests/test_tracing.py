# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for tracing configuration — not invocation spans (those live in the invocations package)."""
import os
from unittest import mock

from azure.ai.agentserver.core import AgentServerHost
from azure.ai.agentserver.core._config import (
    resolve_agent_name,
    resolve_agent_version,
    resolve_appinsights_connection_string,
)



# ------------------------------------------------------------------ #
# Tracing enabled / disabled
# ------------------------------------------------------------------ #


class TestTracingToggle:
    """Tracing is configured when App Insights or OTLP endpoint is available."""

    def test_tracing_disabled_when_no_endpoints(self) -> None:
        env = os.environ.copy()
        env.pop("APPLICATIONINSIGHTS_CONNECTION_STRING", None)
        env.pop("OTEL_EXPORTER_OTLP_ENDPOINT", None)
        with mock.patch.dict(os.environ, env, clear=True):
            mock_configure = mock.MagicMock()
            AgentServerHost(configure_tracing=mock_configure)
            mock_configure.assert_not_called()

    def test_tracing_enabled_via_appinsights_env_var(self) -> None:
        with mock.patch.dict(os.environ, {"APPLICATIONINSIGHTS_CONNECTION_STRING": "InstrumentationKey=test"}):
            mock_configure = mock.MagicMock()
            AgentServerHost(configure_tracing=mock_configure)
            mock_configure.assert_called_once()

    def test_tracing_enabled_via_otlp_env_var(self) -> None:
        with mock.patch.dict(os.environ, {"OTEL_EXPORTER_OTLP_ENDPOINT": "http://localhost:4318"}):
            mock_configure = mock.MagicMock()
            AgentServerHost(configure_tracing=mock_configure)
            mock_configure.assert_called_once()

    def test_tracing_enabled_via_constructor_connection_string(self) -> None:
        mock_configure = mock.MagicMock()
        AgentServerHost(
            applicationinsights_connection_string="InstrumentationKey=ctor",
            configure_tracing=mock_configure,
        )
        mock_configure.assert_called_once_with(connection_string="InstrumentationKey=ctor")

    def test_tracing_disabled_when_configure_tracing_is_none(self) -> None:
        """Passing configure_tracing=None disables tracing entirely."""
        with mock.patch.dict(os.environ, {"APPLICATIONINSIGHTS_CONNECTION_STRING": "InstrumentationKey=test"}):
            # Should not raise even with App Insights configured
            AgentServerHost(configure_tracing=None)


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
            {"APPLICATIONINSIGHTS_CONNECTION_STRING": "InstrumentationKey=env"},
        ):
            assert resolve_appinsights_connection_string(None) == "InstrumentationKey=env"

    def test_none_when_unset(self) -> None:
        env = os.environ.copy()
        env.pop("APPLICATIONINSIGHTS_CONNECTION_STRING", None)
        with mock.patch.dict(os.environ, env, clear=True):
            assert resolve_appinsights_connection_string(None) is None

    def test_explicit_overrides_env_var(self) -> None:
        with mock.patch.dict(
            os.environ,
            {"APPLICATIONINSIGHTS_CONNECTION_STRING": "InstrumentationKey=env"},
        ):
            result = resolve_appinsights_connection_string("InstrumentationKey=explicit")
            assert result == "InstrumentationKey=explicit"


# ------------------------------------------------------------------ #
# _setup_azure_monitor (mocked)
# ------------------------------------------------------------------ #


class TestSetupAzureMonitor:
    """Verify configure_tracing calls the right exporter setup functions."""

    def test_setup_azure_monitor_called_when_conn_str_provided(self) -> None:
        with mock.patch("azure.ai.agentserver.core._tracing._setup_trace_export") as mock_trace:
            with mock.patch("azure.ai.agentserver.core._tracing._setup_log_export"):
                with mock.patch("azure.ai.agentserver.core._tracing._setup_otlp_trace_export"):
                    with mock.patch("azure.ai.agentserver.core._tracing._setup_otlp_log_export"):
                        from azure.ai.agentserver.core import _tracing
                        _tracing.configure_tracing(connection_string="InstrumentationKey=test")
                        mock_trace.assert_called_once()
                        args = mock_trace.call_args[0]
                        assert args[1] == "InstrumentationKey=test"

    def test_setup_azure_monitor_not_called_when_no_conn_str(self) -> None:
        with mock.patch("azure.ai.agentserver.core._tracing._setup_trace_export") as mock_trace:
            with mock.patch("azure.ai.agentserver.core._tracing._setup_log_export"):
                with mock.patch("azure.ai.agentserver.core._tracing._setup_otlp_trace_export"):
                    with mock.patch("azure.ai.agentserver.core._tracing._setup_otlp_log_export"):
                        from azure.ai.agentserver.core import _tracing
                        _tracing.configure_tracing(connection_string=None)
                        mock_trace.assert_not_called()


# ------------------------------------------------------------------ #
# Constructor passes / skips connection string
# ------------------------------------------------------------------ #


class TestConstructorConnectionString:
    """Verify AgentServerHost forwards the connection string to configure_tracing."""

    def test_constructor_passes_connection_string(self) -> None:
        mock_configure = mock.MagicMock()
        AgentServerHost(
            applicationinsights_connection_string="InstrumentationKey=ctor",
            configure_tracing=mock_configure,
        )
        mock_configure.assert_called_once_with(connection_string="InstrumentationKey=ctor")


# ------------------------------------------------------------------ #
# Agent name / version resolution with new env vars
# ------------------------------------------------------------------ #


class TestAgentIdentityResolution:
    """Tests for resolve_agent_name() and resolve_agent_version()."""

    def test_agent_name_from_env(self) -> None:
        with mock.patch.dict(os.environ, {"FOUNDRY_AGENT_NAME": "my-agent"}):
            assert resolve_agent_name() == "my-agent"

    def test_agent_name_default_empty(self) -> None:
        env = os.environ.copy()
        env.pop("FOUNDRY_AGENT_NAME", None)
        with mock.patch.dict(os.environ, env, clear=True):
            assert resolve_agent_name() == ""

    def test_agent_version_from_env(self) -> None:
        with mock.patch.dict(os.environ, {"FOUNDRY_AGENT_VERSION": "2.0"}):
            assert resolve_agent_version() == "2.0"

    def test_agent_version_default_empty(self) -> None:
        env = os.environ.copy()
        env.pop("FOUNDRY_AGENT_VERSION", None)
        with mock.patch.dict(os.environ, env, clear=True):
            assert resolve_agent_version() == ""



