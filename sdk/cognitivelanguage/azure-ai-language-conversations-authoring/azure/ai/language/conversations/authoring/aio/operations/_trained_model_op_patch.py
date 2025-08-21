# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

from typing import Any, Callable, Dict, IO, Iterator, List, Optional, TypeVar, Union, cast, overload
from azure.core.polling import LROPoller, NoPolling, PollingMethod
from azure.core.tracing.decorator import distributed_trace
from azure.core.async_paging import AsyncItemPaged, AsyncList
from azure.core.polling.base_polling import LROBasePolling
from azure.core.polling import AsyncLROPoller, AsyncNoPolling, AsyncPollingMethod
from azure.core.tracing.decorator_async import distributed_trace_async

from ._operations import (
    ProjectOperations as ProjectOperationsGenerated,
    DeploymentOperations as DeploymentOperationsGenerated,
    ExportedModelOperations as ExportedModelOperationsGenerated,
    TrainedModelOperations as TrainedModelOperationsGenerated,
)
from ..._utils.model_base import SdkJSONEncoder, _deserialize
from azure.core.utils import case_insensitive_dict
from azure.core.polling.base_polling import LROBasePolling
from ...models import (
    ProjectTrainedModel,
    EvaluationDetails,
    EvaluationJobResult,
    EvaluationState,
    LoadSnapshotState,
    ProjectTrainedModel,
    EvalSummary,
    StringIndexType,
    UtteranceEvaluationResult,
    ExportedProjectFormat,
    AsyncJobsPollingMethod,
)
from azure.core.paging import ItemPaged
from collections.abc import MutableMapping
from azure.core.pipeline import PipelineResponse
from azure.core.rest import HttpRequest, HttpResponse

JSON = MutableMapping[str, Any]
T = TypeVar("T")
_Unset: Any = object()
ClsType = Optional[Callable[[PipelineResponse[HttpRequest, HttpResponse], T, Dict[str, Any]], Any]]


class TrainedModelOperations(TrainedModelOperationsGenerated):

    def __init__(self, *args, project_name: str, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._project_name = project_name

    @overload
    async def begin_evaluate_model(
        self,
        trained_model_label: str,
        body: EvaluationDetails,
        *,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> AsyncLROPoller[EvaluationJobResult]:
        """Triggers evaluation operation on a trained model.

        :param trained_model_label: The trained model label. Required.
        :type trained_model_label: str
        :param body: The training input parameters. Required.
        :type body: ~azure.ai.language.conversations.authoring.models.EvaluationDetails
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of AsyncLROPoller that returns EvaluationJobResult. The EvaluationJobResult is
         compatible with MutableMapping
        :rtype:
         ~azure.core.polling.AsyncLROPoller[~azure.ai.language.conversations.authoring.models.EvaluationJobResult]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    async def begin_evaluate_model(
        self, trained_model_label: str, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> AsyncLROPoller[EvaluationJobResult]:
        """Triggers evaluation operation on a trained model.

        :param trained_model_label: The trained model label. Required.
        :type trained_model_label: str
        :param body: The training input parameters. Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of AsyncLROPoller that returns EvaluationJobResult. The EvaluationJobResult is
         compatible with MutableMapping
        :rtype:
         ~azure.core.polling.AsyncLROPoller[~azure.ai.language.conversations.authoring.models.EvaluationJobResult]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    async def begin_evaluate_model(
        self, trained_model_label: str, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> AsyncLROPoller[EvaluationJobResult]:
        """Triggers evaluation operation on a trained model.

        :param trained_model_label: The trained model label. Required.
        :type trained_model_label: str
        :param body: The training input parameters. Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of AsyncLROPoller that returns EvaluationJobResult. The EvaluationJobResult is
         compatible with MutableMapping
        :rtype:
         ~azure.core.polling.AsyncLROPoller[~azure.ai.language.conversations.authoring.models.EvaluationJobResult]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace
    async def begin_evaluate_model(  # type: ignore[override]
        self,
        trained_model_label: str,
        body: Union[EvaluationDetails, dict, IO[bytes]],
        *,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> AsyncLROPoller[EvaluationJobResult]:
        return await super()._begin_evaluate_model(
            project_name=self._project_name,
            trained_model_label=trained_model_label,
            body=body,
            content_type=content_type,
            **kwargs,
        )

    @distributed_trace_async
    async def begin_load_snapshot(
        self,
        trained_model_label: str,
        **kwargs: Any
    ) -> AsyncLROPoller[LoadSnapshotState]:
        """Restores the snapshot of this trained model to be the current working directory of the project.

        :param trained_model_label: The trained model label. Required.
        :type trained_model_label: str
        :return: An instance of AsyncLROPoller that returns LoadSnapshotState.
        :rtype: ~azure.core.polling.AsyncLROPoller[~azure.ai.language.conversations.authoring.models.LoadSnapshotState]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        _headers = kwargs.pop("headers", {}) or {}
        _params = kwargs.pop("params", {}) or {}

        cls: ClsType[LoadSnapshotState] = kwargs.pop("cls", None)
        polling: Union[bool, AsyncPollingMethod] = kwargs.pop("polling", True)
        lro_delay = kwargs.pop("polling_interval", self._config.polling_interval)
        cont_token: Optional[str] = kwargs.pop("continuation_token", None)

        if cont_token is None:
            initial = await self._load_snapshot_initial(
                project_name=self._project_name,  # instance-scoped project name
                trained_model_label=trained_model_label,
                cls=lambda x, y, z: x,  # return PipelineResponse
                headers=_headers,
                params=_params,
                **kwargs,
            )
            await initial.http_response.read()  # type: ignore[func-returns-value]
        kwargs.pop("error_map", None)

        def get_long_running_output(pipeline_response):
            obj = _deserialize(LoadSnapshotState, pipeline_response.http_response.json())
            if cls:
                return cls(pipeline_response, obj, {})  # type: ignore[misc]
            return obj

        path_format_arguments = {
            "Endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
        }

        if polling is True:
            polling_method = cast(
                AsyncPollingMethod,
                AsyncJobsPollingMethod(
                    polling_interval=lro_delay,
                    path_format_arguments=path_format_arguments,  # resolves {Endpoint} in Operation-Location
                    **kwargs,
                ),
            )
        elif polling is False:
            polling_method = cast(AsyncPollingMethod, AsyncNoPolling())
        else:
            polling_method = polling  # user-supplied AsyncPollingMethod

        if cont_token:
            return AsyncLROPoller[LoadSnapshotState].from_continuation_token(
                polling_method=polling_method,
                continuation_token=cont_token,
                client=self._client,
                deserialization_callback=get_long_running_output,
            )

        return AsyncLROPoller[LoadSnapshotState](  
            self._client,
            initial, # type: ignore
            get_long_running_output,
            polling_method,
        )

    @distributed_trace_async
    async def delete_trained_model(self, trained_model_label: str, **kwargs: Any) -> None:  # type: ignore[override]
        return await super().delete_trained_model(
            project_name=self._project_name,
            trained_model_label=trained_model_label,
            **kwargs,
        )

    @distributed_trace_async
    async def _get_evaluation_status(  # type: ignore[override]
        self, trained_model_label: str, job_id: str, **kwargs: Any
    ) -> EvaluationState:
        return await super()._get_evaluation_status(
            project_name=self._project_name,
            trained_model_label=trained_model_label,
            job_id=job_id,
            **kwargs,
        )

    @distributed_trace_async
    async def _get_load_snapshot_status(  # type: ignore[override]
        self, trained_model_label: str, job_id: str, **kwargs: Any
    ) -> LoadSnapshotState:
        return await super()._get_load_snapshot_status(
            project_name=self._project_name,
            trained_model_label=trained_model_label,
            job_id=job_id,
            **kwargs,
        )

    @distributed_trace_async
    async def get_model_evaluation_results(  # type: ignore[override]
        self,
        trained_model_label: str,
        *,
        skip: Optional[int] = None,
        string_index_type: Union[str, StringIndexType],
        top: Optional[int] = None,
        **kwargs: Any
    ) -> AsyncItemPaged[UtteranceEvaluationResult]:
        return super().get_model_evaluation_results(
            project_name=self._project_name,
            trained_model_label=trained_model_label,
            skip=skip,
            string_index_type=string_index_type,
            top=top,
            **kwargs,
        )

    @distributed_trace_async
    async def get_model_evaluation_summary(  # type: ignore[override]
        self, trained_model_label: str, **kwargs: Any
    ) -> EvalSummary:
        return await super().get_model_evaluation_summary(
            project_name=self._project_name,
            trained_model_label=trained_model_label,
            **kwargs,
        )

    @distributed_trace_async
    async def get_trained_model(  # type: ignore[override]
        self, trained_model_label: str, **kwargs: Any
    ) -> ProjectTrainedModel:
        return await super().get_trained_model(
            project_name=self._project_name,
            trained_model_label=trained_model_label,
            **kwargs,
        )
