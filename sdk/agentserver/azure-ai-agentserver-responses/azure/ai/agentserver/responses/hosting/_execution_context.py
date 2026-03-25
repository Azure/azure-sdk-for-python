# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Per-request execution context for the Responses server."""

from __future__ import annotations

import asyncio  # pylint: disable=do-not-import-asyncio
from typing import Any

from .._handlers import ResponseContext
from ..models.runtime import ResponseExecution


class _ExecutionContext:  # pylint: disable=too-many-instance-attributes
    """Holds all per-request state for a single create-response call.

    Passed between the routing layer and the orchestrator to avoid
    large keyword-argument bundles on every internal function call.
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
        input_items: list[Any],
        previous_response_id: str | None,
        cancellation_signal: asyncio.Event,
        context: ResponseContext,
        span: Any,
        parsed: Any,
        captured_error: Exception | None = None,
        bg_record: ResponseExecution | None = None,
        handler_events: list[dict[str, Any]] | None = None,
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
        self.cancellation_signal = cancellation_signal
        """Event signalling that the client has requested cancellation."""
        self.context = context
        """Runtime response context for this request."""
        self.span = span
        """Active observability span for this request."""
        self.parsed = parsed
        """Parsed ``CreateResponse`` model instance from the request body."""
        self.captured_error = captured_error
        """Exception captured during handler execution, set after the fact; ``None`` on success."""
        self.bg_record: ResponseExecution | None = bg_record
        """Background execution record created after the first handler event (background+stream only)."""
        self.handler_events: list[dict[str, Any]] = handler_events if handler_events is not None else []
        """Accumulated, normalized handler events emitted so far."""
