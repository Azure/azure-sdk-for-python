# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for graceful-shutdown configuration, lifecycle, and handler dispatch."""
import asyncio
import logging
import os
import signal
from unittest import mock

import pytest

from azure.ai.agentserver.core import AgentServerHost
from azure.ai.agentserver.core._config import resolve_graceful_shutdown_timeout, _DEFAULT_GRACEFUL_SHUTDOWN_TIMEOUT


# ------------------------------------------------------------------ #
# Timeout resolution: explicit > env > default (30s)
# ------------------------------------------------------------------ #


class TestResolveGracefulShutdownTimeout:
    """Tests for resolve_graceful_shutdown_timeout()."""

    def test_explicit_wins(self) -> None:
        assert resolve_graceful_shutdown_timeout(10) == 10

    def test_default(self) -> None:
        assert resolve_graceful_shutdown_timeout(None) == _DEFAULT_GRACEFUL_SHUTDOWN_TIMEOUT

    def test_non_int_explicit_raises(self) -> None:
        with pytest.raises(ValueError, match="expected an integer"):
            resolve_graceful_shutdown_timeout("ten")  # type: ignore[arg-type]

    def test_negative_explicit_clamps_to_zero(self) -> None:
        assert resolve_graceful_shutdown_timeout(-5) == 0

    def test_zero_explicit(self) -> None:
        assert resolve_graceful_shutdown_timeout(0) == 0


# ------------------------------------------------------------------ #
# Hypercorn config receives graceful_timeout
# ------------------------------------------------------------------ #


class TestHypercornConfig:
    """Verify _build_hypercorn_config passes the resolved timeout to Hypercorn."""

    def test_sync_run_passes_timeout(self) -> None:
        agent = AgentServerHost(graceful_shutdown_timeout=15)
        config = agent._build_hypercorn_config("127.0.0.1", 8000)
        assert config.graceful_timeout == 15.0

    def test_async_run_passes_timeout(self) -> None:
        agent = AgentServerHost(graceful_shutdown_timeout=25)
        config = agent._build_hypercorn_config("0.0.0.0", 9000)
        assert config.graceful_timeout == 25.0

    def test_default_timeout_in_config(self) -> None:
        env = os.environ.copy()
        env.pop("AGENT_GRACEFUL_SHUTDOWN_TIMEOUT", None)
        with mock.patch.dict(os.environ, env, clear=True):
            agent = AgentServerHost()
            config = agent._build_hypercorn_config("0.0.0.0", 8088)
            assert config.graceful_timeout == float(_DEFAULT_GRACEFUL_SHUTDOWN_TIMEOUT)


# ------------------------------------------------------------------ #
# Lifespan shutdown logging
# ------------------------------------------------------------------ #


@pytest.mark.asyncio
async def test_lifespan_shutdown_logs(caplog: pytest.LogCaptureFixture) -> None:
    """The lifespan shutdown phase logs the graceful timeout."""
    agent = AgentServerHost(graceful_shutdown_timeout=7)

    # Drive the lifespan manually via the ASGI interface.
    scope = {"type": "lifespan"}
    startup_complete = asyncio.Event()
    shutdown_complete = asyncio.Event()

    async def receive():
        if not startup_complete.is_set():
            startup_complete.set()
            return {"type": "lifespan.startup"}
        await asyncio.sleep(0)
        return {"type": "lifespan.shutdown"}

    async def send(message):
        if message["type"] == "lifespan.shutdown.complete":
            shutdown_complete.set()

    with caplog.at_level(logging.INFO, logger="azure.ai.agentserver"):
        await agent(scope, receive, send)

    assert any("shutting down" in r.message.lower() for r in caplog.records)
    assert any("7" in r.message for r in caplog.records)


# ------------------------------------------------------------------ #
# Shutdown handler decorator
# ------------------------------------------------------------------ #


@pytest.mark.asyncio
async def test_shutdown_handler_called() -> None:
    """The function registered via @shutdown_handler is called during shutdown."""
    agent = AgentServerHost(graceful_shutdown_timeout=5)
    called = False

    @agent.shutdown_handler
    async def on_shutdown():
        nonlocal called
        called = True

    # Drive lifespan
    scope = {"type": "lifespan"}
    startup_done = asyncio.Event()
    shutdown_done = asyncio.Event()

    async def receive():
        if not startup_done.is_set():
            startup_done.set()
            return {"type": "lifespan.startup"}
        await asyncio.sleep(0)
        return {"type": "lifespan.shutdown"}

    async def send(message):
        if message["type"] == "lifespan.shutdown.complete":
            shutdown_done.set()

    await agent(scope, receive, send)
    assert called is True


@pytest.mark.asyncio
async def test_default_shutdown_is_noop() -> None:
    """When no shutdown handler is registered, shutdown succeeds silently."""
    agent = AgentServerHost(graceful_shutdown_timeout=5)

    scope = {"type": "lifespan"}
    startup_done = asyncio.Event()
    shutdown_done = asyncio.Event()

    async def receive():
        if not startup_done.is_set():
            startup_done.set()
            return {"type": "lifespan.startup"}
        await asyncio.sleep(0)
        return {"type": "lifespan.shutdown"}

    async def send(message):
        if message["type"] == "lifespan.shutdown.complete":
            shutdown_done.set()

    # Should not raise
    await agent(scope, receive, send)
    assert shutdown_done.is_set()


# ------------------------------------------------------------------ #
# Failing shutdown is logged, not raised
# ------------------------------------------------------------------ #


@pytest.mark.asyncio
async def test_failing_shutdown_is_logged(caplog: pytest.LogCaptureFixture) -> None:
    """A shutdown handler that raises is logged but does not crash the server."""
    agent = AgentServerHost(graceful_shutdown_timeout=5)

    @agent.shutdown_handler
    async def on_shutdown():
        raise RuntimeError("shutdown kaboom")

    scope = {"type": "lifespan"}
    startup_done = asyncio.Event()

    async def receive():
        if not startup_done.is_set():
            startup_done.set()
            return {"type": "lifespan.startup"}
        await asyncio.sleep(0)
        return {"type": "lifespan.shutdown"}

    sent_messages: list[dict] = []

    async def send(message):
        sent_messages.append(message)

    with caplog.at_level(logging.WARNING, logger="azure.ai.agentserver"):
        await agent(scope, receive, send)

    # The error should be logged
    assert any("on_shutdown" in r.message.lower() or "error" in r.message.lower() for r in caplog.records)
    # Server should still complete shutdown
    assert any(m["type"] == "lifespan.shutdown.complete" for m in sent_messages)


# ------------------------------------------------------------------ #
# Slow shutdown is cancelled with warning
# ------------------------------------------------------------------ #


@pytest.mark.asyncio
async def test_slow_shutdown_cancelled_with_warning(caplog: pytest.LogCaptureFixture) -> None:
    """A shutdown handler exceeding the timeout is cancelled and a warning is logged."""
    agent = AgentServerHost(graceful_shutdown_timeout=1)

    @agent.shutdown_handler
    async def on_shutdown():
        await asyncio.sleep(60)  # way longer than the 1s timeout

    scope = {"type": "lifespan"}
    startup_done = asyncio.Event()

    async def receive():
        if not startup_done.is_set():
            startup_done.set()
            return {"type": "lifespan.startup"}
        await asyncio.sleep(0)
        return {"type": "lifespan.shutdown"}

    sent_messages: list[dict] = []

    async def send(message):
        sent_messages.append(message)

    with caplog.at_level(logging.WARNING, logger="azure.ai.agentserver"):
        await agent(scope, receive, send)

    assert any("did not complete" in r.message.lower() or "timeout" in r.message.lower() for r in caplog.records)
    assert any(m["type"] == "lifespan.shutdown.complete" for m in sent_messages)


# ------------------------------------------------------------------ #
# Fast shutdown completes normally
# ------------------------------------------------------------------ #


@pytest.mark.asyncio
async def test_fast_shutdown_completes_normally() -> None:
    """A shutdown handler that finishes within the timeout completes normally."""
    agent = AgentServerHost(graceful_shutdown_timeout=10)
    completed = False

    @agent.shutdown_handler
    async def on_shutdown():
        nonlocal completed
        await asyncio.sleep(0.01)
        completed = True

    scope = {"type": "lifespan"}
    startup_done = asyncio.Event()

    async def receive():
        if not startup_done.is_set():
            startup_done.set()
            return {"type": "lifespan.startup"}
        await asyncio.sleep(0)
        return {"type": "lifespan.shutdown"}

    sent_messages: list[dict] = []

    async def send(message):
        sent_messages.append(message)

    await agent(scope, receive, send)
    assert completed is True
    assert any(m["type"] == "lifespan.shutdown.complete" for m in sent_messages)


# ------------------------------------------------------------------ #
# Zero timeout passes None (no timeout)
# ------------------------------------------------------------------ #


@pytest.mark.asyncio
async def test_zero_timeout_skips_shutdown_handler() -> None:
    """When graceful_shutdown_timeout=0, the shutdown handler is skipped."""
    agent = AgentServerHost(graceful_shutdown_timeout=0)
    completed = False

    @agent.shutdown_handler
    async def on_shutdown():
        nonlocal completed
        completed = True

    scope = {"type": "lifespan"}
    startup_done = asyncio.Event()

    async def receive():
        if not startup_done.is_set():
            startup_done.set()
            return {"type": "lifespan.startup"}
        await asyncio.sleep(0)
        return {"type": "lifespan.shutdown"}

    sent_messages: list[dict] = []

    async def send(message):
        sent_messages.append(message)

    await agent(scope, receive, send)
    assert completed is False  # handler was NOT called


# ------------------------------------------------------------------ #
# SIGTERM handler registration in run()
# ------------------------------------------------------------------ #


class TestSigtermHandler:
    """Tests for SIGTERM signal handler installed by run()."""

    def _restore_sigterm(self):
        """Fixture-like helper: save and restore the SIGTERM handler."""
        original = signal.getsignal(signal.SIGTERM)
        yield
        signal.signal(signal.SIGTERM, original)

    def test_run_installs_sigterm_handler(self) -> None:
        """run() registers a SIGTERM handler that logs and re-raises."""
        original = signal.getsignal(signal.SIGTERM)
        try:
            agent = AgentServerHost(graceful_shutdown_timeout=5)
            handler_at_serve_time = None

            def fake_asyncio_run(coroutine):
                nonlocal handler_at_serve_time
                handler_at_serve_time = signal.getsignal(signal.SIGTERM)
                coroutine.close()

            with mock.patch("asyncio.run", side_effect=fake_asyncio_run):
                agent.run(host="127.0.0.1", port=9999)

            assert handler_at_serve_time is not None
            assert callable(handler_at_serve_time)
            assert handler_at_serve_time is not original
        finally:
            signal.signal(signal.SIGTERM, original)

    def test_sigterm_handler_logs_and_re_raises(self, caplog: pytest.LogCaptureFixture) -> None:
        """The installed SIGTERM handler logs then re-raises via os.kill."""
        original = signal.getsignal(signal.SIGTERM)
        try:
            agent = AgentServerHost(graceful_shutdown_timeout=5)
            handler_at_serve_time = None

            def fake_asyncio_run(coroutine):
                nonlocal handler_at_serve_time
                handler_at_serve_time = signal.getsignal(signal.SIGTERM)
                coroutine.close()

            with mock.patch("asyncio.run", side_effect=fake_asyncio_run):
                agent.run(host="127.0.0.1", port=9999)

            assert callable(handler_at_serve_time)

            # Invoke the handler and verify it:
            # 1) logs the message
            # 2) restores the original handler
            # 3) calls os.kill to re-raise
            with (
                caplog.at_level(logging.INFO, logger="azure.ai.agentserver"),
                mock.patch("os.kill") as mock_kill,
            ):
                handler_at_serve_time(signal.SIGTERM, None)

            assert any("SIGTERM received" in r.message for r in caplog.records)
            mock_kill.assert_called_once_with(os.getpid(), signal.SIGTERM)
        finally:
            signal.signal(signal.SIGTERM, original)
