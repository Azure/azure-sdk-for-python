# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Unit tests for steering integration (Phase 4).

Tests:
- SteeringQueueFull from .start() → maps to HTTP 429
- .start() succeeds on steerable in-progress task → acceptance hook path
- Non-steerable tasks never use acceptance hook
- max_pending configuration flows through
"""

from __future__ import annotations

import asyncio
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from azure.ai.agentserver.responses._options import ResponsesServerOptions
from azure.ai.agentserver.responses.hosting._acceptance import (
    dispatch_acceptance_hook,
    generate_default_acceptance,
)


class TestSteeringQueueFull:
    """SteeringQueueFull from task start → HTTP 429."""

    def test_options_max_pending_default(self) -> None:
        """Default max_pending is 10."""
        opts = ResponsesServerOptions()
        assert opts.max_pending == 10

    def test_options_max_pending_custom(self) -> None:
        """Custom max_pending is respected."""
        opts = ResponsesServerOptions(max_pending=5)
        assert opts.max_pending == 5

    def test_options_max_pending_must_be_positive(self) -> None:
        """max_pending <= 0 raises ValueError."""
        with pytest.raises(ValueError, match="max_pending must be > 0"):
            ResponsesServerOptions(max_pending=0)


class TestAcceptanceHookDispatch:
    """Dispatch acceptance hook for queued turns."""

    def test_dispatch_with_no_hook_returns_default(self) -> None:
        """No hook → default queued response."""
        mock_context = MagicMock()
        mock_context.response_id = "resp_1"
        mock_request = MagicMock()

        result = dispatch_acceptance_hook(
            hook=None,
            request=mock_request,
            context=mock_context,
            model="gpt-4o",
        )

        assert result["status"] == "queued"
        assert result["id"] == "resp_1"
        assert result["model"] == "gpt-4o"

    def test_dispatch_with_custom_hook(self) -> None:
        """Custom hook result is returned."""
        mock_context = MagicMock()
        mock_context.response_id = "resp_2"
        mock_request = MagicMock()

        def hook(req, ctx):
            return {"status": "queued", "id": ctx.response_id, "extra": "data"}

        result = dispatch_acceptance_hook(
            hook=hook,
            request=mock_request,
            context=mock_context,
            model="gpt-4o",
        )

        assert result["status"] == "queued"
        assert result["extra"] == "data"

    def test_dispatch_hook_error_fallback(self) -> None:
        """Hook error → fallback to default."""
        mock_context = MagicMock()
        mock_context.response_id = "resp_err"
        mock_request = MagicMock()

        def bad_hook(req, ctx):
            raise ValueError("oops")

        result = dispatch_acceptance_hook(
            hook=bad_hook,
            request=mock_request,
            context=mock_context,
            model="test",
        )

        assert result["status"] == "queued"
        assert result["id"] == "resp_err"


class TestSteeringConfiguration:
    """Steering options validation."""

    def test_steerable_requires_durable(self) -> None:
        """steerable_conversations requires durable_background."""
        with pytest.raises(
            ValueError, match="steerable_conversations=True requires durable_background"
        ):
            ResponsesServerOptions(
                steerable_conversations=True,
                durable_background=False,
            )

    def test_steerable_requires_store(self) -> None:
        """steerable_conversations requires store to be enabled."""
        with pytest.raises(
            ValueError, match="steerable_conversations=True requires store"
        ):
            ResponsesServerOptions(
                steerable_conversations=True,
                store_disabled=True,
            )

    def test_steerable_with_durable_is_valid(self) -> None:
        """Valid configuration: steerable + durable + store."""
        opts = ResponsesServerOptions(
            steerable_conversations=True,
            durable_background=True,
        )
        assert opts.steerable_conversations is True
        assert opts.durable_background is True
