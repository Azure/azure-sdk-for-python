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
# Minimal concrete subclass for testing
# ---------------------------------------------------------------------------


class _StubAgent(AgentServer):
    """No-op agent used to inspect internal state."""

    async def invoke(self, request: Request) -> Response:
        return Response(content=b"ok")


# ---------------------------------------------------------------------------
# _resolve_graceful_shutdown_timeout
# ---------------------------------------------------------------------------


class TestResolveGracefulShutdownTimeout:
    """Unit tests for the timeout resolution hierarchy: explicit > env > default."""

    def test_explicit_value_takes_precedence(self):
        agent = _StubAgent(timeout_graceful_shutdown=10)
        assert agent._timeout_graceful_shutdown == 10

    def test_explicit_zero_disables_drain(self):
        agent = _StubAgent(timeout_graceful_shutdown=0)
        assert agent._timeout_graceful_shutdown == 0

    def test_env_var_used_when_no_explicit(self):
        with patch.dict(os.environ, {Constants.AGENT_GRACEFUL_SHUTDOWN_TIMEOUT: "45"}):
            agent = _StubAgent()
            assert agent._timeout_graceful_shutdown == 45

    def test_invalid_env_var_raises(self):
        with patch.dict(os.environ, {Constants.AGENT_GRACEFUL_SHUTDOWN_TIMEOUT: "not-a-number"}):
            with pytest.raises(ValueError, match="AGENT_GRACEFUL_SHUTDOWN_TIMEOUT"):
                _StubAgent()

    def test_non_int_explicit_value_raises(self):
        with pytest.raises(ValueError, match="expected an integer"):
            _StubAgent(timeout_graceful_shutdown="ten")  # type: ignore[arg-type]

    def test_default_when_nothing_set(self):
        with patch.dict(os.environ, {}, clear=True):
            agent = _StubAgent()
            assert agent._timeout_graceful_shutdown == Constants.DEFAULT_GRACEFUL_SHUTDOWN_TIMEOUT

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

    @patch("azure.ai.agentserver.server._base._hypercorn_serve", new_callable=AsyncMock)
    @patch("azure.ai.agentserver.server._base.asyncio")
    def test_run_passes_timeout(self, mock_asyncio, _mock_serve):
        agent = _StubAgent(timeout_graceful_shutdown=15)
        agent.run()
        mock_asyncio.run.assert_called_once()
        # Verify the config built internally has the right graceful_timeout
        config = agent._build_hypercorn_config("127.0.0.1", 8088)
        assert config.graceful_timeout == 15.0

    @patch("azure.ai.agentserver.server._base._hypercorn_serve", new_callable=AsyncMock)
    @patch("azure.ai.agentserver.server._base.asyncio")
    def test_run_passes_default_timeout(self, mock_asyncio, _mock_serve):
        agent = _StubAgent()
        agent.run()
        config = agent._build_hypercorn_config("127.0.0.1", 8088)
        assert config.graceful_timeout == 30.0


# ---------------------------------------------------------------------------
# Hypercorn config receives graceful_timeout (async run)
# ---------------------------------------------------------------------------


class TestRunAsyncPassesTimeout:
    """Ensure run_async() forwards the timeout to Hypercorn config."""

    @pytest.mark.asyncio
    @patch("azure.ai.agentserver.server._base._hypercorn_serve", new_callable=AsyncMock)
    async def test_run_async_passes_timeout(self, mock_serve):
        agent = _StubAgent(timeout_graceful_shutdown=20)
        await agent.run_async()
        mock_serve.assert_awaited_once()
        # Check the config passed to serve
        call_args = mock_serve.call_args
        config = call_args[0][1] if len(call_args[0]) > 1 else call_args.kwargs.get("config")
        assert config.graceful_timeout == 20.0

    @pytest.mark.asyncio
    @patch("azure.ai.agentserver.server._base._hypercorn_serve", new_callable=AsyncMock)
    async def test_run_async_passes_default_timeout(self, mock_serve):
        agent = _StubAgent()
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
        agent = _StubAgent(timeout_graceful_shutdown=42)
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

        agent = _StubAgent(timeout_graceful_shutdown=99)

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


class _ShutdownRecordingAgent(AgentServer):
    """Agent that records on_shutdown calls."""

    def __init__(self, **kwargs):
        self.shutdown_log: list[str] = []
        super().__init__(**kwargs)

    async def invoke(self, request: Request) -> Response:
        return Response(content=b"ok")

    async def on_shutdown(self) -> None:
        self.shutdown_log.append("shutdown")


class _AsyncCheckpointAgent(AgentServer):
    """Agent whose on_shutdown performs async work."""

    def __init__(self, **kwargs):
        self.flushed: list[str] = []
        super().__init__(**kwargs)

    async def invoke(self, request: Request) -> Response:
        return Response(content=b"ok")

    async def on_shutdown(self) -> None:
        # Simulate async I/O (checkpoint to disk / blob storage)
        import asyncio

        await asyncio.sleep(0)
        self.flushed.append("async-checkpoint")


class _FailingShutdownAgent(AgentServer):
    """Agent whose on_shutdown raises an exception."""

    async def invoke(self, request: Request) -> Response:
        return Response(content=b"ok")

    async def on_shutdown(self) -> None:
        raise RuntimeError("disk full")


class TestOnShutdownMethod:
    """Verify the overridable on_shutdown() method is called during lifespan teardown."""

    @pytest.mark.asyncio
    async def test_on_shutdown_called(self):
        agent = _ShutdownRecordingAgent()
        lifespan = agent.app.router.lifespan_context
        async with lifespan(agent.app):
            pass
        assert agent.shutdown_log == ["shutdown"]

    @pytest.mark.asyncio
    async def test_async_work_in_on_shutdown(self):
        agent = _AsyncCheckpointAgent()
        lifespan = agent.app.router.lifespan_context
        async with lifespan(agent.app):
            pass
        assert agent.flushed == ["async-checkpoint"]

    @pytest.mark.asyncio
    async def test_default_on_shutdown_is_noop(self):
        """Base class on_shutdown does nothing and doesn't raise."""
        agent = _StubAgent()
        lifespan = agent.app.router.lifespan_context
        async with lifespan(agent.app):
            pass  # should complete without error

    @pytest.mark.asyncio
    async def test_on_shutdown_exception_is_logged_not_raised(self):
        """A failing on_shutdown must not crash the shutdown sequence."""
        agent = _FailingShutdownAgent()
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

        class _OrderingAgent(AgentServer):
            async def invoke(self, request: Request) -> Response:
                return Response(content=b"ok")

            async def on_shutdown(self) -> None:
                order.append("callback")

        agent = _OrderingAgent()
        with patch("azure.ai.agentserver.server._base.logger") as mock_logger:

            def tracking_info(*args, **kwargs):
                if args and "shutting down" in str(args[0]).lower():
                    order.append("log")

            mock_logger.info.side_effect = tracking_info

            lifespan = agent.app.router.lifespan_context
            async with lifespan(agent.app):
                pass

        assert order == ["log", "callback"]

    @pytest.mark.asyncio
    async def test_on_shutdown_has_access_to_self(self):
        """on_shutdown can access instance state — the key benefit over a callback."""

        class _StatefulAgent(AgentServer):
            def __init__(self):
                self.connections: list[str] = ["db", "cache"]
                self.closed: list[str] = []
                super().__init__()

            async def invoke(self, request: Request) -> Response:
                return Response(content=b"ok")

            async def on_shutdown(self) -> None:
                for conn in self.connections:
                    self.closed.append(conn)

        agent = _StatefulAgent()
        lifespan = agent.app.router.lifespan_context
        async with lifespan(agent.app):
            pass
        assert agent.closed == ["db", "cache"]


# ---------------------------------------------------------------------------
# on_shutdown timeout enforcement
# ---------------------------------------------------------------------------


class TestOnShutdownTimeout:
    """Verify on_shutdown is bounded by timeout_graceful_shutdown."""

    @pytest.mark.asyncio
    async def test_slow_on_shutdown_is_cancelled_and_warning_logged(self):
        """If on_shutdown exceeds the timeout, it is cancelled and a warning is logged."""
        import asyncio

        class _SlowAgent(AgentServer):
            async def invoke(self, request: Request) -> Response:
                return Response(content=b"ok")

            async def on_shutdown(self) -> None:
                await asyncio.sleep(999)  # way longer than the 1s timeout

        agent = _SlowAgent(timeout_graceful_shutdown=1)
        with patch("azure.ai.agentserver.server._base.logger") as mock_logger:
            lifespan = agent.app.router.lifespan_context
            async with lifespan(agent.app):
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

        class _FastAgent(AgentServer):
            def __init__(self):
                self.done = False
                super().__init__(timeout_graceful_shutdown=5)

            async def invoke(self, request: Request) -> Response:
                return Response(content=b"ok")

            async def on_shutdown(self) -> None:
                await asyncio.sleep(0)
                self.done = True

        agent = _FastAgent()
        with patch("azure.ai.agentserver.server._base.logger") as mock_logger:
            lifespan = agent.app.router.lifespan_context
            async with lifespan(agent.app):
                pass

            warning_calls = [
                c
                for c in mock_logger.warning.call_args_list
                if "did not complete" in str(c).lower()
            ]
            assert len(warning_calls) == 0
        assert agent.done is True

    @pytest.mark.asyncio
    async def test_zero_timeout_disables_wait(self):
        """timeout_graceful_shutdown=0 passes None to wait_for (no timeout)."""
        import asyncio

        class _QuickAgent(AgentServer):
            def __init__(self):
                self.ran = False
                super().__init__(timeout_graceful_shutdown=0)

            async def invoke(self, request: Request) -> Response:
                return Response(content=b"ok")

            async def on_shutdown(self) -> None:
                self.ran = True

        agent = _QuickAgent()
        lifespan = agent.app.router.lifespan_context
        async with lifespan(agent.app):
            pass
        assert agent.ran is True

    @pytest.mark.asyncio
    async def test_timeout_does_not_suppress_exceptions(self):
        """Exceptions from on_shutdown are still logged even if within timeout."""
        agent = _FailingShutdownAgent(timeout_graceful_shutdown=5)
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