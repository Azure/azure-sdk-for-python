# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from ._configuration import TextAuthoringProjectClientConfiguration
from ._utils.serialization import Deserializer, Serializer
from typing import Any, TYPE_CHECKING, Union, Optional
from ._client import TextAuthoringClient as AuthoringClientGenerated
from ._client import TextAuthoringProjectClient as AuthoringProjectClientGenerated
from .operations._patch import ProjectOperations, DeploymentOperations, ExportedModelOperations, TrainedModelOperations
from azure.core import PipelineClient
from azure.core.credentials import AzureKeyCredential
from azure.core.pipeline import policies

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential


class TextAuthoringProjectClient(AuthoringProjectClientGenerated):
    """Custom TextAuthoringProjectClient that bypasses generated __init__
    and ensures project_name is mandatory.
    """

    #: Deployment operations group
    deployment: DeploymentOperations
    #: Exported model operations group
    exported_model: ExportedModelOperations
    #: Project operations group
    project: ProjectOperations
    #: Trained model operations group
    trained_model: TrainedModelOperations

    def __init__(
        self, endpoint: str, credential: Union[AzureKeyCredential, "TokenCredential"], *, 
        api_version: Optional[str] = None,
        project_name: str, 
        **kwargs: Any
    ) -> None:
        """
        Initialize a TextAuthoringProjectClient.

        :param str endpoint: Supported Cognitive Services endpoint, e.g.
            ``https://<resource>.cognitiveservices.azure.com``.
        :param credential: Credential used to authenticate requests to the service.
        :type credential: ~azure.core.credentials.AzureKeyCredential or ~azure.core.credentials.TokenCredential
        :keyword str api_version: The API version to use for this operation.
            Default value is ``2025-05-15-preview``.
            Note that overriding this default value may result in unsupported behavior.
        :keyword str project_name: The name of the project to scope operations. **Required**.
        """
        self._project_name = project_name
        _endpoint = f"{endpoint}/language"

        if api_version is not None:
            kwargs["api_version"] = api_version

        # Build configuration
        self._config = TextAuthoringProjectClientConfiguration(
            endpoint=endpoint, credential=credential, project_name=project_name, **kwargs
        )

        # Build policies
        _policies = kwargs.pop("policies", None)
        if _policies is None:
            _policies = [
                policies.RequestIdPolicy(**kwargs),
                self._config.headers_policy,
                self._config.user_agent_policy,
                self._config.proxy_policy,
                policies.ContentDecodePolicy(**kwargs),
                self._config.redirect_policy,
                self._config.retry_policy,
                self._config.authentication_policy,
                self._config.custom_hook_policy,
                self._config.logging_policy,
                policies.DistributedTracingPolicy(**kwargs),
                policies.SensitiveHeaderCleanupPolicy(**kwargs) if self._config.redirect_policy else None,
                self._config.http_logging_policy,
            ]

        # Build pipeline client
        self._client: PipelineClient = PipelineClient(base_url=_endpoint, policies=_policies, **kwargs)

        # Setup serializers
        self._serialize = Serializer()
        self._deserialize = Deserializer()
        self._serialize.client_side_validation = False

        # Assign patched operation groups with project_name
        self.deployment = DeploymentOperations(
            self._client, self._config, self._serialize, self._deserialize, project_name=project_name
        )
        self.project = ProjectOperations(
            self._client, self._config, self._serialize, self._deserialize, project_name=project_name
        )
        self.exported_model = ExportedModelOperations(
            self._client, self._config, self._serialize, self._deserialize, project_name=project_name
        )
        self.trained_model = TrainedModelOperations(
            self._client, self._config, self._serialize, self._deserialize, project_name=project_name
        )


class TextAuthoringClient(AuthoringClientGenerated):

    def __init__(
        self,
        endpoint: str,
        credential: Union[AzureKeyCredential, "TokenCredential"],
        *,
        api_version: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """
        Create a TextAuthoringClient.

        :param str endpoint: Supported Cognitive Services endpoint, e.g.
            ``https://<resource-name>.api.cognitiveservices.azure.com``.
        :param credential: Key or token credential.
        :type credential: ~azure.core.credentials.AzureKeyCredential or
            ~azure.core.credentials.TokenCredential
        :keyword str api_version: The API version to use for this operation.
            Default value is ``2025-05-15-preview``.
            Note that overriding this default value may result in unsupported behavior.
        """
        if api_version is not None:
            kwargs["api_version"] = api_version
        super().__init__(endpoint=endpoint, credential=credential, **kwargs)

    def get_project_client(self, project_name: str) -> TextAuthoringProjectClient:
        return TextAuthoringProjectClient(
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


__all__ = ["TextAuthoringProjectClient", "TextAuthoringClient"]
