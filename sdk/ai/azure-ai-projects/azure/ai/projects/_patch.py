# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import os
from typing import List, Any, Optional
from typing_extensions import Self
from azure.core.credentials import TokenCredential
from azure.ai.agents import AgentsClient
from ._client import AIProjectClient as AIProjectClientGenerated
from .operations import TelemetryOperations, InferenceOperations
from ._patch_prompts import PromptTemplate
from ._patch_telemetry import enable_telemetry

_console_logging_enabled: bool = os.environ.get("ENABLE_AZURE_AI_PROJECTS_CONSOLE_LOGGING", "False").lower() in (
    "true",
    "1",
    "yes",
)
if _console_logging_enabled:
    import sys
    import logging

    azure_logger = logging.getLogger("azure")
    azure_logger.setLevel(logging.DEBUG)
    azure_logger.addHandler(logging.StreamHandler(stream=sys.stdout))
    identity_logger = logging.getLogger("azure.identity")
    identity_logger.setLevel(logging.ERROR)


def _patch_user_agent(user_agent: Optional[str]) -> str:
    # All authenticated external clients exposed by this client will have this application id
    # set on their user-agent. For more info on user-agent HTTP header, see:
    # https://azure.github.io/azure-sdk/general_azurecore.html#telemetry-policy
    USER_AGENT_APP_ID = "AIProjectClient"

    if user_agent:
        # If the calling application has set "user_agent" when constructing the AIProjectClient,
        # take that value and prepend it to USER_AGENT_APP_ID.
        patched_user_agent = f"{user_agent}-{USER_AGENT_APP_ID}"
    else:
        patched_user_agent = USER_AGENT_APP_ID

    return patched_user_agent


class AIProjectClient(AIProjectClientGenerated):  # pylint: disable=too-many-instance-attributes
    """AIProjectClient.

    :ivar agents: The AgentsClient associated with this AIProjectClient.
    :vartype agents: azure.ai.agents.AgentsClient
    :ivar connections: ConnectionsOperations operations
    :vartype connections: azure.ai.projects.operations.ConnectionsOperations
    :ivar inference: InferenceOperations operations
    :vartype inference: azure.ai.projects.operations.InferenceOperations
    :ivar telemetry: TelemetryOperations operations
    :vartype telemetry: azure.ai.projects.operations.TelemetryOperations
    :ivar evaluations: EvaluationsOperations operations
    :vartype evaluations: azure.ai.projects.operations.EvaluationsOperations
    :ivar datasets: DatasetsOperations operations
    :vartype datasets: azure.ai.projects.operations.DatasetsOperations
    :ivar indexes: IndexesOperations operations
    :vartype indexes: azure.ai.projects.operations.IndexesOperations
    :ivar deployments: DeploymentsOperations operations
    :vartype deployments: azure.ai.projects.operations.DeploymentsOperations
    :ivar red_teams: RedTeamsOperations operations
    :vartype red_teams: azure.ai.projects.operations.RedTeamsOperations
    :param endpoint: Project endpoint. In the form
     "https://<your-ai-services-account-name>.services.ai.azure.com/api/projects/_project"
     if your Foundry Hub has only one Project, or to use the default Project in your Hub. Or in the
     form "https://<your-ai-services-account-name>.services.ai.azure.com/api/projects/<your-project-name>"
     if you want to explicitly specify the Foundry Project name. Required.
    :type endpoint: str
    :param credential: Credential used to authenticate requests to the service. Required.
    :type credential: ~azure.core.credentials.TokenCredential
    :keyword api_version: The API version to use for this operation. Default value is
     "2025-05-15-preview". Note that overriding this default value may result in unsupported
     behavior.
    :paramtype api_version: str
    """

    def __init__(self, endpoint: str, credential: TokenCredential, **kwargs: Any) -> None:

        kwargs.setdefault("logging_enable", _console_logging_enabled)

        self._kwargs = kwargs.copy()
        self._patched_user_agent = _patch_user_agent(self._kwargs.pop("user_agent", None))

        super().__init__(endpoint=endpoint, credential=credential, **kwargs)

        self.telemetry = TelemetryOperations(self)  # type: ignore
        self.inference = InferenceOperations(self)  # type: ignore
        self._agents: Optional[AgentsClient] = None

    @property
    def agents(self) -> AgentsClient:  # type: ignore[name-defined]
        """Get the AgentsClient associated with this AIProjectClient.
        The package azure.ai.agents must be installed to use this property.

        :return: The AgentsClient associated with this AIProjectClient.
        :rtype: azure.ai.agents.AgentsClient
        """
        if self._agents is None:
            self._agents = AgentsClient(
                endpoint=self._config.endpoint,
                credential=self._config.credential,
                user_agent=self._patched_user_agent,
                **self._kwargs,
            )
        return self._agents

    def close(self) -> None:
        if self._agents:
            self.agents.close()
        super().close()

    def __enter__(self) -> Self:
        super().__enter__()
        if self._agents:
            self.agents.__enter__()
        return self

    def __exit__(self, *exc_details: Any) -> None:
        if self._agents:
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
