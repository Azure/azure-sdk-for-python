# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import json
from typing import Any, Callable, Dict, IO, Iterator, Optional, TypeVar, Union, cast, overload
from ._client import ConversationAnalysisClient as AnalysisClientGenerated
from collections.abc import MutableMapping
from ..models import (
    AnalyzeConversationOperationInput,
    AnalyzeConversationOperationState,
)
from azure.core.exceptions import (
    ClientAuthenticationError,
    HttpResponseError,
)
from azure.core.pipeline import PipelineResponse
from azure.core.polling import AsyncLROPoller, AsyncNoPolling, AsyncPollingMethod
from azure.core.polling.async_base_polling import AsyncLROBasePolling
from azure.core.rest import AsyncHttpResponse, HttpRequest
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.utils import case_insensitive_dict

from ._configuration import ConversationAnalysisClientConfiguration
from .._utils.model_base import SdkJSONEncoder, _deserialize, _failsafe_deserialize
from .._utils.serialization import Serializer
from .._utils.utils import ClientMixinABC
from .._validation import api_version_validation

from .._utils.model_base import SdkJSONEncoder, _deserialize, _failsafe_deserialize
from .._utils.utils import ClientMixinABC
from .._validation import api_version_validation
from ._configuration import ConversationAnalysisClientConfiguration

JSON = MutableMapping[str, Any]
T = TypeVar("T")
ClsType = Optional[Callable[[PipelineResponse[HttpRequest, AsyncHttpResponse], T, Dict[str, Any]], Any]]


class ConversationAnalysisClient(AnalysisClientGenerated):

    @overload
    async def begin_analyze_conversation_job(
        self, body: AnalyzeConversationOperationInput, *, content_type: str = "application/json", **kwargs: Any
    ) -> AsyncLROPoller[AnalyzeConversationOperationState]:
        """Analyzes the input conversation utterance.

        :param body: The input for the analyze conversations operation. Required.
        :type body: ~azure.ai.language.conversations.models.AnalyzeConversationOperationInput
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: AsyncLROPoller that returns AnalyzeConversationOperationState (mapping-like).
        :rtype: ~azure.core.polling.AsyncLROPoller[~azure.ai.language.conversations.models.AnalyzeConversationOperationState]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    async def begin_analyze_conversation_job(
        self, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> AsyncLROPoller[AnalyzeConversationOperationState]:
        """Analyzes the input conversation utterance.

        :param body: The input for the analyze conversations operation. Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: AsyncLROPoller that returns AnalyzeConversationOperationState (mapping-like).
        :rtype: ~azure.core.polling.AsyncLROPoller[~azure.ai.language.conversations.models.AnalyzeConversationOperationState]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    async def begin_analyze_conversation_job(
        self, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> AsyncLROPoller[AnalyzeConversationOperationState]:
        """Analyzes the input conversation utterance.

        :param body: The input for the analyze conversations operation. Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: AsyncLROPoller that returns AnalyzeConversationOperationState (mapping-like).
        :rtype: ~azure.core.polling.AsyncLROPoller[~azure.ai.language.conversations.models.AnalyzeConversationOperationState]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace_async
    @api_version_validation(
        method_added_on="2023-04-01",
        params_added_on={"2023-04-01": ["api_version", "content_type", "accept"]},
        api_versions_list=["2023-04-01", "2024-05-01", "2024-11-01", "2024-11-15-preview", "2025-05-15-preview"],
    )
    async def begin_analyze_conversation_job(
        self,
        body: Union["AnalyzeConversationOperationInput", JSON, IO[bytes]],
        **kwargs: Any,
    ) -> AsyncLROPoller[AnalyzeConversationOperationState]:
        """Analyzes the input conversation utterance.

        :param body: The input for the analyze conversations operation. Required.
        :type body: ~azure.ai.language.conversations.models.AnalyzeConversationOperationInput or JSON or IO[bytes]
        :return: AsyncLROPoller that returns AnalyzeConversationOperationState (mapping-like).
        :rtype: ~azure.core.polling.AsyncLROPoller[~azure.ai.language.conversations.models.AnalyzeConversationOperationState]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
        polling: Union[bool, AsyncPollingMethod] = kwargs.pop("polling", True)
        lro_delay = kwargs.pop("polling_interval", self._config.polling_interval)
        cont_token: Optional[str] = kwargs.pop("continuation_token", None)
        cls: Optional[ClsType[AnalyzeConversationOperationState]] = kwargs.pop("cls", None)
        kwargs.pop("error_map", None)

        path_format_arguments = {
            "Endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
        }

        def get_long_running_output(pipeline_response: Any) -> AnalyzeConversationOperationState:
            final_response: AsyncHttpResponse = pipeline_response.http_response  # type: ignore[attr-defined]
            # final body is already read by the polling method; .text() returns a str
            if final_response.status_code == 200:
                data = json.loads(final_response.text())
                deserialized = AnalyzeConversationOperationState(data)
                if cls:
                    return cls(pipeline_response, deserialized, {})  # type: ignore[misc]
                return deserialized
            raise HttpResponseError(response=final_response)

        if polling is True:
            polling_method = cast(
                AsyncPollingMethod,
                AsyncLROBasePolling(lro_delay, path_format_arguments=path_format_arguments, **kwargs),
            )
        elif polling is False:
            from azure.core.polling import AsyncNoPolling
            polling_method = cast(AsyncPollingMethod, AsyncNoPolling())
        else:
            polling_method = polling

        if cont_token:
            return AsyncLROPoller.from_continuation_token(  # type: ignore[return-value]
                polling_method=polling_method,
                continuation_token=cont_token,
                client=self._client,
                deserialization_callback=get_long_running_output,
            )

        # Submit the job
        raw_result = await self._analyze_conversation_job_initial(
            body=body,
            content_type=content_type,
            cls=lambda x, y, z: x,
            headers=_headers,
            params=_params,
            **kwargs,
        )
        # Ensure body buffered so get_long_running_output can synchronously parse
        await raw_result.http_response.read()  # type: ignore[attr-defined]

        return AsyncLROPoller(  # type: ignore[return-value]
            self._client,
            raw_result,
            get_long_running_output,
            polling_method,
        )


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """


__all__ = ["ConversationAnalysisClient"]