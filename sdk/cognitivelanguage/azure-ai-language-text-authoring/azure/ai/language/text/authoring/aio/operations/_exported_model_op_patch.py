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
    ExportedModelOperations as ExportedModelOperationsGenerated,
)
from ..._utils.model_base import SdkJSONEncoder, _deserialize
from azure.core.utils import case_insensitive_dict
from azure.core.polling.base_polling import LROBasePolling
from ...models import (
    ExportedTrainedModel,
    ExportedModelDetails,
    ExportedTrainedModel,
    ExportedModelState,
    JobsPollingMethod,
    AsyncJobsPollingMethod,
)
from azure.core.paging import ItemPaged
from collections.abc import MutableMapping
from azure.core.pipeline import PipelineResponse
from azure.core.rest import HttpRequest, HttpResponse
from azure.core.polling.base_polling import LROBasePolling
from azure.core.polling import AsyncLROPoller, AsyncNoPolling, AsyncPollingMethod
from azure.core.tracing.decorator_async import distributed_trace_async

JSON = MutableMapping[str, Any]
T = TypeVar("T")
_Unset: Any = object()
ClsType = Optional[Callable[[PipelineResponse[HttpRequest, HttpResponse], T, Dict[str, Any]], Any]]


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
    ) -> AsyncLROPoller[ExportedModelState]:
        """Creates a new exported model or replaces an existing one.

        :param exported_model_name: The exported model name. Required.
        :type exported_model_name: str
        :param body: The exported model info. Required.
        :type body: ~azure.ai.language.text.authoring.models.ExportedModelDetails
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
        Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of AsyncLROPoller that returns ExportedModelState.
        :rtype: ~azure.core.polling.AsyncLROPoller[~azure.ai.language.text.authoring.models.ExportedModelState]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    async def begin_create_or_update_exported_model(
        self,
        exported_model_name: str,
        body: JSON,
        *,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> AsyncLROPoller[ExportedModelState]:
        """Creates a new exported model or replaces an existing one.

        :param exported_model_name: The exported model name. Required.
        :type exported_model_name: str
        :param body: The exported model info. Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
        Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of AsyncLROPoller that returns ExportedModelState.
        :rtype: ~azure.core.polling.AsyncLROPoller[~azure.ai.language.text.authoring.models.ExportedModelState]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    async def begin_create_or_update_exported_model(
        self,
        exported_model_name: str,
        body: IO[bytes],
        *,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> AsyncLROPoller[ExportedModelState]:
        """Creates a new exported model or replaces an existing one.

        :param exported_model_name: The exported model name. Required.
        :type exported_model_name: str
        :param body: The exported model info. Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
        Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of AsyncLROPoller that returns ExportedModelState.
        :rtype: ~azure.core.polling.AsyncLROPoller[~azure.ai.language.text.authoring.models.ExportedModelState]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace_async
    async def begin_create_or_update_exported_model(
        self,
        exported_model_name: str,
        body: Union[ExportedModelDetails, JSON, IO[bytes]],
        **kwargs: Any
    ) -> AsyncLROPoller[ExportedModelState]:
        """Creates a new exported model or replaces an existing one.

        :param exported_model_name: The exported model name. Required.
        :type exported_model_name: str
        :param body: The exported model info. Required.
        :type body: ~azure.ai.language.text.authoring.models.ExportedModelDetails or JSON or IO[bytes]
        :return: An instance of AsyncLROPoller that returns ExportedModelState.
        :rtype: ~azure.core.polling.AsyncLROPoller[~azure.ai.language.text.authoring.models.ExportedModelState]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
        cls: ClsType[ExportedModelState] = kwargs.pop("cls", None)
        polling: Union[bool, AsyncPollingMethod] = kwargs.pop("polling", True)
        lro_delay = kwargs.pop("polling_interval", self._config.polling_interval)
        cont_token: Optional[str] = kwargs.pop("continuation_token", None)

        if cont_token is None:
            initial = await self._create_or_update_exported_model_initial(
                project_name=self._project_name,  # instance-scoped project name
                exported_model_name=exported_model_name,
                body=body,
                content_type=content_type,
                cls=lambda x, y, z: x,  # return PipelineResponse
                headers=_headers,
                params=_params,
                **kwargs,
            )
            await initial.http_response.read()  # type: ignore[func-returns-value]
        kwargs.pop("error_map", None)

        def get_long_running_output(pipeline_response):
            # Final jobs payload is at the ROOT
            obj = _deserialize(ExportedModelState, pipeline_response.http_response.json())
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
            polling_method = polling  # user-supplied async polling method

        if cont_token:
            return AsyncLROPoller[ExportedModelState].from_continuation_token(
                polling_method=polling_method,
                continuation_token=cont_token,
                client=self._client,
                deserialization_callback=get_long_running_output,
            )

        return AsyncLROPoller[ExportedModelState](  
            self._client,
            initial,# type: ignore
            get_long_running_output,
            polling_method,
        )

    @distributed_trace_async
    async def begin_delete_exported_model(
        self,
        exported_model_name: str,
        **kwargs: Any
    ) -> AsyncLROPoller[ExportedModelState]:
        """Deletes an existing exported model.

        :param exported_model_name: The exported model name. Required.
        :type exported_model_name: str
        :return: An instance of AsyncLROPoller that returns ExportedModelState.
        :rtype: ~azure.core.polling.AsyncLROPoller[~azure.ai.language.text.authoring.models.ExportedModelState]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        _headers = kwargs.pop("headers", {}) or {}
        _params = kwargs.pop("params", {}) or {}

        cls: ClsType[ExportedModelState] = kwargs.pop("cls", None)
        polling: Union[bool, AsyncPollingMethod] = kwargs.pop("polling", True)
        lro_delay = kwargs.pop("polling_interval", self._config.polling_interval)
        cont_token: Optional[str] = kwargs.pop("continuation_token", None)

        if cont_token is None:
            initial = await self._delete_exported_model_initial(
                project_name=self._project_name,  # instance-scoped project name
                exported_model_name=exported_model_name,
                cls=lambda x, y, z: x,  # return PipelineResponse
                headers=_headers,
                params=_params,
                **kwargs,
            )
            await initial.http_response.read()  # type: ignore[func-returns-value]
        kwargs.pop("error_map", None)

        def get_long_running_output(pipeline_response):
            obj = _deserialize(ExportedModelState, pipeline_response.http_response.json())
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
            polling_method = polling  # user-supplied async polling method

        if cont_token:
            return AsyncLROPoller[ExportedModelState].from_continuation_token(
                polling_method=polling_method,
                continuation_token=cont_token,
                client=self._client,
                deserialization_callback=get_long_running_output,
            )

        return AsyncLROPoller[ExportedModelState](  
            self._client,
            initial, # type: ignore
            get_long_running_output,
            polling_method,
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