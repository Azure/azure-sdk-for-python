# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.
Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from collections.abc import MutableMapping # pylint:disable=import-error
from typing import IO, Any, Callable, Dict, Optional, TypeVar, Union, cast, overload

from azure.core.async_paging import AsyncItemPaged
from azure.core.pipeline import PipelineResponse
from azure.core.polling import AsyncLROPoller, AsyncNoPolling, AsyncPollingMethod
from azure.core.rest import HttpRequest, HttpResponse
from azure.core.tracing.decorator_async import distributed_trace_async

from ..._utils.model_base import _deserialize
from ...models._patch import _AsyncJobsPollingMethod
from ...models import (
    TrainingJobResult,
)
from ._operations import ProjectOperations as ProjectOperationsGenerated

JSON = MutableMapping[str, Any]
T = TypeVar("T")
_Unset: Any = object()
ClsType = Optional[
    Callable[[PipelineResponse[HttpRequest, HttpResponse], T, Dict[str, Any]], Any]
]


class ProjectOperations(ProjectOperationsGenerated):
    """Patched ProjectOperationsOperations that auto-injects project_name."""

    def __init__(self, *args, **kwargs: Any):
        super().__init__(*args, **kwargs)

    @distributed_trace_async
    async def begin_cancel_training_job(  # type: ignore[override]
        self,
        job_id: str,
        **kwargs: Any
    ) -> AsyncLROPoller[TrainingJobResult]:
        """
        Cancel a training job.
        :param job_id: The identifier of the training job to cancel. Required.
        :type job_id: str
        :return: An instance of AsyncLROPoller that returns TrainingJobResult.
        :rtype: ~azure.core.polling.AsyncLROPoller[~azure.ai.language.conversations.authoring.models.TrainingJobResult]
        """
        _headers = kwargs.pop("headers", {}) or {}
        _params = kwargs.pop("params", {}) or {}

        cls: ClsType[TrainingJobResult] = kwargs.pop("cls", None)
        polling: Union[bool, AsyncPollingMethod] = kwargs.pop("polling", True)
        lro_delay = kwargs.pop("polling_interval", self._config.polling_interval)
        cont_token: Optional[str] = kwargs.pop("continuation_token", None)

        if cont_token is None:
            # Fire the initial cancel request; keep PipelineResponse for the poller
            initial = await self._cancel_training_job_initial(  # returns PipelineResponse                project_name=self._project_name,
                job_id=job_id,
                cls=lambda x, y, z: x,  # passthrough PipelineResponse
                headers=_headers,
                params=_params,
                **kwargs,
            )
            await initial.http_response.read()  # type: ignore[attr-defined]
        kwargs.pop("error_map", None)

        # Deserialization callback: map the nested "result" object to TrainingJobResult
        def get_long_running_output(pipeline_response):
            body = pipeline_response.http_response.json() or {}
            result_dict = body.get("result", {}) or {}
            obj = _deserialize(TrainingJobResult, result_dict)
            if cls:
                return cls(pipeline_response, obj, {})  # type: ignore[misc]
            return obj

        path_format_arguments = {
            "Endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
        }

        if polling is True:
            polling_method: AsyncPollingMethod = cast(
                AsyncPollingMethod,
                _AsyncJobsPollingMethod(
                    polling_interval=lro_delay,
                    path_format_arguments=path_format_arguments,
                ),
            )
        elif polling is False:
            polling_method = cast(AsyncPollingMethod, AsyncNoPolling())
        else:
            polling_method = polling

        if cont_token:
            return AsyncLROPoller[TrainingJobResult].from_continuation_token(
                polling_method=polling_method,
                continuation_token=cont_token,
                client=self._client,
                deserialization_callback=get_long_running_output,
            )

        return AsyncLROPoller[TrainingJobResult](
            self._client,
            initial, # type: ignore
            get_long_running_output,
            polling_method,  # type: ignore[arg-type]
        )