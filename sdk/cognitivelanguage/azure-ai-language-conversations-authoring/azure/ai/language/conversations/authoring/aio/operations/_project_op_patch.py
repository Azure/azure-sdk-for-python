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

from azure.core.async_paging import AsyncItemPaged
from azure.core.pipeline import PipelineResponse
from azure.core.polling import AsyncLROPoller, AsyncNoPolling, AsyncPollingMethod
from azure.core.rest import HttpRequest, HttpResponse
from azure.core.tracing.decorator import distributed_trace
from azure.core.tracing.decorator_async import distributed_trace_async

from ..._utils.model_base import _deserialize
from ...models._patch import _AsyncJobsPollingMethod
from ...models import (
    AssignedDeploymentResource,
    AssignDeploymentResourcesDetails,
    CopyProjectDetails,
    CopyProjectState,
    DeploymentResourcesState,
    ExportProjectState,
    ExportedProject,
    ExportedProjectFormat,
    ExportedTrainedModel,
    ProjectDeletionState,
    ProjectDeployment,
    ProjectDetails,
    ProjectKind,
    ProjectTrainedModel,
    StringIndexType,
    SwapDeploymentsDetails,
    SwapDeploymentsState,
    TrainingJobDetails,
    TrainingJobResult,
    TrainingState,
    UnassignDeploymentResourcesDetails,
)
from ._operations import ProjectOperations as ProjectOperationsGenerated

JSON = MutableMapping[str, Any]
T = TypeVar("T")
_Unset: Any = object()
ClsType = Optional[
    Callable[[PipelineResponse[HttpRequest, HttpResponse], T, Dict[str, Any]], Any]
]


class ProjectOperations(ProjectOperationsGenerated):
    """Patched ProjectOperationsOperations that auto-injects project_name."""

    def __init__(self, *args, project_name: str, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self._project_name = project_name

    @overload
    async def begin_import(
        self,
        body: ExportedProject,
        *,
        exported_project_format: Optional[Union[str, ExportedProjectFormat]] = None,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> AsyncLROPoller[None]:
        """
        Triggers a job to import a project. If a project with the same name already exists, the data of that project is replaced.

        :param body: The project data to import. Required.
        :type body: ~azure.ai.language.conversations.authoring.models.ExportedProject
        :keyword exported_project_format: The format of the exported project file to use. Known values are: "Conversation" and "Luis". Default value is None.
        :paramtype exported_project_format: str or ~azure.ai.language.conversations.authoring.models.ExportedProjectFormat
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body. Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of AsyncLROPoller that returns None.
        :rtype: ~azure.core.polling.AsyncLROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:

        """

    @overload
    async def begin_import(
        self,
        body: JSON,
        *,
        exported_project_format: Optional[Union[str, ExportedProjectFormat]] = None,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> AsyncLROPoller[None]:
        """
        Triggers a job to import a project. If a project with the same name already exists, the data of that project is replaced.

        :param body: The project data to import. Required.
        :type body: JSON
        :keyword exported_project_format: The format of the exported project file to use. Known values are: "Conversation" and "Luis". Default value is None.
        :paramtype exported_project_format: str or ~azure.ai.language.conversations.authoring.models.ExportedProjectFormat
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body. Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of AsyncLROPoller that returns None.
        :rtype: ~azure.core.polling.AsyncLROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:

        """

    @overload
    async def begin_import(
        self,
        body: IO[bytes],
        *,
        exported_project_format: Optional[Union[str, ExportedProjectFormat]] = None,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> AsyncLROPoller[None]:
        """
        Triggers a job to import a project. If a project with the same name already exists, the data of that project is replaced.

        :param body: The project data to import. Required.
        :type body: IO[bytes]
        :keyword exported_project_format: The format of the exported project file to use. Known values are: "Conversation" and "Luis". Default value is None.
        :paramtype exported_project_format: str or ~azure.ai.language.conversations.authoring.models.ExportedProjectFormat
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body. Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of AsyncLROPoller that returns None.
        :rtype: ~azure.core.polling.AsyncLROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:

        """

    @distributed_trace_async
    async def begin_import(
        self,
        body: Union[ExportedProject, JSON, IO[bytes]],
        *,
        exported_project_format: Optional[Union[str, ExportedProjectFormat]] = None,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> AsyncLROPoller[None]:
        """
        Triggers a job to import a project. If a project with the same name already exists, the data of that project is replaced.

        :param body: The project data to import. Required.
        :type body: ~azure.ai.language.conversations.authoring.models.ExportedProject or JSON or IO[bytes]
        :keyword exported_project_format: The format of the exported project file to use. Known values are: "Conversation" and "Luis".
        :paramtype exported_project_format: str or ~azure.ai.language.conversations.authoring.models.ExportedProjectFormat
        :keyword str content_type: Media type of the request body. Default is "application/json".
        :return: An instance of AsyncLROPoller that returns None.
        :rtype: ~azure.core.polling.AsyncLROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:

        """
        return await super()._begin_import_method(
            project_name=self._project_name,
            body=body,
            exported_project_format=exported_project_format,
            content_type=content_type,
            **kwargs,
        )

    @overload
    async def begin_assign_deployment_resources(
        self, body: AssignDeploymentResourcesDetails, *, content_type: str = "application/json", **kwargs: Any
    ) -> AsyncLROPoller[None]:
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
        :return: An instance of LROPoller that returns None.
        :rtype: ~azure.core.polling.LROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    async def begin_assign_deployment_resources(
        self, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> AsyncLROPoller[None]:
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
        :return: An instance of AsyncLROPoller that returns None.
        :rtype: ~azure.core.polling.AsyncLROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    async def begin_assign_deployment_resources(
        self, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> AsyncLROPoller[None]:
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
        :return: An instance of AsyncLROPoller that returns None.
        :rtype: ~azure.core.polling.AsyncLROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace_async
    async def begin_assign_deployment_resources(
        self, body: Union[AssignDeploymentResourcesDetails, JSON, IO[bytes]], *, content_type: str = "application/json",**kwargs: Any
    ) -> AsyncLROPoller[None]:
        """Assign new Azure resources to a project to allow deploying new deployments to them.
        This API is available only via AAD authentication and not supported via subscription key authentication.
        For more details about AAD authentication, see:
        https://learn.microsoft.com/azure/cognitive-services/authentication?tabs=powershell#authenticate-with-azure-active-directory

        :param body: The new project resources info. Required.
        :type body: ~azure.ai.language.conversations.authoring.models.AssignDeploymentResourcesDetails or JSON or IO[bytes]
        :keyword str content_type: Media type of the request body. Default is "application/json".
        :return: An instance of AsyncLROPoller that returns None.
        :rtype: ~azure.core.polling.AsyncLROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return await super()._begin_assign_deployment_resources(
            project_name=self._project_name, body=body, content_type=content_type, **kwargs
        )

    @overload
    async def begin_swap_deployments(
        self, body: SwapDeploymentsDetails, *, content_type: str = "application/json", **kwargs: Any
    ) -> AsyncLROPoller[None]:
        """Swaps two existing deployments with each other.

        :param body: The job object to swap two deployments. Required.
        :type body: ~azure.ai.language.conversations.authoring.models.SwapDeploymentsDetails
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
        Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of LROPoller that returns None.
        :rtype: ~azure.core.polling.LROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    async def begin_swap_deployments(
        self, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> AsyncLROPoller[None]:
        """Swaps two existing deployments with each other.

        :param body: The job object to swap two deployments. Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
        Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of LROPoller that returns None.
        :rtype: ~azure.core.polling.LROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    async def begin_swap_deployments(
        self, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> AsyncLROPoller[None]:
        """Swaps two existing deployments with each other.

        :param body: The job object to swap two deployments. Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
        Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of LROPoller that returns None.
        :rtype: ~azure.core.polling.LROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace_async
    async def begin_swap_deployments(
        self, body: Union[SwapDeploymentsDetails, JSON, IO[bytes]], *, content_type: str = "application/json",**kwargs: Any
    ) -> AsyncLROPoller[None]:
        """Swaps two existing deployments with each other.

        :param body: The job object to swap two deployments. Required.
        :type body: ~azure.ai.language.conversations.authoring.models.SwapDeploymentsDetails or JSON or IO[bytes]
        :keyword str content_type: Media type of the request body. Default is "application/json".
        :return: An instance of AsyncLROPoller that returns None.
        :rtype: ~azure.core.polling.AsyncLROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return await super()._begin_swap_deployments(
            project_name=self._project_name, body=body, content_type=content_type, **kwargs
        )

    @overload
    async def begin_unassign_deployment_resources(
        self, body: UnassignDeploymentResourcesDetails, *, content_type: str = "application/json", **kwargs: Any
    ) -> AsyncLROPoller[None]:
        """Unassign resources from a project. This disallows deploying new deployments to these resources,
        and deletes existing deployments assigned to them.

        :param body: The info for the deployment resources to be deleted. Required.
        :type body: ~azure.ai.language.conversations.authoring.models.UnassignDeploymentResourcesDetails
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
        Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of AsyncLROPoller that returns None.
        :rtype: ~azure.core.polling.AsyncLROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    async def begin_unassign_deployment_resources(
        self, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> AsyncLROPoller[None]:
        """Unassign resources from a project. This disallows deploying new deployments to these resources,
        and deletes existing deployments assigned to them.

        :param body: The info for the deployment resources to be deleted. Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
        Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of AsyncLROPoller that returns None.
        :rtype: ~azure.core.polling.AsyncLROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    async def begin_unassign_deployment_resources(
        self, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> AsyncLROPoller[None]:
        """Unassign resources from a project. This disallows deploying new deployments to these resources,
        and deletes existing deployments assigned to them.

        :param body: The info for the deployment resources to be deleted. Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
        Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of LROPoller that returns None.
        :rtype: ~azure.core.polling.LROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace_async
    async def begin_unassign_deployment_resources(
        self, body: Union[UnassignDeploymentResourcesDetails, JSON, IO[bytes]], *, content_type: str = "application/json", **kwargs: Any
    ) -> AsyncLROPoller[None]:
        """Unassign resources from a project. This disallows deploying new deployments to these resources,
        and deletes existing deployments assigned to them.

        :param body: The info for the deployment resources to be deleted. Required.
        :type body: ~azure.ai.language.conversations.authoring.models.UnassignDeploymentResourcesDetails or JSON or IO[bytes]
        :keyword str content_type: Media type of the request body. Default is "application/json".
        :return: An instance of LROPoller that returns None.
        :rtype: ~azure.core.polling.LROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return await super()._begin_unassign_deployment_resources(
            project_name=self._project_name, body=body, content_type=content_type, **kwargs
        )

    @distributed_trace_async
    async def begin_cancel_training_job(  # type: ignore[override]
        self,
        job_id: str,
        **kwargs: Any
    ) -> AsyncLROPoller[TrainingJobResult]:
        """
        Cancel a training job.

        :param job_id: The identifier of the training job to cancel. Required.
        :type job_id: str
        :return: An instance of AsyncLROPoller that returns TrainingJobResult.
        :rtype: ~azure.core.polling.AsyncLROPoller[~azure.ai.language.conversations.authoring.models.TrainingJobResult]

        """
        _headers = kwargs.pop("headers", {}) or {}
        _params = kwargs.pop("params", {}) or {}

        cls: ClsType[TrainingJobResult] = kwargs.pop("cls", None)
        polling: Union[bool, AsyncPollingMethod] = kwargs.pop("polling", True)
        lro_delay = kwargs.pop("polling_interval", self._config.polling_interval)
        cont_token: Optional[str] = kwargs.pop("continuation_token", None)

        if cont_token is None:
            # Fire the initial cancel request; keep PipelineResponse for the poller
            initial = await self._cancel_training_job_initial(  # returns PipelineResponse
                project_name=self._project_name,
                job_id=job_id,
                cls=lambda x, y, z: x,  # passthrough PipelineResponse
                headers=_headers,
                params=_params,
                **kwargs,
            )
            await initial.http_response.read()  # type: ignore[attr-defined]
        kwargs.pop("error_map", None)

        # Deserialization callback: map the nested "result" object to TrainingJobResult
        def get_long_running_output(pipeline_response):
            body = pipeline_response.http_response.json() or {}
            result_dict = body.get("result", {}) or {}
            obj = _deserialize(TrainingJobResult, result_dict)
            if cls:
                return cls(pipeline_response, obj, {})  # type: ignore[misc]
            return obj

        path_format_arguments = {
            "Endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
        }

        if polling is True:
            polling_method: AsyncPollingMethod = cast(
                AsyncPollingMethod,
                _AsyncJobsPollingMethod(
                    polling_interval=lro_delay,
                    path_format_arguments=path_format_arguments,
                ),
            )
        elif polling is False:
            polling_method = cast(AsyncPollingMethod, AsyncNoPolling())
        else:
            polling_method = polling

        if cont_token:
            return AsyncLROPoller[TrainingJobResult].from_continuation_token(
                polling_method=polling_method,
                continuation_token=cont_token,
                client=self._client,
                deserialization_callback=get_long_running_output,
            )

        return AsyncLROPoller[TrainingJobResult](
            self._client,
            initial, # type: ignore
            get_long_running_output,
            polling_method,  # type: ignore[arg-type]
        )

    @overload
    async def begin_copy_project(
        self, body: CopyProjectDetails, *, content_type: str = "application/json", **kwargs: Any
    ) -> AsyncLROPoller[None]:
        """Copies an existing project to another Azure resource.

        :param body: The copy project info. Required.
        :type body: ~azure.ai.language.conversations.authoring.models.CopyProjectDetails
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body. Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of LROPoller that returns None.
        :rtype: ~azure.core.polling.LROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:

        """

    @overload
    async def begin_copy_project(
        self, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> AsyncLROPoller[None]:
        """Copies an existing project to another Azure resource.

        :param body: The copy project info. Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body. Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of AsyncLROPoller that returns None.
        :rtype: ~azure.core.polling.AsyncLROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:

        """

    @overload
    async def begin_copy_project(
        self, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> AsyncLROPoller[None]:
        """Copies an existing project to another Azure resource.

        :param body: The copy project info. Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body. Default value is "application/json".
        :keyword str content_type: Media type of the request body. Default is "application/json".
        :return: An instance of AsyncLROPoller that returns None.
        :rtype: ~azure.core.polling.AsyncLROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:

        """

    @distributed_trace_async
    async def begin_copy_project(
        self, body: Union[CopyProjectDetails, JSON, IO[bytes]], *, content_type: str = "application/json", **kwargs: Any
    ) -> AsyncLROPoller[None]:
        """Copies an existing project to another Azure resource.

        :param body: The copy project info. Required.
        :type body: ~azure.ai.language.conversations.authoring.models.CopyProjectDetails or JSON or IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body. Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of LROPoller that returns None.
        :rtype: ~azure.core.polling.LROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:
        
        """
        return await super()._begin_copy_project(
            project_name=self._project_name, body=body, content_type=content_type, **kwargs
        )

    @overload
    async def begin_train(
        self, body: TrainingJobDetails, *, content_type: str = "application/json", **kwargs: Any
    ) -> AsyncLROPoller[TrainingJobResult]:
        """
        Triggers a training job for a project.

        :param body: The training input parameters. Required.
        :type body: ~azure.ai.language.conversations.authoring.models.TrainingJobDetails
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body. Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of AsyncLROPoller that returns TrainingJobResult. The TrainingJobResult is compatible with MutableMapping.
        :rtype: ~azure.core.polling.AsyncLROPoller[~azure.ai.language.conversations.authoring.models.TrainingJobResult]
        :raises ~azure.core.exceptions.HttpResponseError:

        """

    @overload
    async def begin_train(
        self, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> AsyncLROPoller[TrainingJobResult]:
        """
        Triggers a training job for a project.

        :param body: The training input parameters. Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body. Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of AsyncLROPoller that returns TrainingJobResult. The TrainingJobResult is compatible with MutableMapping.
        :rtype: ~azure.core.polling.AsyncLROPoller[~azure.ai.language.conversations.authoring.models.TrainingJobResult]
        :raises ~azure.core.exceptions.HttpResponseError:

        """

    @overload
    async def begin_train(
        self, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> AsyncLROPoller[TrainingJobResult]:
        """
        Triggers a training job for a project.

        :param body: The training input parameters. Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body. Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of AsyncLROPoller that returns TrainingJobResult. The TrainingJobResult is compatible with MutableMapping.
        :rtype: ~azure.core.polling.AsyncLROPoller[~azure.ai.language.conversations.authoring.models.TrainingJobResult]
        :raises ~azure.core.exceptions.HttpResponseError:

        """

    @distributed_trace_async
    async def begin_train(  # type: ignore[override]
        self, body: Union[TrainingJobDetails, JSON, IO[bytes]], *, content_type: str = "application/json", **kwargs: Any
    ) -> AsyncLROPoller[TrainingJobResult]:
        """
        Triggers a training job for a project.

        :param body: The training job request payload.
        :type body: ~azure.ai.language.conversations.authoring.models.TrainingJobDetails or JSON or IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON or binary body. Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of AsyncLROPoller that returns TrainingJobResult.
        :rtype: ~azure.core.polling.AsyncLROPoller[~azure.ai.language.conversations.authoring.models.TrainingJobResult]
        :raises ~azure.core.exceptions.HttpResponseError:

        """
        return await super()._begin_train(
            project_name=self._project_name, body=body, content_type=content_type, **kwargs
        )

    @distributed_trace_async
    async def begin_export(
        self,
        *,
        string_index_type: Union[str, StringIndexType],
        exported_project_format: Optional[Union[str, ExportedProjectFormat]] = None,
        asset_kind: Optional[str] = None,
        trained_model_label: Optional[str] = None,
        **kwargs: Any
    ) -> AsyncLROPoller[None]:
        """Triggers a job to export a project's data.

        :keyword string_index_type: Specifies the method used to interpret string offsets. See
            https://aka.ms/text-analytics-offsets. Known values: "Utf16CodeUnit", "Utf8CodeUnit",
            "Utf32CodeUnit". Required.
        :paramtype string_index_type: str or ~azure.ai.language.conversations.authoring.models.StringIndexType
        :keyword exported_project_format: The export format. Known values: "Conversation", "Luis".
        :paramtype exported_project_format: str or ~azure.ai.language.conversations.authoring.models.ExportedProjectFormat
        :keyword asset_kind: Kind of asset to export.
        :paramtype asset_kind: str
        :keyword trained_model_label: Trained model label to export. If None, exports the working copy.
        :paramtype trained_model_label: str
        :return: An instance of AsyncLROPoller that returns None.
        :rtype: ~azure.core.polling.AsyncLROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return await super()._begin_export(
            project_name=self._project_name,
            asset_kind=asset_kind,
            exported_project_format=exported_project_format,
            string_index_type=string_index_type,
            trained_model_label=trained_model_label,
            **kwargs,
        )

    @overload
    async def copy_project_authorization(
        self,
        *,
        project_kind: Union[str, ProjectKind],
        content_type: str = "application/json",
        storage_input_container_name: Optional[str] = None,
        allow_overwrite: Optional[bool] = None,
        **kwargs: Any
    ) -> CopyProjectDetails:
        """Generates a copy project operation authorization to the current target Azure resource.

        :keyword project_kind: Represents the project kind. Known values are: "Conversation",
         "Orchestration", and "CustomConversationSummarization". Required.
        :paramtype project_kind: str or ~azure.ai.language.conversations.authoring.models.ProjectKind
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :keyword storage_input_container_name: The name of the storage container. Default value is
         None.
        :paramtype storage_input_container_name: str
        :keyword allow_overwrite: Whether to allow an existing project to be overwritten using the
         resulting copy authorization. Default value is None.
        :paramtype allow_overwrite: bool
        :return: CopyProjectDetails. The CopyProjectDetails is compatible with MutableMapping
        :rtype: ~azure.ai.language.conversations.authoring.models.CopyProjectDetails
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    async def copy_project_authorization(
        self, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> CopyProjectDetails:
        """Generates a copy project operation authorization to the current target Azure resource.

        :param body: Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: CopyProjectDetails. The CopyProjectDetails is compatible with MutableMapping
        :rtype: ~azure.ai.language.conversations.authoring.models.CopyProjectDetails
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    async def copy_project_authorization(
        self, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> CopyProjectDetails:
        """Generates a copy project operation authorization to the current target Azure resource.

        :param body: Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: CopyProjectDetails. The CopyProjectDetails is compatible with MutableMapping
        :rtype: ~azure.ai.language.conversations.authoring.models.CopyProjectDetails
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace_async
    async def copy_project_authorization(  # type: ignore[override]
        self,
        body: Union[JSON, IO[bytes]] = _Unset,
        *,
        allow_overwrite: Optional[bool] = _Unset,
        project_kind: Union[str, Any] = _Unset,
        storage_input_container_name: Optional[str] = _Unset,
        **kwargs: Any
    ) -> CopyProjectDetails:
        """Generates a copy project operation authorization to the current target Azure resource.

        :param body: Is either a JSON type or a IO[bytes] type. Required.
        :type body: JSON or IO[bytes]
        :keyword project_kind: Represents the project kind. Known values are: "Conversation",
         "Orchestration", and "CustomConversationSummarization". Required.
        :paramtype project_kind: str or ~azure.ai.language.conversations.authoring.models.ProjectKind
        :keyword storage_input_container_name: The name of the storage container. Default value is
         None.
        :paramtype storage_input_container_name: str
        :keyword allow_overwrite: Whether to allow an existing project to be overwritten using the
         resulting copy authorization. Default value is None.
        :paramtype allow_overwrite: bool
        :return: CopyProjectDetails. The CopyProjectDetails is compatible with MutableMapping
        :rtype: ~azure.ai.language.conversations.authoring.models._models.CopyProjectDetails
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return await super()._copy_project_authorization(
            project_name=self._project_name,
            body=body,
            allow_overwrite=allow_overwrite,
            project_kind=project_kind,
            storage_input_container_name=storage_input_container_name,
            **kwargs,
        )

    @distributed_trace_async
    async def _get_assign_deployment_resources_status(  # type: ignore[override]
        self, job_id: str, **kwargs: Any
    ) -> DeploymentResourcesState:
        """Gets the status of an existing assign deployment resources job.

        :param job_id: The job ID. Required.
        :type job_id: str
        :return: DeploymentResourcesState. The DeploymentResourcesState is compatible with
         MutableMapping
        :rtype: ~azure.ai.language.conversations.authoring.models._models.DeploymentResourcesState
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return await super()._get_assign_deployment_resources_status(
            project_name=self._project_name, job_id=job_id, **kwargs
        )

    @distributed_trace_async
    async def _get_copy_project_status(self, job_id: str, **kwargs: Any) -> CopyProjectState:  # type: ignore[override]
        """Gets the status of an existing copy project job.

        :param job_id: The job ID. Required.
        :type job_id: str
        :return: CopyProjectState. The CopyProjectState is compatible with MutableMapping
        :rtype: ~azure.ai.language.conversations.authoring.models._models.CopyProjectState
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return await super()._get_copy_project_status(project_name=self._project_name, job_id=job_id, **kwargs)

    @distributed_trace_async
    async def _get_export_status(self, job_id: str, **kwargs: Any) -> ExportProjectState:  # type: ignore[override]
        """Gets the status of an export job. Once job completes, returns the project metadata, and assets.

        :param job_id: The job ID. Required.
        :type job_id: str
        :return: ExportProjectState. The ExportProjectState is compatible with MutableMapping
        :rtype: ~azure.ai.language.conversations.authoring.models._models.ExportProjectState
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return await super()._get_export_status(project_name=self._project_name, job_id=job_id, **kwargs)

    @distributed_trace_async
    async def get_project(self, **kwargs: Any) -> ProjectDetails:  # type: ignore[override]
        """Gets the details of a project.

        :return: ProjectDetails. The ProjectDetails is compatible with MutableMapping
        :rtype: ~azure.ai.language.conversations.authoring.models.ProjectDetails
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return await super()._get_project(project_name=self._project_name, **kwargs)

    @distributed_trace_async
    async def _get_project_deletion_status(self, job_id: str, **kwargs: Any) -> ProjectDeletionState:  # type: ignore[override]
        """Gets the status for a project deletion job.

        :param job_id: The job ID. Required.
        :type job_id: str
        :return: ProjectDeletionState. The ProjectDeletionState is compatible with MutableMapping
        :rtype: ~azure.ai.language.conversations.authoring.models._models.ProjectDeletionState
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return await super()._get_project_deletion_status(project_name=self._project_name, job_id=job_id, **kwargs)

    @distributed_trace_async
    async def _get_swap_deployments_status(self, job_id: str, **kwargs: Any) -> SwapDeploymentsState:  # type: ignore[override]
        """Gets the status of an existing swap deployment job.

        :param job_id: The job ID. Required.
        :type job_id: str
        :return: SwapDeploymentsState. The SwapDeploymentsState is compatible with MutableMapping
        :rtype: ~azure.ai.language.conversations.authoring.models._models.SwapDeploymentsState
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return await super()._get_swap_deployments_status(project_name=self._project_name, job_id=job_id, **kwargs)

    @distributed_trace_async
    async def _get_training_status(self, job_id: str, **kwargs: Any) -> TrainingState:  # type: ignore[override]
        """Gets the status for a training job.

        :param job_id: The job ID. Required.
        :type job_id: str
        :return: TrainingState. The TrainingState is compatible with MutableMapping
        :rtype: ~azure.ai.language.conversations.authoring.models.TrainingState
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return await super()._get_training_status(project_name=self._project_name, job_id=job_id, **kwargs)

    @distributed_trace_async
    async def _get_unassign_deployment_resources_status(  # type: ignore[override]
        self, job_id: str, **kwargs: Any
    ) -> DeploymentResourcesState:
        """Gets the status of an existing unassign deployment resources job.

        :param job_id: The job ID. Required.
        :type job_id: str
        :return: DeploymentResourcesState. The DeploymentResourcesState is compatible with
         MutableMapping
        :rtype: ~azure.ai.language.conversations.authoring.models._models.DeploymentResourcesState
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return await super()._get_unassign_deployment_resources_status(
            project_name=self._project_name, job_id=job_id, **kwargs
        )

    @distributed_trace
    def list_deployment_resources(  # type: ignore[override]
        self, *, skip: Optional[int] = _Unset, top: Optional[int] = _Unset, **kwargs: Any
    ) -> AsyncItemPaged[AssignedDeploymentResource]:
        """Lists the deployments resources assigned to the project.

        :keyword top: The number of result items to return. Default value is None.
        :paramtype top: int
        :keyword skip: The number of result items to skip. Default value is None.
        :paramtype skip: int
        :return: An iterator like instance of AssignedDeploymentResource
        :rtype:
         ~azure.core.async_paging.AsyncItemPaged[~azure.ai.language.conversations.authoring.models.AssignedDeploymentResource]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return super().list_deployment_resources(project_name=self._project_name, skip=skip, top=top, **kwargs)

    @distributed_trace
    def list_deployments(  # type: ignore[override]
        self, *, skip: Optional[int] = _Unset, top: Optional[int] = _Unset, **kwargs: Any
    ) -> AsyncItemPaged[ProjectDeployment]:
        """Lists the deployments belonging to a project.

        :keyword top: The number of result items to return. Default value is None.
        :paramtype top: int
        :keyword skip: The number of result items to skip. Default value is None.
        :paramtype skip: int
        :return: An iterator like instance of ProjectDeployment
        :rtype:
         ~azure.core.async_paging.AsyncItemPaged[~azure.ai.language.conversations.authoring.models.ProjectDeployment]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return super().list_deployments(project_name=self._project_name, skip=skip, top=top, **kwargs)

    @distributed_trace
    def list_exported_models(  # type: ignore[override]
        self, *, skip: Optional[int] = _Unset, top: Optional[int] = _Unset, **kwargs: Any
    ) -> AsyncItemPaged[ExportedTrainedModel]:
        """Lists the exported models belonging to a project.

        :keyword top: The number of result items to return. Default value is None.
        :paramtype top: int
        :keyword skip: The number of result items to skip. Default value is None.
        :paramtype skip: int
        :return: An iterator like instance of ExportedTrainedModel
        :rtype:
         ~azure.core.async_paging.AsyncItemPaged[~azure.ai.language.conversations.authoring.models.ExportedTrainedModel]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return super().list_exported_models(project_name=self._project_name, skip=skip, top=top, **kwargs)

    @distributed_trace
    def list_trained_models(  # type: ignore[override]
        self, *, skip: Optional[int] = _Unset, top: Optional[int] = _Unset, **kwargs: Any
    ) -> AsyncItemPaged[ProjectTrainedModel]:
        """Lists the trained models belonging to a project.

        :keyword top: The number of result items to return. Default value is None.
        :paramtype top: int
        :keyword skip: The number of result items to skip. Default value is None.
        :paramtype skip: int
        :return: An iterator like instance of ProjectTrainedModel
        :rtype:
         ~azure.core.async_paging.AsyncItemPaged[~azure.ai.language.conversations.authoring.models.ProjectTrainedModel]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return super().list_trained_models(project_name=self._project_name, skip=skip, top=top, **kwargs)

    @distributed_trace
    def list_training_jobs(  # type: ignore[override]
        self, *, skip: Optional[int] = _Unset, top: Optional[int] = _Unset, **kwargs: Any
    ) -> AsyncItemPaged[TrainingState]:
        """Lists the non-expired training jobs created for a project.

        :keyword top: The number of result items to return. Default value is None.
        :paramtype top: int
        :keyword skip: The number of result items to skip. Default value is None.
        :paramtype skip: int
        :return: An iterator like instance of TrainingState
        :rtype:
         ~azure.core.async_paging.AsyncItemPaged[~azure.ai.language.conversations.authoring.models.TrainingState]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return super().list_training_jobs(project_name=self._project_name, skip=skip, top=top, **kwargs)
