# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List, Dict, Optional, Any, Tuple, overload, Mapping, Literal
from azure.core.polling import LROPoller, AsyncLROPoller, PollingMethod, AsyncPollingMethod
from azure.core.polling.base_polling import (
    LROBasePolling,
    OperationFailed,
    _raise_if_bad_http_status_and_method,
)
from azure.core.polling.async_base_polling import AsyncLROBasePolling
from ._enums import TextResponseFormatConfigurationType
from ._models import TextResponseFormatConfiguration, CustomCredential as CustomCredentialGenerated
from ..models import MemoryStoreUpdateCompletedResult, MemoryStoreUpdateResult
from .._utils.model_base import rest_discriminator, rest_field


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


# Patched in order to set of type of "schema" to dict[str, Any] instead of ResponseFormatJsonSchemaSchema
class TextResponseFormatJsonSchema(TextResponseFormatConfiguration, discriminator="json_schema"):
    """JSON schema.

    :ivar type: The type of response format being defined. Always ``json_schema``. Required.
    :vartype type: str or ~azure.ai.projects.models.JSON_SCHEMA
    :ivar description: A description of what the response format is for, used by the model to
       determine how to respond in the format.
    :vartype description: str
    :ivar name: The name of the response format. Must be a-z, A-Z, 0-9, or contain
       underscores and dashes, with a maximum length of 64. Required.
    :vartype name: str
    :ivar schema: Required.
    :vartype schema: ~azure.ai.projects.models.ResponseFormatJsonSchemaSchema
    :ivar strict:
    :vartype strict: bool
    """

    type: Literal[TextResponseFormatConfigurationType.JSON_SCHEMA] = rest_discriminator(name="type", visibility=["read", "create", "update", "delete", "query"])  # type: ignore
    """The type of response format being defined. Always ``json_schema``. Required."""
    description: Optional[str] = rest_field(visibility=["read", "create", "update", "delete", "query"])
    """A description of what the response format is for, used by the model to
       determine how to respond in the format."""
    name: str = rest_field(visibility=["read", "create", "update", "delete", "query"])
    """The name of the response format. Must be a-z, A-Z, 0-9, or contain
       underscores and dashes, with a maximum length of 64. Required."""
    schema: dict[str, Any] = rest_field(visibility=["read", "create", "update", "delete", "query"])
    """Required."""
    strict: Optional[bool] = rest_field(visibility=["read", "create", "update", "delete", "query"])

    @overload
    def __init__(
        self,
        *,
        name: str,
        schema: dict[str, Any],
        description: Optional[str] = None,
        strict: Optional[bool] = None,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.type = TextResponseFormatConfigurationType.JSON_SCHEMA  # type: ignore


__all__: List[str] = [
    "CustomCredential",
    "UpdateMemoriesLROPollingMethod",
    "AsyncUpdateMemoriesLROPollingMethod",
    "UpdateMemoriesLROPoller",
    "AsyncUpdateMemoriesLROPoller",
    "TextResponseFormatJsonSchema",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
