# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Persistence abstraction for response execution and replay state."""

from __future__ import annotations

from typing import Any, Iterable, Protocol, runtime_checkable

from ..models._generated import ResponseObject


@runtime_checkable
class ResponseProviderProtocol(Protocol):
    """Protocol aligned with the .NET ``IResponsesProvider`` contract.

    Implementations provide response envelope storage plus input/history item lookup.
    """

    async def create_response_async(
        self,
        response: ResponseObject,
        input_items: Iterable[Any] | None,
        history_item_ids: Iterable[str] | None,
    ) -> None:
        """Persist a new response envelope and optional input/history references.

        :param response: The response envelope to persist.
        :type response: ~azure.ai.agentserver.responses.models._generated.ResponseObject
        :param input_items: Optional input items to associate with the response.
        :type input_items: Iterable[Any] | None
        :param history_item_ids: Optional history item IDs to link to the response.
        :type history_item_ids: Iterable[str] | None
        :rtype: None
        """

    async def get_response_async(self, response_id: str) -> ResponseObject:
        """Load one response envelope by ID.

        :param response_id: The unique identifier of the response to retrieve.
        :type response_id: str
        :returns: The response envelope matching the given ID.
        :rtype: ~azure.ai.agentserver.responses.models._generated.ResponseObject
        :raises KeyError: If the response does not exist.
        """

    async def update_response_async(self, response: ResponseObject) -> None:
        """Persist an updated response envelope.

        :param response: The response envelope with updated fields to persist.
        :type response: ~azure.ai.agentserver.responses.models._generated.ResponseObject
        :rtype: None
        """

    async def delete_response_async(self, response_id: str) -> None:
        """Delete a response envelope by ID.

        :param response_id: The unique identifier of the response to delete.
        :type response_id: str
        :rtype: None
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
        """Get response input/history items for one response ID using cursor pagination.

        :param response_id: The unique identifier of the response whose items to fetch.
        :type response_id: str
        :param limit: Maximum number of items to return. Defaults to 20.
        :type limit: int
        :param ascending: Whether to return items in ascending order. Defaults to False.
        :type ascending: bool
        :param after: Cursor ID; only return items after this ID.
        :type after: str | None
        :param before: Cursor ID; only return items before this ID.
        :type before: str | None
        :returns: A list of input/history items matching the pagination criteria.
        :rtype: list[Any]
        """

    async def get_items_async(self, item_ids: Iterable[str]) -> list[Any | None]:
        """Get items by ID (missing IDs produce ``None`` entries).

        :param item_ids: The item identifiers to look up.
        :type item_ids: Iterable[str]
        :returns: A list of items in the same order as *item_ids*; missing items are ``None``.
        :rtype: list[Any | None]
        """

    async def get_history_item_ids_async(
        self,
        previous_response_id: str | None,
        conversation_id: str | None,
        limit: int,
    ) -> list[str]:
        """Get history item IDs for a conversation chain scope.

        :param previous_response_id: Optional response ID to chain history from.
        :type previous_response_id: str | None
        :param conversation_id: Optional conversation ID to scope history lookup.
        :type conversation_id: str | None
        :param limit: Maximum number of history item IDs to return.
        :type limit: int
        :returns: A list of history item IDs within the given scope.
        :rtype: list[str]
        """


@runtime_checkable
class ResponseStreamProviderProtocol(Protocol):
    """Protocol for providers that can persist and replay SSE stream events.

    Implement this protocol alongside :class:`ResponseProviderProtocol` to enable
    SSE replay for responses that are no longer resident in the in-process runtime
    state (for example, after a process restart).
    """

    async def save_stream_events_async(
        self,
        response_id: str,
        events: list[dict[str, Any]],
    ) -> None:
        """Persist the complete ordered list of SSE events for a response.

        Called once when the background+stream response reaches terminal state.
        The *events* list uses the same normalised format that the SSE encoding
        layer expects: ``[{"type": str, "payload": dict}, ...]``.

        :param response_id: The unique identifier of the response.
        :type response_id: str
        :param events: Ordered list of normalised SSE event dicts to persist.
        :type events: list[dict[str, Any]]
        :rtype: None
        """

    async def get_stream_events_async(
        self,
        response_id: str,
    ) -> list[dict[str, Any]] | None:
        """Retrieve the persisted SSE events for a response.

        :param response_id: The unique identifier of the response whose events to retrieve.
        :type response_id: str
        :returns: The ordered list of normalised SSE event dicts, or ``None`` if not found.
        :rtype: list[dict[str, Any]] | None
        """
