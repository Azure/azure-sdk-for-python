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
from azure.core.polling import LROPoller
from azure.core.tracing.decorator import distributed_trace

from ._operations import (
    ProjectOperations as ProjectOperationsGenerated,
    DeploymentOperations as DeploymentOperationsGenerated,
    ExportedModelOperations as ExportedModelOperationsGenerated,
    TrainedModelOperations as TrainedModelOperationsGenerated,
)

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
    UtteranceEvaluationResult,
)
from azure.core.paging import ItemPaged
from collections.abc import MutableMapping

JSON = MutableMapping[str, Any]
_Unset: Any = object()


class ProjectOperations(ProjectOperationsGenerated):
    """Patched ProjectOperationsOperations that auto-injects project_name."""

    def __init__(self, *args, project_name: str, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self._project_name = project_name

    @distributed_trace
    def begin_assign_deployment_resources(  # type: ignore[override]
        self,
        body: Union[AssignDeploymentResourcesDetails, JSON, IO[bytes]],
        *,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> LROPoller[None]:
        """Assign deployment resources without requiring project_name explicitly."""
        return super().begin_assign_deployment_resources(
            project_name=self._project_name, body=body, content_type=content_type, **kwargs
        )

    @distributed_trace
    def begin_cancel_training_job(  # type: ignore[override]
        self, job_id: str, **kwargs: Any
    ) -> LROPoller[TrainingJobResult]:
        """Cancel a training job without requiring project_name explicitly."""
        return super().begin_cancel_training_job(project_name=self._project_name, job_id=job_id, **kwargs)

    @distributed_trace
    def begin_copy_project(  # type: ignore[override]
        self, body: Union[CopyProjectDetails, JSON, IO[bytes]], *, content_type: str = "application/json", **kwargs: Any
    ) -> LROPoller[None]:
        """Copy a project without requiring project_name explicitly."""
        return super().begin_copy_project(
            project_name=self._project_name, body=body, content_type=content_type, **kwargs
        )

    @distributed_trace
    def begin_train(  # type: ignore[override]
        self, body: Union[TrainingJobDetails, JSON, IO[bytes]], *, content_type: str = "application/json", **kwargs: Any
    ) -> LROPoller[TrainingJobResult]:
        """Begin training without requiring project_name explicitly."""
        return super().begin_train(project_name=self._project_name, body=body, content_type=content_type, **kwargs)

    @distributed_trace
    def begin_export(  # type: ignore[override]
        self,
        *,
        asset_kind: Optional[str] = _Unset,
        exported_project_format: Optional[Union[str, Any]] = _Unset,
        string_index_type: Union[str, Any] = _Unset,
        trained_model_label: Optional[str] = _Unset,
        **kwargs: Any
    ) -> LROPoller[None]:
        return super().begin_export(
            project_name=self._project_name,
            asset_kind=asset_kind,
            exported_project_format=exported_project_format,
            string_index_type=string_index_type,
            trained_model_label=trained_model_label,
            **kwargs,
        )

    @distributed_trace
    def begin_swap_deployments(  # type: ignore[override]
        self,
        body: Union[SwapDeploymentsDetails, JSON, IO[bytes]] = _Unset,
        *,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> LROPoller[None]:
        return super().begin_swap_deployments(
            project_name=self._project_name, body=body, content_type=content_type, **kwargs
        )

    @distributed_trace
    def begin_unassign_deployment_resources(  # type: ignore[override]
        self,
        body: Union[UnassignDeploymentResourcesDetails, JSON, IO[bytes]] = _Unset,
        *,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> LROPoller[None]:
        return super().begin_unassign_deployment_resources(
            project_name=self._project_name, body=body, content_type=content_type, **kwargs
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
    def get_project(self, project_name: str = _Unset, **kwargs: Any) -> ProjectMetadata:  # type: ignore[override]
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
    def begin_delete_deployment(self, deployment_name: str, **kwargs: Any) -> LROPoller[None]:  # type: ignore[override]
        return super().begin_delete_deployment(
            project_name=self._project_name, deployment_name=deployment_name, **kwargs
        )

    @distributed_trace
    def begin_delete_deployment_from_resources(  # type: ignore[override]
        self,
        deployment_name: str,
        body: Union[DeleteDeploymentDetails, JSON, IO[bytes]],
        *,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> LROPoller[None]:
        return super().begin_delete_deployment_from_resources(
            project_name=self._project_name,
            deployment_name=deployment_name,
            body=body,
            content_type=content_type,
            **kwargs,
        )

    @distributed_trace
    def begin_deploy_project(  # type: ignore[override]
        self,
        deployment_name: str,
        body: Union[CreateDeploymentDetails, JSON, IO[bytes]],
        *,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> LROPoller[None]:
        return super().begin_deploy_project(
            project_name=self._project_name,
            deployment_name=deployment_name,
            body=body,
            content_type=content_type,
            **kwargs,
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
    def begin_create_or_update_exported_model(  # type: ignore[override]
        self,
        exported_model_name: str,
        body: Union[ExportedModelDetails, JSON, IO[bytes]],
        *,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> LROPoller[None]:
        return super().begin_create_or_update_exported_model(
            project_name=self._project_name,
            exported_model_name=exported_model_name,
            body=body,
            content_type=content_type,
            **kwargs,
        )

    @distributed_trace
    def begin_delete_exported_model(  # type: ignore[override]
        self, exported_model_name: str, **kwargs: Any
    ) -> LROPoller[None]:
        return super().begin_delete_exported_model(
            project_name=self._project_name,
            exported_model_name=exported_model_name,
            **kwargs,
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
    def begin_load_snapshot(self, trained_model_label: str, **kwargs: Any) -> LROPoller[None]:  # type: ignore[override]
        return super().begin_load_snapshot(
            project_name=self._project_name,
            trained_model_label=trained_model_label,
            **kwargs,
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
