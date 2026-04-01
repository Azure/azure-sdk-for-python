# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""HTTP-backed Foundry storage provider for Azure AI Responses."""

from __future__ import annotations

from typing import Any, Iterable
from urllib.parse import quote as _url_quote

from azure.core import AsyncPipelineClient
from azure.core.credentials_async import AsyncTokenCredential
from azure.core.pipeline import policies
from azure.core.rest import HttpRequest

from ..models._generated import ResponseObject  # type: ignore[attr-defined]
from ._foundry_errors import raise_for_storage_error
from ._foundry_serializer import (
    deserialize_history_ids,
    deserialize_items_array,
    deserialize_paged_items,
    deserialize_response,
    serialize_batch_request,
    serialize_create_request,
    serialize_response,
)
from ._foundry_settings import FoundryStorageSettings

_FOUNDRY_TOKEN_SCOPE = "https://ai.azure.com/.default"
_JSON_CONTENT_TYPE = "application/json"


def _encode(value: str) -> str:
    return _url_quote(value, safe="")


class FoundryStorageProvider:
    """An HTTP-backed response storage provider that persists data via the Foundry storage API.

    This class satisfies the
    :class:`~azure.ai.agentserver.responses.store._base.ResponseProviderProtocol` structural
    protocol.  Obtain an instance through the constructor and supply it when building a
    ``ResponsesServer``.

    Uses :class:`~azure.core.AsyncPipelineClient` for HTTP transport, providing
    built-in retry, logging, distributed tracing, and bearer-token authentication.

    :param credential: An async credential used to obtain bearer tokens for the Foundry API.
    :type credential: AsyncTokenCredential
    :param settings: Storage settings. If omitted,
        :meth:`~FoundryStorageSettings.from_env` is called automatically.
    :type settings: FoundryStorageSettings | None

    Example::

        async with FoundryStorageProvider(credential=DefaultAzureCredential()) as provider:
            app = ResponsesServer(handler=my_handler, provider=provider)
    """

    def __init__(
        self,
        credential: AsyncTokenCredential,
        settings: FoundryStorageSettings | None = None,
    ) -> None:
        self._settings = settings or FoundryStorageSettings.from_env()
        self._client: AsyncPipelineClient = AsyncPipelineClient(
            base_url=self._settings.storage_base_url,
            policies=[
                policies.RequestIdPolicy(),
                policies.HeadersPolicy(),
                policies.UserAgentPolicy(
                    sdk_moniker="ai-agentserver-responses",
                ),
                policies.RetryPolicy(),
                policies.AsyncBearerTokenCredentialPolicy(
                    credential, _FOUNDRY_TOKEN_SCOPE,
                ),
                policies.ContentDecodePolicy(),
                policies.DistributedTracingPolicy(),
                policies.HttpLoggingPolicy(),
            ],
        )

    # ------------------------------------------------------------------
    # Async context-manager support
    # ------------------------------------------------------------------

    async def aclose(self) -> None:
        """Close the underlying HTTP pipeline client."""
        await self._client.close()

    async def __aenter__(self) -> "FoundryStorageProvider":
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.aclose()

    # ------------------------------------------------------------------
    # ResponseProviderProtocol implementation
    # ------------------------------------------------------------------

    async def create_response_async(
        self,
        response: ResponseObject,
        input_items: Iterable[Any] | None,
        history_item_ids: Iterable[str] | None,
    ) -> None:
        """Persist a new response with its associated input items and history.

        :param response: The initial response snapshot.
        :type response: ResponseObject
        :param input_items: Ordered input items for this response turn.
        :type input_items: Iterable[Any] | None
        :param history_item_ids: Item IDs from the prior conversation turn, if any.
        :type history_item_ids: Iterable[str] | None
        :raises FoundryApiError: On non-success HTTP response.
        """
        body = serialize_create_request(response, input_items, history_item_ids)
        url = self._settings.build_url("responses")
        request = HttpRequest("POST", url, content=body, headers={"Content-Type": _JSON_CONTENT_TYPE})
        http_resp = await self._client.send_request(request)
        raise_for_storage_error(http_resp)

    async def get_response_async(self, response_id: str) -> ResponseObject:
        """Retrieve a stored response by its ID.

        :param response_id: The response identifier.
        :type response_id: str
        :returns: The deserialized :class:`ResponseObject` model.
        :rtype: ResponseObject
        :raises FoundryResourceNotFoundError: If the response does not exist.
        :raises FoundryApiError: On other non-success HTTP response.
        """
        url = self._settings.build_url(f"responses/{_encode(response_id)}")
        request = HttpRequest("GET", url)
        http_resp = await self._client.send_request(request)
        raise_for_storage_error(http_resp)
        return deserialize_response(http_resp.text())

    async def update_response_async(self, response: ResponseObject) -> None:
        """Persist an updated response snapshot.

        :param response: The updated response model.  Must contain a valid ``id`` field.
        :type response: ResponseObject
        :raises FoundryResourceNotFoundError: If the response does not exist.
        :raises FoundryApiError: On other non-success HTTP response.
        """
        response_id = str(response["id"])  # type: ignore[index]
        body = serialize_response(response)
        url = self._settings.build_url(f"responses/{_encode(response_id)}")
        request = HttpRequest("POST", url, content=body, headers={"Content-Type": _JSON_CONTENT_TYPE})
        http_resp = await self._client.send_request(request)
        raise_for_storage_error(http_resp)

    async def delete_response_async(self, response_id: str) -> None:
        """Delete a stored response and its associated data.

        :param response_id: The response identifier.
        :type response_id: str
        :raises FoundryResourceNotFoundError: If the response does not exist.
        :raises FoundryApiError: On other non-success HTTP response.
        """
        url = self._settings.build_url(f"responses/{_encode(response_id)}")
        request = HttpRequest("DELETE", url)
        http_resp = await self._client.send_request(request)
        raise_for_storage_error(http_resp)

    async def get_input_items_async(
        self,
        response_id: str,
        limit: int = 20,
        ascending: bool = False,
        after: str | None = None,
        before: str | None = None,
    ) -> list[Any]:
        """Retrieve a page of input items for the given response.

        :param response_id: The response whose input items are being listed.
        :type response_id: str
        :param limit: Maximum number of items to return. Defaults to 20.
        :type limit: int
        :param ascending: ``True`` for oldest-first ordering; ``False`` (default) for newest-first.
        :type ascending: bool
        :param after: Start the page after this item ID (cursor-based pagination).
        :type after: str | None
        :param before: End the page before this item ID (cursor-based pagination).
        :type before: str | None
        :returns: A list of deserialized :class:`OutputItem` instances.
        :rtype: list[Any]
        :raises FoundryResourceNotFoundError: If the response does not exist.
        :raises FoundryApiError: On other non-success HTTP response.
        """
        extra: dict[str, str] = {
            "limit": str(limit),
            "order": "asc" if ascending else "desc",
        }
        if after is not None:
            extra["after"] = after
        if before is not None:
            extra["before"] = before

        url = self._settings.build_url(f"responses/{_encode(response_id)}/input_items", **extra)
        request = HttpRequest("GET", url)
        http_resp = await self._client.send_request(request)
        raise_for_storage_error(http_resp)
        return deserialize_paged_items(http_resp.text())

    async def get_items_async(self, item_ids: Iterable[str]) -> list[Any | None]:
        """Retrieve multiple items by their IDs in a single batch request.

        Positions in the returned list correspond to positions in *item_ids*.
        Entries are ``None`` where no item was found for the given ID.

        :param item_ids: The item identifiers to retrieve.
        :type item_ids: Iterable[str]
        :returns: A list of :class:`OutputItem` instances (or ``None`` for missing items).
        :rtype: list[Any | None]
        :raises FoundryApiError: On non-success HTTP response.
        """
        ids = list(item_ids)
        body = serialize_batch_request(ids)
        url = self._settings.build_url("items/batch/retrieve")
        request = HttpRequest("POST", url, content=body, headers={"Content-Type": _JSON_CONTENT_TYPE})
        http_resp = await self._client.send_request(request)
        raise_for_storage_error(http_resp)
        return deserialize_items_array(http_resp.text())

    async def get_history_item_ids_async(
        self,
        previous_response_id: str | None,
        conversation_id: str | None,
        limit: int,
    ) -> list[str]:
        """Retrieve the ordered list of item IDs that form the conversation history.

        :param previous_response_id: The response whose prior turn should be the history anchor.
        :type previous_response_id: str | None
        :param conversation_id: An explicit conversation scope identifier, if available.
        :type conversation_id: str | None
        :param limit: Maximum number of item IDs to return.
        :type limit: int
        :returns: Ordered list of item ID strings.
        :rtype: list[str]
        :raises FoundryApiError: On non-success HTTP response.
        """
        extra: dict[str, str] = {"limit": str(limit)}
        if previous_response_id is not None:
            extra["previous_response_id"] = previous_response_id
        if conversation_id is not None:
            extra["conversation_id"] = conversation_id

        url = self._settings.build_url("history/item_ids", **extra)
        request = HttpRequest("GET", url)
        http_resp = await self._client.send_request(request)
        raise_for_storage_error(http_resp)
        return deserialize_history_ids(http_resp.text())
