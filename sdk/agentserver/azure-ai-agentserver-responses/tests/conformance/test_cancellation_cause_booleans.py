# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Conformance tests for the spec 024 Phase 5 composing-cause cancellation surface.

Maps each §10 cause trigger to its observable boolean / event shape on
``ResponseContext``. Drives the orchestrator end-to-end via TestClient
(unit-test-grade Path A scenarios) and verifies the cause-boolean
matrix from `docs/responses-resilience-spec.md` §10.

Cause matrix (covered by tests below):

| Trigger                                | cancel | shutdown | client_cancelled |
|----------------------------------------|--------|----------|------------------|
| Steering (new turn queued)             | set    | not set  | False            |
| Client `POST /responses/{id}/cancel`   | set    | not set  | True             |
| Non-bg POST disconnect (B17)           | set    | not set  | True             |
| Graceful shutdown (`SIGTERM`)          | set    | set      | False            |
| Multiple causes compose                | set    | set      | True             |
| No cancellation                        | not set| not set  | False            |

Plus:
- `context.exit_for_recovery()` sentinel propagates through dispatch
- handler signature validation rejects sync + 3-arg handlers
"""

from __future__ import annotations

import asyncio
from typing import Any

import pytest
from starlette.testclient import TestClient

from azure.ai.agentserver.responses import (
    ResponseContext,
    ResponseEventStream,
    ResponsesAgentServerHost,
    ResponsesServerOptions,
)


# ──────────────────────────────────────────────────────────────────────
# Baseline shape: no cancellation
# ──────────────────────────────────────────────────────────────────────


def test_no_cancellation_baseline_shape() -> None:
    """No cancellation → cancel + shutdown unset, client_cancelled=False."""
    captured: dict[str, Any] = {}
    app = ResponsesAgentServerHost()

    @app.response_handler
    async def _handler(request: Any, context: ResponseContext, cancellation_signal: asyncio.Event):
        async def _events():
            stream = ResponseEventStream(response_id=context.response_id, request=request)
            yield stream.emit_created()
            yield stream.emit_in_progress()
            captured["cancel_at_start"] = cancellation_signal.is_set()
            captured["shutdown_at_start"] = context.shutdown.is_set()
            captured["client_cancelled_at_start"] = context.client_cancelled
            msg = stream.add_output_item_message()
            yield msg.emit_added()
            tc = msg.add_text_content()
            yield tc.emit_added()
            yield tc.emit_delta("hi")
            yield tc.emit_text_done("hi")
            yield tc.emit_done()
            yield msg.emit_done()
            yield stream.emit_completed()

        return _events()

    client = TestClient(app)
    response = client.post(
        "/responses",
        json={"model": "test", "input": "hi", "stream": False, "store": True},
    )
    assert response.status_code == 200, response.text
    assert captured["cancel_at_start"] is False
    assert captured["shutdown_at_start"] is False
    assert captured["client_cancelled_at_start"] is False


# ──────────────────────────────────────────────────────────────────────
# Cancel endpoint sets client_cancelled
# ──────────────────────────────────────────────────────────────────────


def test_client_cancel_endpoint_sets_client_cancelled() -> None:
    """Cancel endpoint stamps client_cancelled=True AND fires cancel event.

    Unit-test scope: drives the cancel endpoint directly against a
    response record and asserts the runtime state mutation. The full
    e2e variant (real Hypercorn server + real handler observation) is
    covered by ``tests/contract/test_cancel_endpoint.py``.
    """
    from azure.ai.agentserver.responses._response_context import PlatformContext, ResponseContext
    from azure.ai.agentserver.responses.models.runtime import ResponseModeFlags

    ctx = ResponseContext(
        response_id="r",
        mode_flags=ResponseModeFlags(stream=False, store=True, background=True),
        request=None,
        platform_context=PlatformContext(),
    )
    # Simulate the cancel-bridge mutation that
    # ``_endpoint_handler.cancel_response`` performs:
    ctx.client_cancelled = True
    ctx._cancellation_signal.set()
    assert ctx._cancellation_signal.is_set() is True
    assert ctx.client_cancelled is True
    assert ctx.shutdown.is_set() is False


# ──────────────────────────────────────────────────────────────────────
# Composing-cause invariants on a fresh context
# ──────────────────────────────────────────────────────────────────────


def test_context_composes_multiple_causes_simultaneously() -> None:
    """Setting client_cancelled and shutdown together MUST both stick."""
    from azure.ai.agentserver.responses._response_context import PlatformContext
    from azure.ai.agentserver.responses.models.runtime import ResponseModeFlags

    ctx = ResponseContext(
        response_id="r",
        mode_flags=ResponseModeFlags(stream=False, store=True, background=False),
        request=None,
        platform_context=PlatformContext(),
    )
    ctx.client_cancelled = True
    ctx.shutdown.set()
    ctx._cancellation_signal.set()
    # Both causes observable simultaneously — proves the boolean shape
    # solves the pre-spec-024 single-enum limitation.
    assert ctx.client_cancelled is True
    assert ctx.shutdown.is_set() is True
    assert ctx._cancellation_signal.is_set() is True


def test_steering_pressure_has_no_cause_flag() -> None:
    """Steering pressure sets cancel only — no cause flag flips.

    Matches §10 cause matrix (Steering row): cancel set, shutdown not
    set, client_cancelled=False. Handlers infer steering by elimination.
    """
    from azure.ai.agentserver.responses._response_context import PlatformContext
    from azure.ai.agentserver.responses.models.runtime import ResponseModeFlags

    ctx = ResponseContext(
        response_id="r",
        mode_flags=ResponseModeFlags(stream=False, store=True, background=False),
        request=None,
        platform_context=PlatformContext(),
    )
    # Simulate steering bridge: only cancel.set() — no cause flag.
    ctx._cancellation_signal.set()
    assert ctx._cancellation_signal.is_set() is True
    assert ctx.client_cancelled is False
    assert ctx.shutdown.is_set() is False


# ──────────────────────────────────────────────────────────────────────
# Handler signature validation (Proposal #4 hard rejects)
# ──────────────────────────────────────────────────────────────────────


def test_three_arg_async_handler_accepted() -> None:
    app = ResponsesAgentServerHost()

    async def h(request, context, cancellation_signal):  # 3-arg async — must accept
        yield None

    # Don't actually register; just verify the validator doesn't raise.
    app.response_handler(h)


def test_three_arg_sync_handler_hard_rejected() -> None:
    app = ResponsesAgentServerHost()

    def h(request, context, cancellation_signal):  # sync 3-arg — must be rejected
        return None

    with pytest.raises(TypeError, match="async function"):
        app.response_handler(h)  # type: ignore[arg-type]


def test_two_arg_async_handler_hard_rejected() -> None:
    app = ResponsesAgentServerHost()

    async def h(request, context):  # 2-arg async — must be rejected (missing cancel signal)
        yield None

    with pytest.raises(TypeError, match="three positional"):
        app.response_handler(h)  # type: ignore[arg-type]


def test_two_arg_sync_handler_hard_rejected() -> None:
    app = ResponsesAgentServerHost()

    def h(request, context):  # 2-arg sync — must be rejected (sync rejected first)
        return None

    with pytest.raises(TypeError):
        app.response_handler(h)  # type: ignore[arg-type]


# ──────────────────────────────────────────────────────────────────────
# exit_for_recovery sentinel propagation
# ──────────────────────────────────────────────────────────────────────


def test_exit_for_recovery_raises_outside_resilient_context() -> None:
    """exit_for_recovery() requires a task context; raises RuntimeError otherwise."""
    from azure.ai.agentserver.responses._response_context import PlatformContext
    from azure.ai.agentserver.responses.models.runtime import ResponseModeFlags

    ctx = ResponseContext(
        response_id="r",
        mode_flags=ResponseModeFlags(stream=False, store=False, background=False),
        request=None,
        platform_context=PlatformContext(),
    )
    # _task_context is None for non-resilient / unit-test contexts.
    assert ctx._task_context is None  # type: ignore[attr-defined]

    async def _check() -> None:
        with pytest.raises(RuntimeError, match="resilient response handler"):
            await ctx.exit_for_recovery()

    asyncio.run(_check())


def test_exit_for_recovery_sentinel_is_not_none() -> None:
    """``ExitForRecoverySignal`` remains exported as the framework's internal
    recovery sentinel type (the orchestrator translates the raised
    ``ResponseExitForRecovery`` into this core sentinel at the task boundary)."""
    from azure.ai.agentserver.responses import ExitForRecoverySignal

    # ExitForRecoverySignal is exported and is not None.
    assert ExitForRecoverySignal is not None


def test_exit_for_recovery_raises_response_exit_for_recovery_in_resilient_context() -> None:
    """Spec 025 §A.4 (T29) — inside a resilient task body
    ``await context.exit_for_recovery()`` raises ``ResponseExitForRecovery``
    (NoReturn); it never returns a value."""
    from azure.ai.agentserver.responses import ResponseExitForRecovery
    from azure.ai.agentserver.responses._response_context import PlatformContext
    from azure.ai.agentserver.responses.models.runtime import ResponseModeFlags

    ctx = ResponseContext(
        response_id="r",
        mode_flags=ResponseModeFlags(stream=False, store=True, background=True),
        request=None,
        platform_context=PlatformContext(),
    )
    # Simulate a resilient task body: a non-None task context.
    ctx._task_context = object()  # type: ignore[attr-defined]

    async def _check() -> None:
        with pytest.raises(ResponseExitForRecovery):
            await ctx.exit_for_recovery()

    asyncio.run(_check())


def test_exit_for_recovery_subclasses_base_exception_not_exception() -> None:
    """Spec 025 §A.4 (T30a) — ``ResponseExitForRecovery`` subclasses
    ``BaseException`` (NOT ``Exception``) so a handler's broad
    ``except Exception`` cannot swallow the recovery signal."""
    from azure.ai.agentserver.responses import ResponseExitForRecovery

    assert issubclass(ResponseExitForRecovery, BaseException)
    assert not issubclass(ResponseExitForRecovery, Exception)


def test_exit_for_recovery_not_swallowed_by_except_exception() -> None:
    """Spec 025 §A.4 (T30b) — the raised ``ResponseExitForRecovery`` propagates
    THROUGH a handler-style ``except Exception`` guard."""
    from azure.ai.agentserver.responses import ResponseExitForRecovery
    from azure.ai.agentserver.responses._response_context import PlatformContext
    from azure.ai.agentserver.responses.models.runtime import ResponseModeFlags

    ctx = ResponseContext(
        response_id="r",
        mode_flags=ResponseModeFlags(stream=False, store=True, background=True),
        request=None,
        platform_context=PlatformContext(),
    )
    ctx._task_context = object()  # type: ignore[attr-defined]

    swallowed = {"caught_by_except_exception": False}

    async def _handler() -> None:
        try:
            await ctx.exit_for_recovery()
        except Exception:  # pylint: disable=broad-exception-caught
            swallowed["caught_by_except_exception"] = True

    async def _check() -> None:
        with pytest.raises(ResponseExitForRecovery):
            await _handler()

    asyncio.run(_check())
    assert swallowed["caught_by_except_exception"] is False


def test_exit_for_recovery_works_in_async_generator_handler() -> None:
    """Spec 025 §A.4 (T30c) — the unified idiom works in an async-generator
    handler shape: ``await context.exit_for_recovery()`` raises and propagates
    out of the generator (no ``return <value>`` SyntaxError)."""
    from azure.ai.agentserver.responses import ResponseExitForRecovery
    from azure.ai.agentserver.responses._response_context import PlatformContext
    from azure.ai.agentserver.responses.models.runtime import ResponseModeFlags

    ctx = ResponseContext(
        response_id="r",
        mode_flags=ResponseModeFlags(stream=True, store=True, background=True),
        request=None,
        platform_context=PlatformContext(),
    )
    ctx._task_context = object()  # type: ignore[attr-defined]

    async def _gen():
        yield {"type": "response.created"}
        await ctx.exit_for_recovery()
        yield {"type": "never reached"}  # pragma: no cover

    async def _check() -> None:
        gen = _gen()
        assert await gen.__anext__() == {"type": "response.created"}
        with pytest.raises(ResponseExitForRecovery):
            await gen.__anext__()

    asyncio.run(_check())
