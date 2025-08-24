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
from azure.core.polling import AsyncLROPoller, AsyncNoPolling, AsyncPollingMethod
from azure.core.rest import HttpRequest, HttpResponse
from azure.core.tracing.decorator import distributed_trace
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.utils import case_insensitive_dict

from ..._utils.model_base import _deserialize
from ...models import (
    AsyncJobsPollingMethod,
    CreateDeploymentDetails,
    DeleteDeploymentDetails,
    DeploymentDeleteFromResourcesState,
    DeploymentState,
    ProjectDeployment,
)
from ._operations import DeploymentOperations as DeploymentOperationsGenerated

JSON = MutableMapping[str, Any]
T = TypeVar("T")
ClsType = Optional[
    Callable[[PipelineResponse[HttpRequest, HttpResponse], T, Dict[str, Any]], Any]
]


class DeploymentOperations(DeploymentOperationsGenerated):

    def __init__(self, *args, project_name: str, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._project_name = project_name

    @distributed_trace_async
    async def begin_delete_deployment(
        self,
        deployment_name: str,
        **kwargs: Any,
    ) -> AsyncLROPoller[DeploymentState]:
        """Deletes a project deployment.

        :param deployment_name: The deployment name. Required.
        :type deployment_name: str
        :return: AsyncLROPoller that returns DeploymentState.
        :rtype: ~azure.core.polling.AsyncLROPoller[~azure.ai.language.conversations.authoring.models.DeploymentState]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        _headers = kwargs.pop("headers", {}) or {}
        _params = kwargs.pop("params", {}) or {}

        cls: ClsType[DeploymentState] = kwargs.pop("cls", None)
        polling: Union[bool, AsyncPollingMethod] = kwargs.pop("polling", True)
        lro_delay = kwargs.pop("polling_interval", self._config.polling_interval)
        cont_token: Optional[str] = kwargs.pop("continuation_token", None)

        if cont_token is None:
            initial = await self._delete_deployment_initial(
                project_name=self._project_name,  # instance-scoped project name
                deployment_name=deployment_name,
                cls=lambda x, y, z: x,  # return PipelineResponse for poller
                headers=_headers,
                params=_params,
                **kwargs,
            )
            await initial.http_response.read()  # type: ignore
        kwargs.pop("error_map", None)

        def get_long_running_output(pipeline_response):
            obj = _deserialize(DeploymentState, pipeline_response.http_response.json())
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
                    path_format_arguments=path_format_arguments,
                    **kwargs,
                ),
            )
        elif polling is False:
            polling_method = cast(AsyncPollingMethod, AsyncNoPolling())
        else:
            polling_method = polling  # user-supplied async polling method

        if cont_token:
            return AsyncLROPoller[DeploymentState].from_continuation_token(
                polling_method=polling_method,
                continuation_token=cont_token,
                client=self._client,
                deserialization_callback=get_long_running_output,
            )

        return AsyncLROPoller[DeploymentState](
            self._client,
            initial,  # type: ignore
            get_long_running_output,
            polling_method,
        )

    @overload
    async def begin_delete_deployment_from_resources(
        self,
        deployment_name: str,
        body: DeleteDeploymentDetails,
        *,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> AsyncLROPoller[DeploymentDeleteFromResourcesState]:
        """Deletes a project deployment from the specified assigned resources.

        :param deployment_name: The name of the specific deployment of the project to use. Required.
        :type deployment_name: str
        :param body: The options for deleting the deployment. Required.
        :type body: ~azure.ai.language.conversations.authoring.models.DeleteDeploymentDetails
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
        Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of AsyncLROPoller that returns DeploymentDeleteFromResourcesState.
        :rtype: ~azure.core.polling.AsyncLROPoller[~azure.ai.language.conversations.authoring.models.DeploymentDeleteFromResourcesState]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    async def begin_delete_deployment_from_resources(
        self, deployment_name: str, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> AsyncLROPoller[DeploymentDeleteFromResourcesState]:
        """Deletes a project deployment from the specified assigned resources.

        :param deployment_name: The name of the specific deployment of the project to use. Required.
        :type deployment_name: str
        :param body: The options for deleting the deployment. Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
        Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of AsyncLROPoller that returns DeploymentDeleteFromResourcesState.
        :rtype: ~azure.core.polling.AsyncLROPoller[~azure.ai.language.conversations.authoring.models.DeploymentDeleteFromResourcesState]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    async def begin_delete_deployment_from_resources(
        self, deployment_name: str, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> AsyncLROPoller[DeploymentDeleteFromResourcesState]:
        """Deletes a project deployment from the specified assigned resources.

        :param deployment_name: The name of the specific deployment of the project to use. Required.
        :type deployment_name: str
        :param body: The options for deleting the deployment. Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
        Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of AsyncLROPoller that returns DeploymentDeleteFromResourcesState.
        :rtype: ~azure.core.polling.AsyncLROPoller[~azure.ai.language.conversations.authoring.models.DeploymentDeleteFromResourcesState]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace_async
    async def begin_delete_deployment_from_resources(
        self, deployment_name: str, body: Union[DeleteDeploymentDetails, JSON, IO[bytes]], **kwargs: Any
    ) -> AsyncLROPoller[DeploymentDeleteFromResourcesState]:
        """Deletes a project deployment from the specified assigned resources.

        :param deployment_name: The name of the specific deployment of the project to use. Required.
        :type deployment_name: str
        :param body: The options for deleting the deployment. Required.
        :type body: ~azure.ai.language.conversations.authoring.models.DeleteDeploymentDetails or JSON or IO[bytes]
        :return: An instance of AsyncLROPoller that returns DeploymentDeleteFromResourcesState.
        :rtype: ~azure.core.polling.AsyncLROPoller[~azure.ai.language.conversations.authoring.models.DeploymentDeleteFromResourcesState]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
        cls: ClsType[DeploymentDeleteFromResourcesState] = kwargs.pop("cls", None)
        polling: Union[bool, AsyncPollingMethod] = kwargs.pop("polling", True)
        lro_delay = kwargs.pop("polling_interval", self._config.polling_interval)
        cont_token: Optional[str] = kwargs.pop("continuation_token", None)

        if cont_token is None:
            initial = await self._delete_deployment_from_resources_initial(
                project_name=self._project_name,
                deployment_name=deployment_name,
                body=body,
                content_type=content_type,
                cls=lambda x, y, z: x,  # return PipelineResponse
                headers=_headers,
                params=_params,
                **kwargs,
            )
            await initial.http_response.read()  # type: ignore
        kwargs.pop("error_map", None)

        def get_long_running_output(pipeline_response):
            obj = _deserialize(DeploymentDeleteFromResourcesState, pipeline_response.http_response.json())
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
                    path_format_arguments=path_format_arguments,
                    **kwargs,
                ),
            )
        elif polling is False:
            polling_method = cast(AsyncPollingMethod, AsyncNoPolling())
        else:
            polling_method = polling

        if cont_token:
            return AsyncLROPoller[DeploymentDeleteFromResourcesState].from_continuation_token(
                polling_method=polling_method,
                continuation_token=cont_token,
                client=self._client,
                deserialization_callback=get_long_running_output,
            )

        return AsyncLROPoller[DeploymentDeleteFromResourcesState](
            self._client,
            initial,  # type: ignore
            get_long_running_output,
            polling_method,
        )

    @overload
    async def begin_deploy_project(
        self,
        deployment_name: str,
        body: CreateDeploymentDetails,
        *,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> AsyncLROPoller[DeploymentState]:
        """Creates a new deployment or replaces an existing one.

        :param deployment_name: The name of the specific deployment of the project to use. Required.
        :type deployment_name: str
        :param body: The new deployment info. Required.
        :type body: ~azure.ai.language.conversations.authoring.models.CreateDeploymentDetails
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
        Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of AsyncLROPoller that returns DeploymentState.
        :rtype: ~azure.core.polling.AsyncLROPoller[~azure.ai.language.conversations.authoring.models.DeploymentState]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    async def begin_deploy_project(
        self, deployment_name: str, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> AsyncLROPoller[DeploymentState]:
        """Creates a new deployment or replaces an existing one.

        :param deployment_name: The name of the specific deployment of the project to use. Required.
        :type deployment_name: str
        :param body: The new deployment info. Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
        Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of AsyncLROPoller that returns DeploymentState.
        :rtype: ~azure.core.polling.AsyncLROPoller[~azure.ai.language.conversations.authoring.models.DeploymentState]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    async def begin_deploy_project(
        self, deployment_name: str, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> AsyncLROPoller[DeploymentState]:
        """Creates a new deployment or replaces an existing one.

        :param deployment_name: The name of the specific deployment of the project to use. Required.
        :type deployment_name: str
        :param body: The new deployment info. Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
        Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of AsyncLROPoller that returns DeploymentState.
        :rtype: ~azure.core.polling.AsyncLROPoller[~azure.ai.language.conversations.authoring.models.DeploymentState]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace_async
    async def begin_deploy_project(
        self, deployment_name: str, body: Union[CreateDeploymentDetails, JSON, IO[bytes]], **kwargs: Any
    ) -> AsyncLROPoller[DeploymentState]:
        """Creates a new deployment or replaces an existing one.

        :param deployment_name: The name of the specific deployment of the project to use. Required.
        :type deployment_name: str
        :param body: The new deployment info. Required.
        :type body: ~azure.ai.language.conversations.authoring.models.CreateDeploymentDetails or JSON or IO[bytes]
        :return: An instance of AsyncLROPoller that returns DeploymentState.
        :rtype: ~azure.core.polling.AsyncLROPoller[~azure.ai.language.conversations.authoring.models.DeploymentState]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
        cls: ClsType[DeploymentState] = kwargs.pop("cls", None)
        polling: Union[bool, AsyncPollingMethod] = kwargs.pop("polling", True)
        lro_delay = kwargs.pop("polling_interval", self._config.polling_interval)
        cont_token: Optional[str] = kwargs.pop("continuation_token", None)

        if cont_token is None:
            initial = await self._deploy_project_initial(
                project_name=self._project_name,
                deployment_name=deployment_name,
                body=body,
                content_type=content_type,
                cls=lambda x, y, z: x,  # return PipelineResponse
                headers=_headers,
                params=_params,
                **kwargs,
            )
            await initial.http_response.read()  # type: ignore
        kwargs.pop("error_map", None)

        def get_long_running_output(pipeline_response):
            deserialized = _deserialize(DeploymentState, pipeline_response.http_response.json())
            if cls:
                return cls(pipeline_response, deserialized, {})  # type: ignore[misc]
            return deserialized

        path_format_arguments = {
            "Endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
        }

        if polling is True:
            polling_method = cast(
                AsyncPollingMethod,
                AsyncJobsPollingMethod(
                    polling_interval=lro_delay,
                    path_format_arguments=path_format_arguments,
                    **kwargs,
                ),
            )
        elif polling is False:
            polling_method = cast(AsyncPollingMethod, AsyncNoPolling())
        else:
            polling_method = polling

        if cont_token:
            return AsyncLROPoller[DeploymentState].from_continuation_token(
                polling_method=polling_method,
                continuation_token=cont_token,
                client=self._client,
                deserialization_callback=get_long_running_output,
            )

        return AsyncLROPoller[DeploymentState](
            self._client,
            initial,  # type: ignore
            get_long_running_output,
            polling_method,
        )

    @distributed_trace
    async def get_deployment(self, deployment_name: str, **kwargs: Any) -> ProjectDeployment:  # type: ignore[override]
        return await super().get_deployment(project_name=self._project_name, deployment_name=deployment_name, **kwargs)

    @distributed_trace
    async def _get_deployment_delete_from_resources_status(  # type: ignore[override]
        self, deployment_name: str, job_id: str, **kwargs: Any
    ) -> DeploymentDeleteFromResourcesState:
        return await super()._get_deployment_delete_from_resources_status(
            project_name=self._project_name, deployment_name=deployment_name, job_id=job_id, **kwargs
        )

    @distributed_trace
    async def _get_deployment_status(  # type: ignore[override]
        self, deployment_name: str, job_id: str, **kwargs: Any
    ) -> DeploymentState:
        return await super()._get_deployment_status(
            project_name=self._project_name, deployment_name=deployment_name, job_id=job_id, **kwargs
        )
