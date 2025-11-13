# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

from typing import IO, Any, List, Optional, Tuple, Union, cast

from azure.core.polling import LROPoller, NoPolling, PollingMethod
from azure.core.polling.base_polling import (
    LROBasePolling,
    OperationFailed,
    _raise_if_bad_http_status_and_method,
)
from azure.core.tracing.decorator import distributed_trace
from azure.core.utils import case_insensitive_dict

from .._utils.model_base import _deserialize
from .._validation import api_version_validation
from ..models import (
    ItemParam,
    MemoryStoreOperationUsage,
    MemoryStoreOperationUsageInputTokensDetails,
    MemoryStoreOperationUsageOutputTokensDetails,
    MemoryStoreUpdateCompletedResult,
    MemoryStoreUpdateResult,
)
from ._operations import (
    JSON,
    ClsType,
    MemoryStoresOperations as GenerateMemoryStoresOperations,
    _Unset,
)
from ._patch_connections import ConnectionsOperations
from ._patch_datasets import DatasetsOperations
from ._patch_telemetry import TelemetryOperations

_FINISHED = frozenset(["completed", "superseded"])
_FAILED = frozenset(["failed"])


class UpdateMemoriesLROPoller(LROPoller[MemoryStoreUpdateCompletedResult]):
    """Custom LROPoller for Memory Store update operations."""

    _polling_method: "UpdateMemoriesLROPollingMethod"

    @property
    def update_id(self) -> str:
        """Returns the update ID associated with the long-running update memories operation.

        :return: Returns the update ID.
        :rtype: str
        """
        return self._polling_method._current_body.update_id

    @property
    def superseded_by(self) -> Optional[str]:
        """Returns the ID of the operation that superseded this update.

        :return: Returns the ID of the superseding operation, if it exists.
        :rtype: Optional[str]
        """
        # pylint: disable=protected-access
        return self._polling_method._current_body.superseded_by if self._polling_method._current_body else None

    @classmethod
    def from_continuation_token(cls, polling_method: PollingMethod[MemoryStoreUpdateCompletedResult], continuation_token: str, **kwargs: Any) -> "UpdateMemoriesLROPoller":
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


class MemoryStoresOperations(GenerateMemoryStoresOperations):
    @distributed_trace
    @api_version_validation(
        method_added_on="2025-11-15-preview",
        params_added_on={"2025-11-15-preview": ["api_version", "name", "content_type", "accept"]},
        api_versions_list=["2025-11-15-preview"],
    )
    def begin_update_memories(
        self,
        name: str,
        body: Union[JSON, IO[bytes]] = _Unset,
        *,
        scope: str = _Unset,
        conversation_id: Optional[str] = None,
        items: Optional[List[ItemParam]] = None,
        previous_update_id: Optional[str] = None,
        update_delay: Optional[int] = None,
        **kwargs: Any,
    ) -> UpdateMemoriesLROPoller:
        """Update memory store with conversation memories.

        :param name: The name of the memory store to update. Required.
        :type name: str
        :param body: Is either a JSON type or a IO[bytes] type. Required.
        :type body: JSON or IO[bytes]
        :keyword scope: The namespace that logically groups and isolates memories, such as a user ID.
         Required.
        :paramtype scope: str
        :keyword conversation_id: The conversation ID from which to extract memories. Only one of
         conversation_id or items should be provided. Default value is None.
        :paramtype conversation_id: str
        :keyword items: Conversation items from which to extract memories. Only one of conversation_id
         or items should be provided. Default value is None.
        :paramtype items: list[~azure.ai.projects.models.ItemParam]
        :keyword previous_update_id: The unique ID of the previous update request, enabling incremental
         memory updates from where the last operation left off. Cannot be used together with
         conversation_id. Default value is None.
        :paramtype previous_update_id: str
        :keyword update_delay: Timeout period before processing the memory update in seconds.
         If a new update request is received during this period, it will cancel the current request and
         reset the timeout.
         Set to 0 to immediately trigger the update without delay.
         Defaults to 300 (5 minutes). Default value is None.
        :paramtype update_delay: int
        :return: An instance of UpdateMemoriesLROPoller that returns MemoryStoreUpdateCompletedResult. The
         MemoryStoreUpdateCompletedResult is compatible with MutableMapping
        :rtype:
         ~~azure.ai.projects.operations.UpdateMemoriesLROPoller
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
        cls: ClsType[MemoryStoreUpdateResult] = kwargs.pop("cls", None)
        polling: Union[bool, UpdateMemoriesLROPollingMethod] = kwargs.pop("polling", True)
        lro_delay = kwargs.pop("polling_interval", self._config.polling_interval)
        cont_token: Optional[str] = kwargs.pop("continuation_token", None)
        if cont_token is None:
            raw_result = self._update_memories_initial(
                name=name,
                body=body,
                scope=scope,
                conversation_id=conversation_id,
                items=items,
                previous_update_id=previous_update_id,
                update_delay=update_delay,
                content_type=content_type,
                cls=lambda x, y, z: x,
                headers=_headers,
                params=_params,
                **kwargs,
            )
            raw_result.http_response.read()  # type: ignore

            raw_result.http_response.status_code = 202
            raw_result.http_response.headers["Operation-Location"] = (
                f"{self._config.endpoint}/memory_stores/{name}/updates/{raw_result.http_response.json().get('update_id')}?api-version=2025-11-15-preview"
            )

        kwargs.pop("error_map", None)

        def get_long_running_output(pipeline_response):
            response_headers = {}
            response = pipeline_response.http_response
            response_headers["Operation-Location"] = self._deserialize("str", response.headers.get("Operation-Location"))

            deserialized = _deserialize(MemoryStoreUpdateCompletedResult, response.json().get("result", None))
            if deserialized is None:
                usage = MemoryStoreOperationUsage(
                    embedding_tokens=0,
                    input_tokens=0,
                    input_tokens_details=MemoryStoreOperationUsageInputTokensDetails(cached_tokens=0),
                    output_tokens=0,
                    output_tokens_details=MemoryStoreOperationUsageOutputTokensDetails(reasoning_tokens=0),
                    total_tokens=0,
                )
                deserialized = MemoryStoreUpdateCompletedResult(memory_operations=[], usage=usage)
            if cls:
                return cls(pipeline_response, deserialized, response_headers)  # type: ignore
            return deserialized

        path_format_arguments = {
            "endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
        }

        if polling is True:
            polling_method: UpdateMemoriesLROPollingMethod = UpdateMemoriesLROPollingMethod(lro_delay, path_format_arguments=path_format_arguments, **kwargs)
        elif polling is False:
            polling_method = cast(UpdateMemoriesLROPollingMethod, NoPolling())
        else:
            polling_method = polling
        if cont_token:
            return UpdateMemoriesLROPoller.from_continuation_token(
                polling_method=polling_method,
                continuation_token=cont_token,
                client=self._client,
                deserialization_callback=get_long_running_output,
            )
        return UpdateMemoriesLROPoller(
            self._client,
            raw_result,
            get_long_running_output,
            polling_method,  # pylint: disable=possibly-used-before-assignment
        )


__all__: List[str] = [
    "TelemetryOperations",
    "DatasetsOperations",
    "ConnectionsOperations",
    "UpdateMemoriesLROPoller",
    "MemoryStoresOperations",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
