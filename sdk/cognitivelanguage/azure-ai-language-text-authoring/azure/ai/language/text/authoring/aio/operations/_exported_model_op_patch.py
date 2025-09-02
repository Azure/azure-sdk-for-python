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

from azure.core.pipeline import PipelineResponse
from azure.core.polling import AsyncLROPoller
from azure.core.rest import HttpRequest, HttpResponse
from azure.core.tracing.decorator import distributed_trace
from azure.core.tracing.decorator_async import distributed_trace_async

from ...models import (
    ExportedModelDetails,
    ExportedModelState,
    ExportedTrainedModel,
    ExportedModelManifest,
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
    async def begin_create_or_update_exported_model(
        self,
        exported_model_name: str,
        body: ExportedModelDetails,
        *,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> AsyncLROPoller[None]:
        """Creates a new exported model or replaces an existing one.

        :param exported_model_name: The exported model name. Required.
        :type exported_model_name: str
        :param body: The exported model info. Required.
        :type body: ~azure.ai.language.text.authoring.models.ExportedModelDetails
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
        Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of AsyncLROPoller that returns None.
        :rtype: ~azure.core.polling.AsyncLROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    async def begin_create_or_update_exported_model(
        self, exported_model_name: str, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> AsyncLROPoller[None]:
        """Creates a new exported model or replaces an existing one.

        :param exported_model_name: The exported model name. Required.
        :type exported_model_name: str
        :param body: The exported model info. Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
        Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of AsyncLROPoller that returns None.
        :rtype: ~azure.core.polling.AsyncLROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    async def begin_create_or_update_exported_model(
        self, exported_model_name: str, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> AsyncLROPoller[None]:
        """Creates a new exported model or replaces an existing one.

        :param exported_model_name: The exported model name. Required.
        :type exported_model_name: str
        :param body: The exported model info. Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
        Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of AsyncLROPoller that returns None.
        :rtype: ~azure.core.polling.AsyncLROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace_async
    async def begin_create_or_update_exported_model(
        self, exported_model_name: str, body: Union[ExportedModelDetails, JSON, IO[bytes]], *, content_type: str = "application/json",**kwargs: Any
    ) -> AsyncLROPoller[None]:
        """Creates a new exported model or replaces an existing one.

        :param exported_model_name: The exported model name. Required.
        :type exported_model_name: str
        :param body: The exported model info. Required.
        :type body: ~azure.ai.language.text.authoring.models.ExportedModelDetails or JSON or IO[bytes]
        :keyword str content_type: Media type of the request body. Default is "application/json".
        :return: An instance of LROPoller that returns None.
        :rtype: ~azure.core.polling.LROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return await super()._begin_create_or_update_exported_model(
            project_name=self._project_name,
            exported_model_name=exported_model_name,
            body=body,
            content_type=content_type,
            **kwargs,
        )

    @distributed_trace_async
    async def begin_delete_exported_model(
        self, exported_model_name: str, **kwargs: Any
    ) -> AsyncLROPoller[None]:
        """Deletes an existing exported model.

        :param exported_model_name: The exported model name. Required.
        :type exported_model_name: str
        :return: An instance of LROPoller that returns None.
        :rtype: ~azure.core.polling.LROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return await super()._begin_delete_exported_model(
            project_name=self._project_name,
            exported_model_name=exported_model_name,
            **kwargs,
        )

    @distributed_trace
    async def get_exported_model(  # type: ignore[override]
        self, exported_model_name: str, **kwargs: Any
    ) -> ExportedTrainedModel:
        return await super().get_exported_model(
            project_name=self._project_name,
            exported_model_name=exported_model_name,
            **kwargs,
        )

    @distributed_trace
    async def _get_exported_model_job_status(  # type: ignore[override]
        self, exported_model_name: str, job_id: str, **kwargs: Any
    ) -> ExportedModelState:
        return await super()._get_exported_model_job_status(
            project_name=self._project_name,
            exported_model_name=exported_model_name,
            job_id=job_id,
            **kwargs,
        )

    @distributed_trace 
    async def get_exported_model_manifest(
        self, exported_model_name: str, **kwargs: Any
    ) -> ExportedModelManifest:
        """Gets the details and URL needed to download the exported model.

        :param exported_model_name: The exported model name. Required.
        :type exported_model_name: str
        :return: ExportedModelManifest. The ExportedModelManifest is compatible with MutableMapping
        :rtype: ~azure.ai.language.text.authoring.models.ExportedModelManifest
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return await super()._get_exported_model_manifest(
            project_name=self._project_name,
            exported_model_name=exported_model_name,
            **kwargs,
        )