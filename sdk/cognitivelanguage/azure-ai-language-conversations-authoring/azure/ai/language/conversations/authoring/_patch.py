# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Any, TYPE_CHECKING, Union
from ._client import ConversationAuthoringClient as AuthoringClientGenerated
from ._client import ConversationAuthoringProjectClient as AuthoringProjectClientGenerated
from .operations._patch import ProjectOperations, DeploymentOperations, ExportedModelOperations, TrainedModelOperations
from azure.core import PipelineClient
from azure.core.credentials import AzureKeyCredential
from azure.core.pipeline import policies

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential

from ._configuration import ConversationAuthoringClientConfiguration, ConversationAuthoringProjectClientConfiguration
from ._utils.serialization import Deserializer, Serializer


class ConversationAuthoringProjectClient(AuthoringProjectClientGenerated):
    """Custom ConversationAuthoringProjectClient that bypasses generated __init__
    and ensures project_name is mandatory.
    """

    #: Deployment operations group
    deployment_operations: DeploymentOperations
    #: Exported model operations group
    exported_model: ExportedModelOperations
    #: Project operations group
    project_operations: ProjectOperations
    #: Trained model operations group
    trained_model: TrainedModelOperations

    def __init__(
        self, endpoint: str, credential: Union[AzureKeyCredential, "TokenCredential"], project_name: str, **kwargs: Any
    ) -> None:
        self._project_name = project_name
        _endpoint = f"{endpoint}/language"

        # Build configuration
        self._config = ConversationAuthoringProjectClientConfiguration(
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
        self.deployment_operations = DeploymentOperations(
            self._client, self._config, self._serialize, self._deserialize, project_name=project_name
        )
        self.project_operations = ProjectOperations(
            self._client, self._config, self._serialize, self._deserialize, project_name=project_name
        )
        self.exported_model = ExportedModelOperations(
            self._client, self._config, self._serialize, self._deserialize, project_name=project_name
        )
        self.trained_model = TrainedModelOperations(
            self._client, self._config, self._serialize, self._deserialize, project_name=project_name
        )


class ConversationAuthoringClient(AuthoringClientGenerated):
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
