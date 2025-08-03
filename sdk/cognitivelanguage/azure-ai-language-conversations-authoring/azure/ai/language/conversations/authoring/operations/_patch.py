# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Any, Union, IO
from azure.core.polling import LROPoller
from azure.core.tracing.decorator import distributed_trace

from ._operations import ProjectOperationsOperations as ProjectOperationsGenerated
from ..models import (
    ConversationAuthoringAssignDeploymentResourcesDetails,
    ConversationAuthoringTrainingJobResult,
    ConversationAuthoringCopyProjectDetails,
    ConversationAuthoringTrainingJobDetails
)
from collections.abc import MutableMapping
JSON = MutableMapping[str, Any]

class ProjectOperations(ProjectOperationsGenerated):
    """Patched ProjectOperationsOperations that auto-injects project_name."""

    def __init__(self, *args, project_name: str, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self._project_name = project_name

    @distributed_trace
    def begin_assign_deployment_resources( # type: ignore[override]
        self,
        body: Union[ConversationAuthoringAssignDeploymentResourcesDetails, JSON, IO[bytes]],
        *,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> LROPoller[None]:
        """Assign deployment resources without requiring project_name explicitly."""
        return super().begin_assign_deployment_resources(
            project_name=self._project_name,
            body=body,
            content_type=content_type,
            **kwargs
        )

    @distributed_trace
    def begin_cancel_training_job( # type: ignore[override]
        self,
        job_id: str,
        **kwargs: Any
    ) -> LROPoller[ConversationAuthoringTrainingJobResult]:
        """Cancel a training job without requiring project_name explicitly."""
        return super().begin_cancel_training_job(
            project_name=self._project_name,
            job_id=job_id,
            **kwargs
        )

    @distributed_trace
    def begin_copy_project( # type: ignore[override]
        self,
        body: Union[ConversationAuthoringCopyProjectDetails, JSON, IO[bytes]],
        *,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> LROPoller[None]:
        """Copy a project without requiring project_name explicitly."""
        return super().begin_copy_project(
            project_name=self._project_name,
            body=body,
            content_type=content_type,
            **kwargs
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
        return super().begin_train(
            project_name=self._project_name,
            body=body,
            content_type=content_type,
            **kwargs
        )

def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """

__all__ = ["ProjectOperations"]