# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.
Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from ._models import (
    AssignDeploymentResourcesDetails,
    UnassignDeploymentResourcesDetails,
    SwapDeploymentsDetails,
    CopyProjectState,
    ExportProjectState,
    SwapDeploymentsState,
    DeleteDeploymentDetails,
    CreateDeploymentDetails,
    DeploymentDeleteFromResourcesState,
    DeploymentState,
    ExportedModelDetails,
    ExportedModelState,
    LoadSnapshotState,
    DeploymentResourcesState,
    ProjectDeletionState,
    ExportedProject,
    ImportProjectState,
    CopyProjectDetails,
    TrainingJobDetails,
    EvaluationJobResult,
    EvaluationState,
    ExportedCustomSingleLabelClassificationProjectAsset,
    ExportedCustomSingleLabelClassificationDocument,
    ExportedDocumentClass,
    ExportedClass,
    ResourceMetadata,
)


def patch_sdk():
    """Do not remove from this file.
    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """


__all__ = [
    "AssignDeploymentResourcesDetails",
    "UnassignDeploymentResourcesDetails",
    "SwapDeploymentsDetails",
    "DeploymentResourcesState",
    "CopyProjectState",
    "ExportProjectState",
    "SwapDeploymentsState",
    "DeploymentResourcesState",
    "DeleteDeploymentDetails",
    "CreateDeploymentDetails",
    "DeploymentDeleteFromResourcesState",
    "DeploymentState",
    "ExportedModelDetails",
    "ExportedModelState",
    "LoadSnapshotState",
    "DeploymentResourcesState",
    "ProjectDeletionState",
    "ExportedProject",
    "ImportProjectState",
    "CopyProjectDetails",
    "TrainingJobDetails",
    "CopyProjectDetails",
    "EvaluationJobResult",
    "EvaluationState",
    "ExportedCustomSingleLabelClassificationProjectAsset",
    "ExportedCustomSingleLabelClassificationDocument",
    "ExportedDocumentClass",
    "ExportedClass",
    "ResourceMetadata",
]
