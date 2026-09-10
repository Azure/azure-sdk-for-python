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

    # (Spec 024 Phase 5 — Proposal #5) ``max_pending`` option DELETED.
    # The pre-Phase-5 cap validation tests are obsolete — see the
    # Phase 5 test file ``test_phase5_api_simplification.py`` which
    # asserts the option is rejected at construction time.


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

    def test_steerable_with_resilient_background_off_does_not_raise(self) -> None:
        """(Spec 024 Phase 4 — Proposal #9 relaxed composition)

        steerable_conversations=True + resilient_background=False is now
        a VALID combination. Pre-Phase-4 this raised ValueError; the
        guard is removed because the two options are independent.
        """
        options = ResponsesServerOptions(
            steerable_conversations=True,
            resilient_background=False,
        )
        assert options.steerable_conversations is True
        assert options.resilient_background is False

    # (Spec 024 Phase 5 — Proposal #5 / Phase 4 — Proposal #9)
    # ``store_disabled`` option DELETED and the
    # ``steerable + store_disabled`` composition guard is gone (the
    # rejected combination is no longer expressible). See the Phase 5
    # test file for the absence-of-keyword assertion.

    def test_steerable_with_resilient_is_valid(self) -> None:
        """Valid configuration: steerable + resilient + store."""
        opts = ResponsesServerOptions(
            steerable_conversations=True,
            resilient_background=True,
        )
        assert opts.steerable_conversations is True
        assert opts.resilient_background is True
