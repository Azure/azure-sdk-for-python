# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.
Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from collections.abc import MutableMapping  # pylint:disable=import-error
from typing import Any, Callable, Dict, Optional, TypeVar, Union, cast

from azure.core.pipeline import PipelineResponse
from azure.core.polling import LROPoller, NoPolling, PollingMethod
from azure.core.rest import HttpRequest, HttpResponse
from azure.core.tracing.decorator import distributed_trace

from .._utils.model_base import _deserialize
from ..models._patch import _JobsPollingMethod
from ..models import TrainingJobResult
from ._operations import ProjectOperations as ProjectOperationsGenerated

JSON = MutableMapping[str, Any]
T = TypeVar("T")
_Unset: Any = object()
ClsType = Optional[Callable[[PipelineResponse[HttpRequest, HttpResponse], T, Dict[str, Any]], Any]]


class ProjectOperations(ProjectOperationsGenerated):

    @distributed_trace
    def begin_cancel_training_job(  # pylint: disable=function-redefined
        self, job_id: str, **kwargs: Any
    ) -> LROPoller[TrainingJobResult]:
        """
        Cancel a training job without requiring project_name explicitly.

        :param job_id: The identifier of the training job to cancel. Required.
        :type job_id: str
        :return: An instance of LROPoller that returns TrainingJobResult.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.language.conversations.authoring.models.TrainingJobResult]
        """
        _headers = kwargs.pop("headers", {}) or {}
        _params = kwargs.pop("params", {}) or {}

        cls: ClsType[TrainingJobResult] = kwargs.pop("cls", None)
        polling: Union[bool, PollingMethod] = kwargs.pop("polling", True)
        lro_delay = kwargs.pop("polling_interval", self._config.polling_interval)
        cont_token: Optional[str] = kwargs.pop("continuation_token", None)

        if cont_token is None:
            # 1) Send initial cancel request; keep PipelineResponse for the poller
            initial = self._cancel_training_job_initial(
                job_id=job_id,
                cls=lambda x, y, z: x,  # return PipelineResponse unchanged
                headers=_headers,
                params=_params,
                **kwargs,
            )
            initial.http_response.read()  # type: ignore
        kwargs.pop("error_map", None)

        # 2) Deserializer: extract nested "result" as TrainingJobResult
        def get_long_running_output(pipeline_response):
            body = pipeline_response.http_response.json() or {}
            result_dict = body.get("result", {}) or {}
            obj = _deserialize(TrainingJobResult, result_dict)
            if cls:
                return cls(pipeline_response, obj, {})  # type: ignore
            return obj

        # 3) Resolve {Endpoint} in Operation-Location for your poller
        path_format_arguments = {
            "Endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
        }

        # 4) Choose polling method: your JobsPollingMethod by default
        if polling is True:
            polling_method: PollingMethod = cast(
                PollingMethod,
                _JobsPollingMethod(
                    polling_interval=lro_delay,
                    path_format_arguments=path_format_arguments,
                    # any extra kwargs your poller needs
                ),
            )
        elif polling is False:
            polling_method = cast(PollingMethod, NoPolling())
        else:
            polling_method = polling

        # 5) Continuation-token path
        if cont_token:
            return LROPoller[TrainingJobResult].from_continuation_token(
                polling_method=polling_method,
                continuation_token=cont_token,
                client=self._client,
                deserialization_callback=get_long_running_output,
            )

        # 6) Return the poller
        return LROPoller[TrainingJobResult](
            self._client,
            initial,  # type: ignore
            get_long_running_output,
            polling_method,  # type: ignore
        )
