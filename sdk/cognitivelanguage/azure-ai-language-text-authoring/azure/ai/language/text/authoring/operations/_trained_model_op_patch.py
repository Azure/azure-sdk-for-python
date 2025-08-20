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

from ._operations import (
    ProjectOperations as ProjectOperationsGenerated,
    DeploymentOperations as DeploymentOperationsGenerated,
    ExportedModelOperations as ExportedModelOperationsGenerated,
    TrainedModelOperations as TrainedModelOperationsGenerated,
)
from .._utils.model_base import SdkJSONEncoder, _deserialize
from azure.core.utils import case_insensitive_dict
from azure.core.polling.base_polling import LROBasePolling
from ..models import (
    ProjectTrainedModel,
    EvaluationDetails,
    EvaluationJobResult,
    EvaluationState,
    LoadSnapshotState,
    ProjectTrainedModel,
    EvalSummary,
    StringIndexType,
    DocumentEvalResult,
    JobsPollingMethod,
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
    def begin_evaluate_model(
        self,
        trained_model_label: str,
        body: EvaluationDetails,
        *,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> LROPoller[EvaluationJobResult]:
        """Triggers evaluation operation on a trained model.

        :param trained_model_label: The trained model label. Required.
        :type trained_model_label: str
        :param body: The training input parameters. Required.
        :type body: ~azure.ai.language.conversations.authoring.models.EvaluationDetails
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of LROPoller that returns EvaluationJobResult. The EvaluationJobResult is
         compatible with MutableMapping
        :rtype:
         ~azure.core.polling.LROPoller[~azure.ai.language.conversations.authoring.models.EvaluationJobResult]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def begin_evaluate_model(
        self, trained_model_label: str, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> LROPoller[EvaluationJobResult]:
        """Triggers evaluation operation on a trained model.

        :param trained_model_label: The trained model label. Required.
        :type trained_model_label: str
        :param body: The training input parameters. Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of LROPoller that returns EvaluationJobResult. The EvaluationJobResult is
         compatible with MutableMapping
        :rtype:
         ~azure.core.polling.LROPoller[~azure.ai.language.conversations.authoring.models.EvaluationJobResult]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def begin_evaluate_model(
        self, trained_model_label: str, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> LROPoller[EvaluationJobResult]:
        """Triggers evaluation operation on a trained model.

        :param trained_model_label: The trained model label. Required.
        :type trained_model_label: str
        :param body: The training input parameters. Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of LROPoller that returns EvaluationJobResult. The EvaluationJobResult is
         compatible with MutableMapping
        :rtype:
         ~azure.core.polling.LROPoller[~azure.ai.language.conversations.authoring.models.EvaluationJobResult]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace
    def begin_evaluate_model(  # type: ignore[override]
        self,
        trained_model_label: str,
        body: Union[EvaluationDetails, dict, IO[bytes]],
        *,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> LROPoller[EvaluationJobResult]:
        return super()._begin_evaluate_model(
            project_name=self._project_name,
            trained_model_label=trained_model_label,
            body=body,
            content_type=content_type,
            **kwargs,
        )

    @distributed_trace
    def begin_load_snapshot(self, trained_model_label: str, **kwargs: Any) -> LROPoller[LoadSnapshotState]:
        """Restores the snapshot of this trained model to be the current working directory of the project.

        :param trained_model_label: The trained model label. Required.
        :type trained_model_label: str
        :return: An instance of LROPoller that returns LoadSnapshotState.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.language.conversations.authoring.models.LoadSnapshotState]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        _headers = kwargs.pop("headers", {}) or {}
        _params = kwargs.pop("params", {}) or {}

        cls: ClsType[LoadSnapshotState] = kwargs.pop("cls", None)
        polling: Union[bool, PollingMethod] = kwargs.pop("polling", True)
        lro_delay = kwargs.pop("polling_interval", self._config.polling_interval)
        cont_token: Optional[str] = kwargs.pop("continuation_token", None)

        if cont_token is None:
            initial = self._load_snapshot_initial(
                project_name=self._project_name,  # ← use instance-scoped project name
                trained_model_label=trained_model_label,
                cls=lambda x, y, z: x,  # return PipelineResponse
                headers=_headers,
                params=_params,
                **kwargs,
            )
            initial.http_response.read()  # type: ignore
        kwargs.pop("error_map", None)

        def get_long_running_output(pipeline_response):
            obj = _deserialize(LoadSnapshotState, pipeline_response.http_response.json())
            if cls:
                return cls(pipeline_response, obj, {})  # type: ignore
            return obj

        path_format_arguments = {
            "Endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
        }

        if polling is True:
            polling_method: PollingMethod = cast(
                PollingMethod,
                JobsPollingMethod(
                    polling_interval=lro_delay,
                    path_format_arguments=path_format_arguments,  # resolves {Endpoint} in Operation-Location
                    **kwargs,
                ),
            )
        elif polling is False:
            polling_method = cast(PollingMethod, NoPolling())
        else:
            polling_method = polling

        if cont_token:
            return LROPoller[LoadSnapshotState].from_continuation_token(
                polling_method=polling_method,
                continuation_token=cont_token,
                client=self._client,
                deserialization_callback=get_long_running_output,
            )

        return LROPoller[LoadSnapshotState](
            self._client, initial, get_long_running_output, polling_method  # type: ignore
        )

    @distributed_trace
    def delete_trained_model(self, trained_model_label: str, **kwargs: Any) -> None:  # type: ignore[override]
        return super().delete_trained_model(
            project_name=self._project_name,
            trained_model_label=trained_model_label,
            **kwargs,
        )

    @distributed_trace
    def _get_evaluation_status(  # type: ignore[override]
        self, trained_model_label: str, job_id: str, **kwargs: Any
    ) -> EvaluationState:
        return super()._get_evaluation_status(
            project_name=self._project_name,
            trained_model_label=trained_model_label,
            job_id=job_id,
            **kwargs,
        )

    @distributed_trace
    def _get_load_snapshot_status(  # type: ignore[override]
        self, trained_model_label: str, job_id: str, **kwargs: Any
    ) -> LoadSnapshotState:
        return super()._get_load_snapshot_status(
            project_name=self._project_name,
            trained_model_label=trained_model_label,
            job_id=job_id,
            **kwargs,
        )

    @distributed_trace
    def get_model_evaluation_results(  # type: ignore[override]
        self,
        trained_model_label: str,
        *,
        string_index_type: Union[str, StringIndexType],
        top: Optional[int] = None,
        skip: Optional[int] = None,
        **kwargs: Any,
    ) -> ItemPaged[DocumentEvalResult]:
        """Gets model evaluation results for the current project.

        This custom overload removes `project_name` and binds it to `self._project_name`.
        """
        return super().get_model_evaluation_results(
            project_name=self._project_name,
            trained_model_label=trained_model_label,
            string_index_type=string_index_type,
            top=top,
            skip=skip,
            **kwargs,
        )

    @distributed_trace
    def get_model_evaluation_summary(  # type: ignore[override]
        self, trained_model_label: str, **kwargs: Any
    ) -> EvalSummary:
        return super().get_model_evaluation_summary(
            project_name=self._project_name,
            trained_model_label=trained_model_label,
            **kwargs,
        )

    @distributed_trace
    def get_trained_model(  # type: ignore[override]
        self, trained_model_label: str, **kwargs: Any
    ) -> ProjectTrainedModel:
        return super().get_trained_model(
            project_name=self._project_name,
            trained_model_label=trained_model_label,
            **kwargs,
        )