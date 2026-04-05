# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""ResponseContext for user-defined response execution."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Sequence

from azure.ai.agentserver.responses.models._generated.sdk.models._types import InputParam

from .models._generated import CreateResponse, OutputItem
from .models.runtime import ResponseModeFlags

if TYPE_CHECKING:
    from .store._base import ResponseProviderProtocol


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
        raw_body: Any | None = None,
        request: CreateResponse | None = None,
        created_at: datetime | None = None,
        provider: "ResponseProviderProtocol | None" = None,
        input_items: list[InputParam] | None = None,
        previous_response_id: str | None = None,
        conversation_id: str | None = None,
        history_limit: int = 100,
        client_headers: dict[str, str] | None = None,
        query_parameters: dict[str, str] | None = None,
    ) -> None:
        self.response_id = response_id
        self.mode_flags = mode_flags
        self.raw_body = raw_body
        self.request = request
        self.created_at = created_at if created_at is not None else datetime.now(timezone.utc)
        self.is_shutdown_requested: bool = False
        self.client_headers: dict[str, str] = client_headers or {}
        self.query_parameters: dict[str, str] = query_parameters or {}
        self._provider: "ResponseProviderProtocol | None" = provider
        self._input_items: list[InputParam] = list(input_items) if input_items is not None else []
        self._previous_response_id: str | None = previous_response_id
        self.conversation_id: str | None = conversation_id
        self._history_limit: int = history_limit
        self._input_items_cache: Sequence[OutputItem] | None = None
        self._history_cache: Sequence[OutputItem] | None = None

    async def get_input_items(self) -> Sequence[InputParam]:
        """Return and cache request input items.

        :returns: A tuple of input items from the request.
        :rtype: Sequence[InputParam]
        """
        if self._input_items_cache is not None:
            return self._input_items_cache
        self._input_items_cache = tuple(self._input_items)
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
            self._previous_response_id, self.conversation_id, self._history_limit
        )
        if not item_ids:
            self._history_cache = ()
            return self._history_cache

        items = await self._provider.get_items(item_ids)
        self._history_cache = tuple(item for item in items if item is not None)
        return self._history_cache
