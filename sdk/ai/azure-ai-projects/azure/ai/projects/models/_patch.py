# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List, Dict, Optional, Any, Tuple
from azure.core.polling import LROPoller, AsyncLROPoller, PollingMethod, AsyncPollingMethod
from azure.core.polling.base_polling import (
    LROBasePolling,
    OperationFailed,
    _raise_if_bad_http_status_and_method,
)
from azure.core.polling.async_base_polling import AsyncLROBasePolling
from ._models import CustomCredential as CustomCredentialGenerated
from ..models import MemoryStoreUpdateCompletedResult, MemoryStoreUpdateResult


class CustomCredential(CustomCredentialGenerated):
    """Custom credential definition.

    :ivar type: The credential type. Always equals CredentialType.CUSTOM. Required.
    :vartype type: str or ~azure.ai.projects.models.CredentialType
    :ivar credential_keys: The secret custom credential keys. Required.
    :vartype credential_keys: dict[str, str]
    """

    credential_keys: Dict[str, str] = {}
    """The secret custom credential keys. Required."""


_FINISHED = frozenset(["completed", "superseded", "failed"])
_FAILED = frozenset(["failed"])


class UpdateMemoriesLROPollingMethod(LROBasePolling):
    """A custom polling method implementation for Memory Store updates."""

    @property
    def _current_body(self) -> MemoryStoreUpdateResult:
        try:
            return MemoryStoreUpdateResult(self._pipeline_response.http_response.json())
        except Exception:  # pylint: disable=broad-exception-caught
            return MemoryStoreUpdateResult()  # type: ignore[call-overload]

    def finished(self) -> bool:
        """Is this polling finished?

        :return: True/False for whether polling is complete.
        :rtype: bool
        """
        return self._finished(self.status())

    @staticmethod
    def _finished(status) -> bool:
        if hasattr(status, "value"):
            status = status.value
        return str(status).lower() in _FINISHED

    @staticmethod
    def _failed(status) -> bool:
        if hasattr(status, "value"):
            status = status.value
        return str(status).lower() in _FAILED

    def get_continuation_token(self) -> str:
        return self._current_body.update_id

    # pylint: disable=arguments-differ
    def from_continuation_token(self, continuation_token: str, **kwargs: Any) -> Tuple:  # type: ignore[override]
        try:
            client = kwargs["client"]
        except KeyError as exc:
            raise ValueError("Need kwarg 'client' to be recreated from continuation_token") from exc

        try:
            deserialization_callback = kwargs["deserialization_callback"]
        except KeyError as exc:
            raise ValueError("Need kwarg 'deserialization_callback' to be recreated from continuation_token") from exc

        return client, continuation_token, deserialization_callback

    def _poll(self) -> None:
        """Poll status of operation so long as operation is incomplete and
        we have an endpoint to query.

        :raises: OperationFailed if operation status 'Failed' or 'Canceled'.
        :raises: BadStatus if response status invalid.
        :raises: BadResponse if response invalid.
        """

        if not self.finished():
            self.update_status()
        while not self.finished():
            self._delay()
            self.update_status()

        if self._failed(self.status()):
            raise OperationFailed("Operation failed or canceled")

        final_get_url = self._operation.get_final_get_url(self._pipeline_response)
        if final_get_url:
            self._pipeline_response = self.request_status(final_get_url)
            _raise_if_bad_http_status_and_method(self._pipeline_response.http_response)


class AsyncUpdateMemoriesLROPollingMethod(AsyncLROBasePolling):
    """A custom polling method implementation for Memory Store updates."""

    @property
    def _current_body(self) -> MemoryStoreUpdateResult:
        try:
            return MemoryStoreUpdateResult(self._pipeline_response.http_response.json())
        except Exception:  # pylint: disable=broad-exception-caught
            return MemoryStoreUpdateResult()  # type: ignore[call-overload]

    def finished(self) -> bool:
        """Is this polling finished?

        :return: True/False for whether polling is complete.
        :rtype: bool
        """
        return self._finished(self.status())

    @staticmethod
    def _finished(status) -> bool:
        if hasattr(status, "value"):
            status = status.value
        return str(status).lower() in _FINISHED

    @staticmethod
    def _failed(status) -> bool:
        if hasattr(status, "value"):
            status = status.value
        return str(status).lower() in _FAILED

    def get_continuation_token(self) -> str:
        return self._current_body.update_id

    # pylint: disable=arguments-differ
    def from_continuation_token(self, continuation_token: str, **kwargs: Any) -> Tuple:  # type: ignore[override]
        try:
            client = kwargs["client"]
        except KeyError as exc:
            raise ValueError("Need kwarg 'client' to be recreated from continuation_token") from exc

        try:
            deserialization_callback = kwargs["deserialization_callback"]
        except KeyError as exc:
            raise ValueError("Need kwarg 'deserialization_callback' to be recreated from continuation_token") from exc

        return client, continuation_token, deserialization_callback

    async def _poll(self) -> None:
        """Poll status of operation so long as operation is incomplete and
        we have an endpoint to query.

        :raises: OperationFailed if operation status 'Failed' or 'Canceled'.
        :raises: BadStatus if response status invalid.
        :raises: BadResponse if response invalid.
        """

        if not self.finished():
            await self.update_status()
        while not self.finished():
            await self._delay()
            await self.update_status()

        if self._failed(self.status()):
            raise OperationFailed("Operation failed or canceled")

        final_get_url = self._operation.get_final_get_url(self._pipeline_response)
        if final_get_url:
            self._pipeline_response = await self.request_status(final_get_url)
            _raise_if_bad_http_status_and_method(self._pipeline_response.http_response)


class UpdateMemoriesLROPoller(LROPoller[MemoryStoreUpdateCompletedResult]):
    """Custom LROPoller for Memory Store update operations."""

    _polling_method: "UpdateMemoriesLROPollingMethod"

    @property
    def update_id(self) -> str:
        """Returns the update ID associated with the long-running update memories operation.

        :return: Returns the update ID.
        :rtype: str
        """
        return self._polling_method._current_body.update_id  # pylint: disable=protected-access

    @property
    def superseded_by(self) -> Optional[str]:
        """Returns the ID of the operation that superseded this update.

        :return: Returns the ID of the superseding operation, if it exists.
        :rtype: Optional[str]
        """
        return (
            self._polling_method._current_body.superseded_by  # pylint: disable=protected-access
            if self._polling_method._current_body  # pylint: disable=protected-access
            else None
        )

    @classmethod
    def from_continuation_token(
        cls, polling_method: PollingMethod[MemoryStoreUpdateCompletedResult], continuation_token: str, **kwargs: Any
    ) -> "UpdateMemoriesLROPoller":
        """Create a poller from a continuation token.

        :param polling_method: The polling strategy to adopt
        :type polling_method: ~azure.core.polling.PollingMethod
        :param continuation_token: An opaque continuation token
        :type continuation_token: str
        :return: An instance of UpdateMemoriesLROPoller
        :rtype: UpdateMemoriesLROPoller
        :raises ~azure.core.exceptions.HttpResponseError: If the continuation token is invalid.
        """
        (
            client,
            initial_response,
            deserialization_callback,
        ) = polling_method.from_continuation_token(continuation_token, **kwargs)

        return cls(client, initial_response, deserialization_callback, polling_method)


class AsyncUpdateMemoriesLROPoller(AsyncLROPoller[MemoryStoreUpdateCompletedResult]):
    """Custom AsyncLROPoller for Memory Store update operations."""

    _polling_method: "AsyncUpdateMemoriesLROPollingMethod"

    @property
    def update_id(self) -> str:
        """Returns the update ID associated with the long-running update memories operation.

        :return: Returns the update ID.
        :rtype: str
        """
        return self._polling_method._current_body.update_id  # pylint: disable=protected-access

    @property
    def superseded_by(self) -> Optional[str]:
        """Returns the ID of the operation that superseded this update.

        :return: Returns the ID of the superseding operation, if it exists.
        :rtype: Optional[str]
        """
        return (
            self._polling_method._current_body.superseded_by  # pylint: disable=protected-access
            if self._polling_method._current_body  # pylint: disable=protected-access
            else None
        )

    @classmethod
    def from_continuation_token(
        cls,
        polling_method: AsyncPollingMethod[MemoryStoreUpdateCompletedResult],
        continuation_token: str,
        **kwargs: Any,
    ) -> "AsyncUpdateMemoriesLROPoller":
        """Create a poller from a continuation token.

        :param polling_method: The polling strategy to adopt
        :type polling_method: ~azure.core.polling.PollingMethod
        :param continuation_token: An opaque continuation token
        :type continuation_token: str
        :return: An instance of AsyncUpdateMemoriesLROPoller
        :rtype: AsyncUpdateMemoriesLROPoller
        :raises ~azure.core.exceptions.HttpResponseError: If the continuation token is invalid.
        """
        (
            client,
            initial_response,
            deserialization_callback,
        ) = polling_method.from_continuation_token(continuation_token, **kwargs)

        return cls(client, initial_response, deserialization_callback, polling_method)


class ApiType:
    """API type enumeration for API Center resources."""
    
    MCP = "mcp"
    """Model Context Protocol (MCP) server"""
    REST = "rest"
    """REST API"""
    GRAPHQL = "graphql"
    """GraphQL API"""
    GRPC = "grpc"
    """gRPC API"""
    WEBHOOK = "webhook"
    """Webhook API"""
    SOAP = "soap"
    """SOAP API"""
    WEBSOCKET = "websocket"
    """WebSocket API"""


class ApiCenterApi:
    """Represents an API from Azure API Center.
    
    :ivar id: The API identifier
    :vartype id: str
    :ivar name: The API name
    :vartype name: str
    :ivar type: The API type (MCP, REST, GraphQL, etc.)
    :vartype type: str
    :ivar title: The API title/display name
    :vartype title: Optional[str]
    :ivar description: The API description
    :vartype description: Optional[str]
    :ivar kind: The API kind
    :vartype kind: Optional[str]
    :ivar metadata: Additional API metadata
    :vartype metadata: Optional[Dict[str, Any]]
    """
    
    def __init__(
        self,
        *,
        id: str,
        name: str,
        type: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        kind: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ):
        self.id = id
        self.name = name
        self.type = type
        self.title = title
        self.description = description
        self.kind = kind
        self.metadata = metadata or {}
        self._additional_properties = kwargs
    
    def __repr__(self) -> str:
        return f"ApiCenterApi(id={self.id!r}, name={self.name!r}, type={self.type!r})"


class ApiCenterMcpServer:
    """Represents an MCP server from Azure API Center.
    
    :ivar id: The MCP server identifier
    :vartype id: str
    :ivar name: The MCP server name
    :vartype name: str
    :ivar server_url: The MCP server URL
    :vartype server_url: Optional[str]
    :ivar title: The MCP server title/display name
    :vartype title: Optional[str]
    :ivar description: The MCP server description
    :vartype description: Optional[str]
    :ivar connector_id: Service connector identifier
    :vartype connector_id: Optional[str]
    :ivar metadata: Additional server metadata
    :vartype metadata: Optional[Dict[str, Any]]
    """
    
    def __init__(
        self,
        *,
        id: str,
        name: str,
        server_url: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        connector_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ):
        self.id = id
        self.name = name
        self.server_url = server_url
        self.title = title
        self.description = description
        self.connector_id = connector_id
        self.metadata = metadata or {}
        self._additional_properties = kwargs
    
    def __repr__(self) -> str:
        return f"ApiCenterMcpServer(id={self.id!r}, name={self.name!r}, server_url={self.server_url!r})"


__all__: List[str] = [
    "CustomCredential",
    "UpdateMemoriesLROPollingMethod",
    "AsyncUpdateMemoriesLROPollingMethod",
    "UpdateMemoriesLROPoller",
    "AsyncUpdateMemoriesLROPoller",
    "ApiType",
    "ApiCenterApi",
    "ApiCenterMcpServer",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
