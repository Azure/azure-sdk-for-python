# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

import json
from collections.abc import MutableMapping  # pylint:disable=import-error
from typing import Any, Callable, Dict, Generic, IO, Mapping, Optional, TypeVar, Union, cast, overload

from azure.core.async_paging import AsyncItemPaged
from azure.core.exceptions import HttpResponseError
from azure.core.pipeline import PipelineResponse
from azure.core.polling import AsyncLROPoller, AsyncNoPolling, AsyncPollingMethod
from azure.core.rest import AsyncHttpResponse, HttpRequest
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.utils import case_insensitive_dict

from ... import models as _models
from ._operations import _AnalyzeDocumentsClientOperationsMixin as GeneratedAnalyzeDocumentsClientOperationsMixin
from .._lro import AnalyzeDocumentsAsyncLROPollingMethod

JSON = MutableMapping[str, Any]
T = TypeVar("T")
PollingReturnType_co = TypeVar("PollingReturnType_co", covariant=True)
ClsType = Optional[Callable[[PipelineResponse[HttpRequest, AsyncHttpResponse], T, Dict[str, Any]], Any]]


def _parse_operation_id(op_loc: Optional[str]) -> Optional[str]:
    if not op_loc:
        return None
    path = op_loc.rstrip("/")
    if "/" not in path:
        return path
    return path.rsplit("/", 1)[-1]


class AnalyzeDocumentsAsyncLROPoller(AsyncLROPoller[PollingReturnType_co], Generic[PollingReturnType_co]):
    """Custom async poller that returns document analysis task results and exposes operation metadata."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._last_state: Optional[_models.AnalyzeDocumentsJobState] = None

    def _record_state_for_details(self, state: _models.AnalyzeDocumentsJobState) -> None:
        self._last_state = state

    @property
    def details(self) -> Mapping[str, Any]:
        """Metadata associated with the long-running operation.

        :return: Metadata associated with the long-running operation.
        :rtype: Mapping[str, Any]
        """
        try:
            headers = getattr(  # type: ignore[attr-defined]
                self.polling_method(),
                "_initial_response",
            ).http_response.headers
            op_loc = headers.get("Operation-Location") or headers.get("operation-location")
        except (AttributeError, TypeError):
            op_loc = None

        info: Dict[str, Any] = {"operation_id": _parse_operation_id(op_loc)}
        if self._last_state is not None:
            state = self._last_state
            info.update(
                {
                    "status": state.status,
                    "job_id": state.job_id,
                    "display_name": state.display_name,
                    "created_date_time": state.created_date_time,
                    "last_updated_date_time": state.last_updated_date_time,
                    "expiration_date_time": state.expiration_date_time,
                    "statistics": state.statistics,
                    "errors": state.errors,
                    "next_link": state.next_link,
                }
            )
        return info

    @classmethod
    def from_continuation_token(
        cls,
        polling_method: AsyncPollingMethod[PollingReturnType_co],
        continuation_token: str,
        **kwargs: Any,
    ) -> "AnalyzeDocumentsAsyncLROPoller[PollingReturnType_co]":
        client, initial_response, deserialization_callback = polling_method.from_continuation_token(
            continuation_token, **kwargs
        )
        return cls(client, initial_response, deserialization_callback, polling_method)


class _AnalyzeDocumentsClientOperationsMixin(GeneratedAnalyzeDocumentsClientOperationsMixin):
    @overload  # type: ignore[override]
    async def begin_submit_job(
        self, body: _models.AnalyzeDocumentsJob, *, content_type: str = "application/json", **kwargs: Any
    ) -> AnalyzeDocumentsAsyncLROPoller[AsyncItemPaged[_models.Tasks]]:
        ...

    @overload  # type: ignore[override]
    async def begin_submit_job(
        self, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> AnalyzeDocumentsAsyncLROPoller[AsyncItemPaged[_models.Tasks]]:
        ...

    @overload  # type: ignore[override]
    async def begin_submit_job(
        self, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> AnalyzeDocumentsAsyncLROPoller[AsyncItemPaged[_models.Tasks]]:
        ...

    @distributed_trace_async
    async def begin_submit_job(  # type: ignore[override]
        self,
        body: Union[_models.AnalyzeDocumentsJob, JSON, IO[bytes]],
        **kwargs: Any
    ) -> AnalyzeDocumentsAsyncLROPoller[AsyncItemPaged[_models.Tasks]]:
        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
        polling: Union[bool, AsyncPollingMethod[AsyncItemPaged[_models.Tasks]]] = kwargs.pop("polling", True)
        if polling is False:
            raise ValueError("polling=False is not supported for this long-running operation.")
        lro_delay = kwargs.pop("polling_interval", self._config.polling_interval)
        cont_token: Optional[str] = kwargs.pop("continuation_token", None)
        cls: ClsType[AsyncItemPaged[_models.Tasks]] = kwargs.pop("cls", None)
        kwargs.pop("error_map", None)

        path_format_arguments = {
            "Endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
        }

        async def _fetch_state_by_next_link(next_link: str) -> _models.AnalyzeDocumentsJobState:
            req = HttpRequest("GET", next_link)
            resp = await self._client.send_request(req)  # type: ignore[attr-defined]
            if resp.status_code != 200:
                raise HttpResponseError(response=resp)
            return _models.AnalyzeDocumentsJobState(json.loads(resp.text()))

        def _build_pager_from_state(state: _models.AnalyzeDocumentsJobState) -> AsyncItemPaged[_models.Tasks]:
            async def extract_data(s: _models.AnalyzeDocumentsJobState):
                next_link = s.next_link
                tasks_payload = s.tasks
                return next_link, [tasks_payload]

            async def get_next(token: Optional[str]) -> Optional[_models.AnalyzeDocumentsJobState]:
                if token is None:
                    return state
                if not token:
                    return None
                return await _fetch_state_by_next_link(token)

            return AsyncItemPaged(get_next, extract_data)

        poller_holder: Dict[str, AnalyzeDocumentsAsyncLROPoller[AsyncItemPaged[_models.Tasks]]] = {}

        def get_long_running_output(
            pipeline_response: PipelineResponse[HttpRequest, AsyncHttpResponse]
        ) -> AsyncItemPaged[_models.Tasks]:
            final_response = pipeline_response.http_response
            if final_response.status_code == 200:
                op_state = _models.AnalyzeDocumentsJobState(json.loads(final_response.text()))

                poller_ref = poller_holder.get("poller")
                if poller_ref is not None:
                    poller_ref._record_state_for_details(op_state)  # pylint: disable=protected-access

                paged = _build_pager_from_state(op_state)
                return cls(pipeline_response, paged, {}) if cls else paged

            raise HttpResponseError(response=final_response)

        if polling is True:
            polling_method: AsyncPollingMethod[AsyncItemPaged[_models.Tasks]] = cast(
                AsyncPollingMethod[AsyncItemPaged[_models.Tasks]],
                AnalyzeDocumentsAsyncLROPollingMethod(
                    lro_delay,
                    path_format_arguments=path_format_arguments,
                    **kwargs
                ),
            )
        elif polling is False:
            polling_method = cast(AsyncPollingMethod[AsyncItemPaged[_models.Tasks]], AsyncNoPolling())
        else:
            polling_method = cast(AsyncPollingMethod[AsyncItemPaged[_models.Tasks]], polling)

        if cont_token is not None:
            lro_from_token = AnalyzeDocumentsAsyncLROPoller[AsyncItemPaged[_models.Tasks]].from_continuation_token(
                polling_method=polling_method,
                continuation_token=cont_token,
                client=self._client,
                deserialization_callback=get_long_running_output,
            )
            poller_holder["poller"] = lro_from_token
            return lro_from_token

        raw_result = await self._submit_job_initial(
            body=body,
            content_type=content_type,
            cls=lambda x, y, z: x,
            headers=_headers,
            params=_params,
            **kwargs
        )
        await raw_result.http_response.read()  # type: ignore[attr-defined]

        lro: AnalyzeDocumentsAsyncLROPoller[AsyncItemPaged[_models.Tasks]] = AnalyzeDocumentsAsyncLROPoller(
            self._client, raw_result, get_long_running_output, polling_method
        )
        poller_holder["poller"] = lro
        return lro

    @distributed_trace_async
    async def begin_cancel_job(self, job_id: str, **kwargs: Any) -> AsyncLROPoller[None]:
        _headers = kwargs.pop("headers", {}) or {}
        _params = kwargs.pop("params", {}) or {}

        cls = kwargs.pop("cls", None)
        polling: Union[bool, AsyncPollingMethod] = kwargs.pop("polling", True)
        lro_delay = kwargs.pop("polling_interval", self._config.polling_interval)
        cont_token = kwargs.pop("continuation_token", None)

        kwargs.pop("error_map", None)

        def get_long_running_output(pipeline_response):
            if cls:
                return cls(pipeline_response, None, {})
            return None

        path_format_arguments = {
            "Endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
        }

        if polling is True:
            polling_method = cast(
                AsyncPollingMethod,
                AnalyzeDocumentsAsyncLROPollingMethod(
                    lro_delay,
                    path_format_arguments=path_format_arguments,
                    **kwargs
                ),
            )
        elif polling is False:
            polling_method = cast(AsyncPollingMethod, AsyncNoPolling())
        else:
            polling_method = polling

        if cont_token is not None:
            return AsyncLROPoller[None].from_continuation_token(
                polling_method=polling_method,
                continuation_token=cont_token,
                client=self._client,
                deserialization_callback=get_long_running_output,
            )

        raw_result = await self._cancel_job_initial(
            job_id=job_id,
            cls=lambda x, y, z: x,
            headers=_headers,
            params=_params,
            **kwargs
        )
        await raw_result.http_response.read()  # type: ignore[attr-defined]

        return AsyncLROPoller[None](self._client, raw_result, get_long_running_output, polling_method)


__all__: list[str] = [
    "_AnalyzeDocumentsClientOperationsMixin",
    "AnalyzeDocumentsAsyncLROPoller",
]


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
