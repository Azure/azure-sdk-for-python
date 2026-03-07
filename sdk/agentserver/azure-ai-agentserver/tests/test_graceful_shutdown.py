# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for graceful shutdown configuration and lifecycle behaviour."""
import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from starlette.requests import Request
from starlette.responses import Response

from azure.ai.agentserver import AgentServer
from azure.ai.agentserver._constants import Constants


# ---------------------------------------------------------------------------
# Agent factory functions
# ---------------------------------------------------------------------------


def _make_stub_agent(**kwargs) -> AgentServer:
    """Create a no-op agent used to inspect internal state."""
    server = AgentServer(**kwargs)

    @server.invoke_handler
    async def handle(request: Request) -> Response:
        return Response(content=b"ok")

    return server


# ---------------------------------------------------------------------------
# _resolve_graceful_shutdown_timeout
# ---------------------------------------------------------------------------


class TestResolveGracefulShutdownTimeout:
    """Unit tests for the timeout resolution hierarchy: explicit > env > default."""

    def test_explicit_value_takes_precedence(self):
        agent = _make_stub_agent(graceful_shutdown_timeout=10)
        assert agent._graceful_shutdown_timeout == 10

    def test_explicit_zero_disables_drain(self):
        agent = _make_stub_agent(graceful_shutdown_timeout=0)
        assert agent._graceful_shutdown_timeout == 0

    def test_env_var_used_when_no_explicit(self):
        with patch.dict(os.environ, {Constants.AGENT_GRACEFUL_SHUTDOWN_TIMEOUT: "45"}):
            agent = _make_stub_agent()
            assert agent._graceful_shutdown_timeout == 45

    def test_invalid_env_var_raises(self):
        with patch.dict(os.environ, {Constants.AGENT_GRACEFUL_SHUTDOWN_TIMEOUT: "not-a-number"}):
            with pytest.raises(ValueError, match="AGENT_GRACEFUL_SHUTDOWN_TIMEOUT"):
                _make_stub_agent()

    def test_non_int_explicit_value_raises(self):
        with pytest.raises(ValueError, match="expected an integer"):
            _make_stub_agent(graceful_shutdown_timeout="ten")  # type: ignore[arg-type]

    def test_default_when_nothing_set(self):
        with patch.dict(os.environ, {}, clear=True):
            agent = _make_stub_agent()
            assert agent._graceful_shutdown_timeout == Constants.DEFAULT_GRACEFUL_SHUTDOWN_TIMEOUT

    def test_default_is_30_seconds(self):
        assert Constants.DEFAULT_GRACEFUL_SHUTDOWN_TIMEOUT == 30


# ---------------------------------------------------------------------------
# Constant exists
# ---------------------------------------------------------------------------


class TestConstants:
    """Verify the new constant is wired correctly."""

    def test_env_var_name(self):
        assert Constants.AGENT_GRACEFUL_SHUTDOWN_TIMEOUT == "AGENT_GRACEFUL_SHUTDOWN_TIMEOUT"


# ---------------------------------------------------------------------------
# Hypercorn config receives graceful_timeout (sync run)
# ---------------------------------------------------------------------------


class TestRunPassesTimeout:
    """Ensure run() forwards the timeout to Hypercorn config."""

    @patch("hypercorn.asyncio.serve", new_callable=AsyncMock)
    @patch("azure.ai.agentserver.server._base.asyncio")
    def test_run_passes_timeout(self, mock_asyncio, _mock_serve):
        agent = _make_stub_agent(graceful_shutdown_timeout=15)
        agent.run()
        mock_asyncio.run.assert_called_once()
        # Verify the config built internally has the right graceful_timeout
        config = agent._build_hypercorn_config("127.0.0.1", 8088)
        assert config.graceful_timeout == 15.0

    @patch("hypercorn.asyncio.serve", new_callable=AsyncMock)
    @patch("azure.ai.agentserver.server._base.asyncio")
    def test_run_passes_default_timeout(self, mock_asyncio, _mock_serve):
        agent = _make_stub_agent()
        agent.run()
        config = agent._build_hypercorn_config("127.0.0.1", 8088)
        assert config.graceful_timeout == 30.0


# ---------------------------------------------------------------------------
# Hypercorn config receives graceful_timeout (async run)
# ---------------------------------------------------------------------------


class TestRunAsyncPassesTimeout:
    """Ensure run_async() forwards the timeout to Hypercorn config."""

    @pytest.mark.asyncio
    @patch("hypercorn.asyncio.serve", new_callable=AsyncMock)
    async def test_run_async_passes_timeout(self, mock_serve):
        agent = _make_stub_agent(graceful_shutdown_timeout=20)
        await agent.run_async()
        mock_serve.assert_awaited_once()
        # Check the config passed to serve
        call_args = mock_serve.call_args
        config = call_args[0][1] if len(call_args[0]) > 1 else call_args.kwargs.get("config")
        assert config.graceful_timeout == 20.0

    @pytest.mark.asyncio
    @patch("hypercorn.asyncio.serve", new_callable=AsyncMock)
    async def test_run_async_passes_default_timeout(self, mock_serve):
        agent = _make_stub_agent()
        await agent.run_async()
        call_args = mock_serve.call_args
        config = call_args[0][1] if len(call_args[0]) > 1 else call_args.kwargs.get("config")
        assert config.graceful_timeout == 30.0


# ---------------------------------------------------------------------------
# Lifespan shutdown log
# ---------------------------------------------------------------------------


class TestLifespanShutdown:
    """Verify the lifespan emits a shutdown log message."""

    @pytest.mark.asyncio
    async def test_shutdown_log_emitted(self):
        agent = _make_stub_agent(graceful_shutdown_timeout=42)
        # Exercise the full lifespan by sending a request through the ASGI app
        import httpx

        transport = httpx.ASGITransport(app=agent.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            resp = await client.get("/liveness")
            assert resp.status_code == 200

        # The shutdown log is emitted after the lifespan exits.
        # We verify that the app is configured with the correct timeout so the
        # log message references it.  A direct lifespan exercise is below.

    @pytest.mark.asyncio
    async def test_lifespan_shutdown_logs(self):
        """Directly exercise the lifespan context manager and verify shutdown log."""
        import logging

        agent = _make_stub_agent(graceful_shutdown_timeout=99)

        with patch("azure.ai.agentserver.server._base.logger") as mock_logger:
            # Grab the lifespan from the Starlette app
            lifespan = agent.app.router.lifespan_context
            async with lifespan(agent.app):
                pass  # startup yields here

            # After exiting the context manager, shutdown log should fire
            shutdown_calls = [
                c
                for c in mock_logger.info.call_args_list
                if "shutting down" in str(c).lower()
            ]
            assert len(shutdown_calls) == 1
            assert "99" in str(shutdown_calls[0])


# ---------------------------------------------------------------------------
# on_shutdown overridable method
# ---------------------------------------------------------------------------


def _make_shutdown_recording_agent(**kwargs) -> AgentServer:
    """Create an agent that records on_shutdown calls."""
    server = AgentServer(**kwargs)
    server.shutdown_log: list[str] = []

    @server.invoke_handler
    async def handle(request: Request) -> Response:
        return Response(content=b"ok")

    @server.shutdown_handler
    async def shutdown():
        server.shutdown_log.append("shutdown")

    return server


def _make_async_checkpoint_agent(**kwargs) -> AgentServer:
    """Create an agent whose shutdown handler performs async work."""
    server = AgentServer(**kwargs)
    server.flushed: list[str] = []

    @server.invoke_handler
    async def handle(request: Request) -> Response:
        return Response(content=b"ok")

    @server.shutdown_handler
    async def shutdown():
        import asyncio
        await asyncio.sleep(0)
        server.flushed.append("async-checkpoint")

    return server


def _make_failing_shutdown_agent(**kwargs) -> AgentServer:
    """Create an agent whose shutdown handler raises an exception."""
    server = AgentServer(**kwargs)

    @server.invoke_handler
    async def handle(request: Request) -> Response:
        return Response(content=b"ok")

    @server.shutdown_handler
    async def shutdown():
        raise RuntimeError("disk full")

    return server


class TestOnShutdownMethod:
    """Verify the overridable on_shutdown() method is called during lifespan teardown."""

    @pytest.mark.asyncio
    async def test_on_shutdown_called(self):
        agent = _make_shutdown_recording_agent()
        lifespan = agent.app.router.lifespan_context
        async with lifespan(agent.app):
            pass
        assert agent.shutdown_log == ["shutdown"]

    @pytest.mark.asyncio
    async def test_async_work_in_on_shutdown(self):
        agent = _make_async_checkpoint_agent()
        lifespan = agent.app.router.lifespan_context
        async with lifespan(agent.app):
            pass
        assert agent.flushed == ["async-checkpoint"]

    @pytest.mark.asyncio
    async def test_default_on_shutdown_is_noop(self):
        """Base class on_shutdown does nothing and doesn't raise."""
        agent = _make_stub_agent()
        lifespan = agent.app.router.lifespan_context
        async with lifespan(agent.app):
            pass  # should complete without error

    @pytest.mark.asyncio
    async def test_on_shutdown_exception_is_logged_not_raised(self):
        """A failing on_shutdown must not crash the shutdown sequence."""
        agent = _make_failing_shutdown_agent()
        with patch("azure.ai.agentserver.server._base.logger") as mock_logger:
            lifespan = agent.app.router.lifespan_context
            async with lifespan(agent.app):
                pass  # should NOT raise

            exception_calls = [
                c
                for c in mock_logger.exception.call_args_list
                if "on_shutdown" in str(c).lower()
            ]
            assert len(exception_calls) == 1

    @pytest.mark.asyncio
    async def test_on_shutdown_runs_after_shutdown_log(self):
        """on_shutdown fires after the shutdown log message."""
        order: list[str] = []

        server = AgentServer()

        @server.invoke_handler
        async def invoke(request: Request) -> Response:
            return Response(content=b"ok")

        @server.shutdown_handler
        async def shutdown():
            order.append("callback")

        with patch("azure.ai.agentserver.server._base.logger") as mock_logger:

            def tracking_info(*args, **kwargs):
                if args and "shutting down" in str(args[0]).lower():
                    order.append("log")

            mock_logger.info.side_effect = tracking_info

            lifespan = server.app.router.lifespan_context
            async with lifespan(server.app):
                pass

        assert order == ["log", "callback"]

    @pytest.mark.asyncio
    async def test_on_shutdown_has_access_to_state(self):
        """Shutdown handler can access state via closure."""
        connections: list[str] = ["db", "cache"]
        closed: list[str] = []

        server = AgentServer()

        @server.invoke_handler
        async def invoke(request: Request) -> Response:
            return Response(content=b"ok")

        @server.shutdown_handler
        async def shutdown():
            for conn in connections:
                closed.append(conn)

        lifespan = server.app.router.lifespan_context
        async with lifespan(server.app):
            pass
        assert closed == ["db", "cache"]


# ---------------------------------------------------------------------------
# on_shutdown timeout enforcement
# ---------------------------------------------------------------------------


class TestOnShutdownTimeout:
    """Verify on_shutdown is bounded by graceful_shutdown_timeout."""

    @pytest.mark.asyncio
    async def test_slow_on_shutdown_is_cancelled_and_warning_logged(self):
        """If on_shutdown exceeds the timeout, it is cancelled and a warning is logged."""
        import asyncio

        server = AgentServer(graceful_shutdown_timeout=1)

        @server.invoke_handler
        async def invoke(request: Request) -> Response:
            return Response(content=b"ok")

        @server.shutdown_handler
        async def shutdown():
            await asyncio.sleep(999)  # way longer than the 1s timeout

        with patch("azure.ai.agentserver.server._base.logger") as mock_logger:
            lifespan = server.app.router.lifespan_context
            async with lifespan(server.app):
                pass  # should NOT hang

            warning_calls = [
                c
                for c in mock_logger.warning.call_args_list
                if "did not complete" in str(c).lower()
            ]
            assert len(warning_calls) == 1
            assert "1" in str(warning_calls[0])

    @pytest.mark.asyncio
    async def test_fast_on_shutdown_completes_normally(self):
        """on_shutdown that finishes within the timeout succeeds without warnings."""
        import asyncio

        done = False
        server = AgentServer(graceful_shutdown_timeout=5)

        @server.invoke_handler
        async def invoke(request: Request) -> Response:
            return Response(content=b"ok")

        @server.shutdown_handler
        async def shutdown():
            nonlocal done
            await asyncio.sleep(0)
            done = True

        with patch("azure.ai.agentserver.server._base.logger") as mock_logger:
            lifespan = server.app.router.lifespan_context
            async with lifespan(server.app):
                pass

            warning_calls = [
                c
                for c in mock_logger.warning.call_args_list
                if "did not complete" in str(c).lower()
            ]
            assert len(warning_calls) == 0
        assert done is True

    @pytest.mark.asyncio
    async def test_zero_timeout_disables_wait(self):
        """graceful_shutdown_timeout=0 passes None to wait_for (no timeout)."""
        import asyncio

        ran = False
        server = AgentServer(graceful_shutdown_timeout=0)

        @server.invoke_handler
        async def invoke(request: Request) -> Response:
            return Response(content=b"ok")

        @server.shutdown_handler
        async def shutdown():
            nonlocal ran
            ran = True

        lifespan = server.app.router.lifespan_context
        async with lifespan(server.app):
            pass
        assert ran is True

    @pytest.mark.asyncio
    async def test_timeout_does_not_suppress_exceptions(self):
        """Exceptions from on_shutdown are still logged even if within timeout."""
        agent = _make_failing_shutdown_agent(graceful_shutdown_timeout=5)
        with patch("azure.ai.agentserver.server._base.logger") as mock_logger:
            lifespan = agent.app.router.lifespan_context
            async with lifespan(agent.app):
                pass

            exception_calls = [
                c
                for c in mock_logger.exception.call_args_list
                if "on_shutdown" in str(c).lower()
            ]
            assert len(exception_calls) == 1
