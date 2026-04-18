# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Persistence abstraction for response execution and replay state."""

from __future__ import annotations

from typing import TYPE_CHECKING, Iterable, Protocol, runtime_checkable

from ..models._generated import OutputItem, ResponseObject, ResponseStreamEvent

if TYPE_CHECKING:
    from .._response_context import IsolationContext


@runtime_checkable
class ResponseProviderProtocol(Protocol):
    """Protocol for response storage providers.

    Implementations provide response envelope storage plus input/history item lookup.

    Every operation accepts an optional ``isolation`` parameter (S-018).
    Implementations MUST use it to partition data in multi-tenant
    deployments.  When ``None``, the provider operates without tenant
    scoping (suitable for local development).
    """

    async def create_response(
        self,
        response: ResponseObject,
        input_items: Iterable[OutputItem] | None,
        history_item_ids: Iterable[str] | None,
        *,
        isolation: IsolationContext | None = None,
    ) -> None:
        """Persist a new response envelope and optional input/history references.

        :param response: The response envelope to persist.
        :type response: ~azure.ai.agentserver.responses.models._generated.ResponseObject
        :param input_items: Optional resolved output items to associate with the response.
        :type input_items: Iterable[OutputItem] | None
        :param history_item_ids: Optional history item IDs to link to the response.
        :type history_item_ids: Iterable[str] | None
        :keyword isolation: Isolation context for multi-tenant partitioning.
        :paramtype isolation: ~azure.ai.agentserver.responses.IsolationContext | None
        :rtype: None
        """

    async def get_response(self, response_id: str, *, isolation: IsolationContext | None = None) -> ResponseObject:
        """Load one response envelope by ID.

        :param response_id: The unique identifier of the response to retrieve.
        :type response_id: str
        :keyword isolation: Isolation context for multi-tenant partitioning.
        :paramtype isolation: ~azure.ai.agentserver.responses.IsolationContext | None
        :returns: The response envelope matching the given ID.
        :rtype: ~azure.ai.agentserver.responses.models._generated.ResponseObject
        :raises KeyError: If the response does not exist.
        """
        ...

    async def update_response(self, response: ResponseObject, *, isolation: IsolationContext | None = None) -> None:
        """Persist an updated response envelope.

        :param response: The response envelope with updated fields to persist.
        :type response: ~azure.ai.agentserver.responses.models._generated.ResponseObject
        :keyword isolation: Isolation context for multi-tenant partitioning.
        :paramtype isolation: ~azure.ai.agentserver.responses.IsolationContext | None
        :rtype: None
        """

    async def delete_response(self, response_id: str, *, isolation: IsolationContext | None = None) -> None:
        """Delete a response envelope by ID.

        :param response_id: The unique identifier of the response to delete.
        :type response_id: str
        :keyword isolation: Isolation context for multi-tenant partitioning.
        :paramtype isolation: ~azure.ai.agentserver.responses.IsolationContext | None
        :rtype: None
        :raises KeyError: If the response does not exist.
        """

    async def get_input_items(
        self,
        response_id: str,
        limit: int = 20,
        ascending: bool = False,
        after: str | None = None,
        before: str | None = None,
        *,
        isolation: IsolationContext | None = None,
    ) -> list[OutputItem]:
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
        :keyword isolation: Isolation context for multi-tenant partitioning.
        :paramtype isolation: ~azure.ai.agentserver.responses.IsolationContext | None
        :returns: A list of output items matching the pagination criteria.
        :rtype: list[OutputItem]
        """
        ...

    async def get_items(
        self, item_ids: Iterable[str], *, isolation: IsolationContext | None = None
    ) -> list[OutputItem | None]:
        """Get items by ID (missing IDs produce ``None`` entries).

        :param item_ids: The item identifiers to look up.
        :type item_ids: Iterable[str]
        :keyword isolation: Isolation context for multi-tenant partitioning.
        :paramtype isolation: ~azure.ai.agentserver.responses.IsolationContext | None
        :returns: A list of output items in the same order as *item_ids*; missing items are ``None``.
        :rtype: list[OutputItem | None]
        """
        ...

    async def get_history_item_ids(
        self,
        previous_response_id: str | None,
        conversation_id: str | None,
        limit: int,
        *,
        isolation: IsolationContext | None = None,
    ) -> list[str]:
        """Get history item IDs for a conversation chain scope.

        :param previous_response_id: Optional response ID to chain history from.
        :type previous_response_id: str | None
        :param conversation_id: Optional conversation ID to scope history lookup.
        :type conversation_id: str | None
        :param limit: Maximum number of history item IDs to return.
        :type limit: int
        :keyword isolation: Isolation context for multi-tenant partitioning.
        :paramtype isolation: ~azure.ai.agentserver.responses.IsolationContext | None
        :returns: A list of history item IDs within the given scope.
        :rtype: list[str]
        """
        ...


@runtime_checkable
class ResponseStreamProviderProtocol(Protocol):
    """Protocol for providers that can persist and replay SSE stream events.

    Implement this protocol alongside :class:`ResponseProviderProtocol` to enable
    SSE replay for responses that are no longer resident in the in-process runtime
    state (for example, after a process restart).
    """

    async def save_stream_events(
        self,
        response_id: str,
        events: list[ResponseStreamEvent],
        *,
        isolation: IsolationContext | None = None,
    ) -> None:
        """Persist the complete ordered list of SSE events for a response.

        Called once when the background+stream response reaches terminal state.
        The *events* list contains ``ResponseStreamEvent`` model instances.

        :param response_id: The unique identifier of the response.
        :type response_id: str
        :param events: Ordered list of event instances to persist.
        :type events: list[ResponseStreamEvent]
        :keyword isolation: Isolation context for multi-tenant partitioning.
        :paramtype isolation: ~azure.ai.agentserver.responses.IsolationContext | None
        :rtype: None
        """

    async def get_stream_events(
        self,
        response_id: str,
        *,
        isolation: IsolationContext | None = None,
    ) -> list[ResponseStreamEvent] | None:
        """Retrieve the persisted SSE events for a response.

        :param response_id: The unique identifier of the response whose events to retrieve.
        :type response_id: str
        :keyword isolation: Isolation context for multi-tenant partitioning.
        :paramtype isolation: ~azure.ai.agentserver.responses.IsolationContext | None
        :returns: The ordered list of event instances, or ``None`` if not found.
        :rtype: list[ResponseStreamEvent] | None
        """

    async def delete_stream_events(
        self,
        response_id: str,
        *,
        isolation: IsolationContext | None = None,
    ) -> None:
        """Delete persisted SSE events for a response.

        Called when a response is deleted via ``DELETE /responses/{id}``.
        Implementations should remove any stored event data for the given
        response. No-op if no events exist for the ID.

        :param response_id: The unique identifier of the response whose events to remove.
        :type response_id: str
        :keyword isolation: Isolation context for multi-tenant partitioning.
        :paramtype isolation: ~azure.ai.agentserver.responses.IsolationContext | None
        :rtype: None
        """
