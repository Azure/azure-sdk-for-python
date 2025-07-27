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
from ._conversation_project_patch import ConversationAuthoringProject
from ._conversation_deployment_patch import ConversationAuthoringDeployment
from ._conversation_exportedModel_patch import ConversationAuthoringExportedModel
from ._conversation_trainedModel_patch import ConversationAuthoringTrainedModel

class ConversationAuthoringClient(AuthoringClientGenerated):
    def get_project(self, project_name: str) -> ConversationAuthoringProject:
        return ConversationAuthoringProject(self.conversation_authoring_project, project_name)

    def get_deployment(self, project_name: str, deployment_name: str) -> ConversationAuthoringDeployment:
        return ConversationAuthoringDeployment(self.conversation_authoring_deployment, project_name, deployment_name)

    def get_exported_model_client(self, project_name: str, exported_model_name: str) -> ConversationAuthoringExportedModel:
        return ConversationAuthoringExportedModel(self.conversation_authoring_exported_model, project_name, exported_model_name)

    def get_trained_model(self, project_name: str, trained_model_label: str) -> ConversationAuthoringTrainedModel:
        return ConversationAuthoringTrainedModel(
            self.conversation_authoring_trained_model,
            project_name,
            trained_model_label
        )

def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """

__all__ = ["ConversationAuthoringClient"]