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

from azure.core.paging import ItemPaged
from azure.core.pipeline import PipelineResponse
from azure.core.polling import LROPoller, NoPolling, PollingMethod
from azure.core.rest import HttpRequest, HttpResponse
from azure.core.tracing.decorator import distributed_trace
from azure.core.utils import case_insensitive_dict

from .._utils.model_base import _deserialize
from ..models import (
    AssignedDeploymentResource,
    AssignDeploymentResourcesDetails,
    CopyProjectDetails,
    CopyProjectState,
    DeploymentResourcesState,
    ExportProjectState,
    ExportedProject,
    ExportedProjectFormat,
    ExportedTrainedModel,
    ImportProjectState,
    JobsPollingMethod,
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
    def begin_import(
        self,
        body: ExportedProject,
        *,
        exported_project_format: Optional[Union[str, ExportedProjectFormat]] = None,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> LROPoller[None]:
        """
        Triggers a job to import a project. If a project with the same name already exists, the data of that project is replaced.

        :param body: The project data to import. Required.
        :type body: ~azure.ai.language.conversations.authoring.models.ExportedProject
        :keyword exported_project_format: The format of the exported project file to use. Known values are: "Conversation" and "Luis". Default value is None.
        :paramtype exported_project_format: str or ~azure.ai.language.conversations.authoring.models.ExportedProjectFormat
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body. Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of LROPoller that returns None.
        :rtype: ~azure.core.polling.LROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:

        """

    @overload
    def begin_import(
        self,
        body: JSON,
        *,
        exported_project_format: Optional[Union[str, ExportedProjectFormat]] = None,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> LROPoller[None]:
        """
        Triggers a job to import a project. If a project with the same name already exists, the data of that project is replaced.

        :param body: The project data to import. Required.
        :type body: JSON
        :keyword exported_project_format: The format of the exported project file to use. Known values are: "Conversation" and "Luis". Default value is None.
        :paramtype exported_project_format: str or ~azure.ai.language.conversations.authoring.models.ExportedProjectFormat
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body. Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of LROPoller that returns None.
        :rtype: ~azure.core.polling.LROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:

        """

    @overload
    def begin_import(
        self,
        body: IO[bytes],
        *,
        exported_project_format: Optional[Union[str, ExportedProjectFormat]] = None,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> LROPoller[None]:
        """
        Triggers a job to import a project. If a project with the same name already exists, the data of that project is replaced.

        :param body: The project data to import. Required.
        :type body: IO[bytes]
        :keyword exported_project_format: The format of the exported project file to use. Known values are: "Conversation" and "Luis". Default value is None.
        :paramtype exported_project_format: str or ~azure.ai.language.conversations.authoring.models.ExportedProjectFormat
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body. Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of LROPoller that returns None.
        :rtype: ~azure.core.polling.LROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:

        """

    @distributed_trace
    def begin_import(
        self,
        body: Union[ExportedProject, JSON, IO[bytes]],
        *,
        exported_project_format: Optional[Union[str, ExportedProjectFormat]] = None,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> LROPoller[None]:
        """
        Triggers a job to import a project. If a project with the same name already exists, the data of that project is replaced.

        :param body: The project data to import. Required.
        :type body: ~azure.ai.language.conversations.authoring.models.ExportedProject or JSON or IO[bytes]
        :keyword exported_project_format: The format of the exported project file to use. Known values are: "Conversation" and "Luis".
        :paramtype exported_project_format: str or ~azure.ai.language.conversations.authoring.models.ExportedProjectFormat
        :return: An instance of LROPoller that returns None.
        :rtype: ~azure.core.polling.LROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:

        """
        return super()._begin_import_method(
            project_name=self._project_name,
            body=body,
            exported_project_format=exported_project_format,
            content_type=content_type,
            **kwargs,
        )

    @overload
    def begin_assign_deployment_resources(
        self, body: AssignDeploymentResourcesDetails, *, content_type: str = "application/json", **kwargs: Any
    ) -> LROPoller[None]:
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
    def begin_assign_deployment_resources(
        self, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> LROPoller[None]:
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
        :return: An instance of LROPoller that returns None.
        :rtype: ~azure.core.polling.LROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def begin_assign_deployment_resources(
        self, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> LROPoller[None]:
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
        :return: An instance of LROPoller that returns None.
        :rtype: ~azure.core.polling.LROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace
    def begin_assign_deployment_resources(
        self, body: Union[AssignDeploymentResourcesDetails, JSON, IO[bytes]], *, content_type: str = "application/json", **kwargs: Any
    ) -> LROPoller[None]:
        """Assign new Azure resources to a project to allow deploying new deployments to them.
        This API is available only via AAD authentication and not supported via subscription key authentication.
        For more details about AAD authentication, see:
        https://learn.microsoft.com/azure/cognitive-services/authentication?tabs=powershell#authenticate-with-azure-active-directory

        :param body: The new project resources info. Required.
        :type body: ~azure.ai.language.conversations.authoring.models.AssignDeploymentResourcesDetails or JSON or IO[bytes]
        :return: An instance of LROPoller that returns None.
        :rtype: ~azure.core.polling.LROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return super()._begin_assign_deployment_resources(
            project_name=self._project_name, body=body, content_type=content_type, **kwargs
        )

    @overload
    def begin_swap_deployments(
        self, body: SwapDeploymentsDetails, *, content_type: str = "application/json", **kwargs: Any
    ) -> LROPoller[None]:
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
    def begin_swap_deployments(
        self, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> LROPoller[None]:
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
    def begin_swap_deployments(
        self, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> LROPoller[None]:
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

    @distributed_trace
    def begin_swap_deployments(
        self, body: Union[SwapDeploymentsDetails, JSON, IO[bytes]], *, content_type: str = "application/json", **kwargs: Any
    ) -> LROPoller[None]:
        """Swaps two existing deployments with each other.

        :param body: The job object to swap two deployments. Required.
        :type body: ~azure.ai.language.conversations.authoring.models.SwapDeploymentsDetails or JSON or IO[bytes]
        :return: An instance of LROPoller that returns None.
        :rtype: ~azure.core.polling.LROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return super()._begin_swap_deployments(
            project_name=self._project_name, body=body, content_type=content_type, **kwargs
        )

    @overload
    def begin_unassign_deployment_resources(
        self, body: UnassignDeploymentResourcesDetails, *, content_type: str = "application/json", **kwargs: Any
    ) -> LROPoller[None]:
        """Unassign resources from a project. This disallows deploying new deployments to these resources,
        and deletes existing deployments assigned to them.

        :param body: The info for the deployment resources to be deleted. Required.
        :type body: ~azure.ai.language.conversations.authoring.models.UnassignDeploymentResourcesDetails
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
        Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of LROPoller that returns None.
        :rtype: ~azure.core.polling.LROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def begin_unassign_deployment_resources(
        self, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> LROPoller[None]:
        """Unassign resources from a project. This disallows deploying new deployments to these resources,
        and deletes existing deployments assigned to them.

        :param body: The info for the deployment resources to be deleted. Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
        Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of LROPoller that returns None.
        :rtype: ~azure.core.polling.LROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def begin_unassign_deployment_resources(
        self, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> LROPoller[None]:
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

    @distributed_trace
    def begin_unassign_deployment_resources(
        self, body: Union[UnassignDeploymentResourcesDetails, JSON, IO[bytes]], *, content_type: str = "application/json", **kwargs: Any
    ) -> LROPoller[None]:
        """Unassign resources from a project. This disallows deploying new deployments to these resources,
        and deletes existing deployments assigned to them.

        :param body: The info for the deployment resources to be deleted. Required.
        :type body: ~azure.ai.language.conversations.authoring.models.UnassignDeploymentResourcesDetails or JSON or IO[bytes]
        :return: An instance of LROPoller that returns None.
        :rtype: ~azure.core.polling.LROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return super()._begin_unassign_deployment_resources(
            project_name=self._project_name, body=body, content_type=content_type, **kwargs
        )

    @distributed_trace
    def begin_cancel_training_job(  # pylint: disable=function-redefined
        self,
        job_id: str,
        **kwargs: Any
    ) -> LROPoller[TrainingJobResult]:
        """
        Cancel a training job without requiring project_name explicitly.
        
        :param job_id: The identifier of the training job to cancel. Required.
        :type job_id: str
        :return: An instance of LROPoller that returns TrainingJobResult.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.language.conversations.authoring.models.TrainingJobResult]

        """
        _headers = kwargs.pop("headers", {}) or {}
        _params = kwargs.pop("params", {}) or {}

        cls: ClsType[TrainingJobResult] = kwargs.pop("cls", None)
        polling: Union[bool, PollingMethod] = kwargs.pop("polling", True)
        lro_delay = kwargs.pop("polling_interval", self._config.polling_interval)
        cont_token: Optional[str] = kwargs.pop("continuation_token", None)

        if cont_token is None:
            # 1) Send initial cancel request; keep PipelineResponse for the poller
            initial = self._cancel_training_job_initial(
                project_name=self._project_name,
                job_id=job_id,
                cls=lambda x, y, z: x,  # return PipelineResponse unchanged
                headers=_headers,
                params=_params,
                **kwargs,
            )
            initial.http_response.read()  # type: ignore
        kwargs.pop("error_map", None)

        # 2) Deserializer: extract nested "result" as TrainingJobResult
        def get_long_running_output(pipeline_response):
            body = pipeline_response.http_response.json() or {}
            result_dict = body.get("result", {}) or {}
            obj = _deserialize(TrainingJobResult, result_dict)
            if cls:
                return cls(pipeline_response, obj, {})  # type: ignore
            return obj

        # 3) Resolve {Endpoint} in Operation-Location for your poller
        path_format_arguments = {
            "Endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
        }

        # 4) Choose polling method: your JobsPollingMethod by default
        if polling is True:
            polling_method: PollingMethod = cast(
                PollingMethod,
                JobsPollingMethod(
                    polling_interval=lro_delay,
                    path_format_arguments=path_format_arguments,
                    # any extra kwargs your poller needs
                ),
            )
        elif polling is False:
            polling_method = cast(PollingMethod, NoPolling())
        else:
            polling_method = polling

        # 5) Continuation-token path
        if cont_token:
            return LROPoller[TrainingJobResult].from_continuation_token(
                polling_method=polling_method,
                continuation_token=cont_token,
                client=self._client,
                deserialization_callback=get_long_running_output,
            )

        # 6) Return the poller
        return LROPoller[TrainingJobResult](
            self._client,
            initial, # type: ignore
            get_long_running_output,
            polling_method,  # type: ignore
        )

    @overload
    def begin_copy_project(
        self, body: CopyProjectDetails, *, content_type: str = "application/json", **kwargs: Any
    ) -> LROPoller[None]:
        """Copies an existing project to another Azure resource.

        :param body: The copy project info. Required.
        :type body: ~azure.ai.language.conversations.authoring.models.CopyProjectDetails
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
        Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of LROPoller that returns None.
        :rtype: ~azure.core.polling.LROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def begin_copy_project(
        self, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> LROPoller[None]:
        """Copies an existing project to another Azure resource.

        :param body: The copy project info. Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
        Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of LROPoller that returns None.
        :rtype: ~azure.core.polling.LROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def begin_copy_project(
        self, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> LROPoller[None]:
        """Copies an existing project to another Azure resource.

        :param body: The copy project info. Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
        Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of LROPoller that returns None.
        :rtype: ~azure.core.polling.LROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace
    def begin_copy_project(
        self, body: Union[CopyProjectDetails, JSON, IO[bytes]], *, content_type: str = "application/json", **kwargs: Any
    ) -> LROPoller[None]:
        """Copies an existing project to another Azure resource.

        :param body: The copy project info. Required.
        :type body: ~azure.ai.language.conversations.authoring.models.CopyProjectDetails or JSON or IO[bytes]
        :return: An instance of LROPoller that returns None.
        :rtype: ~azure.core.polling.LROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return super()._begin_copy_project(
            project_name=self._project_name, body=body, content_type=content_type, **kwargs
        )

    @overload
    def begin_train(
        self, body: TrainingJobDetails, *, content_type: str = "application/json", **kwargs: Any
    ) -> LROPoller[TrainingJobResult]:
        """Triggers a training job for a project.

        :param body: The training input parameters. Required.
        :type body: ~azure.ai.language.conversations.authoring.models.TrainingJobDetails
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of LROPoller that returns TrainingJobResult. The TrainingJobResult is
         compatible with MutableMapping
        :rtype:
         ~azure.core.polling.LROPoller[~azure.ai.language.conversations.authoring.models.TrainingJobResult]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def begin_train(
        self, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> LROPoller[TrainingJobResult]:
        """Triggers a training job for a project.

        :param body: The training input parameters. Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of LROPoller that returns TrainingJobResult. The TrainingJobResult is
         compatible with MutableMapping
        :rtype:
         ~azure.core.polling.LROPoller[~azure.ai.language.conversations.authoring.models.TrainingJobResult]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def begin_train(
        self, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> LROPoller[TrainingJobResult]:
        """Triggers a training job for a project.

        :param body: The training input parameters. Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of LROPoller that returns TrainingJobResult. The TrainingJobResult is
         compatible with MutableMapping
        :rtype:
         ~azure.core.polling.LROPoller[~azure.ai.language.conversations.authoring.models.TrainingJobResult]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace
    def begin_train(  # type: ignore[override]
        self, body: Union[TrainingJobDetails, JSON, IO[bytes]], *, content_type: str = "application/json", **kwargs: Any
    ) -> LROPoller[TrainingJobResult]:
        """Triggers a training job for a project.

        :param body: The training input parameters. Required.
        :type body: Union[TrainingJobDetails, JSON, IO[bytes]]
        :keyword content_type: Body Parameter content-type. Content type parameter for the request body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of LROPoller that returns TrainingJobResult. The TrainingJobResult is
         compatible with MutableMapping
        :rtype:
         ~azure.core.polling.LROPoller[~azure.ai.language.conversations.authoring.models.TrainingJobResult]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return super()._begin_train(project_name=self._project_name, body=body, content_type=content_type, **kwargs)

    @distributed_trace
    def begin_export(
        self,
        *,
        string_index_type: Union[str, StringIndexType],
        exported_project_format: Optional[Union[str, ExportedProjectFormat]] = None,
        asset_kind: Optional[str] = None,
        trained_model_label: Optional[str] = None,
        **kwargs: Any
    ) -> LROPoller[None]:
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
        :return: An instance of LROPoller that returns None.
        :rtype: ~azure.core.polling.LROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return super()._begin_export(
            project_name=self._project_name,
            asset_kind=asset_kind,
            exported_project_format=exported_project_format,
            string_index_type=string_index_type,
            trained_model_label=trained_model_label,
            **kwargs,
        )

    @overload
    def copy_project_authorization(
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
    def copy_project_authorization(
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
    def copy_project_authorization(
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

    @distributed_trace
    def copy_project_authorization(  # type: ignore[override]
        self,
        body: Union[JSON, IO[bytes]] = _Unset,
        *,
        allow_overwrite: Optional[bool] = _Unset,
        content_type: str = "application/json",
        project_kind: Union[str, Any] = _Unset,
        storage_input_container_name: Optional[str] = _Unset,
        **kwargs: Any
    ) -> CopyProjectDetails:
        return super()._copy_project_authorization(
            project_name=self._project_name,
            body=body,
            allow_overwrite=allow_overwrite,
            content_type=content_type,
            project_kind=project_kind,
            storage_input_container_name=storage_input_container_name,
            **kwargs,
        )

    @distributed_trace
    def _get_assign_deployment_resources_status(  # type: ignore[override]
        self, job_id: str, **kwargs: Any
    ) -> DeploymentResourcesState:
        return super()._get_assign_deployment_resources_status(project_name=self._project_name, job_id=job_id, **kwargs)

    @distributed_trace
    def _get_copy_project_status(self, job_id: str, **kwargs: Any) -> CopyProjectState:  # type: ignore[override]
        return super()._get_copy_project_status(project_name=self._project_name, job_id=job_id, **kwargs)

    @distributed_trace
    def _get_export_status(self, job_id: str, **kwargs: Any) -> ExportProjectState:  # type: ignore[override]
        return super()._get_export_status(project_name=self._project_name, job_id=job_id, **kwargs)

    @distributed_trace
    def get_project(self, **kwargs: Any) -> ProjectDetails:  # type: ignore[override]
        return super()._get_project(project_name=self._project_name, **kwargs)

    @distributed_trace
    def _get_project_deletion_status(self, job_id: str, **kwargs: Any) -> ProjectDeletionState:  # type: ignore[override]
        return super()._get_project_deletion_status(project_name=self._project_name, job_id=job_id, **kwargs)

    @distributed_trace
    def _get_swap_deployments_status(self, job_id: str, **kwargs: Any) -> SwapDeploymentsState:  # type: ignore[override]
        return super()._get_swap_deployments_status(project_name=self._project_name, job_id=job_id, **kwargs)

    @distributed_trace
    def _get_training_status(self, job_id: str, **kwargs: Any) -> TrainingState:  # type: ignore[override]
        return super()._get_training_status(project_name=self._project_name, job_id=job_id, **kwargs)

    @distributed_trace
    def _get_unassign_deployment_resources_status(  # type: ignore[override]
        self, job_id: str, **kwargs: Any
    ) -> DeploymentResourcesState:
        return super()._get_unassign_deployment_resources_status(
            project_name=self._project_name, job_id=job_id, **kwargs
        )

    @distributed_trace
    def list_deployment_resources(  # type: ignore[override]
        self, *, skip: Optional[int] = _Unset, top: Optional[int] = _Unset, **kwargs: Any
    ) -> ItemPaged[AssignedDeploymentResource]:
        return super().list_deployment_resources(project_name=self._project_name, skip=skip, top=top, **kwargs)

    @distributed_trace
    def list_deployments(  # type: ignore[override]
        self, *, skip: Optional[int] = _Unset, top: Optional[int] = _Unset, **kwargs: Any
    ) -> ItemPaged[ProjectDeployment]:
        return super().list_deployments(project_name=self._project_name, skip=skip, top=top, **kwargs)

    @distributed_trace
    def list_exported_models(  # type: ignore[override]
        self, *, skip: Optional[int] = _Unset, top: Optional[int] = _Unset, **kwargs: Any
    ) -> ItemPaged[ExportedTrainedModel]:
        return super().list_exported_models(project_name=self._project_name, skip=skip, top=top, **kwargs)

    @distributed_trace
    def list_trained_models(  # type: ignore[override]
        self, *, skip: Optional[int] = _Unset, top: Optional[int] = _Unset, **kwargs: Any
    ) -> ItemPaged[ProjectTrainedModel]:
        return super().list_trained_models(project_name=self._project_name, skip=skip, top=top, **kwargs)

    @distributed_trace
    def list_training_jobs(  # type: ignore[override]
        self, *, skip: Optional[int] = _Unset, top: Optional[int] = _Unset, **kwargs: Any
    ) -> ItemPaged[TrainingState]:
        return super().list_training_jobs(project_name=self._project_name, skip=skip, top=top, **kwargs)
