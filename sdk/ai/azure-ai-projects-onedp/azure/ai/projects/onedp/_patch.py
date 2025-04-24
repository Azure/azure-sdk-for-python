# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List, Any, Optional, Self
from azure.core.credentials import TokenCredential
from azure.ai.agents import AgentsClient
from ._client import AIProjectClient as AIProjectClientGenerated
from .operations import TelemetryOperations, InferenceOperations, ClientsOperations
from ._patch_prompts import PromptTemplate
from ._patch_telemetry import enable_telemetry


class AIProjectClient(AIProjectClientGenerated):  # pylint: disable=too-many-instance-attributes
    """AIProjectClient.

    :ivar agents: The AgentsClient associated with this AIProjectClient.
    :vartype agents: azure.ai.agents.AgentsClient
    :ivar connections: ConnectionsOperations operations
    :vartype connections: azure.ai.projects.onedp.operations.ConnectionsOperations
    :ivar clients: ClientsOperations operations
    :vartype clients: azure.ai.projects.onedp.operations.ClientsOperations
    :ivar inference: InferenceOperations operations
    :vartype inference: azure.ai.projects.onedp.operations.InferenceOperations
    :ivar telemetry: TelemetryOperations operations
    :vartype telemetry: azure.ai.projects.onedp.operations.TelemetryOperations
    :ivar evaluations: EvaluationsOperations operations
    :vartype evaluations: azure.ai.projects.onedp.operations.EvaluationsOperations
    :ivar datasets: DatasetsOperations operations
    :vartype datasets: azure.ai.projects.onedp.operations.DatasetsOperations
    :ivar indexes: IndexesOperations operations
    :vartype indexes: azure.ai.projects.onedp.operations.IndexesOperations
    :ivar deployments: DeploymentsOperations operations
    :vartype deployments: azure.ai.projects.onedp.operations.DeploymentsOperations
    :ivar red_teams: RedTeamsOperations operations
    :vartype red_teams: azure.ai.projects.onedp.operations.RedTeamsOperations
    :param endpoint: Project endpoint in the form of:
     https://<aiservices-id>.services.ai.azure.com/api/projects/<project-name>. Required.
    :type endpoint: str
    :param credential: Credential used to authenticate requests to the service. Is either a key
     credential type or a token credential type. Required.
    :type credential: ~azure.core.credentials.AzureKeyCredential or
     ~azure.core.credentials.TokenCredential
    :keyword api_version: The API version to use for this operation. Default value is
     "2025-05-15-preview". Note that overriding this default value may result in unsupported
     behavior.
    :paramtype api_version: str
    """

    def __init__(self, endpoint: str, credential: TokenCredential, **kwargs: Any) -> None:
        agents_kwargs = kwargs.copy()
        self._user_agent: Optional[str] = kwargs.get("user_agent", None)
        super().__init__(endpoint=endpoint, credential=credential, **kwargs)
        self.telemetry = TelemetryOperations(self)
        self.inference = InferenceOperations(self)
        self.clients = ClientsOperations(self)
        # TODO: set user_agent here:
        self.agents = AgentsClient(endpoint=endpoint, credential=credential, **agents_kwargs)

    def close(self) -> None:
        self.agents.close()
        super().close()

    def __enter__(self) -> Self:
        super().__enter__()
        self.agents.__enter__()
        return self

    def __exit__(self, *exc_details: Any) -> None:
        self.agents.__exit__(*exc_details)
        super().__exit__(*exc_details)

__all__: List[str] = [
    "AIProjectClient",
    "PromptTemplate",
    "enable_telemetry",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
