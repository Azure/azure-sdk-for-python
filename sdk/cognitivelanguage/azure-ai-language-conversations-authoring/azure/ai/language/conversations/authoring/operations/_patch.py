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
    ProjectOperationsOperations as ProjectOperationsGenerated,
    DeploymentOperationsOperations as DeploymentOperationsGenerated,
    ExportedModelOperations as ExportedModelOperationsGenerated,
    TrainedModelOperations as TrainedModelOperationsGenerated
)

from ..models import (
    ConversationAuthoringAssignDeploymentResourcesDetails,
    ConversationAuthoringTrainingJobResult,
    ConversationAuthoringCopyProjectDetails,
    ConversationAuthoringTrainingJobDetails,
    ConversationAuthoringAssignDeploymentResourcesDetails,
    ConversationAuthoringUnassignDeploymentResourcesDetails,
    ConversationAuthoringSwapDeploymentsDetails,
    ConversationAuthoringCopyProjectDetails,
    ConversationAuthoringDeploymentResourcesState,
    ConversationAuthoringCopyProjectState,
    ConversationAuthoringExportProjectState,
    ConversationAuthoringProjectMetadata,
    ConversationAuthoringProjectDeletionState,
    ConversationAuthoringSwapDeploymentsState,
    ConversationAuthoringTrainingState,
    ConversationAuthoringDeploymentResourcesState,
    ConversationAuthoringAssignedDeploymentResource,
    ConversationAuthoringProjectDeployment,
    ConversationAuthoringExportedTrainedModel,
    ConversationAuthoringProjectTrainedModel,
    ConversationAuthoringDeleteDeploymentDetails,
    ConversationAuthoringCreateDeploymentDetails,
    ConversationAuthoringDeploymentDeleteFromResourcesState,
    ConversationAuthoringDeploymentState,
    ConversationAuthoringExportedModelDetails,
    ConversationAuthoringExportedTrainedModel,
    ConversationAuthoringExportedModelState,
    ConversationAuthoringEvaluationDetails,
    ConversationAuthoringEvaluationJobResult,
    ConversationAuthoringEvaluationState,
    ConversationAuthoringLoadSnapshotState,
    ConversationAuthoringProjectTrainedModel,
    ConversationAuthoringEvalSummary,
    AnalyzeConversationAuthoringUtteranceEvaluationResult,
    StringIndexType
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
        body: Union[ConversationAuthoringAssignDeploymentResourcesDetails, JSON, IO[bytes]],
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
    ) -> LROPoller[ConversationAuthoringTrainingJobResult]:
        """Cancel a training job without requiring project_name explicitly."""
        return super().begin_cancel_training_job(project_name=self._project_name, job_id=job_id, **kwargs)

    @distributed_trace
    def begin_copy_project(  # type: ignore[override]
        self,
        body: Union[ConversationAuthoringCopyProjectDetails, JSON, IO[bytes]],
        *,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> LROPoller[None]:
        """Copy a project without requiring project_name explicitly."""
        return super().begin_copy_project(
            project_name=self._project_name, body=body, content_type=content_type, **kwargs
        )

    @distributed_trace
    def begin_train(  # type: ignore[override]
        self,
        body: Union[ConversationAuthoringTrainingJobDetails, JSON, IO[bytes]],
        *,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> LROPoller[ConversationAuthoringTrainingJobResult]:
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
            **kwargs
        )

    @distributed_trace
    def begin_swap_deployments(  # type: ignore[override]
        self,
        body: Union[ConversationAuthoringSwapDeploymentsDetails, JSON, IO[bytes]] = _Unset,
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
        body: Union[ConversationAuthoringUnassignDeploymentResourcesDetails, JSON, IO[bytes]] = _Unset,
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
    ) -> ConversationAuthoringCopyProjectDetails:
        return super().copy_project_authorization(
            project_name=self._project_name,
            body=body,
            allow_overwrite=allow_overwrite,
            content_type=content_type,
            project_kind=project_kind,
            storage_input_container_name=storage_input_container_name,
            **kwargs
        )

    @distributed_trace
    def get_assign_deployment_resources_status(  # type: ignore[override]
        self, job_id: str, **kwargs: Any
    ) -> ConversationAuthoringDeploymentResourcesState:
        return super().get_assign_deployment_resources_status(project_name=self._project_name, job_id=job_id, **kwargs)

    @distributed_trace
    def get_copy_project_status(  # type: ignore[override]
        self, job_id: str, **kwargs: Any
    ) -> ConversationAuthoringCopyProjectState:
        return super().get_copy_project_status(project_name=self._project_name, job_id=job_id, **kwargs)

    @distributed_trace
    def get_export_status(  # type: ignore[override]
        self, job_id: str, **kwargs: Any
    ) -> ConversationAuthoringExportProjectState:
        return super().get_export_status(project_name=self._project_name, job_id=job_id, **kwargs)

    @distributed_trace
    def get_project(  # type: ignore[override]
        self,
        project_name: str = _Unset,
        **kwargs: Any
    ) -> ConversationAuthoringProjectMetadata:
        return super().get_project(
            project_name=self._project_name,
            **kwargs
        )

    @distributed_trace
    def get_project_deletion_status(  # type: ignore[override]
        self,
        job_id: str,
        **kwargs: Any
    ) -> ConversationAuthoringProjectDeletionState:
        return super().get_project_deletion_status(
            project_name=self._project_name,
            job_id=job_id,
            **kwargs
        )

    @distributed_trace
    def get_swap_deployments_status(  # type: ignore[override]
        self,
        job_id: str,
        **kwargs: Any
    ) -> ConversationAuthoringSwapDeploymentsState:
        return super().get_swap_deployments_status(
            project_name=self._project_name,
            job_id=job_id,
            **kwargs
        )

    @distributed_trace
    def get_training_status(  # type: ignore[override]
        self,
        job_id: str,
        **kwargs: Any
    ) -> ConversationAuthoringTrainingState:
        return super().get_training_status(
            project_name=self._project_name,
            job_id=job_id,
            **kwargs
        )

    @distributed_trace
    def get_unassign_deployment_resources_status(  # type: ignore[override]
        self,
        job_id: str,
        **kwargs: Any
    ) -> ConversationAuthoringDeploymentResourcesState:
        return super().get_unassign_deployment_resources_status(
            project_name=self._project_name,
            job_id=job_id,
            **kwargs
        )

    @distributed_trace
    def list_deployment_resources(  # type: ignore[override]
        self,
        *,
        skip: Optional[int] = _Unset,
        top: Optional[int] = _Unset,
        **kwargs: Any
    ) -> ItemPaged[ConversationAuthoringAssignedDeploymentResource]:
        return super().list_deployment_resources(
            project_name=self._project_name,
            skip=skip,
            top=top,
            **kwargs
        )

    @distributed_trace
    def list_deployments(  # type: ignore[override]
        self,
        *,
        skip: Optional[int] = _Unset,
        top: Optional[int] = _Unset,
        **kwargs: Any
    ) -> ItemPaged[ConversationAuthoringProjectDeployment]:
        return super().list_deployments(
            project_name=self._project_name,
            skip=skip,
            top=top,
            **kwargs
        )

    @distributed_trace
    def list_exported_models(  # type: ignore[override]
        self,
        *,
        skip: Optional[int] = _Unset,
        top: Optional[int] = _Unset,
        **kwargs: Any
    ) -> ItemPaged[ConversationAuthoringExportedTrainedModel]:
        return super().list_exported_models(
            project_name=self._project_name,
            skip=skip,
            top=top,
            **kwargs
        )

    @distributed_trace
    def list_trained_models(  # type: ignore[override]
        self,
        *,
        skip: Optional[int] = _Unset,
        top: Optional[int] = _Unset,
        **kwargs: Any
    ) -> ItemPaged[ConversationAuthoringProjectTrainedModel]:
        return super().list_trained_models(
            project_name=self._project_name,
            skip=skip,
            top=top,
            **kwargs
        )

    @distributed_trace
    def list_training_jobs(  # type: ignore[override]
        self,
        *,
        skip: Optional[int] = _Unset,
        top: Optional[int] = _Unset,
        **kwargs: Any
    ) -> ItemPaged[ConversationAuthoringTrainingState]:
        return super().list_training_jobs(
            project_name=self._project_name,
            skip=skip,
            top=top,
            **kwargs
        )
    
class DeploymentOperations(DeploymentOperationsGenerated):
    
    def __init__(self, *args, project_name: str, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._project_name = project_name

    @distributed_trace
    def begin_delete_deployment( # type: ignore[override]
        self,
        deployment_name: str,
        **kwargs: Any
    ) -> LROPoller[None]:
        return super().begin_delete_deployment(
            project_name=self._project_name,
            deployment_name=deployment_name,
            **kwargs
        )

    @distributed_trace
    def begin_delete_deployment_from_resources( # type: ignore[override]
        self,
        deployment_name: str,
        body: Union[ConversationAuthoringDeleteDeploymentDetails, JSON, IO[bytes]],
        *,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> LROPoller[None]:
        return super().begin_delete_deployment_from_resources(
            project_name=self._project_name,
            deployment_name=deployment_name,
            body=body,
            content_type=content_type,
            **kwargs
        )

    @distributed_trace
    def begin_deploy_project( # type: ignore[override]
        self,
        deployment_name: str,
        body: Union[ConversationAuthoringCreateDeploymentDetails, JSON, IO[bytes]],
        *,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> LROPoller[None]:
        return super().begin_deploy_project(
            project_name=self._project_name,
            deployment_name=deployment_name,
            body=body,
            content_type=content_type,
            **kwargs
        )

    @distributed_trace
    def get_deployment( # type: ignore[override]
        self,
        deployment_name: str,
        **kwargs: Any
    ) -> ConversationAuthoringProjectDeployment:
        return super().get_deployment(
            project_name=self._project_name,
            deployment_name=deployment_name,
            **kwargs
        )

    @distributed_trace
    def get_deployment_delete_from_resources_status( # type: ignore[override]
        self,
        deployment_name: str,
        job_id: str,
        **kwargs: Any
    ) -> ConversationAuthoringDeploymentDeleteFromResourcesState:
        return super().get_deployment_delete_from_resources_status(
            project_name=self._project_name,
            deployment_name=deployment_name,
            job_id=job_id,
            **kwargs
        )

    @distributed_trace
    def get_deployment_status( # type: ignore[override]
        self,
        deployment_name: str,
        job_id: str,
        **kwargs: Any
    ) -> ConversationAuthoringDeploymentState:
        return super().get_deployment_status(
            project_name=self._project_name,
            deployment_name=deployment_name,
            job_id=job_id,
            **kwargs
        )
    
class ExportedModelOperations(ExportedModelOperationsGenerated):

    def __init__(self, *args, project_name: str, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._project_name = project_name

    @distributed_trace
    def begin_create_or_update_exported_model(  # type: ignore[override]
        self,
        exported_model_name: str,
        body: Union[ConversationAuthoringExportedModelDetails, JSON, IO[bytes]],
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
        self,
        exported_model_name: str,
        **kwargs: Any
    ) -> LROPoller[None]:
        return super().begin_delete_exported_model(
            project_name=self._project_name,
            exported_model_name=exported_model_name,
            **kwargs,
        )

    @distributed_trace
    def get_exported_model(  # type: ignore[override]
        self,
        exported_model_name: str,
        **kwargs: Any
    ) -> ConversationAuthoringExportedTrainedModel:
        return super().get_exported_model(
            project_name=self._project_name,
            exported_model_name=exported_model_name,
            **kwargs,
        )

    @distributed_trace
    def get_exported_model_job_status(  # type: ignore[override]
        self,
        exported_model_name: str,
        job_id: str,
        **kwargs: Any
    ) -> ConversationAuthoringExportedModelState:
        return super().get_exported_model_job_status(
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
        body: Union[ConversationAuthoringEvaluationDetails, dict, IO[bytes]],
        *,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> LROPoller[ConversationAuthoringEvaluationJobResult]:
        return super().begin_evaluate_model(
            project_name=self._project_name,
            trained_model_label=trained_model_label,
            body=body,
            content_type=content_type,
            **kwargs,
        )

    @distributed_trace
    def begin_load_snapshot(  # type: ignore[override]
        self,
        trained_model_label: str,
        **kwargs: Any
    ) -> LROPoller[None]:
        return super().begin_load_snapshot(
            project_name=self._project_name,
            trained_model_label=trained_model_label,
            **kwargs,
        )

    @distributed_trace
    def delete_trained_model(  # type: ignore[override]
        self,
        trained_model_label: str,
        **kwargs: Any
    ) -> None:
        return super().delete_trained_model(
            project_name=self._project_name,
            trained_model_label=trained_model_label,
            **kwargs,
        )

    @distributed_trace
    def get_evaluation_status(  # type: ignore[override]
        self,
        trained_model_label: str,
        job_id: str,
        **kwargs: Any
    ) -> ConversationAuthoringEvaluationState:
        return super().get_evaluation_status(
            project_name=self._project_name,
            trained_model_label=trained_model_label,
            job_id=job_id,
            **kwargs,
        )

    @distributed_trace
    def get_load_snapshot_status(  # type: ignore[override]
        self,
        trained_model_label: str,
        job_id: str,
        **kwargs: Any
    ) -> ConversationAuthoringLoadSnapshotState:
        return super().get_load_snapshot_status(
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
    ) -> ItemPaged[AnalyzeConversationAuthoringUtteranceEvaluationResult]:
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
        self,
        trained_model_label: str,
        **kwargs: Any
    ) -> ConversationAuthoringEvalSummary:
        return super().get_model_evaluation_summary(
            project_name=self._project_name,
            trained_model_label=trained_model_label,
            **kwargs,
        )

    @distributed_trace
    def get_trained_model(  # type: ignore[override]
        self,
        trained_model_label: str,
        **kwargs: Any
    ) -> ConversationAuthoringProjectTrainedModel:
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
