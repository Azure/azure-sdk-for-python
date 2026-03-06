# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Operations for checkpoint items."""

from typing import Any, ClassVar, Dict, List, Optional

from azure.core.exceptions import ResourceNotFoundError
from azure.core.pipeline.transport import HttpRequest
from azure.core.tracing.decorator_async import distributed_trace_async

from ....tools.client.operations._base import BaseOperations
from .._models import (
    CheckpointItem,
    CheckpointItemId,
    CheckpointItemRequest,
    CheckpointItemResponse,
    ListCheckpointItemIdsResponse,
)


class CheckpointItemOperations(BaseOperations):
    """Operations for managing checkpoint items."""

    _API_VERSION: ClassVar[str] = "2025-11-15-preview"

    _HEADERS: ClassVar[Dict[str, str]] = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    _QUERY_PARAMS: ClassVar[Dict[str, Any]] = {"api-version": _API_VERSION}

    def _items_path(self, item_id: Optional[str] = None) -> str:
        """Get the API path for item operations.

        :param item_id: Optional item identifier.
        :type item_id: Optional[str]
        :return: The API path.
        :rtype: str
        """
        base = "/checkpoints/items"
        return f"{base}/{item_id}" if item_id else base

    def _build_create_batch_request(self, items: List[CheckpointItem]) -> HttpRequest:
        """Build the HTTP request for creating items in batch.

        :param items: The checkpoint items to create.
        :type items: List[CheckpointItem]
        :return: The HTTP request.
        :rtype: HttpRequest
        """
        request_models = [CheckpointItemRequest.from_item(item) for item in items]
        return self._client.post(
            self._items_path(),
            params=self._QUERY_PARAMS,
            headers=self._HEADERS,
            content=[model.model_dump(by_alias=True) for model in request_models],
        )

    def _build_read_request(self, item_id: CheckpointItemId) -> HttpRequest:
        """Build the HTTP request for reading an item.

        :param item_id: The checkpoint item identifier.
        :type item_id: CheckpointItemId
        :return: The HTTP request.
        :rtype: HttpRequest
        """
        params = dict(self._QUERY_PARAMS)
        params["sessionId"] = item_id.session_id
        if item_id.parent_id:
            params["parentId"] = item_id.parent_id
        return self._client.get(
            self._items_path(item_id.item_id),
            params=params,
            headers=self._HEADERS,
        )

    def _build_delete_request(self, item_id: CheckpointItemId) -> HttpRequest:
        """Build the HTTP request for deleting an item.

        :param item_id: The checkpoint item identifier.
        :type item_id: CheckpointItemId
        :return: The HTTP request.
        :rtype: HttpRequest
        """
        params = dict(self._QUERY_PARAMS)
        params["sessionId"] = item_id.session_id
        if item_id.parent_id:
            params["parentId"] = item_id.parent_id
        return self._client.delete(
            self._items_path(item_id.item_id),
            params=params,
            headers=self._HEADERS,
        )

    def _build_list_ids_request(
        self, session_id: str, parent_id: Optional[str] = None
    ) -> HttpRequest:
        """Build the HTTP request for listing item IDs.

        :param session_id: The session identifier.
        :type session_id: str
        :param parent_id: Optional parent item identifier.
        :type parent_id: Optional[str]
        :return: The HTTP request.
        :rtype: HttpRequest
        """
        params = dict(self._QUERY_PARAMS)
        params["sessionId"] = session_id
        if parent_id:
            params["parentId"] = parent_id
        return self._client.get(
            self._items_path(),
            params=params,
            headers=self._HEADERS,
        )

    @distributed_trace_async
    async def create_batch(self, items: List[CheckpointItem]) -> List[CheckpointItem]:
        """Create checkpoint items in batch.

        :param items: The checkpoint items to create.
        :type items: List[CheckpointItem]
        :return: The created checkpoint items.
        :rtype: List[CheckpointItem]
        """
        if not items:
            return []

        request = self._build_create_batch_request(items)
        response = await self._send_request(request)
        async with response:
            json_response = self._extract_response_json(response)
            if isinstance(json_response, list):
                return [
                    CheckpointItemResponse.model_validate(item).to_item()
                    for item in json_response
                ]
            # Single item response
            return [CheckpointItemResponse.model_validate(json_response).to_item()]

    @distributed_trace_async
    async def read(self, item_id: CheckpointItemId) -> Optional[CheckpointItem]:
        """Read a checkpoint item by ID.

        :param item_id: The checkpoint item identifier.
        :type item_id: CheckpointItemId
        :return: The checkpoint item if found, None otherwise.
        :rtype: Optional[CheckpointItem]
        """
        request = self._build_read_request(item_id)
        try:
            response = await self._send_request(request)
            async with response:
                json_response = self._extract_response_json(response)
                item_response = CheckpointItemResponse.model_validate(json_response)
            return item_response.to_item()
        except ResourceNotFoundError:
            return None

    @distributed_trace_async
    async def delete(self, item_id: CheckpointItemId) -> bool:
        """Delete a checkpoint item.

        :param item_id: The checkpoint item identifier.
        :type item_id: CheckpointItemId
        :return: True if the item was deleted, False if not found.
        :rtype: bool
        """
        request = self._build_delete_request(item_id)
        try:
            response = await self._send_request(request)
            async with response:
                pass  # No response body expected
            return True
        except ResourceNotFoundError:
            return False

    @distributed_trace_async
    async def list_ids(
        self, session_id: str, parent_id: Optional[str] = None
    ) -> List[CheckpointItemId]:
        """List checkpoint item IDs for a session.

        :param session_id: The session identifier.
        :type session_id: str
        :param parent_id: Optional parent item identifier for filtering.
        :type parent_id: Optional[str]
        :return: List of checkpoint item identifiers.
        :rtype: List[CheckpointItemId]
        """
        request = self._build_list_ids_request(session_id, parent_id)
        response = await self._send_request(request)
        async with response:
            json_response = self._extract_response_json(response)
            list_response = ListCheckpointItemIdsResponse.model_validate(json_response)
        return [item.to_item_id() for item in list_response.value]
