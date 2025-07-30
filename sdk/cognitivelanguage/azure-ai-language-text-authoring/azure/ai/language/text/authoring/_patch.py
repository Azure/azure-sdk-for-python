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
from ._text_project_patch import TextAuthoringProjectClient
from ._text_deployment_patch import TextAuthoringDeploymentClient
from ._text_exportedModel_patch import TextAuthoringExportedModelClient
from ._text_trainedModel_patch import TextAuthoringTrainedModelClient

class TextAuthoringClient(AuthoringClientGenerated):
    def get_project_client(self, project_name: str) -> TextAuthoringProjectClient:
        return TextAuthoringProjectClient(self.text_authoring_project, project_name)

    def get_deployment_client(self, project_name: str, deployment_name: str) -> TextAuthoringDeploymentClient:
        return TextAuthoringDeploymentClient(self.text_authoring_deployment, project_name, deployment_name)

    def get_exported_model_client(self, project_name: str, exported_model_name: str) -> TextAuthoringExportedModelClient:
        return TextAuthoringExportedModelClient(self.text_authoring_exported_model, project_name, exported_model_name)

    def get_trained_model_client(self, project_name: str, trained_model_label: str) -> TextAuthoringTrainedModelClient:
        return TextAuthoringTrainedModelClient(
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

__all__ = ["TextAuthoringClient"]