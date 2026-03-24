# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Per-request execution context for the Responses server."""

from __future__ import annotations

import asyncio  # pylint: disable=do-not-import-asyncio
from dataclasses import dataclass, field
from typing import Any

from .._handlers import RuntimeResponseContext
from ._runtime_state import _ExecutionRecord


@dataclass
class _ExecutionContext:  # pylint: disable=too-many-instance-attributes
    """Holds all per-request state for a single create-response call.

    Passed between the routing layer and the orchestrator to avoid
    large keyword-argument bundles on every internal function call.
    """

    response_id: str
    """The assigned response identifier."""

    agent_reference: Any
    """Normalized agent reference dictionary."""

    model: str | None
    """Model name, or ``None`` if not specified."""

    store: bool
    """Whether to persist the execution record after the response completes."""

    background: bool
    """Whether this is a background (non-blocking) request."""

    stream: bool
    """Whether to produce SSE streaming output."""

    input_items: list[Any]
    """Extracted input items from the request body."""

    previous_response_id: str | None
    """Previous response ID for conversation chaining, or ``None``."""

    cancellation_signal: asyncio.Event
    """Event signalling that the client has requested cancellation."""

    context: RuntimeResponseContext
    """Runtime response context for this request."""

    span: Any
    """Active observability span for this request."""

    parsed: Any
    """Parsed ``CreateResponse`` model instance from the request body."""

    captured_error: Exception | None = None
    """Exception captured during handler execution, set after the fact; ``None`` on success."""

    bg_record: _ExecutionRecord | None = None
    """Background execution record created after the first handler event (background+stream only)."""

    handler_events: list[dict[str, Any]] = field(default_factory=list)
    """Accumulated, normalized handler events emitted so far."""
