# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Unit tests for the acceptance hook (Phase 4 — Steering).

Tests:
- @app.response_acceptor registers the hook
- Default acceptance hook returns queued response shape
- Custom hook called with (request, context) → custom queued response
- Hook errors fall back to default behavior
"""

from __future__ import annotations

import asyncio
from typing import Any

import pytest

from azure.ai.agentserver.responses import (
    CreateResponse,
    ResponseContext,
    ResponseObject,
    ResponsesAgentServerHost,
    ResponsesServerOptions,
)


class TestAcceptanceHookRegistration:
    """Verify @app.response_acceptor decorator registration."""

    def test_register_acceptor_via_decorator(self) -> None:
        """@app.response_acceptor registers the hook on the app."""
        options = ResponsesServerOptions(
            resilient_background=True,
            steerable_conversations=True,
        )
        app = ResponsesAgentServerHost(options=options)

        @app.response_acceptor
        def my_acceptor(request: CreateResponse, context: ResponseContext) -> ResponseObject:
            return ResponseObject({"status": "queued", "id": context.response_id})

        assert app._acceptance_hook is not None
        assert app._acceptance_hook is my_acceptor

    def test_no_acceptor_by_default(self) -> None:
        """Without @response_acceptor, the hook is None."""
        options = ResponsesServerOptions(resilient_background=True)
        app = ResponsesAgentServerHost(options=options)
        assert app._acceptance_hook is None


class TestDefaultAcceptanceBehavior:
    """Default acceptance creates a queued response envelope."""

    def test_default_queued_response_shape(self) -> None:
        """Default acceptance returns a dict-native ResponseObject with status=queued."""
        from azure.ai.agentserver.responses.hosting._acceptance import (
            generate_default_acceptance,
        )

        response = generate_default_acceptance(
            response_id="resp_123",
            model="gpt-4o",
        )
        assert isinstance(response, dict)
        assert response["id"] == "resp_123"
        assert response["status"] == "queued"
        assert response["object"] == "response"
        assert response["model"] == "gpt-4o"
        assert response["output"] == []

    def test_default_queued_response_includes_model(self) -> None:
        """Default acceptance carries through the model name."""
        from azure.ai.agentserver.responses.hosting._acceptance import (
            generate_default_acceptance,
        )

        response = generate_default_acceptance(
            response_id="resp_456",
            model="test-model",
        )
        assert response["model"] == "test-model"


class TestCustomAcceptanceHook:
    """Custom acceptance hooks override the default."""

    def test_custom_hook_called_with_request_context(self) -> None:
        """Custom hook receives request and context; typed return is normalized to a dict."""
        from azure.ai.agentserver.responses.hosting._acceptance import (
            dispatch_acceptance_hook,
        )

        captured: dict[str, Any] = {}

        def my_hook(request: CreateResponse, context: ResponseContext) -> ResponseObject:
            captured["request"] = request
            captured["context"] = context
            return ResponseObject({"status": "queued", "id": context.response_id, "custom": True})

        # Create minimal mock objects
        from unittest.mock import MagicMock

        mock_request = MagicMock(spec=CreateResponse)
        mock_context = MagicMock(spec=ResponseContext)
        mock_context.response_id = "resp_custom"

        result = dispatch_acceptance_hook(
            hook=my_hook,
            request=mock_request,
            context=mock_context,
            model="gpt-4o",
        )

        # dispatch returns a plain dict for the internal HTTP path.
        assert isinstance(result, dict)
        assert result["status"] == "queued"
        assert result["custom"] is True
        assert captured["request"] is mock_request
        assert captured["context"] is mock_context

    def test_hook_returning_plain_dict_is_tolerated(self) -> None:
        """A hook that returns a plain dict (not a ResponseObject) still works."""
        from azure.ai.agentserver.responses.hosting._acceptance import (
            dispatch_acceptance_hook,
        )
        from unittest.mock import MagicMock

        def dict_hook(request: CreateResponse, context: ResponseContext) -> Any:
            return {"id": context.response_id}  # no status set

        mock_context = MagicMock(spec=ResponseContext)
        mock_context.response_id = "resp_dict"
        result = dispatch_acceptance_hook(
            hook=dict_hook,
            request=MagicMock(spec=CreateResponse),
            context=mock_context,
            model=None,
        )
        assert result["id"] == "resp_dict"
        assert result["status"] == "queued"  # defaulted

    def test_hook_error_falls_back_to_default(self) -> None:
        """If custom hook raises, fall back to default acceptance."""
        from azure.ai.agentserver.responses.hosting._acceptance import (
            dispatch_acceptance_hook,
        )
        from unittest.mock import MagicMock

        def bad_hook(request: CreateResponse, context: ResponseContext) -> ResponseObject:
            raise RuntimeError("Hook failed")

        mock_request = MagicMock(spec=CreateResponse)
        mock_context = MagicMock(spec=ResponseContext)
        mock_context.response_id = "resp_fallback"

        result = dispatch_acceptance_hook(
            hook=bad_hook,
            request=mock_request,
            context=mock_context,
            model="test-model",
        )

        # Falls back to default
        assert isinstance(result, dict)
        assert result["status"] == "queued"
        assert result["id"] == "resp_fallback"
        assert result["model"] == "test-model"
