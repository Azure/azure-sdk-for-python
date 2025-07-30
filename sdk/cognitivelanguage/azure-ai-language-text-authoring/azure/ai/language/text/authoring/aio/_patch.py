# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List
from ._client import AuthoringClient as AuthoringClientGenerated
from ._text_project_patch import TextAuthoringProjectClientAsync
from ._text_deployment_patch import TextAuthoringDeploymentClientAsync
from ._text_exportedModel_patch import TextAuthoringExportedModelClientAsync
from ._text_trainedModel_patch import TextAuthoringTrainedModelClientAsync

class TextAuthoringClientAsync(AuthoringClientGenerated):
    def get_project_client(self, project_name: str) -> TextAuthoringProjectClientAsync:
        return TextAuthoringProjectClientAsync(self.text_authoring_project, project_name)

    def get_deployment_client(self, project_name: str, deployment_name: str) -> TextAuthoringDeploymentClientAsync:
        return TextAuthoringDeploymentClientAsync(self.text_authoring_deployment, project_name, deployment_name)

    def get_exported_model_client(self, project_name: str, exported_model_name: str) -> TextAuthoringExportedModelClientAsync:
        return TextAuthoringExportedModelClientAsync(self.text_authoring_exported_model, project_name, exported_model_name)

    def get_trained_model_client(self, project_name: str, trained_model_label: str) -> TextAuthoringTrainedModelClientAsync:
        return TextAuthoringTrainedModelClientAsync(
            self.text_authoring_trained_model,
            project_name,
            trained_model_label
        )

def patch_sdk():
    """Do not remove from this file.
    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """

__all__ = ["TextAuthoringClientAsync"]