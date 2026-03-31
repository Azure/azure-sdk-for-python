# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Per-request execution context for the Responses server."""

from __future__ import annotations

import asyncio  # pylint: disable=do-not-import-asyncio
from typing import Any

from azure.ai.agentserver.responses.models._generated.sdk.models._types import InputParam

from .._response_context import ResponseContext


class _ExecutionContext:  # pylint: disable=too-many-instance-attributes
    """Holds all per-request *input* state for a single create-response call.

    Passed between the routing layer and the orchestrator to avoid
    large keyword-argument bundles on every internal function call.
    All fields are set once at construction and treated as immutable by
    the orchestrator.  Mutable in-flight state (accumulated events,
    background record, captured error) lives in :class:`_PipelineState`
    inside the orchestrator methods.
    """

    def __init__(
        self,
        *,
        response_id: str,
        agent_reference: Any,
        model: str | None,
        store: bool,
        background: bool,
        stream: bool,
        input_items: list[InputParam],
        previous_response_id: str | None,
        conversation_id: str | None,
        cancellation_signal: asyncio.Event,
        span: Any,
        parsed: Any,
        agent_session_id: str | None = None,
        context: ResponseContext | None = None,
    ) -> None:
        self.response_id = response_id
        """The assigned response identifier."""
        self.agent_reference = agent_reference
        """Normalized agent reference dictionary."""
        self.model = model
        """Model name, or ``None`` if not specified."""
        self.store = store
        """Whether to persist the execution record after the response completes."""
        self.background = background
        """Whether this is a background (non-blocking) request."""
        self.stream = stream
        """Whether to produce SSE streaming output."""
        self.input_items = input_items
        """Extracted input items from the request body."""
        self.previous_response_id = previous_response_id
        """Previous response ID for conversation chaining, or ``None``."""
        self.conversation_id = conversation_id
        """Conversation ID for grouping related responses, or ``None``."""
        self.cancellation_signal = cancellation_signal
        """Event signalling that the client has requested cancellation."""
        self.agent_session_id = agent_session_id
        """Resolved session ID for this request (S-048)."""
        self.context: ResponseContext | None = context
        """Runtime response context for this request.  Set after construction
        via :meth:`_ResponseEndpointHandler._create_response_context`."""
        self.span = span
        """Active observability span for this request."""
        self.parsed = parsed
        """Parsed ``CreateResponse`` model instance from the request body."""
