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
from typing import IO, Any, Callable, Dict, Optional, TypeVar, Union, overload

from azure.core.async_paging import AsyncItemPaged
from azure.core.pipeline import PipelineResponse
from azure.core.polling import AsyncLROPoller
from azure.core.rest import HttpRequest, HttpResponse
from azure.core.tracing.decorator import distributed_trace
from azure.core.tracing.decorator_async import distributed_trace_async

from ...models import (
    EvalSummary,
    EvaluationDetails,
    EvaluationJobResult,
    EvaluationState,
    LoadSnapshotState,
    ProjectTrainedModel,
    StringIndexType,
    DocumentEvalResult,
)
from ._operations import TrainedModelOperations as TrainedModelOperationsGenerated

JSON = MutableMapping[str, Any]
T = TypeVar("T")
ClsType = Optional[
    Callable[[PipelineResponse[HttpRequest, HttpResponse], T, Dict[str, Any]], Any]
]


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
        :type body: ~azure.ai.language.text.authoring.models.EvaluationDetails
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of AsyncLROPoller that returns EvaluationJobResult. The EvaluationJobResult is
         compatible with MutableMapping
        :rtype:
         ~azure.core.polling.AsyncLROPoller[~azure.ai.language.text.authoring.models.EvaluationJobResult]
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
         ~azure.core.polling.AsyncLROPoller[~azure.ai.language.text.authoring.models.EvaluationJobResult]
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
         ~azure.core.polling.AsyncLROPoller[~azure.ai.language.text.authoring.models.EvaluationJobResult]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace
    async def begin_evaluate_model(  # type: ignore[override]
        self,
        trained_model_label: str,
        body: Union[EvaluationDetails, JSON, IO[bytes]],
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
    async def begin_load_snapshot(self, trained_model_label: str, **kwargs: Any) -> AsyncLROPoller[None]:
        """Restores the snapshot of this trained model to be the current working directory of the project.

        :param trained_model_label: The trained model label. Required.
        :type trained_model_label: str
        :return: An instance of LROPoller that returns None.
        :rtype: ~azure.core.polling.LROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return await super()._begin_load_snapshot(
            project_name=self._project_name,
            trained_model_label=trained_model_label,
            **kwargs,
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

    @distributed_trace
    def get_model_evaluation_results(  # type: ignore[override]
        self,
        trained_model_label: str,
        *,
        skip: Optional[int] = None,
        string_index_type: Union[str, StringIndexType],
        top: Optional[int] = None,
        **kwargs: Any
    ) -> AsyncItemPaged[DocumentEvalResult]:
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