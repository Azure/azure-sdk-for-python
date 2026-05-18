# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Unit tests for ResponseContext.get_input_items() item-reference resolution."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock

import pytest

from azure.ai.agentserver.responses._response_context import IsolationContext, ResponseContext
from azure.ai.agentserver.responses.models._generated import (
    CreateResponse,
    Item,
    ItemMessage,
    ItemReferenceParam,
    MessageContentInputTextContent,
    MessageRole,
    OutputItemMessage,
)
from azure.ai.agentserver.responses.models._helpers import to_output_item
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
    return CreateResponse(model="test-model", input=inp)


# ------------------------------------------------------------------
# Basic: no references — items pass through as-is
# ------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_input_items__no_references_passes_through() -> None:
    """Inline items are returned as Item subtypes (ItemMessage)."""
    msg = ItemMessage(role=MessageRole.USER, content=[MessageContentInputTextContent(text="hello")])
    request = _make_request([msg])
    ctx = ResponseContext(
        response_id="resp_001",
        mode_flags=_mode_flags(),
        request=request,
        input_items=[msg],
    )

    items = await ctx.get_input_items()

    assert len(items) == 1
    assert isinstance(items[0], ItemMessage)
    assert isinstance(items[0], Item)
    assert items[0].role == MessageRole.USER


# ------------------------------------------------------------------
# Reference resolution: single reference
# ------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_input_items__resolves_single_reference() -> None:
    """A single ItemReferenceParam is resolved and converted to an Item subtype."""
    ref = ItemReferenceParam(id="item_abc")
    resolved_item = OutputItemMessage(id="item_abc", role="assistant", content=[], status="completed")
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
    # Resolved via to_item(): OutputItemMessage → ItemMessage
    assert isinstance(items[0], ItemMessage)
    assert items[0].role == "assistant"
    provider.get_items.assert_awaited_once_with(["item_abc"], isolation=ctx.isolation)


# ------------------------------------------------------------------
# Reference resolution: mixed inline + references
# ------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_input_items__mixed_inline_and_references() -> None:
    """Inline items and references are interleaved; references are resolved in-place."""
    inline_msg = ItemMessage(role=MessageRole.USER, content=[MessageContentInputTextContent(text="hi")])
    ref1 = ItemReferenceParam(id="item_111")
    ref2 = ItemReferenceParam(id="item_222")
    resolved1 = OutputItemMessage(id="item_111", role="assistant", content=[], status="completed")
    resolved2 = OutputItemMessage(id="item_222", role="user", content=[], status="completed")
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

    # inline passed through as Item, references resolved via to_item()
    assert len(items) == 3
    assert isinstance(items[0], ItemMessage)
    assert isinstance(items[1], ItemMessage)  # resolved from OutputItemMessage
    assert items[1].role == "assistant"
    assert isinstance(items[2], ItemMessage)  # resolved from OutputItemMessage
    assert items[2].role == "user"


# ------------------------------------------------------------------
# Unresolvable references are dropped
# ------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_input_items__unresolvable_references_dropped() -> None:
    """References that resolve to None are silently dropped."""
    ref1 = ItemReferenceParam(id="item_exists")
    ref2 = ItemReferenceParam(id="item_missing")
    resolved1 = OutputItemMessage(id="item_exists", role="assistant", content=[], status="completed")
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
    assert isinstance(items[0], ItemMessage)  # resolved via to_item()


# ------------------------------------------------------------------
# No provider — references returned as-is (no resolution)
# ------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_input_items__no_provider_no_resolution() -> None:
    """Without a provider, ItemReferenceParam entries are silently dropped (unresolvable)."""
    inline_msg = ItemMessage(role=MessageRole.USER, content=[MessageContentInputTextContent(text="hi")])
    ref = ItemReferenceParam(id="item_xyz")

    request = _make_request([inline_msg, ref])
    ctx = ResponseContext(
        response_id="resp_005",
        mode_flags=_mode_flags(),
        request=request,
        input_items=[inline_msg, ref],
        # no provider
    )

    items = await ctx.get_input_items()

    # inline item returned as Item subtype; reference placeholder is dropped
    assert len(items) == 1
    assert isinstance(items[0], ItemMessage)


# ------------------------------------------------------------------
# Caching: second call returns cached result without re-resolving
# ------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_input_items__caches_result() -> None:
    """Calling get_input_items() twice returns the cached result."""
    ref = ItemReferenceParam(id="item_cache")
    resolved = OutputItemMessage(id="item_cache", role="assistant", content=[], status="completed")
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
    assert isinstance(items[0], ItemMessage)
    assert items[0].role == MessageRole.USER


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
# Isolation context is forwarded to provider
# ------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_input_items__forwards_isolation() -> None:
    """Isolation context is passed through to provider.get_items()."""
    ref = ItemReferenceParam(id="item_iso")
    resolved = OutputItemMessage(id="item_iso", role="assistant", content=[], status="completed")
    provider = _mock_provider(get_items_return=[resolved])
    isolation = IsolationContext(user_key="user_123", chat_key="chat_456")

    request = _make_request([ref])
    ctx = ResponseContext(
        response_id="resp_009",
        mode_flags=_mode_flags(),
        request=request,
        input_items=[ref],
        provider=provider,
        isolation=isolation,
    )

    items = await ctx.get_input_items()

    assert len(items) == 1
    assert isinstance(items[0], ItemMessage)  # resolved via to_item()
    provider.get_items.assert_awaited_once_with(["item_iso"], isolation=isolation)


# ------------------------------------------------------------------
# All references unresolvable — empty result
# ------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_input_items__all_references_unresolvable() -> None:
    """When all references resolve to None, result is empty."""
    ref1 = ItemReferenceParam(id="item_gone1")
    ref2 = ItemReferenceParam(id="item_gone2")
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
    msg1 = ItemMessage(role=MessageRole.USER, content=[MessageContentInputTextContent(text="first")])
    ref = ItemReferenceParam(id="item_mid")
    msg2 = ItemMessage(role=MessageRole.USER, content=[MessageContentInputTextContent(text="last")])
    resolved = OutputItemMessage(id="item_mid", role="assistant", content=[], status="completed")
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
    assert isinstance(items[0], ItemMessage)
    assert isinstance(items[1], ItemMessage)  # resolved via to_item()
    assert items[1].role == "assistant"
    assert isinstance(items[2], ItemMessage)


# ------------------------------------------------------------------
# to_output_item: unit tests for the conversion function
# ------------------------------------------------------------------


def test_to_output_item__converts_item_message() -> None:
    """ItemMessage is converted to OutputItemMessage with generated ID."""
    msg = ItemMessage(role=MessageRole.USER, content=[MessageContentInputTextContent(text="hello")])
    result = to_output_item(msg, "resp_123")
    assert result is not None
    assert isinstance(result, OutputItemMessage)
    assert result.id.startswith("msg_")
    assert result.status == "completed"
    assert result.role == MessageRole.USER


def test_to_output_item__returns_none_for_reference() -> None:
    """ItemReferenceParam is non-convertible — returns None."""
    ref = ItemReferenceParam(id="item_abc")
    result = to_output_item(ref)
    assert result is None


# ------------------------------------------------------------------
# _get_input_items_for_persistence: resolves references for storage
# ------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_input_items_for_persistence__resolves_references() -> None:
    """_get_input_items_for_persistence resolves item_reference entries to OutputItem."""
    inline_msg = ItemMessage(role=MessageRole.USER, content=[MessageContentInputTextContent(text="hi")])
    ref = ItemReferenceParam(id="item_ref1")
    resolved = OutputItemMessage(id="item_ref1", role="assistant", content=[], status="completed")
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
    assert all(isinstance(item, OutputItemMessage) for item in output_items)


@pytest.mark.asyncio
async def test_get_input_items_for_persistence__no_references_passes_through() -> None:
    """When no references exist, all inline items are returned as OutputItem."""
    msg = ItemMessage(role=MessageRole.USER, content=[MessageContentInputTextContent(text="hello")])
    request = _make_request([msg])
    ctx = ResponseContext(
        response_id="resp_persist_002",
        mode_flags=_mode_flags(),
        request=request,
        input_items=[msg],
    )

    output_items = await ctx._get_input_items_for_persistence()

    assert len(output_items) == 1
    assert isinstance(output_items[0], OutputItemMessage)


@pytest.mark.asyncio
async def test_get_input_items_for_persistence__unresolvable_dropped() -> None:
    """Unresolvable references are dropped from the persistence result."""
    ref = ItemReferenceParam(id="item_gone")
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
