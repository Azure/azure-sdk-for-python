# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.
Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Any, TYPE_CHECKING, Union, Optional
from azure.core.credentials import AzureKeyCredential
from ._client import ConversationAuthoringClient as AuthoringClientGenerated
from ._client import ConversationAuthoringProjectClient as AuthoringProjectClientGenerated
from .operations import (
    DeploymentOperations,
    ExportedModelOperations,
    ProjectOperations,
    TrainedModelOperations
)

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential


class ConversationAuthoringProjectClient(AuthoringProjectClientGenerated):

    #: Deployment operations group
    deployment: DeploymentOperations
    #: Exported model operations group
    exported_model: ExportedModelOperations
    #: Project operations group
    project: ProjectOperations
    #: Trained model operations group
    trained_model: TrainedModelOperations

    def __init__(  # pylint: disable=super-init-not-called
        self,
        endpoint: str,
        credential: Union[AzureKeyCredential, "TokenCredential"],
        *,
        api_version: Optional[str] = None,
        project_name: str,
        **kwargs: Any,
    ) -> None:
        """
        Initialize a ConversationAuthoringProjectClient.

        :param str endpoint: Supported Cognitive Services endpoint, e.g.
            ``https://<resource>.cognitiveservices.azure.com``.
        :param credential: Credential used to authenticate requests to the service.
        :type credential: ~azure.core.credentials.AzureKeyCredential or ~azure.core.credentials.TokenCredential
        :keyword str api_version: The API version to use for this operation.
            Default value is ``2025-11-15-preview``.
            Note that overriding this default value may result in unsupported behavior.
        :keyword str project_name: The name of the project to scope operations. **Required**.
        """
        if api_version is not None:
            kwargs["api_version"] = api_version
        super().__init__(endpoint=endpoint, credential=credential, project_name=project_name, **kwargs)


class ConversationAuthoringClient(AuthoringClientGenerated):

    def __init__(
        self,
        endpoint: str,
        credential: Union[AzureKeyCredential, "TokenCredential"],
        *,
        api_version: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """
        Create a ConversationAuthoringClient.
        
        :param str endpoint: Supported Cognitive Services endpoint, e.g.
            ``https://<resource-name>.api.cognitiveservices.azure.com``.
        :param credential: Key or token credential.
        :type credential: ~azure.core.credentials.AzureKeyCredential or
            ~azure.core.credentials.TokenCredential
        :keyword str api_version: The API version to use for this operation.
            Default value is ``2025-11-15-preview``.
            Note that overriding this default value may result in unsupported behavior.
        """
        if api_version is not None:
            kwargs["api_version"] = api_version
        super().__init__(endpoint=endpoint, credential=credential, **kwargs)

    def get_project_client(self, project_name: str) -> ConversationAuthoringProjectClient:
        return ConversationAuthoringProjectClient(
            endpoint=self._config.endpoint,
            credential=self._config.credential,
            project_name=project_name,
        )


def patch_sdk():
    """Do not remove from this file.
    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """


__all__ = ["ConversationAuthoringProjectClient", "ConversationAuthoringClient"]
