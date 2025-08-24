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
from ._project_op_patch_deployment_relate import _ProjectOperationsDeploymentsRelated
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


class ProjectOperations(_ProjectOperationsDeploymentsRelated):
    """Patched ProjectOperationsOperations that auto-injects project_name."""

    def __init__(self, *args, project_name: str, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self._project_name = project_name

    @overload
    def begin_import(
        self,
        body: ExportedProject,
        *,
        format: Optional[str] = None,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> LROPoller[ImportProjectState]:
        """Triggers a job to import a project. If a project with the same name already exists,
        the data of that project is replaced.

        :param body: The project data to import. Required.
        :type body: ~azure.ai.language.text.authoring.models.ExportedProject
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
        Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of LROPoller that returns ImportProjectState.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.language.text.authoring.models.ImportProjectState]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def begin_import(
        self, body: JSON, *, format: Optional[str] = None, content_type: str = "application/json", **kwargs: Any
    ) -> LROPoller[ImportProjectState]:
        """Triggers a job to import a project. If a project with the same name already exists,
        the data of that project is replaced.

        :param body: The project data to import. Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
        Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of LROPoller that returns ImportProjectState.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.language.text.authoring.models.ImportProjectState]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def begin_import(
        self, body: IO[bytes], *, format: Optional[str] = None, content_type: str = "application/json", **kwargs: Any
    ) -> LROPoller[ImportProjectState]:
        """Triggers a job to import a project. If a project with the same name already exists,
        the data of that project is replaced.

        :param body: The project data to import. Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
        Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of LROPoller that returns ImportProjectState.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.language.text.authoring.models.ImportProjectState]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace
    def begin_import(
        self, body: Union[ExportedProject, JSON, IO[bytes]], *, format: Optional[str] = None, **kwargs: Any
    ) -> LROPoller[ImportProjectState]:
        """Triggers a job to import a project. If a project with the same name already exists,
        the data of that project is replaced.

        :param body: The project data to import. Required.
        :type body: ~azure.ai.language.text.authoring.models.ExportedProject or JSON or IO[bytes]
        :return: An instance of LROPoller that returns ImportProjectState.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.language.text.authoring.models.ImportProjectState]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
        cls: ClsType[ImportProjectState] = kwargs.pop("cls", None)
        polling: Union[bool, PollingMethod] = kwargs.pop("polling", True)
        lro_delay = kwargs.pop("polling_interval", self._config.polling_interval)
        cont_token: Optional[str] = kwargs.pop("continuation_token", None)

        if cont_token is None:
            initial = self._import_method_initial(
                project_name=self._project_name,  # ← use instance project name
                body=body,
                format=format,
                content_type=content_type,
                cls=lambda x, y, z: x,  # return PipelineResponse
                headers=_headers,
                params=_params,
                **kwargs,
            )
            initial.http_response.read()  # type: ignore
        kwargs.pop("error_map", None)

        def get_long_running_output(pipeline_response):
            # Final payload is at the ROOT of the jobs response
            obj = _deserialize(ImportProjectState, pipeline_response.http_response.json())
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
            return LROPoller[ImportProjectState].from_continuation_token(
                polling_method=polling_method,
                continuation_token=cont_token,
                client=self._client,
                deserialization_callback=get_long_running_output,
            )

        return LROPoller[ImportProjectState](
            self._client, initial, get_long_running_output, polling_method  # type: ignore
        )

    @distributed_trace
    def begin_cancel_training_job(  # type: ignore[override]
        self, job_id: str, **kwargs: Any
    ) -> LROPoller[TrainingJobResult]:
        """Cancel a training job without requiring project_name explicitly."""
        return super().begin_cancel_training_job(project_name=self._project_name, job_id=job_id, **kwargs)

    @overload
    def begin_copy_project(
        self, body: CopyProjectDetails, *, content_type: str = "application/json", **kwargs: Any
    ) -> LROPoller[CopyProjectState]:
        """Copies an existing project to another Azure resource.

        :param body: The copy project info. Required.
        :type body: ~azure.ai.language.text.authoring.models.CopyProjectDetails
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
        Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of LROPoller that returns CopyProjectState.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.language.text.authoring.models.CopyProjectState]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def begin_copy_project(
        self, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> LROPoller[CopyProjectState]:
        """Copies an existing project to another Azure resource.

        :param body: The copy project info. Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
        Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of LROPoller that returns CopyProjectState.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.language.text.authoring.models.CopyProjectState]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def begin_copy_project(
        self, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> LROPoller[CopyProjectState]:
        """Copies an existing project to another Azure resource.

        :param body: The copy project info. Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
        Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of LROPoller that returns CopyProjectState.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.language.text.authoring.models.CopyProjectState]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace
    def begin_copy_project(
        self, body: Union[CopyProjectDetails, JSON, IO[bytes]], **kwargs: Any
    ) -> LROPoller[CopyProjectState]:
        """Copies an existing project to another Azure resource.

        :param body: The copy project info. Required.
        :type body: ~azure.ai.language.text.authoring.models.CopyProjectDetails or JSON or IO[bytes]
        :return: An instance of LROPoller that returns CopyProjectState.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.language.text.authoring.models.CopyProjectState]
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
                **kwargs,
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

    @overload
    def begin_train(
        self, body: TrainingJobDetails, *, content_type: str = "application/json", **kwargs: Any
    ) -> LROPoller[TrainingJobResult]:
        """Triggers a training job for a project.

        :param body: The training input parameters. Required.
        :type body: ~azure.ai.language.text.authoring.models.TrainingJobDetails
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of LROPoller that returns TrainingJobResult. The TrainingJobResult is
         compatible with MutableMapping
        :rtype:
         ~azure.core.polling.LROPoller[~azure.ai.language.text.authoring.models.TrainingJobResult]
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
         ~azure.core.polling.LROPoller[~azure.ai.language.text.authoring.models.TrainingJobResult]
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
         ~azure.core.polling.LROPoller[~azure.ai.language.text.authoring.models.TrainingJobResult]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace
    def begin_train(  # type: ignore[override]
        self, body: Union[TrainingJobDetails, JSON, IO[bytes]], *, content_type: str = "application/json", **kwargs: Any
    ) -> LROPoller[TrainingJobResult]:
        """Begin training without requiring project_name explicitly."""
        return super()._begin_train(project_name=self._project_name, body=body, content_type=content_type, **kwargs)

    @distributed_trace
    def begin_export(
        self,
        *,
        string_index_type: Union[str, StringIndexType],
        asset_kind: Optional[str] = None,
        trained_model_label: Optional[str] = None,
        **kwargs: Any
    ) -> LROPoller[ExportProjectState]:
        """Triggers a job to export a project's data.

        :keyword string_index_type: Specifies the method used to interpret string offsets. See
            https://aka.ms/text-analytics-offsets. Known values: "Utf16CodeUnit", "Utf8CodeUnit",
            "Utf32CodeUnit". Required.
        :paramtype string_index_type: str or ~azure.ai.language.text.authoring.models.StringIndexType
        :keyword asset_kind: Kind of asset to export.
        :paramtype asset_kind: str
        :keyword trained_model_label: Trained model label to export. If None, exports the working copy.
        :paramtype trained_model_label: str
        :return: An instance of LROPoller that returns ExportProjectState.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.language.text.authoring.models.ExportProjectState]
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
                asset_kind=asset_kind,
                trained_model_label=trained_model_label,
                cls=lambda x, y, z: x,  # return PipelineResponse
                headers=_headers,
                params=_params,
                **kwargs,
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

        :keyword project_kind: Represents the project kind. Known values are:
         "CustomSingleLabelClassification", "CustomMultiLabelClassification", "CustomEntityRecognition",
         "CustomAbstractiveSummarization", "CustomHealthcare", and "CustomTextSentiment". Required.
        :paramtype project_kind: str or ~azure.ai.language.text.authoring.models.ProjectKind
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
        :rtype: ~azure.ai.language.text.authoring.models.CopyProjectDetails
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
        :rtype: ~azure.ai.language.text.authoring.models.CopyProjectDetails
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
        :rtype: ~azure.ai.language.text.authoring.models.CopyProjectDetails
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
