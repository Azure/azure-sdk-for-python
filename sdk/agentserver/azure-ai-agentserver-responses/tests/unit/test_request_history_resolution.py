# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Exact-query request ownership, storage call counts, and cancellation contracts."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from azure.ai.agentserver.responses import ResponsesServerOptions
from azure.ai.agentserver.responses._response_context import (
    PlatformContext,
    ResponseContext,
    _resolve_history_item_ids,
)
from azure.ai.agentserver.responses.hosting import _orchestrator as orch
from azure.ai.agentserver.responses.hosting._execution_context import _ExecutionContext
from azure.ai.agentserver.responses.hosting._runtime_state import _RuntimeState
from azure.ai.agentserver.responses.models import CreateResponse
from azure.ai.agentserver.responses.models.runtime import ResponseExecution, ResponseModeFlags
from azure.ai.agentserver.responses.store._base import ResponseProviderProtocol
from azure.ai.agentserver.responses.store._foundry_errors import FoundryResourceNotFoundError
from azure.ai.agentserver.responses.streaming import ResponseEventStream


def _provider(ids=None):
    provider = MagicMock(spec=ResponseProviderProtocol)
    provider.get_history_item_ids = AsyncMock(return_value=["history"] if ids is None else ids)
    provider.get_items = AsyncMock(return_value=[{"id": "history"}])
    provider.create_response = AsyncMock()
    provider.update_response = AsyncMock()
    return provider


def _context(provider, prefetched=None, *, conversation=None, previous="previous"):
    return ResponseContext(
        response_id="response",
        mode_flags=ResponseModeFlags(stream=True, store=True, background=False),
        provider=provider,
        input_items=[],
        previous_response_id=previous,
        conversation_id=conversation,
        prefetched_history_ids=prefetched,
        platform_context=PlatformContext(user_id_key="user", call_id="call"),
    )


async def _resolve(owner, provider, *, previous="previous", conversation=None, limit=100, platform=None):
    return await _resolve_history_item_ids(
        provider,
        previous,
        conversation,
        limit,
        context=platform if platform is not None else (owner.platform_context if owner is not None else None),
        request_context=owner,
    )


@pytest.mark.parametrize("ids", [[], ["history"]])
@pytest.mark.parametrize("seeded", [False, True])
async def test_empty_and_nonempty_snapshots_are_reused_and_defensive(ids, seeded):
    ids = list(ids)
    provider = _provider(ids)
    owner = _context(provider, ids if seeded else None)
    first = await _resolve(owner, provider)
    first.append("caller-mutation")
    assert await _resolve(owner, provider) == ids
    (
        provider.get_history_item_ids.assert_not_awaited()
        if seeded
        else provider.get_history_item_ids.assert_awaited_once()
    )
    ids.append("provider-or-prefetch-mutation")
    assert "provider-or-prefetch-mutation" not in await _resolve(owner, provider)


@pytest.mark.parametrize("difference", ["provider", "previous", "conversation", "limit", "user", "call", "no-platform"])
async def test_different_queries_or_identities_do_not_hit(difference):
    provider = _provider()
    owner = _context(provider)
    await _resolve(owner, provider)
    second_provider = _provider() if difference == "provider" else provider
    identity = PlatformContext(
        user_id_key="other" if difference == "user" else "user", call_id="other" if difference == "call" else "call"
    )
    await _resolve_history_item_ids(
        second_provider,
        "other" if difference == "previous" else "previous",
        "conv" if difference == "conversation" else None,
        1 if difference == "limit" else 100,
        context=None if difference == "no-platform" else identity,
        request_context=owner,
    )
    assert provider.get_history_item_ids.await_count == (1 if difference == "provider" else 2)
    if difference == "provider":
        second_provider.get_history_item_ids.assert_awaited_once()
    # A new PlatformContext with equal values is equivalent, not a new caller.
    assert await _resolve(owner, provider, platform=PlatformContext(user_id_key="user", call_id="call")) == ["history"]
    assert provider.get_history_item_ids.await_count == (1 if difference == "provider" else 2)


async def test_absent_and_empty_identity_values_are_distinct():
    provider = _provider()
    owner = _context(provider)
    identities = [
        None,
        PlatformContext(),
        PlatformContext(user_id_key=""),
        PlatformContext(call_id=""),
        PlatformContext(user_id_key="", call_id=""),
    ]
    for identity in identities * 2:
        await _resolve_history_item_ids(provider, "previous", None, 100, context=identity, request_context=owner)
    assert provider.get_history_item_ids.await_count == 5


async def test_no_owner_and_new_request_never_reuse_old_results():
    provider = _provider()
    for owner in (None, None, _context(provider), _context(provider)):
        await _resolve(owner, provider)
    assert provider.get_history_item_ids.await_count == 4


async def test_mutated_identity_during_fetch_does_not_poison_key():
    provider = _provider()
    owner = _context(provider)
    started, release = asyncio.Event(), asyncio.Event()

    async def fetch(*args, context):
        started.set()
        await release.wait()
        return [context.call_id]

    provider.get_history_item_ids.side_effect = fetch
    task = asyncio.create_task(_resolve(owner, provider))
    await started.wait()
    owner.platform_context.call_id = "new-call"
    release.set()
    assert await task == ["call"]
    assert await _resolve(owner, provider) == ["new-call"]
    assert provider.get_history_item_ids.await_count == 2


async def test_concurrent_equal_lookups_single_flight_and_waiter_cancellation():
    provider = _provider()
    owner = _context(provider)
    started, release = asyncio.Event(), asyncio.Event()

    async def fetch(*args, **kwargs):
        started.set()
        await release.wait()
        return ["history"]

    provider.get_history_item_ids.side_effect = fetch
    leader = asyncio.create_task(_resolve(owner, provider))
    await started.wait()
    waiters = [asyncio.create_task(_resolve(owner, provider)) for _ in range(8)]
    await asyncio.sleep(0)
    waiters[0].cancel()
    with pytest.raises(asyncio.CancelledError):
        await waiters.pop(0)
    assert not leader.done()
    release.set()
    assert await asyncio.gather(leader, *waiters) == [["history"]] * 8
    provider.get_history_item_ids.assert_awaited_once()


@pytest.mark.parametrize("failure", ["cancel", "error"])
async def test_failed_or_cancelled_leader_releases_lock_and_is_not_cached(failure):
    provider = _provider()
    owner = _context(provider)
    started, release = asyncio.Event(), asyncio.Event()
    calls = 0

    async def fetch(*args, **kwargs):
        nonlocal calls
        calls += 1
        if calls == 1:
            started.set()
            await release.wait()
            raise FoundryResourceNotFoundError("first lookup failed")
        return ["retried"]

    provider.get_history_item_ids.side_effect = fetch
    leader = asyncio.create_task(_resolve(owner, provider))
    await started.wait()
    waiter = asyncio.create_task(_resolve(owner, provider))
    await asyncio.sleep(0)
    if failure == "cancel":
        leader.cancel()
    else:
        release.set()
    with pytest.raises(asyncio.CancelledError if failure == "cancel" else FoundryResourceNotFoundError):
        await leader
    assert await asyncio.wait_for(waiter, 2) == ["retried"]
    assert await _resolve(owner, provider) == ["retried"]
    assert calls == 2


@pytest.mark.parametrize("difference", ["query", "request"])
async def test_distinct_queries_or_requests_run_concurrently(difference):
    provider = _provider()
    owner = _context(provider)
    both_started, release = asyncio.Event(), asyncio.Event()
    calls = 0

    async def fetch(*args, **kwargs):
        nonlocal calls
        calls += 1
        if calls == 2:
            both_started.set()
        await release.wait()
        return ["history"]

    provider.get_history_item_ids.side_effect = fetch
    tasks = [
        asyncio.create_task(
            _resolve(
                owner if difference == "query" else _context(provider),
                provider,
                limit=limit if difference == "query" else 100,
            )
        )
        for limit in (1, 2)
    ]
    try:
        await asyncio.wait_for(both_started.wait(), 2)
    finally:
        release.set()
        await asyncio.gather(*tasks)
    assert calls == 2


async def test_concurrent_handler_materialization_and_persistence_share_ids():
    provider = _provider()
    owner = _context(provider)
    started, release = asyncio.Event(), asyncio.Event()

    async def fetch(*args, **kwargs):
        started.set()
        await release.wait()
        return ["history"]

    provider.get_history_item_ids.side_effect = fetch
    materialization = asyncio.create_task(owner.get_history())
    await started.wait()
    readers = [asyncio.create_task(owner.get_history()) for _ in range(8)]
    persistence_ids = asyncio.create_task(_resolve(owner, provider))
    release.set()
    histories = await asyncio.gather(materialization, *readers)
    assert await persistence_ids == ["history"]
    assert all(value is histories[0] for value in histories)
    assert await owner.get_history() is histories[0]
    provider.get_history_item_ids.assert_awaited_once()
    provider.get_items.assert_awaited_once()
    # Arbitrary item batches are not covered by the history cache.
    await provider.get_items(["other"])
    await provider.get_items(["other"])
    assert provider.get_items.await_count == 3


@pytest.mark.parametrize("failure", ["cancel", "error"])
async def test_materialization_failure_retries_without_refetching_successful_ids(failure):
    provider = _provider()
    owner = _context(provider)
    started, release = asyncio.Event(), asyncio.Event()
    calls = 0

    async def items(*args, **kwargs):
        nonlocal calls
        calls += 1
        if calls == 1:
            started.set()
            await release.wait()
            raise RuntimeError("item retrieval failed")
        return [{"id": "history"}]

    provider.get_items.side_effect = items
    leader = asyncio.create_task(owner.get_history())
    await started.wait()
    waiter = asyncio.create_task(owner.get_history())
    if failure == "cancel":
        leader.cancel()
    else:
        release.set()
    with pytest.raises(asyncio.CancelledError if failure == "cancel" else RuntimeError):
        await leader
    assert await asyncio.wait_for(waiter, 2) == ({"id": "history"},)
    provider.get_history_item_ids.assert_awaited_once()
    assert provider.get_items.await_count == 2


@pytest.mark.parametrize("difference", ["provider", "previous", "conversation", "limit", "user", "call"])
async def test_materialized_cache_respects_query_changes(difference):
    provider = _provider()
    owner = _context(provider)
    await owner.get_history()
    if difference == "provider":
        owner._provider = _provider()
    elif difference == "previous":
        owner._previous_response_id = "new-previous"
    elif difference == "conversation":
        owner.conversation_id = "new-conversation"
    elif difference == "limit":
        owner._history_limit = 1
    elif difference == "user":
        owner.platform_context.user_id_key = ""
    else:
        owner.platform_context.call_id = ""
    await owner.get_history()
    assert provider.get_history_item_ids.await_count == (1 if difference == "provider" else 2)
    assert owner._provider.get_items.await_count == (1 if difference == "provider" else 2)


@pytest.mark.parametrize("path", ["bg-created", "bg-terminal", "stream-created", "stream-terminal", "sync"])
@pytest.mark.parametrize("prefetched", [None, [], ["history"]])
@pytest.mark.parametrize("with_owner", [False, True])
@pytest.mark.parametrize("handler_first", [False, True])
async def test_all_persistence_callsites_use_exact_request_resolver(
    monkeypatch, path, prefetched, with_owner, handler_first
):
    provider = _provider()
    owner = _context(provider, prefetched) if with_owner else None
    if owner is not None and handler_first:
        await owner.get_history()
    options = ResponsesServerOptions(resilient_background=False)

    async def handler(request, context, cancellation_signal):
        stream = ResponseEventStream(response_id="response", model="m")
        yield stream.emit_created()
        yield stream.emit_completed()

    obj = orch._ResponseOrchestrator(
        create_fn=handler,
        runtime_state=_RuntimeState(),
        runtime_options=options,
        provider=provider,
    )
    obj._safe_emit = AsyncMock()
    subject = MagicMock(last_cursor=AsyncMock(return_value=None))
    monkeypatch.setattr(orch.streams, "get_or_create", AsyncMock(return_value=subject))
    background = path.startswith("bg-")
    ctx = _ExecutionContext(
        response_id="response",
        agent_reference={},
        model="m",
        store=True,
        background=background,
        stream=path != "sync",
        input_items=[],
        previous_response_id="previous",
        conversation_id=None,
        cancellation_signal=asyncio.Event(),
        span=MagicMock(),
        parsed=CreateResponse(model="m", input="hi"),
        context=owner,
        prefetched_history_ids=prefetched,
    )
    stream = ResponseEventStream(response_id="response", model="m")
    first, terminal = stream.emit_created(), stream.emit_completed()
    state = orch._PipelineState()
    state.handler_events.extend([first, terminal])
    state.pending_terminal = terminal
    record = ResponseExecution(
        response_id="response",
        mode_flags=ResponseModeFlags(stream=ctx.stream, store=True, background=background),
        status="in_progress",
        previous_response_id="previous",
        input_items=[],
        response_context=owner,
    )
    snapshot = orch._extract_response_snapshot_from_events(
        state.handler_events,
        response_id="response",
        agent_reference={},
        model="m",
    )
    record.set_response_snapshot(snapshot)
    if path == "bg-created":
        assert await orch._bg_persist_at_created(
            record,
            store=True,
            provider=provider,
            context=owner,
            response_id="response",
            history_limit=100,
            initial_snapshot=snapshot,
        )
    elif path == "bg-terminal":
        await orch._bg_persist_terminal(
            record,
            store=True,
            provider=provider,
            context=owner,
            response_id="response",
            history_limit=100,
            exit_for_recovery=False,
            provider_created=False,
            agent_reference={},
            model="m",
        )
    elif path == "stream-created":
        await obj._register_bg_execution(ctx, state, first)
    elif path == "stream-terminal":
        await obj._persist_and_resolve_terminal(ctx, state, record)
    else:
        await obj._run_sync_inner(ctx, orch._PipelineState())
    provider.create_response.assert_awaited_once()
    expected = prefetched if with_owner and prefetched is not None else ["history"]
    assert provider.create_response.await_args.args[2] == expected
    assert provider.get_history_item_ids.await_count == (0 if with_owner and prefetched is not None else 1)
    if with_owner:
        # Persistence's fallback lookup is now also shared with subsequent handler reads.
        assert await _resolve(owner, provider) == expected
        await owner.get_history()
        await owner.get_history()
        assert provider.get_history_item_ids.await_count == (0 if prefetched is not None else 1)
        assert provider.get_items.await_count == (1 if expected else 0)


@pytest.mark.parametrize("mode", ["fresh", "resumed", "recovered"])
async def test_task_handoff_keeps_fresh_cache_but_resets_recovered_lifetime(monkeypatch, mode):
    from azure.ai.agentserver.responses.hosting import _resilient_orchestrator as resilient
    from azure.ai.agentserver.responses.hosting._resilient_input import ResilientResponseInput, RuntimeRefs

    provider = _provider()
    owner = _context(provider, ["history"])
    initial = await owner.get_history()
    provider.get_items.return_value = [{"id": "new-lifetime"}]
    obj = resilient.ResilientResponseOrchestrator(
        create_fn=AsyncMock(),
        options=ResponsesServerOptions(),
        provider=provider,
        runtime_state=_RuntimeState(),
    )
    parsed = CreateResponse(model="m", input="hi", previous_response_id="previous", store=True, background=True)
    params = ResilientResponseInput(
        request=parsed,
        response_id="response",
        disposition="re-invoke",
        user_id_key="user",
        call_id="call",
    ).to_task_input()
    assert "history" not in str(params)
    monkeypatch.setitem(
        resilient._RUNTIME_REFS,
        "response",
        RuntimeRefs(record=MagicMock(), context=owner, parsed=parsed, cancel=asyncio.Event()),
    )
    seen = []

    async def run(task_context, record, context, **kwargs):
        seen.append(await context.get_history())

    monkeypatch.setattr(obj, "_run_handler_in_task", run)
    monkeypatch.setattr(obj, "_setup_cancel_bridge", MagicMock(return_value=None))
    task_context = MagicMock(
        input=params,
        entry_mode=mode,
        is_steered_turn=False,
        pending_input_count=0,
        cancel=asyncio.Event(),
        shutdown=asyncio.Event(),
    )
    await obj._execute_in_task(task_context)
    assert len(seen) == 1
    if mode == "recovered":
        assert seen[0] == ({"id": "new-lifetime"},)
        provider.get_history_item_ids.assert_awaited_once()
        assert provider.get_items.await_count == 2
    else:
        assert seen[0] is initial
        provider.get_history_item_ids.assert_not_awaited()
        provider.get_items.assert_awaited_once()


async def test_reconstruction_from_serialized_input_never_reuses_previous_lifetime_ids():
    from azure.ai.agentserver.responses.hosting._resilient_orchestrator import _reconstruct_from_params
    from azure.ai.agentserver.responses.hosting._resilient_input import ResilientResponseInput

    provider = _provider()
    params = ResilientResponseInput(
        request=CreateResponse(model="m", input="hi", previous_response_id="previous"),
        response_id="response",
        disposition="re-invoke",
        user_id_key="user",
        call_id="call",
    ).to_task_input()
    for _ in range(2):
        _, owner = _reconstruct_from_params(
            params=params,
            response_id="response",
            provider=provider,
            runtime_state=_RuntimeState(),
            runtime_options=ResponsesServerOptions(),
        )
        await owner.get_history()
        assert await _resolve(owner, provider) == ["history"]
    assert provider.get_history_item_ids.await_count == 2
    assert provider.get_items.await_count == 2
