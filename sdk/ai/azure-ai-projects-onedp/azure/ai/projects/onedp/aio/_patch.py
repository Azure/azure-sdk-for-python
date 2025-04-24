# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List, Optional, Any
from azure.core.credentials_async import AsyncTokenCredential
from ._client import AIProjectClient as AIProjectClientGenerated
from .operations import InferenceOperations, ClientsOperations, TelemetryOperations


class AIProjectClient(AIProjectClientGenerated):  # pylint: disable=too-many-instance-attributes
    """AIProjectClient.

    :ivar connections: ConnectionsOperations operations
    :vartype connections: azure.ai.projects.onedp.aio.operations.ConnectionsOperations
    :ivar clients: ClientsOperations operations
    :vartype clients: azure.ai.projects.onedp.aio.operations.ClientsOperations
    :ivar inference: InferenceOperations operations
    :vartype inference: azure.ai.projects.onedp.aio.operations.InferenceOperations
    :ivar telemetry: TelemetryOperations operations
    :vartype telemetry: azure.ai.projects.onedp.aio.operations.TelemetryOperations
    :ivar evaluations: EvaluationsOperations operations
    :vartype evaluations: azure.ai.projects.onedp.aio.operations.EvaluationsOperations
    :ivar datasets: DatasetsOperations operations
    :vartype datasets: azure.ai.projects.onedp.aio.operations.DatasetsOperations
    :ivar indexes: IndexesOperations operations
    :vartype indexes: azure.ai.projects.onedp.aio.operations.IndexesOperations
    :ivar deployments: DeploymentsOperations operations
    :vartype deployments: azure.ai.projects.onedp.aio.operations.DeploymentsOperations
    :ivar red_teams: RedTeamsOperations operations
    :vartype red_teams: azure.ai.projects.onedp.aio.operations.RedTeamsOperations
    :param endpoint: Project endpoint in the form of:
     https://<aiservices-id>.services.ai.azure.com/api/projects/<project-name>. Required.
    :type endpoint: str
    :param credential: Credential used to authenticate requests to the service. Is either a key
     credential type or a token credential type. Required.
    :type credential: ~azure.core.credentials.AzureKeyCredential or
     ~azure.core.credentials_async.AsyncTokenCredential
    :keyword api_version: The API version to use for this operation. Default value is
     "2025-05-15-preview". Note that overriding this default value may result in unsupported
     behavior.
    :paramtype api_version: str
    """

    def __init__(
        self, endpoint: str, credential: AsyncTokenCredential, **kwargs: Any
    ) -> None:
        self._user_agent: Optional[str] = kwargs.get("user_agent", None)
        super().__init__(endpoint=endpoint, credential=credential, **kwargs)
        self.telemetry = TelemetryOperations(self)
        self.inference = InferenceOperations(self)
        self.clients = ClientsOperations(self)


__all__: List[str] = ["AIProjectClient"]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
