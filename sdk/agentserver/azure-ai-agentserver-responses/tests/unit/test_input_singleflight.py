# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Request-local concurrency contracts for input materialization."""

from __future__ import annotations

import asyncio
from typing import Any, cast
from unittest.mock import AsyncMock

import pytest

from azure.ai.agentserver.responses._response_context import PlatformContext, ResponseContext
from azure.ai.agentserver.responses.models import CreateResponse
from azure.ai.agentserver.responses.models.runtime import ResponseModeFlags


def _message(item_id: str, text: str = "resolved") -> dict[str, Any]:
    return {"id": item_id, "type": "message", "role": "user", "content": [{"type": "input_text", "text": text}]}


def _context(provider: Any, *, identity: PlatformContext | None = None) -> ResponseContext:
    return ResponseContext(
        response_id="resp_singleflight",
        mode_flags=ResponseModeFlags(stream=True, store=True, background=False),
        request=cast(CreateResponse, {"input": [{"type": "item_reference", "id": "item_ref"}]}),
        provider=provider,
        platform_context=identity,
    )


class _ControlledProvider:
    def __init__(self) -> None:
        self.started = asyncio.Event()
        self.release = asyncio.Event()
        self.get_items = AsyncMock(side_effect=self._read)

    async def _read(self, item_ids: list[str], *, context: PlatformContext) -> list[dict[str, Any]]:
        self.started.set()
        await self.release.wait()
        return [_message(item_id) for item_id in item_ids]


@pytest.mark.asyncio
async def test_concurrent_public_readers_and_persistence_share_one_batch() -> None:
    provider = _ControlledProvider()
    ctx = _context(provider)
    first = asyncio.create_task(ctx.get_input_items())
    await asyncio.wait_for(provider.started.wait(), 5)
    text = asyncio.create_task(ctx.get_input_text())
    persisted = asyncio.create_task(ctx._get_input_items_for_persistence())
    try:
        await asyncio.sleep(0)
        assert provider.get_items.await_count == 1
    finally:
        provider.release.set()
        results = await asyncio.gather(first, text, persisted)

    assert len(results[0]) == len(results[2]) == 1
    assert results[1] == "resolved"
    provider.get_items.assert_awaited_once_with(["item_ref"], context=ctx.platform_context)
    assert await ctx.get_input_items() is results[0]


@pytest.mark.asyncio
async def test_cancelled_waiter_does_not_cancel_owner_or_publish_partial_result() -> None:
    provider = _ControlledProvider()
    ctx = _context(provider)
    owner = asyncio.create_task(ctx.get_input_items())
    await asyncio.wait_for(provider.started.wait(), 5)
    waiter = asyncio.create_task(ctx.get_input_items())
    try:
        await asyncio.sleep(0)
        waiter.cancel()
        with pytest.raises(asyncio.CancelledError):
            await waiter
        assert not owner.done()
    finally:
        provider.release.set()
        result = await owner

    assert await ctx.get_input_items() is result
    assert provider.get_items.await_count == 1


@pytest.mark.asyncio
async def test_cancelled_owner_releases_waiter_to_retry() -> None:
    provider = _ControlledProvider()
    ctx = _context(provider)
    owner = asyncio.create_task(ctx.get_input_items())
    await asyncio.wait_for(provider.started.wait(), 5)
    waiter = asyncio.create_task(ctx.get_input_items())
    try:
        await asyncio.sleep(0)
        owner.cancel()
        with pytest.raises(asyncio.CancelledError):
            await owner
    finally:
        provider.release.set()
    result = await asyncio.wait_for(waiter, 5)

    assert len(result) == 1
    assert provider.get_items.await_count == 2
    assert await ctx.get_input_items() is result


@pytest.mark.asyncio
async def test_failed_owner_releases_waiter_to_retry() -> None:
    started = asyncio.Event()
    release = asyncio.Event()

    async def fail(*args: Any, **kwargs: Any) -> None:
        started.set()
        await release.wait()
        raise RuntimeError("storage unavailable")

    provider = AsyncMock()
    provider.get_items.side_effect = fail
    ctx = _context(provider)
    owner = asyncio.create_task(ctx.get_input_items())
    await asyncio.wait_for(started.wait(), 5)
    waiter = asyncio.create_task(ctx.get_input_items())
    try:
        await asyncio.sleep(0)
        provider.get_items.side_effect = None
        provider.get_items.return_value = [_message("item_ref")]
    finally:
        release.set()
    with pytest.raises(RuntimeError, match="storage unavailable"):
        await owner
    result = await asyncio.wait_for(waiter, 5)

    assert len(result) == 1
    assert provider.get_items.await_count == 2
    assert await ctx.get_input_items() is result


@pytest.mark.asyncio
@pytest.mark.parametrize("items", [[], [None]])
async def test_successful_empty_materialization_is_reused(items: list[Any]) -> None:
    provider = AsyncMock()
    provider.get_items.return_value = items
    ctx = _context(provider)

    first, second = await asyncio.gather(ctx.get_input_items(), ctx.get_input_items())

    assert first == second == ()
    provider.get_items.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.parametrize("same_identity", [False, True])
async def test_different_request_contexts_never_share_materialization(same_identity: bool) -> None:
    provider = _ControlledProvider()
    first_identity = PlatformContext(user_id_key="user-a", call_id="call-a")
    second_identity = first_identity if same_identity else PlatformContext(user_id_key="user-b", call_id="call-b")
    first_ctx = _context(provider, identity=first_identity)
    second_ctx = _context(provider, identity=second_identity)
    first = asyncio.create_task(first_ctx.get_input_items())
    second = asyncio.create_task(second_ctx.get_input_items())
    try:
        await asyncio.wait_for(provider.started.wait(), 5)
        await asyncio.sleep(0)
        assert provider.get_items.await_count == 2
    finally:
        provider.release.set()
        results = await asyncio.gather(first, second)

    assert results[0] is not results[1]
    assert provider.get_items.await_args_list[0].kwargs["context"] is first_identity
    assert provider.get_items.await_args_list[1].kwargs["context"] is second_identity


@pytest.mark.asyncio
async def test_unresolved_mode_does_not_wait_for_reference_fetch() -> None:
    provider = _ControlledProvider()
    ctx = _context(provider)
    resolved = asyncio.create_task(ctx.get_input_items())
    await asyncio.wait_for(provider.started.wait(), 5)
    try:
        unresolved = await asyncio.wait_for(ctx.get_input_items(resolve_references=False), 5)
        assert unresolved[0]["type"] == "item_reference"
        assert not resolved.done()
    finally:
        provider.release.set()
        result = await resolved

    assert result[0]["type"] == "message"
    assert provider.get_items.await_count == 1


@pytest.mark.asyncio
async def test_shared_result_preserves_cached_mutation_semantics() -> None:
    provider = AsyncMock()
    provider.get_items.return_value = [_message("item_ref")]
    ctx = _context(provider)
    result = await ctx.get_input_items()
    result[0]["content"][0]["text"] = "handler mutation"  # type: ignore[index]

    assert await ctx.get_input_text() == "handler mutation"
    provider.get_items.assert_awaited_once()


@pytest.mark.asyncio
async def test_order_duplicates_and_missing_reference_behavior_is_unchanged() -> None:
    provider = AsyncMock()
    provider.get_items.return_value = [_message("duplicate"), None, _message("duplicate")]
    ctx = _context(provider)
    ctx.request = cast(
        CreateResponse,
        {
            "input": [
                _message("inline", "inline"),
                {"type": "item_reference", "id": "duplicate"},
                {"type": "item_reference", "id": "missing"},
                {"type": "item_reference", "id": "duplicate"},
            ]
        },
    )

    result, text = await asyncio.gather(ctx.get_input_items(), ctx.get_input_text())

    assert [item["id"] for item in result] == ["inline", "duplicate", "duplicate"]  # type: ignore[typeddict-item]
    assert text == "inline\nresolved\nresolved"
    provider.get_items.assert_awaited_once_with(["duplicate", "missing", "duplicate"], context=ctx.platform_context)
