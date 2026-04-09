# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""ResponseContext for user-defined response execution."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Sequence

from azure.ai.agentserver.responses.models._generated.sdk.models._types import InputParam

from .models._generated import CreateResponse, ItemReferenceParam, OutputItem
from .models._helpers import get_input_expanded, to_output_item
from .models.runtime import ResponseModeFlags

if TYPE_CHECKING:
    from .store._base import ResponseProviderProtocol


@dataclass(frozen=True)
class IsolationContext:
    """Platform-injected isolation keys for multi-tenant state partitioning.

    The Foundry hosting platform injects ``x-agent-user-isolation-key`` and
    ``x-agent-chat-isolation-key`` headers on every protocol request (not on
    health probes).  These opaque strings serve as partition keys:

    - ``user_key`` — unique per user across all sessions; use for user-private state.
    - ``chat_key`` — represents where conversation state lives; in 1:1 chats the
      two keys are equal.

    When the headers are absent (e.g. local development), both keys are ``None``.
    When the platform sends the header with an empty value, the key is an empty
    string.  Use ``is None`` to detect whether the header was present at all.
    """

    user_key: str | None = None
    """Partition key for user-private state (from ``x-agent-user-isolation-key``).
    ``None`` when the header was not sent."""

    chat_key: str | None = None
    """Partition key for conversation/shared state (from ``x-agent-chat-isolation-key``).
    ``None`` when the header was not sent."""


class ResponseContext:
    """Runtime context exposed to response handlers and used by hosting orchestration.

    - response identifier
    - shutdown signal flag
    - raw body access
    - async input/history resolution
    """

    def __init__(
        self,
        *,
        response_id: str,
        mode_flags: ResponseModeFlags,
        raw_body: dict[str, Any] | None = None,
        request: CreateResponse | None = None,
        created_at: datetime | None = None,
        provider: "ResponseProviderProtocol | None" = None,
        input_items: list[InputParam] | None = None,
        previous_response_id: str | None = None,
        conversation_id: str | None = None,
        history_limit: int = 100,
        client_headers: dict[str, str] | None = None,
        query_parameters: dict[str, str] | None = None,
        isolation: IsolationContext | None = None,
    ) -> None:
        self.response_id = response_id
        self.mode_flags = mode_flags
        self.raw_body = raw_body
        self.request = request
        self.created_at = created_at if created_at is not None else datetime.now(timezone.utc)
        self.is_shutdown_requested: bool = False
        self.client_headers: dict[str, str] = client_headers or {}
        self.query_parameters: dict[str, str] = query_parameters or {}
        self.isolation: IsolationContext = isolation if isolation is not None else IsolationContext()
        self._provider: "ResponseProviderProtocol | None" = provider
        self._input_items: list[InputParam] = list(input_items) if input_items is not None else []
        self._previous_response_id: str | None = previous_response_id
        self.conversation_id: str | None = conversation_id
        self._history_limit: int = history_limit
        self._input_items_cache: Sequence[OutputItem] | None = None
        self._history_cache: Sequence[OutputItem] | None = None

    async def get_input_items(self) -> Sequence[OutputItem]:
        """Return and cache request input items, resolving item references.

        Inline items are converted from :class:`Item` to :class:`OutputItem`
        via :func:`to_output_item` (mirroring .NET ``ItemConversion.ToOutputItem``).
        :class:`ItemReferenceParam` entries are batch-resolved via the
        provider's :meth:`get_items` method.  Unresolvable references
        (provider returns ``None``) are silently dropped.

        :returns: A tuple of output items with references resolved.
        :rtype: Sequence[OutputItem]
        """
        if self._input_items_cache is not None:
            return self._input_items_cache

        # Normalise raw input (strings, dicts) into typed Item instances
        # via get_input_expanded — mirrors .NET GetInputExpanded().
        if self.request is not None:
            expanded = get_input_expanded(self.request)
        else:
            expanded = list(self._input_items)  # type: ignore[arg-type]

        if not expanded:
            self._input_items_cache = ()
            return self._input_items_cache

        # Collect ItemReferenceParam positions and IDs for batch resolution.
        # Non-reference items are converted to OutputItem via to_output_item.
        reference_ids: list[str] = []
        reference_positions: list[int] = []
        results: list[OutputItem | None] = []

        for item in expanded:
            if isinstance(item, ItemReferenceParam):
                reference_ids.append(item.id)
                reference_positions.append(len(results))
                results.append(None)  # placeholder
            else:
                output = to_output_item(item, self.response_id)
                if output is not None:
                    results.append(output)

        # Batch-resolve references if we have a provider and pending refs.
        if reference_ids and self._provider is not None:
            resolved = await self._provider.get_items(reference_ids, isolation=self.isolation)
            for idx, pos in enumerate(reference_positions):
                if idx < len(resolved) and resolved[idx] is not None:
                    results[pos] = resolved[idx]

        # Remove unresolved (None) placeholders.
        self._input_items_cache = tuple(item for item in results if item is not None)
        return self._input_items_cache

    async def get_history(self) -> Sequence[OutputItem]:
        """Resolve and cache conversation history items via the provider.

        :returns: A tuple of conversation history items.
        :rtype: Sequence[OutputItem]
        """
        if self._history_cache is not None:
            return self._history_cache

        if self._provider is None:
            self._history_cache = ()
            return self._history_cache

        item_ids = await self._provider.get_history_item_ids(
            self._previous_response_id,
            self.conversation_id,
            self._history_limit,
            isolation=self.isolation,
        )
        if not item_ids:
            self._history_cache = ()
            return self._history_cache

        items = await self._provider.get_items(item_ids, isolation=self.isolation)
        self._history_cache = tuple(item for item in items if item is not None)
        return self._history_cache
