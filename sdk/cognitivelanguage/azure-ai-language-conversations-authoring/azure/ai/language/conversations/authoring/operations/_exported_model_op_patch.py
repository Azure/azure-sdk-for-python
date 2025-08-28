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

from azure.core.pipeline import PipelineResponse
from azure.core.polling import LROPoller, NoPolling, PollingMethod
from azure.core.rest import HttpRequest, HttpResponse
from azure.core.tracing.decorator import distributed_trace
from azure.core.utils import case_insensitive_dict

from .._utils.model_base import _deserialize
from ..models import (
    ExportedModelDetails,
    ExportedModelState,
    ExportedTrainedModel,
    JobsPollingMethod,
)
from ._operations import ExportedModelOperations as ExportedModelOperationsGenerated

JSON = MutableMapping[str, Any]
T = TypeVar("T")
ClsType = Optional[
    Callable[[PipelineResponse[HttpRequest, HttpResponse], T, Dict[str, Any]], Any]
]

class ExportedModelOperations(ExportedModelOperationsGenerated):

    def __init__(self, *args, project_name: str, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._project_name = project_name

    @overload
    def begin_create_or_update_exported_model(
        self,
        exported_model_name: str,
        body: ExportedModelDetails,
        *,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> LROPoller[None]:
        """Creates a new exported model or replaces an existing one.

        :param exported_model_name: The exported model name. Required.
        :type exported_model_name: str
        :param body: The exported model info. Required.
        :type body: ~azure.ai.language.conversations.authoring.models.ExportedModelDetails
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
        Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of LROPoller that returns None.
        :rtype: ~azure.core.polling.LROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def begin_create_or_update_exported_model(
        self, exported_model_name: str, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> LROPoller[None]:
        """Creates a new exported model or replaces an existing one.

        :param exported_model_name: The exported model name. Required.
        :type exported_model_name: str
        :param body: The exported model info. Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
        Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of LROPoller that returns None.
        :rtype: ~azure.core.polling.LROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def begin_create_or_update_exported_model(
        self, exported_model_name: str, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> LROPoller[None]:
        """Creates a new exported model or replaces an existing one.

        :param exported_model_name: The exported model name. Required.
        :type exported_model_name: str
        :param body: The exported model info. Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
        Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of LROPoller that returns None.
        :rtype: ~azure.core.polling.LROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace
    def begin_create_or_update_exported_model(
        self, exported_model_name: str, body: Union[ExportedModelDetails, JSON, IO[bytes]], *, content_type: str = "application/json", **kwargs: Any
    ) -> LROPoller[None]:
        """Creates a new exported model or replaces an existing one.

        :param exported_model_name: The exported model name. Required.
        :type exported_model_name: str
        :param body: The exported model info. Required.
        :type body: ~azure.ai.language.conversations.authoring.models.ExportedModelDetails or JSON or IO[bytes]
        :return: An instance of LROPoller that returns None.
        :rtype: ~azure.core.polling.LROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return super()._begin_create_or_update_exported_model(
            project_name=self._project_name,
            exported_model_name=exported_model_name,
            body=body,
            content_type=content_type,
            **kwargs,
        )

    @distributed_trace
    def begin_delete_exported_model(self, exported_model_name: str, **kwargs: Any) -> LROPoller[None]:
        """Deletes an existing exported model.

        :param exported_model_name: The exported model name. Required.
        :type exported_model_name: str
        :return: An instance of LROPoller that returns None.
        :rtype: ~azure.core.polling.LROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return super()._begin_delete_exported_model(
            project_name=self._project_name,
            exported_model_name=exported_model_name,
            **kwargs,
        )

    @distributed_trace
    def get_exported_model(  # type: ignore[override]
        self, exported_model_name: str, **kwargs: Any
    ) -> ExportedTrainedModel:
        return super().get_exported_model(
            project_name=self._project_name,
            exported_model_name=exported_model_name,
            **kwargs,
        )

    @distributed_trace
    def _get_exported_model_job_status(  # type: ignore[override]
        self, exported_model_name: str, job_id: str, **kwargs: Any
    ) -> ExportedModelState:
        return super()._get_exported_model_job_status(
            project_name=self._project_name,
            exported_model_name=exported_model_name,
            job_id=job_id,
            **kwargs,
        )
