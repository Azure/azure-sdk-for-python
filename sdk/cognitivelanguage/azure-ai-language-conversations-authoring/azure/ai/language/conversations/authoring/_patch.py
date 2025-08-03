# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List, cast
from ._client import ConversationAuthoringClient as AuthoringClientGenerated
from ._client import ConversationAuthoringProjectClient as AuthoringProjectClientGenerated
from .operations._patch import (
    ProjectOperations,
    DeploymentOperations,
    ExportedModelOperations
)


class ConversationAuthoringProjectClient(AuthoringProjectClientGenerated):

    #: Deployment operations group
    deployment_operations: DeploymentOperations
    #: Exported model operations group
    # exported_model: ExportedModelOperations
    #: Project operations group
    project_operations: ProjectOperations
    #: Trained model operations group
    # trained_model: TrainedModelOperations

    def __init__(self, parent_client, project_name: str, **kwargs):
        super().__init__(
            endpoint=parent_client._config.endpoint,
            credential=parent_client._config.credential,
            project_name=project_name,
            **kwargs
        )
        self._project_name = project_name

        self.project_operations = ProjectOperations(
            self._client, self._config, self._serialize, self._deserialize, project_name=project_name
        )
        self.deployment_operations = DeploymentOperations(
            self._client, self._config, self._serialize, self._deserialize, project_name=project_name
        )
        self.exported_model = ExportedModelOperations(
            self._client, self._config, self._serialize, self._deserialize, project_name=project_name
        )
        # self.trained_model = TrainedModelOperations(
        #     self._client, self._config, self._serialize, self._deserialize, project_name=project_name
        # )


class ConversationAuthoringClient(AuthoringClientGenerated):
    def get_project_client(self, project_name: str) -> ConversationAuthoringProjectClient:
        return ConversationAuthoringProjectClient(self, project_name)


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """


__all__ = ["ConversationAuthoringProjectClient", "ConversationAuthoringClient"]
