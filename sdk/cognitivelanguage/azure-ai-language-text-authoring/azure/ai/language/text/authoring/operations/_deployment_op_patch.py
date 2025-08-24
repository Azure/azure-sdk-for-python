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
    ProjectDeployment,
    ExportedTrainedModel,
    ProjectTrainedModel,
    DeleteDeploymentDetails,
    CreateDeploymentDetails,
    DeploymentDeleteFromResourcesState,
    DeploymentState,
    JobsPollingMethod,
    DeploymentResourcesState,
    ExportedProject,
    ImportProjectState,
)
from azure.core.paging import ItemPaged
from collections.abc import MutableMapping
from azure.core.pipeline import PipelineResponse
from azure.core.rest import HttpRequest, HttpResponse

JSON = MutableMapping[str, Any]
T = TypeVar("T")
_Unset: Any = object()
ClsType = Optional[Callable[[PipelineResponse[HttpRequest, HttpResponse], T, Dict[str, Any]], Any]]


class DeploymentOperations(DeploymentOperationsGenerated):

    def __init__(self, *args, project_name: str, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._project_name = project_name

    @distributed_trace
    def begin_delete_deployment(self, deployment_name: str, **kwargs: Any) -> LROPoller[DeploymentState]:
        """Deletes a project deployment.

        :param deployment_name: The name of the specific deployment of the project to use. Required.
        :type deployment_name: str
        :return: An instance of LROPoller that returns DeploymentState.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.language.text.authoring.models.DeploymentState]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        _headers = kwargs.pop("headers", {}) or {}
        _params = kwargs.pop("params", {}) or {}

        cls: ClsType[DeploymentState] = kwargs.pop("cls", None)
        polling: Union[bool, PollingMethod] = kwargs.pop("polling", True)
        lro_delay = kwargs.pop("polling_interval", self._config.polling_interval)
        cont_token: Optional[str] = kwargs.pop("continuation_token", None)

        if cont_token is None:
            initial = self._delete_deployment_initial(
                project_name=self._project_name,  # ← use instance-scoped project name
                deployment_name=deployment_name,
                cls=lambda x, y, z: x,  # return PipelineResponse
                headers=_headers,
                params=_params,
                **kwargs,
            )
            initial.http_response.read()  # type: ignore
        kwargs.pop("error_map", None)

        def get_long_running_output(pipeline_response):
            obj = _deserialize(DeploymentState, pipeline_response.http_response.json())
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
            return LROPoller[DeploymentState].from_continuation_token(
                polling_method=polling_method,
                continuation_token=cont_token,
                client=self._client,
                deserialization_callback=get_long_running_output,
            )

        return LROPoller[DeploymentState](
            self._client, initial, get_long_running_output, polling_method  # type: ignore
        )

    @overload
    def begin_delete_deployment_from_resources(
        self,
        deployment_name: str,
        body: DeleteDeploymentDetails,
        *,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> LROPoller[DeploymentDeleteFromResourcesState]:
        """Deletes a project deployment from the specified assigned resources.

        :param deployment_name: The name of the specific deployment of the project to use. Required.
        :type deployment_name: str
        :param body: The options for deleting the deployment. Required.
        :type body: ~azure.ai.language.text.authoring.models.DeleteDeploymentDetails
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
        Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of LROPoller that returns DeploymentDeleteFromResourcesState.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.language.text.authoring.models.DeploymentDeleteFromResourcesState]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def begin_delete_deployment_from_resources(
        self, deployment_name: str, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> LROPoller[DeploymentDeleteFromResourcesState]:
        """Deletes a project deployment from the specified assigned resources.

        :param deployment_name: The name of the specific deployment of the project to use. Required.
        :type deployment_name: str
        :param body: The options for deleting the deployment. Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
        Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of LROPoller that returns DeploymentDeleteFromResourcesState.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.language.text.authoring.models.DeploymentDeleteFromResourcesState]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def begin_delete_deployment_from_resources(
        self, deployment_name: str, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> LROPoller[DeploymentDeleteFromResourcesState]:
        """Deletes a project deployment from the specified assigned resources.

        :param deployment_name: The name of the specific deployment of the project to use. Required.
        :type deployment_name: str
        :param body: The options for deleting the deployment. Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
        Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of LROPoller that returns DeploymentDeleteFromResourcesState.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.language.text.authoring.models.DeploymentDeleteFromResourcesState]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace
    def begin_delete_deployment_from_resources(
        self, deployment_name: str, body: Union[DeleteDeploymentDetails, JSON, IO[bytes]], **kwargs: Any
    ) -> LROPoller[DeploymentDeleteFromResourcesState]:
        """Deletes a project deployment from the specified assigned resources.

        :param deployment_name: The name of the specific deployment of the project to use. Required.
        :type deployment_name: str
        :param body: The options for deleting the deployment. Required.
        :type body: ~azure.ai.language.text.authoring.models.DeleteDeploymentDetails or JSON or IO[bytes]
        :return: An instance of LROPoller that returns DeploymentDeleteFromResourcesState.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.language.text.authoring.models.DeploymentDeleteFromResourcesState]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
        cls: ClsType[DeploymentDeleteFromResourcesState] = kwargs.pop("cls", None)
        polling: Union[bool, PollingMethod] = kwargs.pop("polling", True)
        lro_delay = kwargs.pop("polling_interval", self._config.polling_interval)
        cont_token: Optional[str] = kwargs.pop("continuation_token", None)

        if cont_token is None:
            initial = self._delete_deployment_from_resources_initial(
                project_name=self._project_name,  # ← use instance-scoped project name
                deployment_name=deployment_name,
                body=body,
                content_type=content_type,
                cls=lambda x, y, z: x,  # return PipelineResponse
                headers=_headers,
                params=_params,
                **kwargs,
            )
            initial.http_response.read()  # type: ignore
        kwargs.pop("error_map", None)

        def get_long_running_output(pipeline_response):
            # Final jobs payload is at the ROOT
            obj = _deserialize(DeploymentDeleteFromResourcesState, pipeline_response.http_response.json())
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
            return LROPoller[DeploymentDeleteFromResourcesState].from_continuation_token(
                polling_method=polling_method,
                continuation_token=cont_token,
                client=self._client,
                deserialization_callback=get_long_running_output,
            )

        return LROPoller[DeploymentDeleteFromResourcesState](
            self._client, initial, get_long_running_output, polling_method  # type: ignore
        )

    @overload
    def begin_deploy_project(
        self,
        deployment_name: str,
        body: CreateDeploymentDetails,
        *,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> LROPoller[DeploymentState]:
        """Creates a new deployment or replaces an existing one.

        :param project_name: The name of the project to use. Required.
        :type project_name: str
        :param deployment_name: The name of the specific deployment of the project to use. Required.
        :type deployment_name: str
        :param body: The new deployment info. Required.
        :type body: ~azure.ai.language.text.authoring.models.CreateDeploymentDetails
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of LROPoller that returns DeploymentState.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.language.text.authoring.models.DeploymentState]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def begin_deploy_project(
        self, deployment_name: str, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> LROPoller[DeploymentState]:
        """Creates a new deployment or replaces an existing one.

        :param project_name: The name of the project to use. Required.
        :type project_name: str
        :param deployment_name: The name of the specific deployment of the project to use. Required.
        :type deployment_name: str
        :param body: The new deployment info. Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of LROPoller that returns DeploymentState.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.language.text.authoring.models.DeploymentState]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def begin_deploy_project(
        self, deployment_name: str, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> LROPoller[DeploymentState]:
        """Creates a new deployment or replaces an existing one.

        :param project_name: The name of the project to use. Required.
        :type project_name: str
        :param deployment_name: The name of the specific deployment of the project to use. Required.
        :type deployment_name: str
        :param body: The new deployment info. Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of LROPoller that returns DeploymentState.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.language.text.authoring.models.DeploymentState]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace
    def begin_deploy_project(
        self, deployment_name: str, body: Union[CreateDeploymentDetails, JSON, IO[bytes]], **kwargs: Any
    ) -> LROPoller[DeploymentState]:
        """Creates a new deployment or replaces an existing one.

        :param deployment_name: The name of the specific deployment of the project to use. Required.
        :type deployment_name: str
        :param body: The new deployment info. Required.
        :type body: ~azure.ai.language.text.authoring.models.CreateDeploymentDetails or JSON or IO[bytes]
        :return: An instance of LROPoller that returns DeploymentState.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.language.text.authoring.models.DeploymentState]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
        cls: ClsType[DeploymentState] = kwargs.pop("cls", None)
        polling: Union[bool, PollingMethod] = kwargs.pop("polling", True)
        lro_delay = kwargs.pop("polling_interval", self._config.polling_interval)
        cont_token: Optional[str] = kwargs.pop("continuation_token", None)

        if cont_token is None:
            initial = self._deploy_project_initial(
                project_name=self._project_name,
                deployment_name=deployment_name,
                body=body,
                content_type=content_type,
                cls=lambda x, y, z: x,  # return PipelineResponse
                headers=_headers,
                params=_params,
                **kwargs,
            )
            initial.http_response.read()  # type: ignore
        kwargs.pop("error_map", None)

        def get_long_running_output(pipeline_response):
            # Final payload is at the root; deserialize into typed model
            deserialized = _deserialize(DeploymentState, pipeline_response.http_response.json())
            if cls:
                return cls(pipeline_response, deserialized, {})  # type: ignore
            return deserialized

        path_format_arguments = {
            "Endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
        }

        if polling is True:
            polling_method: PollingMethod = cast(
                PollingMethod,
                JobsPollingMethod(lro_delay, path_format_arguments=path_format_arguments, **kwargs),
            )
        elif polling is False:
            polling_method = cast(PollingMethod, NoPolling())
        else:
            polling_method = polling

        if cont_token:
            return LROPoller[DeploymentState].from_continuation_token(
                polling_method=polling_method,
                continuation_token=cont_token,
                client=self._client,
                deserialization_callback=get_long_running_output,
            )

        return LROPoller[DeploymentState](
            self._client, initial, get_long_running_output, polling_method  # type: ignore
        )

    @distributed_trace
    def get_deployment(self, deployment_name: str, **kwargs: Any) -> ProjectDeployment:  # type: ignore[override]
        return super().get_deployment(project_name=self._project_name, deployment_name=deployment_name, **kwargs)

    @distributed_trace
    def _get_deployment_delete_from_resources_status(  # type: ignore[override]
        self, deployment_name: str, job_id: str, **kwargs: Any
    ) -> DeploymentDeleteFromResourcesState:
        return super()._get_deployment_delete_from_resources_status(
            project_name=self._project_name, deployment_name=deployment_name, job_id=job_id, **kwargs
        )

    @distributed_trace
    def _get_deployment_status(  # type: ignore[override]
        self, deployment_name: str, job_id: str, **kwargs: Any
    ) -> DeploymentState:
        return super()._get_deployment_status(
            project_name=self._project_name, deployment_name=deployment_name, job_id=job_id, **kwargs
        )
