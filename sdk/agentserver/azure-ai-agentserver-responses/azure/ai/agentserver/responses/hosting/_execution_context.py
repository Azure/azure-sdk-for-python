# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Per-request execution context for the Responses server."""

from __future__ import annotations

import asyncio  # pylint: disable=do-not-import-asyncio
from typing import TYPE_CHECKING, Any

from .._response_context import ResponseContext
from ..models._generated import AgentReference, CreateResponse, OutputItem

if TYPE_CHECKING:
    from ._observability import CreateSpan


class _ExecutionContext:  # pylint: disable=too-many-instance-attributes
    """Holds all per-request state for a single create-response call.

    Passed between the routing layer and the orchestrator. All fields
    except ``context`` are set once at construction.
    """

    def __init__(
        self,
        *,
        response_id: str,
        agent_reference: AgentReference | dict[str, Any],
        model: str | None,
        store: bool,
        background: bool,
        stream: bool,
        input_items: list[OutputItem],
        previous_response_id: str | None,
        conversation_id: str | None,
        cancellation_signal: asyncio.Event,
        span: "CreateSpan",
        parsed: CreateResponse,
        agent_session_id: str | None = None,
        context: ResponseContext | None = None,
        user_isolation_key: str | None = None,
        chat_isolation_key: str | None = None,
        prefetched_history_ids: list[str] | None = None,
    ) -> None:
        self.response_id = response_id
        self.agent_reference = agent_reference
        self.model = model
        self.store = store
        self.background = background
        self.stream = stream
        self.input_items = input_items
        self.previous_response_id = previous_response_id
        self.conversation_id = conversation_id
        self.cancellation_signal = cancellation_signal
        self.span = span
        self.parsed = parsed
        self.agent_session_id = agent_session_id
        self.context = context
        self.user_isolation_key = user_isolation_key
        self.chat_isolation_key = chat_isolation_key
        self.prefetched_history_ids = prefetched_history_ids
