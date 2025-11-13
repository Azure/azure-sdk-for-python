# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Union, Optional, Any, List, overload, IO, cast
from azure.core.tracing.decorator import distributed_trace
from azure.core.polling import NoPolling
from azure.core.utils import case_insensitive_dict
from .. import models as _models
from ..models import (
    MemoryStoreOperationUsage,
    MemoryStoreOperationUsageInputTokensDetails,
    MemoryStoreOperationUsageOutputTokensDetails,
    MemoryStoreUpdateCompletedResult,
    UpdateMemoriesLROPoller,
    UpdateMemoriesLROPollingMethod,
)
from ._operations import JSON, _Unset, ClsType, MemoryStoresOperations as GenerateMemoryStoresOperations
from .._validation import api_version_validation
from .._utils.model_base import _deserialize


class MemoryStoresOperations(GenerateMemoryStoresOperations):

    @overload
    def begin_update_memories(
        self,
        name: str,
        *,
        scope: str,
        content_type: str = "application/json",
        items: Optional[List[_models.ItemParam]] = None,
        previous_update_id: Optional[str] = None,
        update_delay: Optional[int] = None,
        **kwargs: Any,
    ) -> UpdateMemoriesLROPoller:
        """Update memory store with conversation memories.

        :param name: The name of the memory store to update. Required.
        :type name: str
        :keyword scope: The namespace that logically groups and isolates memories, such as a user ID.
         Required.
        :paramtype scope: str
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :keyword items: Conversation items from which to extract memories. Default value is None.
        :paramtype items: list[~azure.ai.projects.models.ItemParam]
        :keyword previous_update_id: The unique ID of the previous update request, enabling incremental
         memory updates from where the last operation left off. Default value is None.
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
         ~azure.ai.projects.models.UpdateMemoriesLROPoller
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def begin_update_memories(
        self, name: str, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> UpdateMemoriesLROPoller:
        """Update memory store with conversation memories.

        :param name: The name of the memory store to update. Required.
        :type name: str
        :param body: Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of UpdateMemoriesLROPoller that returns MemoryStoreUpdateCompletedResult. The
         MemoryStoreUpdateCompletedResult is compatible with MutableMapping
        :rtype:
         ~azure.ai.projects.models.UpdateMemoriesLROPoller
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def begin_update_memories(
        self, name: str, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> UpdateMemoriesLROPoller:
        """Update memory store with conversation memories.

        :param name: The name of the memory store to update. Required.
        :type name: str
        :param body: Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of UpdateMemoriesLROPoller that returns MemoryStoreUpdateCompletedResult. The
         MemoryStoreUpdateCompletedResult is compatible with MutableMapping
        :rtype:
         ~azure.ai.projects.models.UpdateMemoriesLROPoller
        :raises ~azure.core.exceptions.HttpResponseError:
        """

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
        items: Optional[List[_models.ItemParam]] = None,
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
         ~azure.ai.projects.models.UpdateMemoriesLROPoller
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
        cls: ClsType[MemoryStoreUpdateCompletedResult] = kwargs.pop("cls", None)
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

            raw_result.http_response.status_code = 202  # type:  ignore
            raw_result.http_response.headers["Operation-Location"] = (  # type: ignore
                f"{self._config.endpoint}/memory_stores/{name}/updates/{raw_result.http_response.json().get('update_id')}?api-version=2025-11-15-preview"  # type: ignore
            )

        kwargs.pop("error_map", None)

        def get_long_running_output(pipeline_response):
            response_headers = {}
            response = pipeline_response.http_response
            response_headers["Operation-Location"] = self._deserialize(
                "str", response.headers.get("Operation-Location")
            )

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
            polling_method: UpdateMemoriesLROPollingMethod = UpdateMemoriesLROPollingMethod(
                lro_delay, path_format_arguments=path_format_arguments, **kwargs
            )
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
            raw_result,  # type: ignore[possibly-undefined]
            get_long_running_output,
            polling_method,  # pylint: disable=possibly-used-before-assignment
        )
