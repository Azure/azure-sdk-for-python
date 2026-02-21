# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import json
from typing import Any, Callable, Dict, IO, Mapping, Optional, TypeVar, Union, cast, overload, Generic, TYPE_CHECKING
from collections.abc import MutableMapping  # pylint:disable=import-error
from urllib.parse import urlparse
from azure.core.exceptions import (
    HttpResponseError,
)
from azure.core.pipeline import PipelineResponse
from azure.core.polling import AsyncLROPoller, AsyncNoPolling, AsyncPollingMethod
from azure.core.polling.async_base_polling import AsyncLROBasePolling
from azure.core.rest import AsyncHttpResponse, HttpRequest
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.utils import case_insensitive_dict
from azure.core.credentials import AzureKeyCredential
from azure.core.async_paging import AsyncItemPaged
from ._client import ConversationAnalysisClient as AnalysisClientGenerated
from ..models import AnalyzeConversationOperationInput, AnalyzeConversationOperationState, ConversationActions

from .._validation import api_version_validation

if TYPE_CHECKING:
    from azure.core.credentials_async import AsyncTokenCredential

JSON = MutableMapping[str, Any]
T = TypeVar("T")
ClsType = Optional[Callable[[PipelineResponse[HttpRequest, AsyncHttpResponse], T, Dict[str, Any]], Any]]


def _parse_operation_id(op_loc: Optional[str]) -> Optional[str]:
    """Extract the operation ID from an Operation-Location URL.

    :param op_loc: The ``Operation-Location`` header value or URL to parse.
        If ``None`` or malformed, no ID can be extracted.
    :type op_loc: Optional[str]
    :return: The trailing path segment as the operation ID, or ``None`` if not found.
    :rtype: Optional[str]
    """
    if not op_loc:
        return None
    path = urlparse(op_loc).path.rstrip("/")
    if "/" not in path:
        return None
    return path.rsplit("/", 1)[-1]


PollingReturnType_co = TypeVar("PollingReturnType_co", covariant=True)


class AnalyzeConversationAsyncLROPoller(AsyncLROPoller[PollingReturnType_co], Generic[PollingReturnType_co]):
    """Async poller that returns PollingReturnType_co and exposes operation metadata."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        # populated by your deserialization callback in begin_*_async
        self._last_state: Optional["AnalyzeConversationOperationState"] = None

    def _record_state_for_details(self, state: "AnalyzeConversationOperationState") -> None:
        """Internal: update the state used by ``.details``.

        :param state: The latest operation state to expose via ``details``.
        :type state: AnalyzeConversationOperationState
        :return: None
        :rtype: None
        """
        self._last_state = state

    @property
    def details(self) -> Mapping[str, Any]:
        """Metadata associated with the long-running operation.

        :return: A mapping with keys like ``operation_id`` and, when available,
            ``status``, ``job_id``, ``display_name``, ``created_date_time``,
            ``last_updated_date_time``, ``expiration_date_time``, ``statistics``,
            ``errors``, and ``next_link``.
        :rtype: Mapping[str, Any]
        """
        try:
            headers = getattr(self.polling_method(), "_initial_response").http_response.headers  # type: ignore[attr-defined]
            op_loc = headers.get("Operation-Location") or headers.get("operation-location")
        except (AttributeError, TypeError):
            # missing attributes in the chain, or headers is not a mapping
            op_loc = None

        info: Dict[str, Any] = {"operation_id": _parse_operation_id(op_loc)}

        # Enrich from final state if available
        if self._last_state is not None:
            s = self._last_state
            info.update(
                {
                    "status": s.status,
                    "job_id": s.job_id,
                    "display_name": s.display_name,
                    "created_date_time": s.created_date_time,
                    "last_updated_date_time": s.last_updated_date_time,
                    "expiration_date_time": s.expiration_date_time,
                    "statistics": s.statistics,
                    "errors": s.errors,
                    "next_link": s.next_link,
                }
            )
        return info

    @classmethod
    def from_continuation_token(
        cls,
        polling_method: AsyncPollingMethod[PollingReturnType_co],
        continuation_token: str,
        **kwargs: Any,
    ) -> "AnalyzeConversationAsyncLROPoller[PollingReturnType_co]":
        client, initial_response, deserialization_callback = polling_method.from_continuation_token(
            continuation_token, **kwargs
        )
        return cls(client, initial_response, deserialization_callback, polling_method)


class ConversationAnalysisClient(AnalysisClientGenerated):

    def __init__(
        self,
        endpoint: str,
        credential: Union[AzureKeyCredential, "AsyncTokenCredential"],
        *,
        api_version: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Create a ConversationAnalysisClient.
        :param endpoint: Supported Cognitive Services endpoint.
        :type endpoint: str
        :param credential: Key or token credential.
        :type credential: ~azure.core.credentials.AzureKeyCredential or ~azure.core.credentials.TokenCredential
        :keyword api_version: The API version to use for this operation. Default value is
        "2025-11-15-preview". Note that overriding this default value may result in unsupported
        behavior.
        :paramtype api_version: str`
        """
        if api_version is not None:
            kwargs["api_version"] = api_version
        super().__init__(endpoint=endpoint, credential=credential, **kwargs)

    @overload
    async def begin_analyze_conversation_job(
        self, body: AnalyzeConversationOperationInput, *, content_type: str = "application/json", **kwargs: Any
    ) -> AnalyzeConversationAsyncLROPoller[AsyncItemPaged["ConversationActions"]]:
        """Analyzes the input conversation utterance.

        :param body: The input for the analyze conversations operation. Required.
        :type body: ~azure.ai.language.conversations.models.AnalyzeConversationOperationInput
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: An async poller whose ``result()`` yields ``AsyncItemPaged[ConversationActions]``; exposes metadata via ``.details``.
        :rtype: ~azure.ai.language.conversations.AnalyzeConversationAsyncLROPoller[
                ~azure.core.async_paging.AsyncItemPaged[~azure.ai.language.conversations.models.ConversationActions]]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    async def begin_analyze_conversation_job(
        self, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> AnalyzeConversationAsyncLROPoller[AsyncItemPaged["ConversationActions"]]:
        """Analyzes the input conversation utterance.

        :param body: The input for the analyze conversations operation. Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: An async poller whose ``result()`` yields ``AsyncItemPaged[ConversationActions]``; exposes metadata via ``.details``.
        :rtype: ~azure.ai.language.conversations.AnalyzeConversationAsyncLROPoller[
                ~azure.core.async_paging.AsyncItemPaged[~azure.ai.language.conversations.models.ConversationActions]]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    async def begin_analyze_conversation_job(
        self, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> AnalyzeConversationAsyncLROPoller[AsyncItemPaged["ConversationActions"]]:
        """Analyzes the input conversation utterance.

        :param body: The input for the analyze conversations operation. Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: An async poller whose ``result()`` yields ``AsyncItemPaged[ConversationActions]``; exposes metadata via ``.details``.
        :rtype: ~azure.ai.language.conversations.AnalyzeConversationAsyncLROPoller[
                ~azure.core.async_paging.AsyncItemPaged[~azure.ai.language.conversations.models.ConversationActions]]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace_async
    @api_version_validation(
        method_added_on="2023-04-01",
        params_added_on={"2023-04-01": ["api_version", "content_type", "accept"]},
        api_versions_list=["2023-04-01", "2024-05-01", "2024-11-01", "2025-05-15-preview", "2025-11-15-preview"],
    )
    async def begin_analyze_conversation_job(  # type: ignore[override]
        self, body: Union[AnalyzeConversationOperationInput, JSON, IO[bytes]], **kwargs: Any
    ) -> AnalyzeConversationAsyncLROPoller[AsyncItemPaged["ConversationActions"]]:
        """Analyzes the input conversation utterance.

        :param body: The input for the analyze conversations operation. Required.
        :type body: ~azure.ai.language.conversations.models.AnalyzeConversationOperationInput or JSON or IO[bytes]
        :return: An async poller whose ``result()`` yields ``AsyncItemPaged[ConversationActions]``; exposes metadata via ``.details``.
        :rtype: ~azure.ai.language.conversations.AnalyzeConversationAsyncLROPoller[
                ~azure.core.async_paging.AsyncItemPaged[~azure.ai.language.conversations.models.ConversationActions]]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
        polling: Union[bool, AsyncPollingMethod[AsyncItemPaged["ConversationActions"]]] = kwargs.pop("polling", True)
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

        def _build_pager_from_state(state: AnalyzeConversationOperationState) -> AsyncItemPaged["ConversationActions"]:
            async def extract_data(s: AnalyzeConversationOperationState):
                next_link = s.next_link
                actions: ConversationActions = s.actions
                return next_link, [actions]

            async def get_next(token: Optional[str]) -> Optional[AnalyzeConversationOperationState]:
                if token is None:
                    return state
                if not token:
                    return None
                return await _fetch_state_by_next_link(token)

            return AsyncItemPaged(get_next, extract_data)

        # holder to let the deserializer set poller._last_state
        poller_holder: Dict[str, AnalyzeConversationAsyncLROPoller[AsyncItemPaged["ConversationActions"]]] = {}

        # ---- deserializer: final HTTP -> AsyncItemPaged[ConversationActions]
        def get_long_running_output(pipeline_response):
            final = pipeline_response.http_response
            if final.status_code == 200:
                data = json.loads(final.text())
                op_state = AnalyzeConversationOperationState(data)

                poller_ref = poller_holder["poller"]
                poller_ref._record_state_for_details(op_state) # pylint:disable=protected-access

                paged = _build_pager_from_state(op_state)
                return cls(pipeline_response, paged, {}) if cls else paged
            raise HttpResponseError(response=final)

        # ---- polling method
        if polling is True:
            polling_method: AsyncPollingMethod[AsyncItemPaged["ConversationActions"]] = cast(
                AsyncPollingMethod[AsyncItemPaged["ConversationActions"]],
                AsyncLROBasePolling(lro_delay, path_format_arguments=path_format_arguments, **kwargs),
            )
        elif polling is False:
            polling_method = cast(AsyncPollingMethod[AsyncItemPaged["ConversationActions"]], AsyncNoPolling())
        else:
            polling_method = cast(AsyncPollingMethod[AsyncItemPaged["ConversationActions"]], polling)

        # ---- resume path
        if cont_token:
            return AnalyzeConversationAsyncLROPoller[AsyncItemPaged["ConversationActions"]].from_continuation_token(
                polling_method=polling_method,
                continuation_token=cont_token,
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
        lro: AnalyzeConversationAsyncLROPoller[AsyncItemPaged["ConversationActions"]] = (
            AnalyzeConversationAsyncLROPoller(self._client, raw_result, get_long_running_output, polling_method)
        )
        poller_holder["poller"] = lro
        return lro


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """


__all__ = ["ConversationAnalysisClient", "AnalyzeConversationAsyncLROPoller"]
