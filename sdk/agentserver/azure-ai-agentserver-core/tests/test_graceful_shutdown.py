# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for graceful-shutdown configuration, lifecycle, and handler dispatch."""
import asyncio
import logging
import os
import signal
from typing import Any
from unittest import mock

import pytest

from azure.ai.agentserver.core import AgentServerHost
from azure.ai.agentserver.core._config import (
    resolve_graceful_shutdown_timeout,
    _DEFAULT_GRACEFUL_SHUTDOWN_TIMEOUT,
)


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
async def test_slow_shutdown_cancelled_with_warning(
    caplog: pytest.LogCaptureFixture,
) -> None:
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
    """Tests for the shutdown-trigger handler installed by run().

     note: ``AgentServerHost.run`` registers signal handlers
    via ``loop.add_signal_handler(SIG, _on_signal)`` rather than
    ``signal.signal(SIG, ...)``. The handler:

    1. Invokes every callback in ``_pre_shutdown_callbacks``.
    2. Sets the ``signal_event`` so Hypercorn's ``shutdown_trigger``
       awaitable resolves and graceful drain begins.

    These tests inspect the local namespace of the inner
    ``_serve_with_shutdown_trigger`` coroutine via a stub-out of
    ``asyncio.run`` that captures the coroutine before letting it run.
    """

    def test_run_installs_signal_handler_via_event_loop(self) -> None:
        """run() registers signal handlers via loop.add_signal_handler
        . We verify by intercepting asyncio.get_event_loop
                with a stub whose add_signal_handler captures registrations.
        """
        agent = AgentServerHost(graceful_shutdown_timeout=5)
        captured_handlers: list[tuple[Any, Any]] = []

        # Stub out hypercorn.serve so the coroutine returns after
        # add_signal_handler is called but before it tries to bind a
        # port (which would fail in a test environment without root).
        async def fake_hypercorn_serve(*_args, **_kwargs):
            return None

        # Stub get_event_loop to return a fake loop whose
        # add_signal_handler records what was registered.
        class _FakeLoop:
            def add_signal_handler(self, sig, callback, *args):
                captured_handlers.append((sig, callback))

        with (
            mock.patch(
                "hypercorn.asyncio.serve",
                side_effect=fake_hypercorn_serve,
            ),
            mock.patch("asyncio.get_event_loop", return_value=_FakeLoop()),
        ):
            agent.run(host="127.0.0.1", port=9999)

        # At minimum SIGTERM should have been registered. SIGINT and
        # SIGBREAK may or may not be on this platform.
        registered_sigs = [sig for sig, _ in captured_handlers]
        assert signal.SIGTERM in registered_sigs, (
            f": AgentServerHost.run MUST register a SIGTERM "
            f"handler via loop.add_signal_handler. Registered: "
            f"{[getattr(s, 'name', s) for s in registered_sigs]}"
        )
        # Every registered handler MUST be callable (the lambda /
        # _on_signal closure).
        for sig, callback in captured_handlers:
            assert callable(callback), f"Registered signal handler for {sig} is not callable: {callback!r}"

    def test_signal_handler_fires_pre_shutdown_callbacks(self) -> None:
        """The installed signal handler invokes every registered
        pre-shutdown callback BEFORE setting the signal event (so
        callbacks fire before Hypercorn begins draining).

         contract: ``register_pre_shutdown_callback`` callbacks
        run synchronously inside the signal handler.
        """
        agent = AgentServerHost(graceful_shutdown_timeout=5)
        fired: list[str] = []
        agent.register_pre_shutdown_callback(lambda: fired.append("cb-1"))
        agent.register_pre_shutdown_callback(lambda: fired.append("cb-2"))

        captured_handler: dict[str, Any] = {}

        async def fake_hypercorn_serve(*_args, **_kwargs):
            return None

        class _FakeLoop:
            def add_signal_handler(self, sig, callback, *args):
                if sig == signal.SIGTERM:
                    captured_handler["fn"] = callback

        with (
            mock.patch(
                "hypercorn.asyncio.serve",
                side_effect=fake_hypercorn_serve,
            ),
            mock.patch("asyncio.get_event_loop", return_value=_FakeLoop()),
        ):
            agent.run(host="127.0.0.1", port=9999)

        # Now invoke the captured signal handler — it should fire all
        # registered pre-shutdown callbacks in registration order.
        assert "fn" in captured_handler, "No SIGTERM handler was captured during run()"
        captured_handler["fn"]()
        assert fired == ["cb-1", "cb-2"], f"Pre-shutdown callbacks did not fire in registration order. " f"Got: {fired}"

    def test_signal_handler_isolates_callback_exceptions(self) -> None:
        """A raising pre-shutdown callback MUST NOT prevent later
        callbacks from firing AND MUST NOT prevent the shutdown event
        from being set. Otherwise a buggy callback would deadlock the
        graceful drain."""
        agent = AgentServerHost(graceful_shutdown_timeout=5)
        fired: list[str] = []

        def bad_callback():
            fired.append("bad-before-raise")
            raise RuntimeError("boom")

        def good_callback():
            fired.append("good-after-bad")

        agent.register_pre_shutdown_callback(bad_callback)
        agent.register_pre_shutdown_callback(good_callback)

        captured_handler: dict[str, Any] = {}

        async def fake_hypercorn_serve(*_args, **_kwargs):
            return None

        class _FakeLoop:
            def add_signal_handler(self, sig, callback, *args):
                if sig == signal.SIGTERM:
                    captured_handler["fn"] = callback

        with (
            mock.patch(
                "hypercorn.asyncio.serve",
                side_effect=fake_hypercorn_serve,
            ),
            mock.patch("asyncio.get_event_loop", return_value=_FakeLoop()),
        ):
            agent.run(host="127.0.0.1", port=9999)

        # Invoke the handler — bad_callback raises, but good_callback
        # must still fire.
        captured_handler["fn"]()
        assert fired == ["bad-before-raise", "good-after-bad"], f"Callback exception isolation broken: got {fired}"
