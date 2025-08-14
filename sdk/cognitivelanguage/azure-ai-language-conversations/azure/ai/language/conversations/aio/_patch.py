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
    ConversationActions
)
from azure.core.polling import AsyncNoPolling
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
from azure.core.async_paging import AsyncItemPaged

from ._configuration import ConversationAnalysisClientConfiguration
from .._utils.model_base import SdkJSONEncoder, _deserialize, _failsafe_deserialize
from .._utils.serialization import Serializer
from .._utils.utils import ClientMixinABC
from .._validation import api_version_validation

from .._utils.model_base import SdkJSONEncoder, _deserialize, _failsafe_deserialize
from .._utils.utils import ClientMixinABC
from .._validation import api_version_validation
from ._configuration import ConversationAnalysisClientConfiguration

from ._operations import (
    AnalyzeConversationAsyncLROPoller
)

JSON = MutableMapping[str, Any]
T = TypeVar("T")
ClsType = Optional[Callable[[PipelineResponse[HttpRequest, AsyncHttpResponse], T, Dict[str, Any]], Any]]


class ConversationAnalysisClient(AnalysisClientGenerated):

    @overload
    async def begin_analyze_conversation_job(
        self, body: AnalyzeConversationOperationInput, *, content_type: str = "application/json", **kwargs: Any
    ) -> AnalyzeConversationAsyncLROPoller:
        """Analyzes the input conversation utterance.

        :param body: The input for the analyze conversations operation. Required.
        :type body: ~azure.ai.language.conversations.models.AnalyzeConversationOperationInput
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: An async poller whose ``result()`` yields AsyncItemPaged[ConversationActions]; exposes metadata via ``.details``.
        :rtype: ~azure.core.polling.AsyncLROPoller[~azure.core.async_paging.AsyncItemPaged[~azure.ai.language.conversations.models.ConversationActions]]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    async def begin_analyze_conversation_job(
        self, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> AnalyzeConversationAsyncLROPoller:
        """Analyzes the input conversation utterance.

        :param body: The input for the analyze conversations operation. Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: An async poller whose ``result()`` yields AsyncItemPaged[ConversationActions]; exposes metadata via ``.details``.
        :rtype: ~azure.core.polling.AsyncLROPoller[~azure.core.async_paging.AsyncItemPaged[~azure.ai.language.conversations.models.ConversationActions]]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    async def begin_analyze_conversation_job(
        self, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> AnalyzeConversationAsyncLROPoller:
        """Analyzes the input conversation utterance.

        :param body: The input for the analyze conversations operation. Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: An async poller whose ``result()`` yields AsyncItemPaged[ConversationActions]; exposes metadata via ``.details``.
        :rtype: ~azure.core.polling.AsyncLROPoller[~azure.core.async_paging.AsyncItemPaged[~azure.ai.language.conversations.models.ConversationActions]]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace_async
    @api_version_validation(
        method_added_on="2023-04-01",
        params_added_on={"2023-04-01": ["api_version", "content_type", "accept"]},
        api_versions_list=["2023-04-01", "2024-05-01", "2024-11-01", "2024-11-15-preview", "2025-05-15-preview"],
    )
    async def begin_analyze_conversation_job(  # type: ignore[override]
        self, body: Union[AnalyzeConversationOperationInput, JSON, IO[bytes]], **kwargs: Any
    ) -> AnalyzeConversationAsyncLROPoller:
        """Analyzes the input conversation utterance.

        :param body: The input for the analyze conversations operation. Required.
        :type body: ~azure.ai.language.conversations.models.AnalyzeConversationOperationInput or JSON or IO[bytes]
        :return: An async poller whose ``result()`` yields AsyncItemPaged[ConversationActions]; exposes metadata via ``.details``.
        :rtype: ~azure.core.polling.AsyncLROPoller[~azure.core.async_paging.AsyncItemPaged[~azure.ai.language.conversations.models.ConversationActions]]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
        polling: Union[bool, AsyncPollingMethod] = kwargs.pop("polling", True)
        lro_delay = kwargs.pop("polling_interval", self._config.polling_interval)
        cont_token: Optional[str] = kwargs.pop("continuation_token", None)
        cls = kwargs.pop("cls", None)  # optional custom deserializer
        kwargs.pop("error_map", None)

        path_format_arguments = {
            "Endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
        }

        # ---- paging helpers (state -> AsyncItemPaged[ConversationActions])

        async def _fetch_state_by_next_link(next_link: str) -> AnalyzeConversationOperationState:
            req = HttpRequest("GET", next_link)
            resp = await self._client.send_request(req)  # type: ignore[attr-defined]
            if resp.status_code != 200:
                raise HttpResponseError(response=resp)
            await resp.read()
            data = json.loads(resp.text())
            return AnalyzeConversationOperationState(data)

        def _build_pager_from_state(
            state: AnalyzeConversationOperationState,
        ) -> AsyncItemPaged[ConversationActions]:
            # Convert a state into (next_link, items)
            async def extract_data(s: AnalyzeConversationOperationState):
                next_link = s.next_link
                actions: ConversationActions = s.actions
                return next_link, [actions]

            # Async fetch next state. First call (token is None) returns the initial state.
            async def get_next(token: Optional[str]) -> Optional[AnalyzeConversationOperationState]:
                if token is None:
                    return state
                if not token:
                    return None
                return await _fetch_state_by_next_link(token)

            return AsyncItemPaged(get_next, extract_data)

        # holder to let the deserializer set poller._last_state
        poller_holder: dict[str, AnalyzeConversationAsyncLROPoller] = {}

        # ---- deserializer: final HTTP -> AsyncItemPaged[ConversationActions]
        def get_long_running_output(pipeline_response):
            final = pipeline_response.http_response
            if final.status_code == 200:
                data = json.loads(final.text())
                op_state = AnalyzeConversationOperationState(data)

                poller_ref = poller_holder["poller"]
                poller_ref._last_state = op_state  # type: ignore[attr-defined]

                paged = _build_pager_from_state(op_state)
                return cls(pipeline_response, paged, {}) if cls else paged
            raise HttpResponseError(response=final)

        # ---- polling method
        if polling is True:
            polling_method: AsyncPollingMethod = AsyncLROBasePolling(
                lro_delay, path_format_arguments=path_format_arguments, **kwargs
            )
        elif polling is False:
            polling_method = cast(AsyncPollingMethod, AsyncNoPolling())
        else:
            polling_method = cast(AsyncPollingMethod, polling)

        # ---- resume path
        if cont_token:
            return AnalyzeConversationAsyncLROPoller.from_continuation_token(
                polling_method=polling_method, continuation_token=cont_token
            )

        # ---- submit job
        raw_result = await self._analyze_conversation_job_initial(
            body=body,
            content_type=content_type,
            cls=lambda x, y, z: x,  # passthrough
            headers=_headers,
            params=_params,
            **kwargs,
        )
        # buffer initial body so .text() is available later
        await raw_result.http_response.read()  # type: ignore[attr-defined]

        # ---- build custom async poller
        lro: AnalyzeConversationAsyncLROPoller = AnalyzeConversationAsyncLROPoller(
            self._client, raw_result, get_long_running_output, polling_method
        )
        poller_holder["poller"] = lro
        return lro


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """


__all__ = ["ConversationAnalysisClient"]