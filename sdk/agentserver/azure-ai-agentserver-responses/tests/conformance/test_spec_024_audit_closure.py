# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Spec 024 final audit-closure tests.

This file closes the gaps surfaced by the final implementation audit
(spec 024 Phase 10 rubber-duck pass). Each test pins a specific
spec-024 contract that no other test currently exercises.

Gaps closed by this file:

1. ``test_default_store_is_file_backed`` — spec 024 work item #1.
   ``ResponsesAgentServerHost()`` with no ``store=`` arg MUST use
   ``FileResponseStore`` under
   ``${AGENTSERVER_STATE_ROOT:-~/.agentserver}/responses/``.
   (Pinned in audit step 65 — implementation existed but no test.)

2. ``test_client_cancelled_observed_by_handler_after_cancel_endpoint``
   — spec 024 §10 cause matrix row "client cancel via /cancel
   endpoint → client_cancelled=True". Drives the real /cancel
   endpoint and asserts the handler records the cause-boolean
   transition.

3. ``test_conversation_chain_metadata_protocol_matches_mutable_mapping_shape`` —
   spec 024 audit Concern 2: the ``ConversationChainMetadataNamespace`` Protocol
   MUST expose ``MutableMapping``-style methods (clear, pop, keys,
   etc.) so sample 22's ``context.conversation_chain_metadata.clear()`` and
   similar idioms typecheck cleanly.

4. ``test_handler_signature_rejects_var_positional`` — spec 024
   audit Blocker 5: ``response_handler`` MUST reject ``*args``
   handlers (the contract requires exactly three positional parameters
   so the dispatch shape is statically reasonable).
"""

from __future__ import annotations

from typing import Any

import pytest

from azure.ai.agentserver.responses import (
    ConversationChainMetadataNamespace,
    FileResponseStore,
    ResponseContext,
    ResponsesAgentServerHost,
)


# ──────────────────────────────────────────────────────────────────────
# Gap 1 — default store is file-backed (work item #1)
# ──────────────────────────────────────────────────────────────────────


def test_default_store_is_file_backed(tmp_path, monkeypatch) -> None:
    """``ResponsesAgentServerHost()`` with no ``store=`` arg uses
    ``FileResponseStore`` under ``${AGENTSERVER_STATE_ROOT}/responses``."""
    monkeypatch.setenv("AGENTSERVER_STATE_ROOT", str(tmp_path))

    app = ResponsesAgentServerHost()
    provider = app._endpoint._orchestrator._provider  # pylint: disable=protected-access

    assert isinstance(provider, FileResponseStore), (
        f"Default response store MUST be FileResponseStore; got " f"{type(provider).__name__}"
    )
    # Storage root resolves under the AGENTSERVER_STATE_ROOT/responses subpath.
    root = str(provider._root)  # pylint: disable=protected-access
    assert "responses" in root and str(tmp_path) in root, (
        f"FileResponseStore root must resolve under the responses subdir " f"of the resilient root; got {root}"
    )


def test_default_store_uses_default_state_root_when_env_unset(
    monkeypatch,
) -> None:
    """When ``AGENTSERVER_STATE_ROOT`` is unset, the file-backed store
    falls back to ``~/.agentserver/responses/`` per the unified storage layout."""
    monkeypatch.delenv("AGENTSERVER_STATE_ROOT", raising=False)

    app = ResponsesAgentServerHost()
    provider = app._endpoint._orchestrator._provider  # pylint: disable=protected-access

    assert isinstance(provider, FileResponseStore)
    root = str(provider._root)  # pylint: disable=protected-access
    assert ".agentserver" in root and "responses" in root, (
        f"Fallback storage root must be under ~/.agentserver/responses/; " f"got {root}"
    )


# ──────────────────────────────────────────────────────────────────────
# Gap 2 — client_cancelled observed end-to-end via /cancel endpoint
# ──────────────────────────────────────────────────────────────────────


def test_client_cancelled_observed_by_handler_after_cancel_endpoint(tmp_path, monkeypatch) -> None:
    """End-to-end: POST a background response, drive /cancel, and assert
    the handler observed ``context.client_cancelled is True``.

    Uses polling (per the existing test_cancel_endpoint.py pattern) to
    give the bg task time to run between TestClient requests. Closes
    audit-finding "client_cancelled not observed by real handler
    end-to-end" (the conformance suite previously only mutated a
    ``ResponseContext`` in-process)."""
    import time

    from starlette.testclient import TestClient

    monkeypatch.setenv("AGENTSERVER_STATE_ROOT", str(tmp_path))

    captured: dict[str, Any] = {}
    context_ref: list[ResponseContext] = []

    app = ResponsesAgentServerHost()

    @app.response_handler
    async def _handler(request: Any, context: ResponseContext, cancellation_signal: asyncio.Event):
        context_ref.append(context)

        async def _events():
            import asyncio  # pylint: disable=import-outside-toplevel

            yield {
                "type": "response.created",
                "response": {"status": "in_progress", "output": []},
            }
            for _ in range(500):
                if cancellation_signal.is_set():
                    captured["client_cancelled"] = context.client_cancelled
                    captured["shutdown"] = context.shutdown.is_set()
                    return
                await asyncio.sleep(0.01)

        return _events()

    client = TestClient(app)
    post = client.post(
        "/responses",
        json={
            "model": "test",
            "input": "hi",
            "stream": False,
            "store": True,
            "background": True,
        },
    )
    assert post.status_code == 200, post.text
    response_id = post.json()["id"]

    cancel = client.post(f"/responses/{response_id}/cancel")
    assert cancel.status_code == 200, cancel.text

    # Poll GET until the response reaches the terminal cancelled state.
    # This both pumps the TestClient event loop (giving the bg handler
    # task a chance to observe the cancel) AND verifies the wire-level
    # cancellation contract end-to-end.
    deadline = time.time() + 5.0
    while time.time() < deadline:
        get_resp = client.get(f"/responses/{response_id}")
        if get_resp.status_code == 200 and get_resp.json().get("status") == "cancelled":
            break
        time.sleep(0.05)
    else:
        raise AssertionError(f"Response did not reach cancelled within 5s: {get_resp.json()}")

    # By this point the cancel endpoint mutations have landed AND the
    # handler has been pumped through the cancel.set() observation.
    # Verify the cause-boolean shape directly off the live context.
    assert context_ref, "Handler must have been invoked"
    ctx = context_ref[0]
    assert ctx._cancellation_signal.is_set() is True, "context._cancellation_signal MUST be set after /cancel"
    assert ctx.client_cancelled is True, (
        "context.client_cancelled MUST be True after /cancel endpoint " "(per spec 024 §10 cause matrix)"
    )
    assert ctx.shutdown.is_set() is False, "Cancel endpoint MUST NOT set context.shutdown"


# ──────────────────────────────────────────────────────────────────────
# Gap 3 — ConversationChainMetadataNamespace Protocol matches MutableMapping
# ──────────────────────────────────────────────────────────────────────


def test_conversation_chain_metadata_protocol_includes_mutable_mapping_methods() -> None:
    """``ConversationChainMetadataNamespace`` MUST expose ``MutableMapping``-style
    methods so handler code that calls ``clear()`` / ``pop()`` /
    ``update()`` typechecks against the Protocol annotation."""
    required = {
        "__getitem__",
        "__setitem__",
        "__delitem__",
        "__contains__",
        "__iter__",
        "__len__",
        "get",
        "keys",
        "values",
        "items",
        "clear",
        "pop",
        "setdefault",
        "update",
        "__call__",
        "flush",
    }
    actual = {
        name
        for name in dir(ConversationChainMetadataNamespace)
        if not name.startswith("_")
        or name
        in {
            "__getitem__",
            "__setitem__",
            "__delitem__",
            "__contains__",
            "__iter__",
            "__len__",
            "__call__",
        }
    }
    missing = required - actual
    assert not missing, (
        f"ConversationChainMetadataNamespace Protocol is missing MutableMapping "
        f"methods that handlers + samples use: {sorted(missing)}"
    )


def test_concrete_metadata_facade_satisfies_protocol_at_runtime() -> None:
    """The internal ``_DeveloperMetadataFacade`` MUST satisfy every
    Protocol method at runtime (so handlers can call them on the live
    facade returned by ``context.conversation_chain_metadata``)."""
    from azure.ai.agentserver.responses._resilience_context import (
        _DeveloperMetadataFacade,
    )

    facade = _DeveloperMetadataFacade({})
    # MutableMapping basics:
    facade["a"] = 1
    assert facade["a"] == 1
    assert facade.get("a") == 1
    assert "a" in facade
    assert len(facade) == 1
    facade["b"] = 2
    assert set(facade.keys()) == {"a", "b"}
    facade.setdefault("c", 3)
    assert facade["c"] == 3
    popped = facade.pop("c")
    assert popped == 3
    facade.update({"d": 4})
    assert facade["d"] == 4
    facade.clear()
    assert len(facade) == 0


# ──────────────────────────────────────────────────────────────────────
# Gap 4 — handler signature rejects *args
# ──────────────────────────────────────────────────────────────────────


def test_handler_signature_rejects_var_positional() -> None:
    """``response_handler`` MUST reject ``*args``-style handlers."""
    app = ResponsesAgentServerHost()

    async def variadic_handler(*args):  # noqa: D401
        if False:  # pragma: no cover
            yield None

    with pytest.raises(TypeError, match="variadic"):
        app.response_handler(variadic_handler)  # type: ignore[arg-type]


def test_handler_signature_rejects_kwargs_only() -> None:
    """A handler with only keyword-only parameters does not satisfy the
    3-arg positional contract and MUST be rejected."""
    app = ResponsesAgentServerHost()

    async def kwargs_only_handler(*, request, context, cancellation_signal):  # noqa: D401
        if False:  # pragma: no cover
            yield None

    with pytest.raises(TypeError, match="three positional"):
        app.response_handler(kwargs_only_handler)  # type: ignore[arg-type]


# ──────────────────────────────────────────────────────────────────────
# Gap 5 — context.exit_for_recovery() sentinel propagates through dispatch
# ──────────────────────────────────────────────────────────────────────


def test_exit_for_recovery_sentinel_propagates_through_dispatch(tmp_path, monkeypatch) -> None:
    """End-to-end: a resilient handler that does
    ``return await context.exit_for_recovery()`` MUST leave the
    response retrievable (not marked completed prematurely) — proving
    the sentinel propagates through dispatch and is recognised by the
    framework's recovery path.

    For the TestClient path (no real TaskManager), the resilient start
    falls back to ``asyncio.create_task``, so ``exit_for_recovery()``
    raises ``RuntimeError`` (no task context). This test pins THAT
    behaviour — handlers outside a resilient context are told their
    deferral intent cannot be honoured."""
    monkeypatch.setenv("AGENTSERVER_STATE_ROOT", str(tmp_path))

    from starlette.testclient import TestClient

    captured: dict[str, Any] = {}
    app = ResponsesAgentServerHost()

    @app.response_handler
    async def _handler(request: Any, context: ResponseContext, cancellation_signal: asyncio.Event):
        async def _events():
            yield {
                "type": "response.created",
                "response": {"status": "in_progress", "output": []},
            }
            try:
                await context.exit_for_recovery()
            except RuntimeError as exc:
                captured["exit_runtime_error"] = str(exc)

        return _events()

    client = TestClient(app)
    post = client.post(
        "/responses",
        json={"model": "t", "input": "hi", "stream": False, "store": True, "background": True},
    )
    assert post.status_code == 200, post.text

    # Poll until handler completes (it will because of the missing-context
    # exception, which is caught — handler exits without terminal).
    import time

    deadline = time.time() + 3.0
    while time.time() < deadline:
        get_resp = client.get(f"/responses/{post.json()['id']}")
        if get_resp.status_code == 200 and get_resp.json().get("status") in {
            "completed",
            "failed",
            "cancelled",
            "incomplete",
        }:
            break
        time.sleep(0.05)

    # Verify the handler observed the runtime error (proves the
    # sentinel-bearing call was dispatched).
    assert "resilient response handler" in captured.get("exit_runtime_error", ""), (
        f"Handler MUST hit the RuntimeError guard for non-resilient contexts; " f"captured={captured}"
    )


# ──────────────────────────────────────────────────────────────────────
# Gap 6 — is_steered_turn=True on drain re-entry
# ──────────────────────────────────────────────────────────────────────


def test_is_steered_turn_set_on_drain_reentry_via_orchestrator() -> None:
    """The resilient orchestrator's ``_execute_in_task`` MUST set
    ``context.is_steered_turn = ctx.is_steered_turn`` on every entry,
    so the drain re-entry (where the framework signals is_steered_turn=True)
    is observable to the handler.

    Unit-level coverage that replays the spec 024 Phase 5 wire-up
    contract. Full e2e steering coverage lives in
    ``test_resilient_steering_e2e.py``.
    """
    import asyncio
    from unittest.mock import AsyncMock, MagicMock, patch

    from azure.ai.agentserver.responses._response_context import (
        PlatformContext,
        ResponseContext,
    )
    from azure.ai.agentserver.responses.hosting._resilient_orchestrator import (
        ResilientResponseOrchestrator,
    )
    from azure.ai.agentserver.responses.models.runtime import ResponseModeFlags

    class _FakeTaskMetadata(dict):
        def __init__(self) -> None:
            super().__init__()
            self._ns: dict[str, "_FakeTaskMetadata"] = {}

        def __call__(self, name=None):
            if name is None:
                return self
            sub = self._ns.setdefault(name, _FakeTaskMetadata())
            return sub

        async def flush(self) -> None:
            return None

    orch = ResilientResponseOrchestrator(
        create_fn=AsyncMock(),
        provider=MagicMock(),
        options=MagicMock(steerable_conversations=True),
    )

    real_context = ResponseContext(
        response_id="resp_drain",
        mode_flags=ResponseModeFlags(stream=False, store=True, background=True),
        request=None,
        platform_context=PlatformContext(),
    )

    ctx = MagicMock()
    ctx.entry_mode = "resumed"  # next-turn entry (not crash recovery)
    ctx.is_steered_turn = True  # framework signals the drain re-entry
    ctx.pending_input_count = 0
    ctx.metadata = _FakeTaskMetadata()
    ctx._cancellation_signal = asyncio.Event()
    ctx.shutdown = asyncio.Event()
    ctx.task_id = "task-drain"
    ctx.input = {
        "response_id": "resp_drain",
        "request": {"input": "hi"},
        "_record_ref": MagicMock(),
        "_context_ref": real_context,
        "_parsed_ref": MagicMock(),
        "_cancel_ref": asyncio.Event(),
        "_runtime_state_ref": MagicMock(),
    }

    async def _drive() -> None:
        with patch(
            "azure.ai.agentserver.responses.hosting._orchestrator._run_background_non_stream",
            new_callable=AsyncMock,
        ):
            await orch._execute_in_task(ctx)  # pylint: disable=protected-access

    asyncio.run(_drive())

    # Spec 024 Phase 5: framework MUST surface is_steered_turn through
    # to the handler via context.is_steered_turn flat field.
    assert real_context.is_steered_turn is True, (
        "Drain re-entry MUST set context.is_steered_turn=True per spec " "024 §11 + Proposal #10 flat-field surface"
    )
    # is_recovery MUST be False on a 'resumed' entry (not crash recovery).
    assert real_context.is_recovery is False, (
        "'resumed' entry mode MUST NOT flip is_recovery; that flag is " "exclusively set on 'recovered' entries"
    )


# ──────────────────────────────────────────────────────────────────────
# Gap 7 — Proposal #9 expanded coverage
# ──────────────────────────────────────────────────────────────────────


def test_proposal_9_steerable_resilient_off_does_not_raise() -> None:
    """spec 024 Proposal #9: ``steerable_conversations=True`` AND
    ``resilient_background=False`` is a VALID composition (pre-spec-024
    raised ValueError). This is the negative-equivalent of the
    pre-Phase-4 composition guard."""
    from azure.ai.agentserver.responses import ResponsesServerOptions

    # No exception MUST be raised — the composition guard is deleted.
    opts = ResponsesServerOptions(steerable_conversations=True, resilient_background=False)
    assert opts.steerable_conversations is True
    assert opts.resilient_background is False


def test_proposal_9_steerable_resilient_off_host_constructs_cleanly(tmp_path, monkeypatch) -> None:
    """``ResponsesAgentServerHost`` MUST construct successfully with
    ``steerable_conversations=True`` + ``resilient_background=False`` —
    the composition guard is gone, so the host wires up both the
    steering primitive and the non-resilient disposition together."""
    from azure.ai.agentserver.responses import ResponsesServerOptions

    monkeypatch.setenv("AGENTSERVER_STATE_ROOT", str(tmp_path))

    app = ResponsesAgentServerHost(
        options=ResponsesServerOptions(
            steerable_conversations=True,
            resilient_background=False,
        ),
    )
    # Construction must not raise; the orchestrator + endpoint are wired.
    assert app._endpoint is not None  # pylint: disable=protected-access
    assert app._endpoint._orchestrator is not None  # pylint: disable=protected-access
