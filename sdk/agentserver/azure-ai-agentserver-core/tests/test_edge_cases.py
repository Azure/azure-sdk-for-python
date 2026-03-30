# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Hosting-specific edge-case tests."""
import logging
import os
from unittest import mock

import pytest
import httpx

from azure.ai.agentserver.core import AgentHost
from azure.ai.agentserver.core._config import resolve_log_level
from azure.ai.agentserver.core._constants import Constants


# ------------------------------------------------------------------ #
# POST /readiness → 405
# ------------------------------------------------------------------ #


@pytest.fixture()
def client() -> httpx.AsyncClient:
    agent = AgentHost()
    return httpx.AsyncClient(
        transport=httpx.ASGITransport(app=agent.app),
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
    """Log-level configuration via the AgentHost constructor."""

    def test_log_level_via_constructor(self) -> None:
        AgentHost(log_level="DEBUG")  # side-effect: configures logger
        lib_logger = logging.getLogger("azure.ai.agentserver")
        assert lib_logger.level == logging.DEBUG

    def test_log_level_warning_via_constructor(self) -> None:
        AgentHost(log_level="WARNING")  # side-effect: configures logger
        lib_logger = logging.getLogger("azure.ai.agentserver")
        assert lib_logger.level == logging.WARNING

    def test_log_level_case_insensitive(self) -> None:
        AgentHost(log_level="error")  # side-effect: configures logger
        lib_logger = logging.getLogger("azure.ai.agentserver")
        assert lib_logger.level == logging.ERROR


# ------------------------------------------------------------------ #
# Log level via env var
# ------------------------------------------------------------------ #


class TestLogLevelEnvVar:
    """Log-level configuration via the AGENT_LOG_LEVEL environment variable."""

    def test_log_level_via_env_var(self) -> None:
        with mock.patch.dict(os.environ, {Constants.AGENT_LOG_LEVEL: "CRITICAL"}):
            AgentHost()  # side-effect: configures logger
            lib_logger = logging.getLogger("azure.ai.agentserver")
            assert lib_logger.level == logging.CRITICAL

    def test_constructor_overrides_env_var(self) -> None:
        with mock.patch.dict(os.environ, {Constants.AGENT_LOG_LEVEL: "CRITICAL"}):
            AgentHost(log_level="DEBUG")  # side-effect: configures logger
            lib_logger = logging.getLogger("azure.ai.agentserver")
            assert lib_logger.level == logging.DEBUG


# ------------------------------------------------------------------ #
# Invalid log level raises
# ------------------------------------------------------------------ #


class TestInvalidLogLevel:
    """Invalid log levels are rejected with ValueError."""

    def test_invalid_log_level_raises(self) -> None:
        with pytest.raises(ValueError, match="Invalid log level"):
            AgentHost(log_level="TRACE")

    def test_invalid_log_level_via_env_raises(self) -> None:
        with mock.patch.dict(os.environ, {Constants.AGENT_LOG_LEVEL: "VERBOSE"}):
            with pytest.raises(ValueError, match="Invalid log level"):
                AgentHost()


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

    def test_env_var_fallback(self) -> None:
        with mock.patch.dict(os.environ, {Constants.AGENT_LOG_LEVEL: "ERROR"}):
            assert resolve_log_level(None) == "ERROR"

    def test_default_info(self) -> None:
        env = os.environ.copy()
        env.pop(Constants.AGENT_LOG_LEVEL, None)
        with mock.patch.dict(os.environ, env, clear=True):
            assert resolve_log_level(None) == "INFO"
