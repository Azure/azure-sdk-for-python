# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Persistence abstraction for response execution and replay state."""

from __future__ import annotations

from typing import Any, Iterable, Protocol, runtime_checkable

from ..models._generated import Response


@runtime_checkable
class ResponseProviderProtocol(Protocol):
    """Protocol aligned with the .NET ``IResponsesProvider`` contract.

    Implementations provide response envelope storage plus input/history item lookup.
    """

    async def create_response_async(
        self,
        response: Response,
        input_items: Iterable[Any] | None,
        history_item_ids: Iterable[str] | None,
    ) -> None:
        """Persist a new response envelope and optional input/history references."""

    async def get_response_async(self, response_id: str) -> Response:
        """Load one response envelope by ID.

        :raises KeyError: If the response does not exist.
        """

    async def update_response_async(self, response: Response) -> None:
        """Persist an updated response envelope."""

    async def delete_response_async(self, response_id: str) -> None:
        """Delete a response envelope by ID.

        :raises KeyError: If the response does not exist.
        """

    async def get_input_items_async(
        self,
        response_id: str,
        limit: int = 20,
        ascending: bool = False,
        after: str | None = None,
        before: str | None = None,
    ) -> list[Any]:
        """Get response input/history items for one response ID using cursor pagination."""

    async def get_items_async(self, item_ids: Iterable[str]) -> list[Any | None]:
        """Get items by ID (missing IDs produce ``None`` entries)."""

    async def get_history_item_ids_async(
        self,
        previous_response_id: str | None,
        conversation_id: str | None,
        limit: int,
    ) -> list[str]:
        """Get history item IDs for a conversation chain scope."""


