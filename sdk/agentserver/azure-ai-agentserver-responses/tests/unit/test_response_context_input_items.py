# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Unit tests for ResponseContext.get_input_items() item-reference resolution."""

from __future__ import annotations

from typing import Any, cast
from unittest.mock import AsyncMock

import pytest

from azure.ai.agentserver.responses._response_context import PlatformContext, ResponseContext
from azure.ai.agentserver.responses.models import (
    CreateResponse,
    Item,
    ItemMessage,
    ItemReferenceParam,
    MessageContentInputTextContent,
    OutputItemMessage,
)
from azure.ai.agentserver.responses.models._helpers import to_item, to_output_item
from azure.ai.agentserver.responses.models.runtime import ResponseModeFlags


def _mode_flags() -> ResponseModeFlags:
    return ResponseModeFlags(stream=True, store=True, background=False)


def _mock_provider(**overrides: Any) -> Any:
    """Create a mock provider with default stubs."""
    provider = AsyncMock()
    provider.get_items = AsyncMock(return_value=overrides.get("get_items_return", []))
    return provider


def _make_request(inp: Any) -> CreateResponse:
    """Build a minimal CreateResponse with the given input."""
    return cast(CreateResponse, {"model": "test-model", "input": inp})


def _item_ref(item_id: str) -> ItemReferenceParam:
    return cast(ItemReferenceParam, {"id": item_id})


def _assert_message(item: Any, role: str | None = None) -> None:
    assert isinstance(item, dict)
    assert item.get("type") == "message"
    if role is not None:
        assert item.get("role") == role


def _assert_output_message(item: Any) -> None:
    _assert_message(item)
    assert str(item.get("id", "")).startswith("msg_") or str(item.get("id", "")).startswith("item_")
    assert item.get("status") == "completed"


# ------------------------------------------------------------------
# Basic: no references — items pass through as-is
# ------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_input_items__no_references_passes_through() -> None:
    """Inline items are returned as Item subtypes (ItemMessage)."""
    msg = cast(ItemMessage, {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "hello"}]})
    request = _make_request([msg])
    ctx = ResponseContext(
        response_id="resp_001",
        mode_flags=_mode_flags(),
        request=request,
        input_items=[msg],
    )

    items = await ctx.get_input_items()

    assert len(items) == 1
    _assert_message(items[0], "user")


# ------------------------------------------------------------------
# Reference resolution: single reference
# ------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_input_items__resolves_single_reference() -> None:
    """A single ItemReferenceParam is resolved and converted to an Item subtype."""
    ref = _item_ref("item_abc")
    resolved_item = cast(
        OutputItemMessage,
        {"id": "item_abc", "type": "message", "role": "assistant", "content": [], "status": "completed"},
    )
    provider = _mock_provider(get_items_return=[resolved_item])

    request = _make_request([ref])
    ctx = ResponseContext(
        response_id="resp_002",
        mode_flags=_mode_flags(),
        request=request,
        input_items=[ref],
        provider=provider,
    )

    items = await ctx.get_input_items()

    assert len(items) == 1
    # Resolved via to_item(): OutputItemMessage -> Item wire payload
    _assert_message(items[0], "assistant")
    provider.get_items.assert_awaited_once_with(["item_abc"], context=ctx.platform_context)


# ------------------------------------------------------------------
# Reference resolution: mixed inline + references
# ------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_input_items__mixed_inline_and_references() -> None:
    """Inline items and references are interleaved; references are resolved in-place."""
    inline_msg = cast(
        ItemMessage, {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "hi"}]}
    )
    ref1 = _item_ref("item_111")
    ref2 = _item_ref("item_222")
    resolved1 = cast(
        OutputItemMessage,
        {"id": "item_111", "type": "message", "role": "assistant", "content": [], "status": "completed"},
    )
    resolved2 = cast(
        OutputItemMessage, {"id": "item_222", "type": "message", "role": "user", "content": [], "status": "completed"}
    )
    provider = _mock_provider(get_items_return=[resolved1, resolved2])

    request = _make_request([inline_msg, ref1, ref2])
    ctx = ResponseContext(
        response_id="resp_003",
        mode_flags=_mode_flags(),
        request=request,
        input_items=[inline_msg, ref1, ref2],
        provider=provider,
    )

    items = await ctx.get_input_items()

    # inline passed through as Item wire payload, references resolved via to_item()
    assert len(items) == 3
    _assert_message(items[0], "user")
    _assert_message(items[1], "assistant")  # resolved from OutputItemMessage
    _assert_message(items[2], "user")  # resolved from OutputItemMessage


# ------------------------------------------------------------------
# Unresolvable references are dropped
# ------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_input_items__unresolvable_references_dropped() -> None:
    """References that resolve to None are silently dropped."""
    ref1 = _item_ref("item_exists")
    ref2 = _item_ref("item_missing")
    resolved1 = cast(
        OutputItemMessage,
        {"id": "item_exists", "type": "message", "role": "assistant", "content": [], "status": "completed"},
    )
    provider = _mock_provider(get_items_return=[resolved1, None])

    request = _make_request([ref1, ref2])
    ctx = ResponseContext(
        response_id="resp_004",
        mode_flags=_mode_flags(),
        request=request,
        input_items=[ref1, ref2],
        provider=provider,
    )

    items = await ctx.get_input_items()

    assert len(items) == 1
    _assert_message(items[0])  # resolved via to_item()


# ------------------------------------------------------------------
# No provider — references returned as-is (no resolution)
# ------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_input_items__no_provider_no_resolution() -> None:
    """Without a provider, ItemReferenceParam entries are silently dropped (unresolvable)."""
    inline_msg = cast(
        ItemMessage, {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "hi"}]}
    )
    ref = _item_ref("item_xyz")

    request = _make_request([inline_msg, ref])
    ctx = ResponseContext(
        response_id="resp_005",
        mode_flags=_mode_flags(),
        request=request,
        input_items=[inline_msg, ref],
        # no provider
    )

    items = await ctx.get_input_items()

    # inline item returned as Item wire payload; reference placeholder is dropped
    assert len(items) == 1
    _assert_message(items[0], "user")


# ------------------------------------------------------------------
# Caching: second call returns cached result without re-resolving
# ------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_input_items__caches_result() -> None:
    """Calling get_input_items() twice returns the cached result."""
    ref = _item_ref("item_cache")
    resolved = cast(
        OutputItemMessage,
        {"id": "item_cache", "type": "message", "role": "assistant", "content": [], "status": "completed"},
    )
    provider = _mock_provider(get_items_return=[resolved])

    request = _make_request([ref])
    ctx = ResponseContext(
        response_id="resp_006",
        mode_flags=_mode_flags(),
        request=request,
        input_items=[ref],
        provider=provider,
    )

    first = await ctx.get_input_items()
    second = await ctx.get_input_items()

    assert first is second
    # Provider should only be called once
    assert provider.get_items.await_count == 1


# ------------------------------------------------------------------
# String input is expanded to ItemMessage
# ------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_input_items__string_input_expanded() -> None:
    """A plain string input is normalized to an ItemMessage via get_input_expanded."""
    request = _make_request("Hello world")
    ctx = ResponseContext(
        response_id="resp_007",
        mode_flags=_mode_flags(),
        request=request,
        input_items=["Hello world"],  # type: ignore[list-item]
    )

    items = await ctx.get_input_items()

    assert len(items) == 1
    _assert_message(items[0], "user")


# ------------------------------------------------------------------
# Empty input returns empty tuple
# ------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_input_items__empty_input() -> None:
    """Empty input returns an empty tuple."""
    request = _make_request([])
    ctx = ResponseContext(
        response_id="resp_008",
        mode_flags=_mode_flags(),
        request=request,
        input_items=[],
    )

    items = await ctx.get_input_items()

    assert items == ()


# ------------------------------------------------------------------
# Platform context is forwarded to provider
# ------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_input_items__forwards_platform_context() -> None:
    """Platform context is passed through to provider.get_items()."""
    ref = _item_ref("item_iso")
    resolved = cast(
        OutputItemMessage,
        {"id": "item_iso", "type": "message", "role": "assistant", "content": [], "status": "completed"},
    )
    provider = _mock_provider(get_items_return=[resolved])
    isolation = PlatformContext(user_id_key="user_123", call_id="call_456")

    request = _make_request([ref])
    ctx = ResponseContext(
        response_id="resp_009",
        mode_flags=_mode_flags(),
        request=request,
        input_items=[ref],
        provider=provider,
        platform_context=isolation,
    )

    items = await ctx.get_input_items()

    assert len(items) == 1
    _assert_message(items[0])  # resolved via to_item()
    provider.get_items.assert_awaited_once_with(["item_iso"], context=isolation)


# ------------------------------------------------------------------
# All references unresolvable — empty result
# ------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_input_items__all_references_unresolvable() -> None:
    """When all references resolve to None, result is empty."""
    ref1 = _item_ref("item_gone1")
    ref2 = _item_ref("item_gone2")
    provider = _mock_provider(get_items_return=[None, None])

    request = _make_request([ref1, ref2])
    ctx = ResponseContext(
        response_id="resp_010",
        mode_flags=_mode_flags(),
        request=request,
        input_items=[ref1, ref2],
        provider=provider,
    )

    items = await ctx.get_input_items()

    assert items == ()


# ------------------------------------------------------------------
# Order is preserved: inline, resolved ref, inline
# ------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_input_items__preserves_order() -> None:
    """Order of inline items and resolved references matches input order."""
    msg1 = cast(ItemMessage, {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "first"}]})
    ref = _item_ref("item_mid")
    msg2 = cast(ItemMessage, {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "last"}]})
    resolved = cast(
        OutputItemMessage,
        {"id": "item_mid", "type": "message", "role": "assistant", "content": [], "status": "completed"},
    )
    provider = _mock_provider(get_items_return=[resolved])

    request = _make_request([msg1, ref, msg2])
    ctx = ResponseContext(
        response_id="resp_011",
        mode_flags=_mode_flags(),
        request=request,
        input_items=[msg1, ref, msg2],
        provider=provider,
    )

    items = await ctx.get_input_items()

    assert len(items) == 3
    _assert_message(items[0], "user")
    _assert_message(items[1], "assistant")  # resolved via to_item()
    _assert_message(items[2], "user")


# ------------------------------------------------------------------
# to_output_item: unit tests for the conversion function
# ------------------------------------------------------------------


def test_to_output_item__converts_item_message() -> None:
    """ItemMessage is converted to OutputItemMessage with generated ID."""
    msg = cast(ItemMessage, {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "hello"}]})
    result = to_output_item(msg, "resp_123")
    assert result is not None
    _assert_output_message(result)
    assert result["role"] == "user"


def test_to_output_item__returns_none_for_reference() -> None:
    """ItemReferenceParam is non-convertible — returns None."""
    ref = _item_ref("item_abc")
    result = to_output_item(ref)
    assert result is None


@pytest.mark.parametrize(
    "item_type",
    ["memory_search_call", "tool_search_call", "tool_search_output"],
)
def test_to_output_item__defaults_new_required_status_items(item_type: str) -> None:
    result = to_output_item(cast(Item, {"type": item_type}), "resp_123")

    assert result is not None
    assert result["status"] == "completed"


def test_to_output_item__preserves_tool_search_status() -> None:
    item = cast(Item, {"type": "tool_search_call", "status": "in_progress"})

    result = to_output_item(item, "resp_123")

    assert result is not None
    assert result["status"] == "in_progress"


@pytest.mark.parametrize(
    "output_item",
    [
        {"type": "structured_outputs", "id": "item_1"},
        {"type": "oauth_consent_request", "id": "item_2"},
        {"type": "workflow_action", "id": "item_3"},
    ],
)
def test_to_item__returns_none_for_output_only_types(output_item: dict[str, str]) -> None:
    assert to_item(cast(OutputItemMessage, output_item)) is None


# ------------------------------------------------------------------
# _get_input_items_for_persistence: resolves references for storage
# ------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_input_items_for_persistence__resolves_references() -> None:
    """_get_input_items_for_persistence resolves item_reference entries to OutputItem."""
    inline_msg = cast(
        ItemMessage, {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "hi"}]}
    )
    ref = _item_ref("item_ref1")
    resolved = cast(
        OutputItemMessage,
        {"id": "item_ref1", "type": "message", "role": "assistant", "content": [], "status": "completed"},
    )
    provider = _mock_provider(get_items_return=[resolved])

    request = _make_request([inline_msg, ref])
    ctx = ResponseContext(
        response_id="resp_persist_001",
        mode_flags=_mode_flags(),
        request=request,
        input_items=[inline_msg, ref],
        provider=provider,
    )

    output_items = await ctx._get_input_items_for_persistence()

    # Both items should be converted to OutputItem — including the resolved reference
    assert len(output_items) == 2
    assert all(isinstance(item, dict) and item.get("type") == "message" for item in output_items)


@pytest.mark.asyncio
async def test_get_input_items_for_persistence__no_references_passes_through() -> None:
    """When no references exist, all inline items are returned as OutputItem."""
    msg = cast(ItemMessage, {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "hello"}]})
    request = _make_request([msg])
    ctx = ResponseContext(
        response_id="resp_persist_002",
        mode_flags=_mode_flags(),
        request=request,
        input_items=[msg],
    )

    output_items = await ctx._get_input_items_for_persistence()

    assert len(output_items) == 1
    _assert_output_message(output_items[0])


@pytest.mark.asyncio
async def test_get_input_items_for_persistence__unresolvable_dropped() -> None:
    """Unresolvable references are dropped from the persistence result."""
    ref = _item_ref("item_gone")
    provider = _mock_provider(get_items_return=[None])

    request = _make_request([ref])
    ctx = ResponseContext(
        response_id="resp_persist_003",
        mode_flags=_mode_flags(),
        request=request,
        input_items=[ref],
        provider=provider,
    )

    output_items = await ctx._get_input_items_for_persistence()

    assert len(output_items) == 0
