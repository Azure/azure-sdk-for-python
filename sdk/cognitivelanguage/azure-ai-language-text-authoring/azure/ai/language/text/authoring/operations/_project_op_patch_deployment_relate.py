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
)
from .._utils.model_base import SdkJSONEncoder, _deserialize
from azure.core.utils import case_insensitive_dict
from azure.core.polling.base_polling import LROBasePolling
from ..models import (
    AssignDeploymentResourcesDetails,
    TrainingJobResult,
    CopyProjectDetails,
    TrainingJobDetails,
    AssignDeploymentResourcesDetails,
    UnassignDeploymentResourcesDetails,
    SwapDeploymentsDetails,
    CopyProjectDetails,
    DeploymentResourcesState,
    CopyProjectState,
    ExportProjectState,
    ProjectDetails,
    ProjectDeletionState,
    SwapDeploymentsState,
    TrainingState,
    DeploymentResourcesState,
    AssignedDeploymentResource,
    ProjectDeployment,
    ExportedTrainedModel,
    ProjectTrainedModel,
    ExportedTrainedModel,
    ProjectTrainedModel,
    EvalSummary,
    StringIndexType,
    JobsPollingMethod,
    DeploymentResourcesState,
    ExportedProject,
    ImportProjectState,
    ProjectKind,
)
from azure.core.paging import ItemPaged
from collections.abc import MutableMapping
from azure.core.pipeline import PipelineResponse
from azure.core.rest import HttpRequest, HttpResponse

JSON = MutableMapping[str, Any]
T = TypeVar("T")
_Unset: Any = object()
ClsType = Optional[Callable[[PipelineResponse[HttpRequest, HttpResponse], T, Dict[str, Any]], Any]]


class _ProjectOperationsDeploymentsRelated(ProjectOperationsGenerated):

    def __init__(self, *args, project_name: str, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self._project_name = project_name

    @overload
    def begin_assign_deployment_resources(
        self, body: AssignDeploymentResourcesDetails, *, content_type: str = "application/json", **kwargs: Any
    ) -> LROPoller[DeploymentResourcesState]:
        """Assign new Azure resources to a project to allow deploying new deployments to them. This API is
        available only via AAD authentication and not supported via subscription key authentication.
        For more details about AAD authentication, check here:
        `https://learn.microsoft.com/en-us/azure/cognitive-services/authentication?tabs=powershell#authenticate-with-azure-active-directory
        <https://learn.microsoft.com/en-us/azure/cognitive-services/authentication?tabs=powershell#authenticate-with-azure-active-directory>`_.

        :param body: The new project resources info. Required.
        :type body: ~azure.ai.language.conversations.authoring.models.AssignDeploymentResourcesDetails
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
        Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of LROPoller that returns DeploymentResourcesState.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.language.conversations.authoring.models.DeploymentResourcesState]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def begin_assign_deployment_resources(
        self, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> LROPoller[DeploymentResourcesState]:
        """Assign new Azure resources to a project to allow deploying new deployments to them. This API is
        available only via AAD authentication and not supported via subscription key authentication.
        For more details about AAD authentication, check here:
        `https://learn.microsoft.com/en-us/azure/cognitive-services/authentication?tabs=powershell#authenticate-with-azure-active-directory
        <https://learn.microsoft.com/en-us/azure/cognitive-services/authentication?tabs=powershell#authenticate-with-azure-active-directory>`_.

        :param body: The new project resources info. Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
        Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of LROPoller that returns DeploymentResourcesState.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.language.conversations.authoring.models.DeploymentResourcesState]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def begin_assign_deployment_resources(
        self, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> LROPoller[DeploymentResourcesState]:
        """Assign new Azure resources to a project to allow deploying new deployments to them. This API is
        available only via AAD authentication and not supported via subscription key authentication.
        For more details about AAD authentication, check here:
        `https://learn.microsoft.com/en-us/azure/cognitive-services/authentication?tabs=powershell#authenticate-with-azure-active-directory
        <https://learn.microsoft.com/en-us/azure/cognitive-services/authentication?tabs=powershell#authenticate-with-azure-active-directory>`_.

        :param body: The new project resources info. Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
        Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of LROPoller that returns DeploymentResourcesState.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.language.conversations.authoring.models.DeploymentResourcesState]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace
    def begin_assign_deployment_resources(
        self, body: Union[AssignDeploymentResourcesDetails, JSON, IO[bytes]], **kwargs: Any
    ) -> LROPoller[DeploymentResourcesState]:
        """Assign new Azure resources to a project to allow deploying new deployments to them.
        This API is available only via AAD authentication and not supported via subscription key authentication.
        For more details about AAD authentication, see:
        https://learn.microsoft.com/azure/cognitive-services/authentication?tabs=powershell#authenticate-with-azure-active-directory

        :param body: The new project resources info. Required.
        :type body: ~azure.ai.language.conversations.authoring.models.AssignDeploymentResourcesDetails or JSON or IO[bytes]
        :return: An instance of LROPoller that returns DeploymentResourcesJobState.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.language.conversations.authoring.models.DeploymentResourcesJobState]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
        cls: ClsType[DeploymentResourcesState] = kwargs.pop("cls", None)
        polling: Union[bool, PollingMethod] = kwargs.pop("polling", True)
        lro_delay = kwargs.pop("polling_interval", self._config.polling_interval)
        cont_token: Optional[str] = kwargs.pop("continuation_token", None)

        if cont_token is None:
            initial = self._assign_deployment_resources_initial(
                project_name=self._project_name,  # <-- use instance project name
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
            # Job payload is at the ROOT of the polling response
            obj = _deserialize(DeploymentResourcesState, pipeline_response.http_response.json())
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
                    header_name="Operation-Location",  # service returns jobs URL here
                    final_via_async_url=True,  # take final body from jobs URL
                    path_format_arguments=path_format_arguments,
                    **kwargs,
                ),
            )
        elif polling is False:
            polling_method = cast(PollingMethod, NoPolling())
        else:
            polling_method = polling

        if cont_token:
            return LROPoller[DeploymentResourcesState].from_continuation_token(
                polling_method=polling_method,
                continuation_token=cont_token,
                client=self._client,
                deserialization_callback=get_long_running_output,
            )

        return LROPoller[DeploymentResourcesState](
            self._client, initial, get_long_running_output, polling_method  # type: ignore
        )

    @overload
    def begin_swap_deployments(
        self, body: SwapDeploymentsDetails, *, content_type: str = "application/json", **kwargs: Any
    ) -> LROPoller[SwapDeploymentsState]:
        """Swaps two existing deployments with each other.

        :param body: The job object to swap two deployments. Required.
        :type body: ~azure.ai.language.conversations.authoring.models.SwapDeploymentsDetails
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
        Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of LROPoller that returns SwapDeploymentsState.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.language.conversations.authoring.models.SwapDeploymentsState]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def begin_swap_deployments(
        self, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> LROPoller[SwapDeploymentsState]:
        """Swaps two existing deployments with each other.

        :param body: The job object to swap two deployments. Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
        Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of LROPoller that returns SwapDeploymentsState.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.language.conversations.authoring.models.SwapDeploymentsState]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def begin_swap_deployments(
        self, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> LROPoller[SwapDeploymentsState]:
        """Swaps two existing deployments with each other.

        :param body: The job object to swap two deployments. Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
        Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of LROPoller that returns SwapDeploymentsState.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.language.conversations.authoring.models.SwapDeploymentsState]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace
    def begin_swap_deployments(
        self, body: Union[SwapDeploymentsDetails, JSON, IO[bytes]], **kwargs: Any
    ) -> LROPoller[SwapDeploymentsState]:
        """Swaps two existing deployments with each other.

        :param body: The job object to swap two deployments. Required.
        :type body: ~azure.ai.language.conversations.authoring.models.SwapDeploymentsDetails or JSON or IO[bytes]
        :return: An instance of LROPoller that returns SwapDeploymentsState.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.language.conversations.authoring.models.SwapDeploymentsState]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
        cls: ClsType[SwapDeploymentsState] = kwargs.pop("cls", None)
        polling: Union[bool, PollingMethod] = kwargs.pop("polling", True)
        lro_delay = kwargs.pop("polling_interval", self._config.polling_interval)
        cont_token: Optional[str] = kwargs.pop("continuation_token", None)

        if cont_token is None:
            initial = self._swap_deployments_initial(
                project_name=self._project_name,  # ← use instance project name
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
            # Job payload is at the ROOT of the polling response
            obj = _deserialize(SwapDeploymentsState, pipeline_response.http_response.json())
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
            return LROPoller[SwapDeploymentsState].from_continuation_token(
                polling_method=polling_method,
                continuation_token=cont_token,
                client=self._client,
                deserialization_callback=get_long_running_output,
            )

        return LROPoller[SwapDeploymentsState](
            self._client, initial, get_long_running_output, polling_method  # type: ignore
        )

    @overload
    def begin_unassign_deployment_resources(
        self, body: UnassignDeploymentResourcesDetails, *, content_type: str = "application/json", **kwargs: Any
    ) -> LROPoller[DeploymentResourcesState]:
        """Unassign resources from a project. This disallows deploying new deployments to these resources,
        and deletes existing deployments assigned to them.

        :param body: The info for the deployment resources to be deleted. Required.
        :type body: ~azure.ai.language.conversations.authoring.models.UnassignDeploymentResourcesDetails
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
        Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of LROPoller that returns DeploymentResourcesState.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.language.conversations.authoring.models.DeploymentResourcesState]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def begin_unassign_deployment_resources(
        self, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> LROPoller[DeploymentResourcesState]:
        """Unassign resources from a project. This disallows deploying new deployments to these resources,
        and deletes existing deployments assigned to them.

        :param body: The info for the deployment resources to be deleted. Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
        Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of LROPoller that returns DeploymentResourcesState.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.language.conversations.authoring.models.DeploymentResourcesState]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def begin_unassign_deployment_resources(
        self, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> LROPoller[DeploymentResourcesState]:
        """Unassign resources from a project. This disallows deploying new deployments to these resources,
        and deletes existing deployments assigned to them.

        :param body: The info for the deployment resources to be deleted. Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
        Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of LROPoller that returns DeploymentResourcesState.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.language.conversations.authoring.models.DeploymentResourcesState]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace
    def begin_unassign_deployment_resources(
        self, body: Union[UnassignDeploymentResourcesDetails, JSON, IO[bytes]], **kwargs: Any
    ) -> LROPoller[DeploymentResourcesState]:
        """Unassign resources from a project. This disallows deploying new deployments to these resources,
        and deletes existing deployments assigned to them.

        :param body: The info for the deployment resources to be deleted. Required.
        :type body: ~azure.ai.language.conversations.authoring.models.UnassignDeploymentResourcesDetails or JSON or IO[bytes]
        :return: An instance of LROPoller that returns DeploymentResourcesState.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.language.conversations.authoring.models.DeploymentResourcesState]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
        cls: ClsType[DeploymentResourcesState] = kwargs.pop("cls", None)
        polling: Union[bool, PollingMethod] = kwargs.pop("polling", True)
        lro_delay = kwargs.pop("polling_interval", self._config.polling_interval)
        cont_token: Optional[str] = kwargs.pop("continuation_token", None)

        if cont_token is None:
            initial = self._unassign_deployment_resources_initial(
                project_name=self._project_name,  # ← use instance project name
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
            # Job payload is at the ROOT of the polling response
            obj = _deserialize(DeploymentResourcesState, pipeline_response.http_response.json())
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
            return LROPoller[DeploymentResourcesState].from_continuation_token(
                polling_method=polling_method,
                continuation_token=cont_token,
                client=self._client,
                deserialization_callback=get_long_running_output,
            )

        return LROPoller[DeploymentResourcesState](
            self._client, initial, get_long_running_output, polling_method  # type: ignore
        )