# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Per-request execution context for the Responses server."""

from __future__ import annotations

import asyncio  # pylint: disable=do-not-import-asyncio
from dataclasses import dataclass, field
from typing import Any

from azure.ai.agentserver.responses.models._generated.sdk.models._types import InputParam

from .._response_context import ResponseContext


@dataclass(slots=True)
class _ExecutionContext:
    """Holds all per-request state for a single create-response call.

    Passed between the routing layer and the orchestrator. All fields
    except ``context`` are set once at construction.
    """

    response_id: str
    agent_reference: Any
    model: str | None
    store: bool
    background: bool
    stream: bool
    input_items: list[InputParam]
    previous_response_id: str | None
    conversation_id: str | None
    cancellation_signal: asyncio.Event
    span: Any
    parsed: Any
    agent_session_id: str | None = None
    context: ResponseContext | None = None
    user_isolation_key: str | None = None
    chat_isolation_key: str | None = None
