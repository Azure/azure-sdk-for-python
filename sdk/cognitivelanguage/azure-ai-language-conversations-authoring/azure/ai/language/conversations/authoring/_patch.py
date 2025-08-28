# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from collections.abc import MutableMapping # pylint:disable=import-error
from typing import TYPE_CHECKING, Any, Callable, Dict, Optional, TypeVar, Union, cast

from azure.core import PipelineClient
from azure.core.credentials import AzureKeyCredential
from azure.core.pipeline import PipelineResponse, policies
from azure.core.polling import LROPoller, NoPolling, PollingMethod
from azure.core.rest import HttpRequest, HttpResponse
from azure.core.tracing.decorator import distributed_trace

from ._client import (
    ConversationAuthoringClient as AuthoringClientGenerated,
    ConversationAuthoringProjectClient as AuthoringProjectClientGenerated,
)
from ._configuration import ConversationAuthoringProjectClientConfiguration
from ._utils.model_base import _deserialize
from ._utils.serialization import Deserializer, Serializer
from .models import JobsPollingMethod, ProjectDeletionState
from .operations._patch import (
    DeploymentOperations,
    ExportedModelOperations,
    ProjectOperations,
    TrainedModelOperations,
)

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential

JSON = MutableMapping[str, Any]
T = TypeVar("T")
ClsType = Optional[
    Callable[[PipelineResponse[HttpRequest, HttpResponse], T, Dict[str, Any]], Any]
]

class ConversationAuthoringProjectClient(AuthoringProjectClientGenerated): # pylint: disable=client-accepts-api-version-keyword
    """Custom ConversationAuthoringProjectClient that bypasses generated __init__
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

    def __init__( # pylint: disable=super-init-not-called
        self,
        endpoint: str,
        credential: Union[AzureKeyCredential, "TokenCredential"],
        *,
        project_name: str,
        **kwargs: Any,
    ) -> None:
        """Initialize a ConversationAuthoringProjectClient.

        :param str endpoint: Supported Cognitive Services endpoint, e.g.
            "https://<resource>.cognitiveservices.azure.com".
        :param credential: Credential used to authenticate requests to the service.
        :type credential: ~azure.core.credentials.AzureKeyCredential or
            ~azure.core.credentials_async.AsyncTokenCredential
        :keyword str project_name: The name of the project to scope operations. Required.
        :keyword Any kwargs: Additional keyword arguments.
        :rtype: None
        """
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
            Default value is ``2025-05-15-preview``.
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

    @distributed_trace
    def begin_delete_project(self, project_name: str, **kwargs: Any) -> LROPoller[None]: # pylint: disable=delete-operation-wrong-return-type
        """Deletes a project.

        :param project_name: The name of the project to delete. Required.
        :type project_name: str
        :return: An instance of LROPoller that returns None
        :rtype: ~azure.core.polling.LROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return super()._begin_delete_project(
            project_name=project_name, **kwargs
        )


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """


__all__ = ["ConversationAuthoringProjectClient", "ConversationAuthoringClient"]
