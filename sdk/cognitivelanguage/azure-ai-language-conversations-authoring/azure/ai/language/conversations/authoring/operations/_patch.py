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
    DeleteDeploymentDetails,
    CreateDeploymentDetails,
    DeploymentDeleteFromResourcesState,
    DeploymentState,
    ExportedModelDetails,
    ExportedTrainedModel,
    ExportedModelState,
    EvaluationDetails,
    EvaluationJobResult,
    EvaluationState,
    LoadSnapshotState,
    ProjectTrainedModel,
    EvalSummary,
    StringIndexType,
    UtteranceEvaluationResult,
    ExportedProjectFormat,
    JobsPollingMethod,
    DeploymentResourcesState
)
from azure.core.paging import ItemPaged
from collections.abc import MutableMapping
from azure.core.pipeline import PipelineResponse
from azure.core.rest import HttpRequest, HttpResponse
JSON = MutableMapping[str, Any]
T = TypeVar("T")
_Unset: Any = object()
ClsType = Optional[Callable[[PipelineResponse[HttpRequest, HttpResponse], T, Dict[str, Any]], Any]]


class ProjectOperations(ProjectOperationsGenerated):
    """Patched ProjectOperationsOperations that auto-injects project_name."""

    def __init__(self, *args, project_name: str, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self._project_name = project_name

    @distributed_trace
    def begin_assign_deployment_resources(
        self,
        body: Union[AssignDeploymentResourcesDetails, JSON, IO[bytes]],
        **kwargs: Any
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
                cls=lambda x, y, z: x,           # return PipelineResponse
                headers=_headers,
                params=_params,
                **kwargs
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
                    header_name="Operation-Location",     # service returns jobs URL here
                    final_via_async_url=True,             # take final body from jobs URL
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

    @distributed_trace
    def begin_cancel_training_job(  # type: ignore[override]
        self, job_id: str, **kwargs: Any
    ) -> LROPoller[TrainingJobResult]:
        """Cancel a training job without requiring project_name explicitly."""
        return super().begin_cancel_training_job(project_name=self._project_name, job_id=job_id, **kwargs)

    @distributed_trace
    def begin_copy_project(
        self,
        body: Union[CopyProjectDetails, JSON, IO[bytes]],
        **kwargs: Any
    ) -> LROPoller[CopyProjectState]:
        """Copies an existing project to another Azure resource.

        :param body: The copy project info. Required.
        :type body: ~azure.ai.language.conversations.authoring.models.CopyProjectDetails or JSON or IO[bytes]
        :return: An instance of LROPoller that returns CopyProjectState.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.language.conversations.authoring.models.CopyProjectState]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
        cls: ClsType[CopyProjectState] = kwargs.pop("cls", None)
        polling: Union[bool, PollingMethod] = kwargs.pop("polling", True)
        lro_delay = kwargs.pop("polling_interval", self._config.polling_interval)
        cont_token: Optional[str] = kwargs.pop("continuation_token", None)

        if cont_token is None:
            initial = self._copy_project_initial(
                project_name=self._project_name,  # ← use instance project name
                body=body,
                content_type=content_type,
                cls=lambda x, y, z: x,  # return PipelineResponse
                headers=_headers,
                params=_params,
                **kwargs
            )
            initial.http_response.read()  # type: ignore
        kwargs.pop("error_map", None)

        def get_long_running_output(pipeline_response):
            # Final payload is at the root of the jobs response
            obj = _deserialize(CopyProjectState, pipeline_response.http_response.json())
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
            return LROPoller[CopyProjectState].from_continuation_token(
                polling_method=polling_method,
                continuation_token=cont_token,
                client=self._client,
                deserialization_callback=get_long_running_output,
            )

        return LROPoller[CopyProjectState](
            self._client, initial, get_long_running_output, polling_method  # type: ignore
        )

    @distributed_trace
    def begin_train(  # type: ignore[override]
        self, body: Union[TrainingJobDetails, JSON, IO[bytes]], *, content_type: str = "application/json", **kwargs: Any
    ) -> LROPoller[TrainingJobResult]:
        """Begin training without requiring project_name explicitly."""
        return super().begin_train(project_name=self._project_name, body=body, content_type=content_type, **kwargs)

    @distributed_trace
    def begin_export(
        self,
        *,
        string_index_type: Union[str, StringIndexType],
        exported_project_format: Optional[Union[str, ExportedProjectFormat]] = None,
        asset_kind: Optional[str] = None,
        trained_model_label: Optional[str] = None,
        **kwargs: Any
    ) -> LROPoller[ExportProjectState]:
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
        :return: An instance of LROPoller that returns ExportProjectState.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.language.conversations.authoring.models.ExportProjectState]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        _headers = kwargs.pop("headers", {}) or {}
        _params = kwargs.pop("params", {}) or {}

        cls: ClsType[ExportProjectState] = kwargs.pop("cls", None)
        polling: Union[bool, PollingMethod] = kwargs.pop("polling", True)
        lro_delay = kwargs.pop("polling_interval", self._config.polling_interval)
        cont_token: Optional[str] = kwargs.pop("continuation_token", None)

        if cont_token is None:
            initial = self._export_initial(
                project_name=self._project_name,  # ← use instance-scoped project name
                string_index_type=string_index_type,
                exported_project_format=exported_project_format,
                asset_kind=asset_kind,
                trained_model_label=trained_model_label,
                cls=lambda x, y, z: x,  # return PipelineResponse
                headers=_headers,
                params=_params,
                **kwargs
            )
            initial.http_response.read()  # type: ignore
        kwargs.pop("error_map", None)

        def get_long_running_output(pipeline_response):
            obj = _deserialize(ExportProjectState, pipeline_response.http_response.json())
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
            return LROPoller[ExportProjectState].from_continuation_token(
                polling_method=polling_method,
                continuation_token=cont_token,
                client=self._client,
                deserialization_callback=get_long_running_output,
            )

        return LROPoller[ExportProjectState](
            self._client, initial, get_long_running_output, polling_method  # type: ignore
        )

    @distributed_trace
    def begin_swap_deployments(
        self,
        body: Union[SwapDeploymentsDetails, JSON, IO[bytes]],
        **kwargs: Any
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
                **kwargs
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

    @distributed_trace
    def begin_unassign_deployment_resources(
        self,
        body: Union[UnassignDeploymentResourcesDetails, JSON, IO[bytes]],
        **kwargs: Any
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
                project_name=self._project_name,   # ← use instance project name
                body=body,
                content_type=content_type,
                cls=lambda x, y, z: x,            # return PipelineResponse
                headers=_headers,
                params=_params,
                **kwargs
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
        return super().copy_project_authorization(
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
    def get_project(self, project_name: str = _Unset, **kwargs: Any) -> ProjectDetails:  # type: ignore[override]
        return super().get_project(project_name=self._project_name, **kwargs)

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


class DeploymentOperations(DeploymentOperationsGenerated):

    def __init__(self, *args, project_name: str, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._project_name = project_name

    
    @distributed_trace
    def begin_delete_deployment(
        self,
        deployment_name: str,
        **kwargs: Any
    ) -> LROPoller[DeploymentState]:
        """Deletes a project deployment.

        :param deployment_name: The name of the specific deployment of the project to use. Required.
        :type deployment_name: str
        :return: An instance of LROPoller that returns DeploymentState.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.language.conversations.authoring.models.DeploymentState]
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
                project_name=self._project_name,     # ← use instance-scoped project name
                deployment_name=deployment_name,
                cls=lambda x, y, z: x,               # return PipelineResponse
                headers=_headers,
                params=_params,
                **kwargs
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

    @distributed_trace
    def begin_delete_deployment_from_resources(
        self,
        deployment_name: str,
        body: Union[DeleteDeploymentDetails, JSON, IO[bytes]],
        **kwargs: Any
    ) -> LROPoller[DeploymentDeleteFromResourcesState]:
        """Deletes a project deployment from the specified assigned resources.

        :param deployment_name: The name of the specific deployment of the project to use. Required.
        :type deployment_name: str
        :param body: The options for deleting the deployment. Required.
        :type body: ~azure.ai.language.conversations.authoring.models.DeleteDeploymentDetails or JSON or IO[bytes]
        :return: An instance of LROPoller that returns DeploymentDeleteFromResourcesState.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.language.conversations.authoring.models.DeploymentDeleteFromResourcesState]
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
                project_name=self._project_name,        # ← use instance-scoped project name
                deployment_name=deployment_name,
                body=body,
                content_type=content_type,
                cls=lambda x, y, z: x,                  # return PipelineResponse
                headers=_headers,
                params=_params,
                **kwargs
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
        :type body: ~azure.ai.language.conversations.authoring.models.CreateDeploymentDetails
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of LROPoller that returns DeploymentState.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.language.conversations.authoring.models.DeploymentState]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def begin_deploy_project(
        self,
        deployment_name: str,
        body: JSON,
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
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of LROPoller that returns DeploymentState.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.language.conversations.authoring.models.DeploymentState]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def begin_deploy_project(
        self,
        deployment_name: str,
        body: IO[bytes],
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
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of LROPoller that returns DeploymentState.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.language.conversations.authoring.models.DeploymentState]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace
    def begin_deploy_project(
        self,
        deployment_name: str,
        body: Union[CreateDeploymentDetails, JSON, IO[bytes]],
        **kwargs: Any
    ) -> LROPoller[DeploymentState]:
        """Creates a new deployment or replaces an existing one.

        :param deployment_name: The name of the specific deployment of the project to use. Required.
        :type deployment_name: str
        :param body: The new deployment info. Required.
        :type body: ~azure.ai.language.conversations.authoring.models.CreateDeploymentDetails or JSON or IO[bytes]
        :return: An instance of LROPoller that returns DeploymentState.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.language.conversations.authoring.models.DeploymentState]
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
                **kwargs
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


class ExportedModelOperations(ExportedModelOperationsGenerated):

    def __init__(self, *args, project_name: str, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._project_name = project_name

    @distributed_trace
    def begin_create_or_update_exported_model(
        self,
        exported_model_name: str,
        body: Union[ExportedModelDetails, JSON, IO[bytes]],
        **kwargs: Any
    ) -> LROPoller[ExportedModelState]:
        """Creates a new exported model or replaces an existing one.

        :param exported_model_name: The exported model name. Required.
        :type exported_model_name: str
        :param body: The exported model info. Required.
        :type body: ~azure.ai.language.conversations.authoring.models.ExportedModelDetails or JSON or IO[bytes]
        :return: An instance of LROPoller that returns ExportedModelState.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.language.conversations.authoring.models.ExportedModelState]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
        cls: ClsType[ExportedModelState] = kwargs.pop("cls", None)
        polling: Union[bool, PollingMethod] = kwargs.pop("polling", True)
        lro_delay = kwargs.pop("polling_interval", self._config.polling_interval)
        cont_token: Optional[str] = kwargs.pop("continuation_token", None)

        if cont_token is None:
            initial = self._create_or_update_exported_model_initial(
                project_name=self._project_name,         # ← use instance-scoped project name
                exported_model_name=exported_model_name,
                body=body,
                content_type=content_type,
                cls=lambda x, y, z: x,                   # return PipelineResponse
                headers=_headers,
                params=_params,
                **kwargs
            )
            initial.http_response.read()  # type: ignore
        kwargs.pop("error_map", None)

        def get_long_running_output(pipeline_response):
            # Final jobs payload is at the ROOT
            obj = _deserialize(ExportedModelState, pipeline_response.http_response.json())
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
            return LROPoller[ExportedModelState].from_continuation_token(
                polling_method=polling_method,
                continuation_token=cont_token,
                client=self._client,
                deserialization_callback=get_long_running_output,
            )

        return LROPoller[ExportedModelState](
            self._client, initial, get_long_running_output, polling_method  # type: ignore
        )

    @distributed_trace
    def begin_delete_exported_model(
        self,
        exported_model_name: str,
        **kwargs: Any
    ) -> LROPoller[ExportedModelState]:
        """Deletes an existing exported model.

        :param exported_model_name: The exported model name. Required.
        :type exported_model_name: str
        :return: An instance of LROPoller that returns ExportedModelState.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.language.conversations.authoring.models.ExportedModelState]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        _headers = kwargs.pop("headers", {}) or {}
        _params = kwargs.pop("params", {}) or {}

        cls: ClsType[ExportedModelState] = kwargs.pop("cls", None)
        polling: Union[bool, PollingMethod] = kwargs.pop("polling", True)
        lro_delay = kwargs.pop("polling_interval", self._config.polling_interval)
        cont_token: Optional[str] = kwargs.pop("continuation_token", None)

        if cont_token is None:
            initial = self._delete_exported_model_initial(
                project_name=self._project_name,        # ← use instance-scoped project name
                exported_model_name=exported_model_name,
                cls=lambda x, y, z: x,                  # return PipelineResponse
                headers=_headers,
                params=_params,
                **kwargs
            )
            initial.http_response.read()  # type: ignore
        kwargs.pop("error_map", None)

        def get_long_running_output(pipeline_response):
            obj = _deserialize(ExportedModelState, pipeline_response.http_response.json())
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
            return LROPoller[ExportedModelState].from_continuation_token(
                polling_method=polling_method,
                continuation_token=cont_token,
                client=self._client,
                deserialization_callback=get_long_running_output,
            )

        return LROPoller[ExportedModelState](
            self._client, initial, get_long_running_output, polling_method  # type: ignore
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


class TrainedModelOperations(TrainedModelOperationsGenerated):

    def __init__(self, *args, project_name: str, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._project_name = project_name

    @distributed_trace
    def begin_evaluate_model(  # type: ignore[override]
        self,
        trained_model_label: str,
        body: Union[EvaluationDetails, dict, IO[bytes]],
        *,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> LROPoller[EvaluationJobResult]:
        return super().begin_evaluate_model(
            project_name=self._project_name,
            trained_model_label=trained_model_label,
            body=body,
            content_type=content_type,
            **kwargs,
        )

    @distributed_trace
    def begin_load_snapshot(
        self,
        trained_model_label: str,
        **kwargs: Any
    ) -> LROPoller[LoadSnapshotState]:
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
                project_name=self._project_name,          # ← use instance-scoped project name
                trained_model_label=trained_model_label,
                cls=lambda x, y, z: x,                    # return PipelineResponse
                headers=_headers,
                params=_params,
                **kwargs
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
        skip: Optional[int] = None,
        string_index_type: Union[str, StringIndexType],
        top: Optional[int] = None,
        **kwargs: Any
    ) -> ItemPaged[UtteranceEvaluationResult]:
        return super().get_model_evaluation_results(
            project_name=self._project_name,
            trained_model_label=trained_model_label,
            skip=skip,
            string_index_type=string_index_type,
            top=top,
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


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """


__all__ = ["ProjectOperations", "DeploymentOperations", "ExportedModelOperations", "TrainedModelOperations"]
