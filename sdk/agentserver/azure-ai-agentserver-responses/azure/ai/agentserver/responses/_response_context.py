# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""ResponseContext for user-defined response execution."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Sequence

from azure.ai.agentserver.responses.models._generated.sdk.models._types import InputParam

from .models._generated import (
    CreateResponse,
    Item,
    ItemMessage,
    ItemReferenceParam,
    MessageContentInputTextContent,
    OutputItem,
)
from .models._helpers import get_input_expanded, to_item, to_output_item
from .models.runtime import ResponseModeFlags

if TYPE_CHECKING:
    from .store._base import ResponseProviderProtocol


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

    def __init__(self, *, user_key: str | None = None, chat_key: str | None = None) -> None:
        self.user_key = user_key
        """Partition key for user-private state (from ``x-agent-user-isolation-key``).
        ``None`` when the header was not sent."""

        self.chat_key = chat_key
        """Partition key for conversation/shared state (from ``x-agent-chat-isolation-key``).
        ``None`` when the header was not sent."""


class ResponseContext:  # pylint: disable=too-many-instance-attributes
    """Runtime context exposed to response handlers and used by hosting orchestration.

    - response identifier
    - shutdown signal flag
    - async input/history resolution
    """

    def __init__(
        self,
        *,
        response_id: str,
        mode_flags: ResponseModeFlags,
        request: CreateResponse | None = None,
        created_at: datetime | None = None,
        provider: "ResponseProviderProtocol | None" = None,
        input_items: list[InputParam] | list[OutputItem] | None = None,
        previous_response_id: str | None = None,
        conversation_id: str | None = None,
        history_limit: int = 100,
        client_headers: dict[str, str] | None = None,
        query_parameters: dict[str, str] | None = None,
        isolation: IsolationContext | None = None,
        prefetched_history_ids: list[str] | None = None,
    ) -> None:
        self.response_id = response_id
        self.mode_flags = mode_flags
        self.request = request
        self.created_at = created_at if created_at is not None else datetime.now(timezone.utc)
        self.is_shutdown_requested: bool = False
        self.client_headers: dict[str, str] = client_headers or {}
        self.query_parameters: dict[str, str] = query_parameters or {}
        self.isolation: IsolationContext = isolation if isolation is not None else IsolationContext()
        self._provider: "ResponseProviderProtocol | None" = provider
        _items: list[Any]
        if input_items is not None:
            _items = list(input_items)
        else:
            _items = []
        self._input_items: list[Any] = _items
        self._previous_response_id: str | None = previous_response_id
        self.conversation_id: str | None = conversation_id
        self._history_limit: int = history_limit
        self._input_items_resolved_cache: Sequence[Item] | None = None
        self._input_items_unresolved_cache: Sequence[Item] | None = None
        self._history_cache: Sequence[OutputItem] | None = None
        self._prefetched_history_ids: list[str] | None = prefetched_history_ids

    async def get_input_items(self, *, resolve_references: bool = True) -> Sequence[Item]:
        """Return the caller's input items as :class:`Item` subtypes.

        Inline items are returned as-is — the same :class:`Item` subtypes from
        the original request (e.g. :class:`ItemMessage`,
        :class:`FunctionCallOutputItemParam`).
        :class:`ItemReferenceParam` entries are batch-resolved via the
        provider and converted back to :class:`Item` subtypes.
        Unresolvable references (provider returns ``None``) are silently dropped.

        :keyword resolve_references: When ``True`` (default),
            :class:`ItemReferenceParam` items are resolved via the provider and
            returned as their concrete :class:`Item` subtype.  When ``False``,
            item references are left as :class:`ItemReferenceParam` in the
            returned sequence.
        :type resolve_references: bool
        :returns: A tuple of input items.
        :rtype: Sequence[Item]
        """
        if resolve_references:
            return await self._get_input_items_resolved()
        return await self._get_input_items_unresolved()

    async def get_input_text(self, *, resolve_references: bool = True) -> str:
        """Resolve input items and extract all text content as a single string.

        Convenience method that calls :meth:`get_input_items`, filters for
        :class:`ItemMessage` items, expands their content, and joins all
        :class:`MessageContentInputTextContent` text values with newline
        separators.

        :keyword resolve_references: When ``True`` (default), item references
            are resolved before extracting text.
        :type resolve_references: bool
        :returns: The combined text content, or ``""`` if no text found.
        :rtype: str
        """
        items = await self.get_input_items(resolve_references=resolve_references)
        texts: list[str] = []
        for item in items:
            if isinstance(item, ItemMessage):
                for part in getattr(item, "content", None) or []:
                    if isinstance(part, MessageContentInputTextContent):
                        text = getattr(part, "text", None)
                        if text is not None:
                            texts.append(text)
        return "\n".join(texts)

    async def _get_input_items_for_persistence(self) -> Sequence[OutputItem]:
        """Return input items as :class:`OutputItem` for storage persistence.

        The orchestrator needs :class:`OutputItem` instances when creating the
        stored response.  This method resolves references (so stored items are
        always concrete), converts each :class:`Item` to :class:`OutputItem`,
        and caches the result.

        :returns: A tuple of output items suitable for persistence.
        :rtype: Sequence[OutputItem]
        """
        items = await self.get_input_items(resolve_references=True)
        return tuple(out for item in items if (out := to_output_item(item, self.response_id)) is not None)

    # ------------------------------------------------------------------
    # Private resolution helpers (cached independently per mode)
    # ------------------------------------------------------------------

    async def _get_input_items_resolved(self) -> Sequence[Item]:
        """Resolve and cache input items with references resolved.

        :returns: A tuple of resolved input items.
        :rtype: Sequence[Item]
        """
        if self._input_items_resolved_cache is not None:
            return self._input_items_resolved_cache

        expanded = self._expand_input()
        if not expanded:
            self._input_items_resolved_cache = ()
            return self._input_items_resolved_cache

        # Collect ItemReferenceParam positions and IDs for batch resolution.
        reference_ids: list[str] = []
        reference_positions: list[int] = []
        results: list[Item | None] = []

        for item in expanded:
            if isinstance(item, ItemReferenceParam):
                reference_ids.append(item.id)
                reference_positions.append(len(results))
                results.append(None)  # placeholder
            else:
                results.append(item)

        # Batch-resolve references if we have a provider and pending refs.
        if reference_ids and self._provider is not None:
            resolved = await self._provider.get_items(reference_ids, isolation=self.isolation)
            for idx, pos in enumerate(reference_positions):
                if idx < len(resolved) and resolved[idx] is not None:
                    converted = to_item(resolved[idx])  # type: ignore[arg-type]
                    if converted is not None:
                        results[pos] = converted

        # Remove unresolved (None) placeholders.
        self._input_items_resolved_cache = tuple(item for item in results if item is not None)
        return self._input_items_resolved_cache

    async def _get_input_items_unresolved(self) -> Sequence[Item]:
        """Return input items without resolving references.

        :returns: A tuple of unresolved input items.
        :rtype: Sequence[Item]
        """
        if self._input_items_unresolved_cache is not None:
            return self._input_items_unresolved_cache

        expanded = self._expand_input()
        self._input_items_unresolved_cache = tuple(expanded)
        return self._input_items_unresolved_cache

    def _expand_input(self) -> list[Item]:
        """Normalize raw input into typed Item instances.

        :returns: A list of typed Item instances.
        :rtype: list[Item]
        """
        if self.request is not None:
            return get_input_expanded(self.request)
        return list(self._input_items)  # type: ignore[arg-type]

    async def get_history(self) -> Sequence[OutputItem]:
        """Resolve and cache conversation history items via the provider.

        When prefetched history IDs are available (from eager validation),
        the provider's ``get_history_item_ids`` call is skipped and only
        ``get_items`` is invoked to materialise the items.

        :returns: A tuple of conversation history items.
        :rtype: Sequence[OutputItem]
        """
        if self._history_cache is not None:
            return self._history_cache

        if self._provider is None:
            self._history_cache = ()
            return self._history_cache

        # No conversation context — nothing to look up.
        if not self._previous_response_id and not self.conversation_id:
            self._history_cache = ()
            return self._history_cache

        # Use eagerly-prefetched IDs when available; otherwise call provider.
        if self._prefetched_history_ids is not None:
            item_ids = self._prefetched_history_ids
        else:
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
