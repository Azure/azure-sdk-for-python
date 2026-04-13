# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Hosting-specific edge-case tests."""
import logging

import pytest
import httpx

from azure.ai.agentserver.core import AgentServerHost
from azure.ai.agentserver.core._config import resolve_log_level


# ------------------------------------------------------------------ #
# POST /readiness → 405
# ------------------------------------------------------------------ #


@pytest.fixture()
def client() -> httpx.AsyncClient:
    agent = AgentServerHost()
    return httpx.AsyncClient(
        transport=httpx.ASGITransport(app=agent),
        base_url="http://testserver",
    )


@pytest.mark.asyncio
async def test_post_readiness_returns_405(client: httpx.AsyncClient) -> None:
    """POST /readiness is method-not-allowed."""
    resp = await client.post("/readiness")
    assert resp.status_code == 405


# ------------------------------------------------------------------ #
# Log level via constructor
# ------------------------------------------------------------------ #


class TestLogLevelConstructor:
    """Log-level configuration via the AgentServerHost constructor."""

    def test_log_level_via_constructor(self) -> None:
        AgentServerHost(log_level="DEBUG")
        root = logging.getLogger()
        assert root.level == logging.DEBUG

    def test_log_level_warning_via_constructor(self) -> None:
        AgentServerHost(log_level="WARNING")
        root = logging.getLogger()
        assert root.level == logging.WARNING

    def test_log_level_case_insensitive(self) -> None:
        AgentServerHost(log_level="error")
        root = logging.getLogger()
        assert root.level == logging.ERROR


# ------------------------------------------------------------------ #
# Log level via env var
# ------------------------------------------------------------------ #


class TestInvalidLogLevel:
    """Invalid log levels are rejected with ValueError."""

    def test_invalid_log_level_raises(self) -> None:
        with pytest.raises(ValueError, match="Invalid log level"):
            AgentServerHost(log_level="TRACE")


# ------------------------------------------------------------------ #
# resolve_log_level unit tests
# ------------------------------------------------------------------ #


class TestResolveLogLevel:
    """Unit tests for resolve_log_level()."""

    def test_explicit_debug(self) -> None:
        assert resolve_log_level("DEBUG") == "DEBUG"

    def test_explicit_info(self) -> None:
        assert resolve_log_level("INFO") == "INFO"

    def test_explicit_warning(self) -> None:
        assert resolve_log_level("WARNING") == "WARNING"

    def test_explicit_error(self) -> None:
        assert resolve_log_level("ERROR") == "ERROR"

    def test_explicit_critical(self) -> None:
        assert resolve_log_level("CRITICAL") == "CRITICAL"

    def test_case_insensitive(self) -> None:
        assert resolve_log_level("debug") == "DEBUG"

    def test_invalid_raises(self) -> None:
        with pytest.raises(ValueError, match="Invalid log level"):
            resolve_log_level("TRACE")

    def test_default_info(self) -> None:
        assert resolve_log_level(None) == "INFO"
