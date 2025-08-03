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

from ._operations import ProjectOperationsOperations as ProjectOperationsGenerated
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
)
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


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """


__all__ = ["ProjectOperations"]
