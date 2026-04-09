# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Per-request execution context for the Responses server."""

from __future__ import annotations

import asyncio  # pylint: disable=do-not-import-asyncio
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from .._response_context import ResponseContext
from ..models._generated import AgentReference, CreateResponse, OutputItem

if TYPE_CHECKING:
    from ._observability import CreateSpan


@dataclass(slots=True)
class _ExecutionContext:
    """Holds all per-request state for a single create-response call.

    Passed between the routing layer and the orchestrator. All fields
    except ``context`` are set once at construction.
    """

    response_id: str
    agent_reference: AgentReference | dict[str, Any]
    model: str | None
    store: bool
    background: bool
    stream: bool
    input_items: list[OutputItem]
    previous_response_id: str | None
    conversation_id: str | None
    cancellation_signal: asyncio.Event
    span: CreateSpan
    parsed: CreateResponse
    agent_session_id: str | None = None
    context: ResponseContext | None = None
    user_isolation_key: str | None = None
    chat_isolation_key: str | None = None
