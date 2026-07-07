# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Unit tests for _resolve_input_items_for_persistence orchestrator helper."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock

import pytest

from azure.ai.agentserver.responses._response_context import ResponseContext
from azure.ai.agentserver.responses.hosting._orchestrator import _resolve_input_items_for_persistence
from azure.ai.agentserver.responses.models._generated import (
    CreateResponse,
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
    provider = AsyncMock()
    provider.get_items = AsyncMock(return_value=overrides.get("get_items_return", []))
    return provider


def _make_request(inp: Any) -> CreateResponse:
    return CreateResponse(model="test-model", input=inp)


# ------------------------------------------------------------------
# References are resolved and returned as OutputItem
# ------------------------------------------------------------------


@pytest.mark.asyncio
async def test_resolves_references_via_context() -> None:
    """item_reference entries are resolved to concrete OutputItem for persistence."""
    inline_msg = ItemMessage(role=MessageRole.USER, content=[MessageContentInputTextContent(text="hi")])
    ref = ItemReferenceParam(id="item_ref1")
    resolved = OutputItemMessage(id="item_ref1", role="assistant", content=[], status="completed")
    provider = _mock_provider(get_items_return=[resolved])

    request = _make_request([inline_msg, ref])
    ctx = ResponseContext(
        response_id="resp_001",
        mode_flags=_mode_flags(),
        request=request,
        input_items=[inline_msg, ref],
        provider=provider,
    )

    # The fallback only has the inline message (reference was stripped by to_output_item)
    fallback = [out for item in [inline_msg] if (out := to_output_item(item, "resp_001")) is not None]
    assert len(fallback) == 1  # only inline message

    result = await _resolve_input_items_for_persistence(ctx, fallback)

    # Should have BOTH items: resolved reference + inline message
    assert result is not None
    assert len(result) == 2
    assert all(isinstance(item, OutputItemMessage) for item in result)


# ------------------------------------------------------------------
# Falls back to pre-expanded items when context is None
# ------------------------------------------------------------------


@pytest.mark.asyncio
async def test_fallback_when_no_context() -> None:
    """When context is None, returns the fallback items."""
    msg = ItemMessage(role=MessageRole.USER, content=[MessageContentInputTextContent(text="hi")])
    fallback = [out for item in [msg] if (out := to_output_item(item, "resp_002")) is not None]

    result = await _resolve_input_items_for_persistence(None, fallback)

    assert result is not None
    assert len(result) == 1


# ------------------------------------------------------------------
# Falls back on resolution failure
# ------------------------------------------------------------------


@pytest.mark.asyncio
async def test_fallback_on_resolution_error() -> None:
    """When context._get_input_items_for_persistence raises, falls back."""
    msg = ItemMessage(role=MessageRole.USER, content=[MessageContentInputTextContent(text="hi")])
    ref = ItemReferenceParam(id="item_bad")
    provider = _mock_provider()
    provider.get_items = AsyncMock(side_effect=RuntimeError("provider down"))

    request = _make_request([msg, ref])
    ctx = ResponseContext(
        response_id="resp_003",
        mode_flags=_mode_flags(),
        request=request,
        input_items=[msg, ref],
        provider=provider,
    )

    fallback = [out for item in [msg] if (out := to_output_item(item, "resp_003")) is not None]
    result = await _resolve_input_items_for_persistence(ctx, fallback)

    # Falls back to the pre-expanded list (reference dropped)
    assert result is not None
    assert len(result) == 1


# ------------------------------------------------------------------
# Returns None when both are empty
# ------------------------------------------------------------------


@pytest.mark.asyncio
async def test_returns_none_for_empty_inputs() -> None:
    """Empty inputs yield None."""
    request = _make_request([])
    ctx = ResponseContext(
        response_id="resp_004",
        mode_flags=_mode_flags(),
        request=request,
        input_items=[],
    )

    result = await _resolve_input_items_for_persistence(ctx, [])
    assert result is None


# ------------------------------------------------------------------
# Cache reuse: context resolves once, persistence reuses cache
# ------------------------------------------------------------------


@pytest.mark.asyncio
async def test_no_double_fetch_via_cache() -> None:
    """The provider is called only once even if both handler and persistence paths run."""
    ref = ItemReferenceParam(id="item_cache")
    resolved = OutputItemMessage(id="item_cache", role="assistant", content=[], status="completed")
    provider = _mock_provider(get_items_return=[resolved])

    request = _make_request([ref])
    ctx = ResponseContext(
        response_id="resp_005",
        mode_flags=_mode_flags(),
        request=request,
        input_items=[ref],
        provider=provider,
    )

    # Simulate handler calling get_input_items first
    await ctx.get_input_items(resolve_references=True)
    assert provider.get_items.await_count == 1

    # Now persistence path — should reuse the cache
    result = await _resolve_input_items_for_persistence(ctx, [])
    assert result is not None
    assert len(result) == 1
    # Still only one provider.get_items call
    assert provider.get_items.await_count == 1
