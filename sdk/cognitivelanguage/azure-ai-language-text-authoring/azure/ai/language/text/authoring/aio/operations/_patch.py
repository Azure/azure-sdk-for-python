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
from azure.core.polling import AsyncLROPoller, AsyncNoPolling, AsyncPollingMethod
from azure.core.tracing.decorator import distributed_trace

from ._operations import (
    ProjectOperations as ProjectOperationsGenerated,
    DeploymentOperations as DeploymentOperationsGenerated,
    ExportedModelOperations as ExportedModelOperationsGenerated,
    TrainedModelOperations as TrainedModelOperationsGenerated,
)

from ...models import (
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
    ProjectMetadata,
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
    DocumentEvalResult,
    ExportedModelManifest,
)
from azure.core.async_paging import AsyncItemPaged, AsyncList
from collections.abc import MutableMapping

JSON = MutableMapping[str, Any]
_Unset: Any = object()


class ProjectOperations(ProjectOperationsGenerated):
    """Patched ProjectOperationsOperations that auto-injects project_name."""

    def __init__(self, *args, project_name: str, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self._project_name = project_name

    @distributed_trace
    async def begin_assign_deployment_resources(  # type: ignore[override]
        self,
        body: Union[AssignDeploymentResourcesDetails, JSON, IO[bytes]],
        *,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> AsyncLROPoller[None]:
        """Assign deployment resources without requiring project_name explicitly."""
        return await super().begin_assign_deployment_resources(
            project_name=self._project_name, body=body, content_type=content_type, **kwargs
        )

    @distributed_trace
    async def begin_cancel_training_job(  # type: ignore[override]
        self, job_id: str, **kwargs: Any
    ) -> AsyncLROPoller[TrainingJobResult]:
        """Cancel a training job without requiring project_name explicitly."""
        return await super().begin_cancel_training_job(project_name=self._project_name, job_id=job_id, **kwargs)

    @distributed_trace
    async def begin_copy_project(  # type: ignore[override]
        self,
        body: Union[CopyProjectDetails, JSON, IO[bytes]],
        *,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> AsyncLROPoller[None]:
        """Copy a project without requiring project_name explicitly."""
        return await super().begin_copy_project(
            project_name=self._project_name, body=body, content_type=content_type, **kwargs
        )

    @distributed_trace
    async def begin_train(  # type: ignore[override]
        self,
        body: Union[TrainingJobDetails, JSON, IO[bytes]],
        *,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> AsyncLROPoller[TrainingJobResult]:
        """Begin training without requiring project_name explicitly."""
        return await super().begin_train(
            project_name=self._project_name, body=body, content_type=content_type, **kwargs
        )

    @distributed_trace
    async def begin_export(  # type: ignore[override]
        self,
        *,
        asset_kind: Optional[str] = _Unset,
        exported_project_format: Optional[Union[str, Any]] = _Unset,
        string_index_type: Union[str, Any] = _Unset,
        trained_model_label: Optional[str] = _Unset,
        **kwargs: Any
    ) -> AsyncLROPoller[None]:
        return await super().begin_export(
            project_name=self._project_name,
            asset_kind=asset_kind,
            exported_project_format=exported_project_format,
            string_index_type=string_index_type,
            trained_model_label=trained_model_label,
            **kwargs,
        )

    @distributed_trace
    async def begin_swap_deployments(  # type: ignore[override]
        self,
        body: Union[SwapDeploymentsDetails, JSON, IO[bytes]] = _Unset,
        *,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> AsyncLROPoller[None]:
        return await super().begin_swap_deployments(
            project_name=self._project_name, body=body, content_type=content_type, **kwargs
        )

    @distributed_trace
    async def begin_unassign_deployment_resources(  # type: ignore[override]
        self,
        body: Union[UnassignDeploymentResourcesDetails, JSON, IO[bytes]] = _Unset,
        *,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> AsyncLROPoller[None]:
        return await super().begin_unassign_deployment_resources(
            project_name=self._project_name, body=body, content_type=content_type, **kwargs
        )

    @distributed_trace
    async def copy_project_authorization(  # type: ignore[override]
        self,
        body: Union[JSON, IO[bytes]] = _Unset,
        *,
        allow_overwrite: Optional[bool] = _Unset,
        content_type: str = "application/json",
        project_kind: Union[str, Any] = _Unset,
        storage_input_container_name: Optional[str] = _Unset,
        **kwargs: Any
    ) -> CopyProjectDetails:
        return await super().copy_project_authorization(
            project_name=self._project_name,
            body=body,
            allow_overwrite=allow_overwrite,
            content_type=content_type,
            project_kind=project_kind,
            storage_input_container_name=storage_input_container_name,
            **kwargs,
        )

    @distributed_trace
    async def get_assign_deployment_resources_status(  # type: ignore[override]
        self, job_id: str, **kwargs: Any
    ) -> DeploymentResourcesState:
        return await super().get_assign_deployment_resources_status(
            project_name=self._project_name, job_id=job_id, **kwargs
        )

    @distributed_trace
    async def get_copy_project_status(  # type: ignore[override]
        self, job_id: str, **kwargs: Any
    ) -> CopyProjectState:
        return await super().get_copy_project_status(project_name=self._project_name, job_id=job_id, **kwargs)

    @distributed_trace
    async def get_export_status(  # type: ignore[override]
        self, job_id: str, **kwargs: Any
    ) -> ExportProjectState:
        return await super().get_export_status(project_name=self._project_name, job_id=job_id, **kwargs)

    @distributed_trace
    async def get_project(  # type: ignore[override]
        self, project_name: str = _Unset, **kwargs: Any
    ) -> ProjectMetadata:
        return await super().get_project(project_name=self._project_name, **kwargs)

    @distributed_trace
    async def get_project_deletion_status(  # type: ignore[override]
        self, job_id: str, **kwargs: Any
    ) -> ProjectDeletionState:
        return await super().get_project_deletion_status(project_name=self._project_name, job_id=job_id, **kwargs)

    @distributed_trace
    async def get_swap_deployments_status(  # type: ignore[override]
        self, job_id: str, **kwargs: Any
    ) -> SwapDeploymentsState:
        return await super().get_swap_deployments_status(project_name=self._project_name, job_id=job_id, **kwargs)

    @distributed_trace
    async def get_training_status(  # type: ignore[override]
        self, job_id: str, **kwargs: Any
    ) -> TrainingState:
        return await super().get_training_status(project_name=self._project_name, job_id=job_id, **kwargs)

    @distributed_trace
    async def get_unassign_deployment_resources_status(  # type: ignore[override]
        self, job_id: str, **kwargs: Any
    ) -> DeploymentResourcesState:
        return await super().get_unassign_deployment_resources_status(
            project_name=self._project_name, job_id=job_id, **kwargs
        )

    @distributed_trace
    async def list_deployment_resources(  # type: ignore[override]
        self, *, skip: Optional[int] = _Unset, top: Optional[int] = _Unset, **kwargs: Any
    ) -> AsyncItemPaged[AssignedDeploymentResource]:
        return super().list_deployment_resources(project_name=self._project_name, skip=skip, top=top, **kwargs)

    @distributed_trace
    async def list_deployments(  # type: ignore[override]
        self, *, skip: Optional[int] = _Unset, top: Optional[int] = _Unset, **kwargs: Any
    ) -> AsyncItemPaged[ProjectDeployment]:
        return super().list_deployments(project_name=self._project_name, skip=skip, top=top, **kwargs)

    @distributed_trace
    async def list_exported_models(  # type: ignore[override]
        self, *, skip: Optional[int] = _Unset, top: Optional[int] = _Unset, **kwargs: Any
    ) -> AsyncItemPaged[ExportedTrainedModel]:
        return super().list_exported_models(project_name=self._project_name, skip=skip, top=top, **kwargs)

    @distributed_trace
    async def list_trained_models(  # type: ignore[override]
        self, *, skip: Optional[int] = _Unset, top: Optional[int] = _Unset, **kwargs: Any
    ) -> AsyncItemPaged[ProjectTrainedModel]:
        return super().list_trained_models(project_name=self._project_name, skip=skip, top=top, **kwargs)

    @distributed_trace
    async def list_training_jobs(  # type: ignore[override]
        self, *, skip: Optional[int] = _Unset, top: Optional[int] = _Unset, **kwargs: Any
    ) -> AsyncItemPaged[TrainingState]:
        return super().list_training_jobs(project_name=self._project_name, skip=skip, top=top, **kwargs)


class DeploymentOperations(DeploymentOperationsGenerated):

    def __init__(self, *args, project_name: str, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._project_name = project_name

    @distributed_trace
    async def begin_delete_deployment(self, deployment_name: str, **kwargs: Any) -> AsyncLROPoller[None]:  # type: ignore[override]
        return await super().begin_delete_deployment(
            project_name=self._project_name, deployment_name=deployment_name, **kwargs
        )

    @distributed_trace
    async def begin_delete_deployment_from_resources(  # type: ignore[override]
        self,
        deployment_name: str,
        body: Union[DeleteDeploymentDetails, JSON, IO[bytes]],
        *,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> AsyncLROPoller[None]:
        return await super().begin_delete_deployment_from_resources(
            project_name=self._project_name,
            deployment_name=deployment_name,
            body=body,
            content_type=content_type,
            **kwargs,
        )

    @distributed_trace
    async def begin_deploy_project(  # type: ignore[override]
        self,
        deployment_name: str,
        body: Union[CreateDeploymentDetails, JSON, IO[bytes]],
        *,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> AsyncLROPoller[None]:
        return await super().begin_deploy_project(
            project_name=self._project_name,
            deployment_name=deployment_name,
            body=body,
            content_type=content_type,
            **kwargs,
        )

    @distributed_trace
    async def get_deployment(  # type: ignore[override]
        self, deployment_name: str, **kwargs: Any
    ) -> ProjectDeployment:
        return await super().get_deployment(project_name=self._project_name, deployment_name=deployment_name, **kwargs)

    @distributed_trace
    async def get_deployment_delete_from_resources_status(  # type: ignore[override]
        self, deployment_name: str, job_id: str, **kwargs: Any
    ) -> DeploymentDeleteFromResourcesState:
        return await super().get_deployment_delete_from_resources_status(
            project_name=self._project_name, deployment_name=deployment_name, job_id=job_id, **kwargs
        )

    @distributed_trace
    async def get_deployment_status(  # type: ignore[override]
        self, deployment_name: str, job_id: str, **kwargs: Any
    ) -> DeploymentState:
        return await super().get_deployment_status(
            project_name=self._project_name, deployment_name=deployment_name, job_id=job_id, **kwargs
        )


class ExportedModelOperations(ExportedModelOperationsGenerated):

    def __init__(self, *args, project_name: str, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._project_name = project_name

    @distributed_trace
    async def begin_create_or_update_exported_model(  # type: ignore[override]
        self,
        exported_model_name: str,
        body: Union[ExportedModelDetails, JSON, IO[bytes]],
        *,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> AsyncLROPoller[None]:
        return await super().begin_create_or_update_exported_model(
            project_name=self._project_name,
            exported_model_name=exported_model_name,
            body=body,
            content_type=content_type,
            **kwargs,
        )

    @distributed_trace
    async def begin_delete_exported_model(  # type: ignore[override]
        self, exported_model_name: str, **kwargs: Any
    ) -> AsyncLROPoller[None]:
        return await super().begin_delete_exported_model(
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
    async def get_exported_model_job_status(  # type: ignore[override]
        self, exported_model_name: str, job_id: str, **kwargs: Any
    ) -> ExportedModelState:
        return await super().get_exported_model_job_status(
            project_name=self._project_name,
            exported_model_name=exported_model_name,
            job_id=job_id,
            **kwargs,
        )

    @distributed_trace
    async def get_exported_model_manifest(  # type: ignore[override]
        self, exported_model_name: str, **kwargs: Any
    ) -> ExportedModelManifest:
        return await super().get_exported_model_manifest(
            project_name=self._project_name,
            exported_model_name=exported_model_name,
            **kwargs,
        )


class TrainedModelOperations(TrainedModelOperationsGenerated):

    def __init__(self, *args, project_name: str, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._project_name = project_name

    @distributed_trace
    async def begin_evaluate_model(  # type: ignore[override]
        self,
        trained_model_label: str,
        body: Union[EvaluationDetails, dict, IO[bytes]],
        *,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> AsyncLROPoller[EvaluationJobResult]:
        return await super().begin_evaluate_model(
            project_name=self._project_name,
            trained_model_label=trained_model_label,
            body=body,
            content_type=content_type,
            **kwargs,
        )

    @distributed_trace
    async def begin_load_snapshot(self, trained_model_label: str, **kwargs: Any) -> AsyncLROPoller[None]:  # type: ignore[override]
        return await super().begin_load_snapshot(
            project_name=self._project_name,
            trained_model_label=trained_model_label,
            **kwargs,
        )

    @distributed_trace
    async def delete_trained_model(self, trained_model_label: str, **kwargs: Any) -> None:  # type: ignore[override]
        return await super().delete_trained_model(
            project_name=self._project_name,
            trained_model_label=trained_model_label,
            **kwargs,
        )

    @distributed_trace
    async def get_evaluation_status(  # type: ignore[override]
        self, trained_model_label: str, job_id: str, **kwargs: Any
    ) -> EvaluationState:
        return await super().get_evaluation_status(
            project_name=self._project_name,
            trained_model_label=trained_model_label,
            job_id=job_id,
            **kwargs,
        )

    @distributed_trace
    async def get_load_snapshot_status(  # type: ignore[override]
        self, trained_model_label: str, job_id: str, **kwargs: Any
    ) -> LoadSnapshotState:
        return await super().get_load_snapshot_status(
            project_name=self._project_name,
            trained_model_label=trained_model_label,
            job_id=job_id,
            **kwargs,
        )

    @distributed_trace
    async def get_model_evaluation_results(  # type: ignore[override]
        self,
        trained_model_label: str,
        *,
        skip: Optional[int] = None,
        string_index_type: Union[str, StringIndexType],
        top: Optional[int] = None,
        **kwargs: Any
    ) -> AsyncItemPaged[DocumentEvalResult]:
        return super().get_model_evaluation_results(
            project_name=self._project_name,
            trained_model_label=trained_model_label,
            skip=skip,
            string_index_type=string_index_type,
            top=top,
            **kwargs,
        )

    @distributed_trace
    async def get_model_evaluation_summary(  # type: ignore[override]
        self, trained_model_label: str, **kwargs: Any
    ) -> EvalSummary:
        return await super().get_model_evaluation_summary(
            project_name=self._project_name,
            trained_model_label=trained_model_label,
            **kwargs,
        )

    @distributed_trace
    async def get_trained_model(  # type: ignore[override]
        self, trained_model_label: str, **kwargs: Any
    ) -> ProjectTrainedModel:
        return await super().get_trained_model(
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
