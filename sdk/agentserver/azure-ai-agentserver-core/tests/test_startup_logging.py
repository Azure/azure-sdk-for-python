# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Unit tests for startup configuration logging and URI masking."""
import logging

import pytest

from azure.ai.agentserver.core._base import _mask_uri, _NOT_SET


class TestMaskUri:
    """Tests for the _mask_uri helper that redacts sensitive URI components."""

    def test_empty_string_returns_not_set(self) -> None:
        assert _mask_uri("") == _NOT_SET

    def test_none_like_empty_returns_not_set(self) -> None:
        # Whitespace-only
        assert _mask_uri("   ") == _NOT_SET

    def test_https_uri_strips_path_and_query(self) -> None:
        result = _mask_uri("https://myproject.azure.com/subscriptions/abc?api-version=2024")
        assert result == "https://myproject.azure.com"

    def test_http_uri_with_port(self) -> None:
        result = _mask_uri("http://localhost:8080/some/path")
        assert result == "http://localhost:8080"

    def test_https_uri_with_credentials_in_userinfo(self) -> None:
        result = _mask_uri("https://user:password@myhost.com/resource")
        assert result == "https://myhost.com"

    def test_uri_with_only_scheme_and_host(self) -> None:
        result = _mask_uri("https://myhost.com")
        assert result == "https://myhost.com"

    def test_non_uri_string_returns_redacted(self) -> None:
        # A bare string with no scheme won't parse properly
        result = _mask_uri("not-a-uri")
        assert result == "(redacted)"

    def test_connection_string_format_is_redacted(self) -> None:
        # Connection strings like AppInsights don't have scheme://host format
        result = _mask_uri("InstrumentationKey=abc;IngestionEndpoint=https://x.in.ai")
        assert result == "(redacted)"


class TestStartupConfigurationLogging:
    """Tests that startup configuration is logged during lifespan."""

    @pytest.fixture
    def _clean_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Remove all platform env vars to get a clean baseline."""
        for var in [
            "FOUNDRY_AGENT_NAME",
            "FOUNDRY_AGENT_VERSION",
            "FOUNDRY_HOSTING_ENVIRONMENT",
            "FOUNDRY_PROJECT_ENDPOINT",
            "FOUNDRY_PROJECT_ARM_ID",
            "FOUNDRY_AGENT_SESSION_ID",
            "PORT",
            "APPLICATIONINSIGHTS_CONNECTION_STRING",
            "OTEL_EXPORTER_OTLP_ENDPOINT",
            "SSE_KEEPALIVE_INTERVAL",
        ]:
            monkeypatch.delenv(var, raising=False)

    @pytest.mark.usefixtures("_clean_env")
    @pytest.mark.asyncio
    async def test_startup_logs_platform_environment(self, caplog: pytest.LogCaptureFixture) -> None:
        """Lifespan startup emits platform environment log line."""
        from azure.ai.agentserver.core import AgentServerHost

        app = AgentServerHost()

        with caplog.at_level(logging.INFO, logger="azure.ai.agentserver"):
            async with app.router.lifespan_context(app):
                pass

        platform_logs = [r for r in caplog.records if "Platform environment" in r.message]
        assert len(platform_logs) == 1
        msg = platform_logs[0].message
        assert "is_hosted=False" in msg
        assert "port=8088" in msg

    @pytest.mark.usefixtures("_clean_env")
    @pytest.mark.asyncio
    async def test_startup_logs_connectivity(self, caplog: pytest.LogCaptureFixture) -> None:
        """Lifespan startup emits connectivity log line with masked URIs."""
        from azure.ai.agentserver.core import AgentServerHost

        app = AgentServerHost()

        with caplog.at_level(logging.INFO, logger="azure.ai.agentserver"):
            async with app.router.lifespan_context(app):
                pass

        connectivity_logs = [r for r in caplog.records if "Connectivity" in r.message]
        assert len(connectivity_logs) == 1
        msg = connectivity_logs[0].message
        assert "project_endpoint=(not set)" in msg
        assert "appinsights_configured=False" in msg

    @pytest.mark.usefixtures("_clean_env")
    @pytest.mark.asyncio
    async def test_startup_logs_host_options(self, caplog: pytest.LogCaptureFixture) -> None:
        """Lifespan startup emits host options log line."""
        from azure.ai.agentserver.core import AgentServerHost

        app = AgentServerHost()

        with caplog.at_level(logging.INFO, logger="azure.ai.agentserver"):
            async with app.router.lifespan_context(app):
                pass

        host_logs = [r for r in caplog.records if "Host options" in r.message]
        assert len(host_logs) == 1
        msg = host_logs[0].message
        assert "shutdown_timeout=30s" in msg
        assert "protocols=" in msg

    @pytest.mark.asyncio
    async def test_startup_masks_project_endpoint(
        self, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Project endpoint URI is masked to scheme://host only."""
        monkeypatch.setenv("FOUNDRY_PROJECT_ENDPOINT", "https://myproject.azure.com/sub/123?key=secret")
        monkeypatch.delenv("FOUNDRY_HOSTING_ENVIRONMENT", raising=False)
        monkeypatch.delenv("PORT", raising=False)

        from azure.ai.agentserver.core import AgentServerHost

        app = AgentServerHost()

        with caplog.at_level(logging.INFO, logger="azure.ai.agentserver"):
            async with app.router.lifespan_context(app):
                pass

        connectivity_logs = [r for r in caplog.records if "Connectivity" in r.message]
        assert len(connectivity_logs) == 1
        msg = connectivity_logs[0].message
        assert "project_endpoint=https://myproject.azure.com" in msg
        # Must NOT contain the path or query
        assert "/sub/123" not in msg
        assert "key=secret" not in msg

    @pytest.mark.asyncio
    async def test_appinsights_connection_string_never_logged(
        self, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ) -> None:
        """AppInsights connection string value must never appear in logs."""
        secret = "InstrumentationKey=00000000-0000-0000-0000-000000000000;IngestionEndpoint=https://dc.ai"
        monkeypatch.setenv("APPLICATIONINSIGHTS_CONNECTION_STRING", secret)
        monkeypatch.delenv("FOUNDRY_HOSTING_ENVIRONMENT", raising=False)
        monkeypatch.delenv("PORT", raising=False)

        from azure.ai.agentserver.core import AgentServerHost

        app = AgentServerHost(configure_observability=None)

        with caplog.at_level(logging.DEBUG, logger="azure.ai.agentserver"):
            async with app.router.lifespan_context(app):
                pass

        # The boolean flag should be logged
        connectivity_logs = [r for r in caplog.records if "Connectivity" in r.message]
        assert len(connectivity_logs) == 1
        assert "appinsights_configured=True" in connectivity_logs[0].message

        # The actual connection string must NEVER appear in any log record
        all_messages = " ".join(r.message for r in caplog.records)
        assert "InstrumentationKey" not in all_messages
        assert secret not in all_messages
