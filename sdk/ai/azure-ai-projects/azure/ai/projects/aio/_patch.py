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
from azure.core.credentials_async import AsyncTokenCredential
from azure.ai.agents.aio import AgentsClient
from ._client import AIProjectClient as AIProjectClientGenerated
from .._patch import _patch_user_agent
from .operations import InferenceOperations, TelemetryOperations

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


class AIProjectClient(AIProjectClientGenerated):  # pylint: disable=too-many-instance-attributes
    """AIProjectClient.

    :ivar agents: The asynchronous AgentsClient associated with this AIProjectClient.
    :vartype agents: azure.ai.agents.aio.AgentsClient
    :ivar connections: ConnectionsOperations operations
    :vartype connections: azure.ai.projects.aio.operations.ConnectionsOperations
    :ivar inference: InferenceOperations operations
    :vartype inference: azure.ai.projects.aio.operations.InferenceOperations
    :ivar telemetry: TelemetryOperations operations
    :vartype telemetry: azure.ai.projects.aio.operations.TelemetryOperations
    :ivar evaluations: EvaluationsOperations operations
    :vartype evaluations: azure.ai.projects.aio.operations.EvaluationsOperations
    :ivar datasets: DatasetsOperations operations
    :vartype datasets: azure.ai.projects.aio.operations.DatasetsOperations
    :ivar indexes: IndexesOperations operations
    :vartype indexes: azure.ai.projects.aio.operations.IndexesOperations
    :ivar deployments: DeploymentsOperations operations
    :vartype deployments: azure.ai.projects.aio.operations.DeploymentsOperations
    :ivar red_teams: RedTeamsOperations operations
    :vartype red_teams: azure.ai.projects.aio.operations.RedTeamsOperations
    :param endpoint: Project endpoint. In the form
     "https://<your-ai-services-account-name>.services.ai.azure.com/api/projects/_project"
     if your Foundry Hub has only one Project, or to use the default Project in your Hub. Or in the
     form "https://<your-ai-services-account-name>.services.ai.azure.com/api/projects/<your-project-name>"
     if you want to explicitly specify the Foundry Project name. Required.
    :type endpoint: str
    :param credential: Credential used to authenticate requests to the service. Required.
    :type credential: ~azure.core.credentials_async.AsyncTokenCredential
    :keyword api_version: The API version to use for this operation. Default value is
     "2025-05-15-preview". Note that overriding this default value may result in unsupported
     behavior.
    :paramtype api_version: str
    """

    def __init__(self, endpoint: str, credential: AsyncTokenCredential, **kwargs: Any) -> None:

        kwargs.setdefault("logging_enable", _console_logging_enabled)

        self._kwargs = kwargs.copy()
        self._patched_user_agent = _patch_user_agent(self._kwargs.pop("user_agent", None))

        super().__init__(endpoint=endpoint, credential=credential, **kwargs)

        self.telemetry = TelemetryOperations(self)  # type: ignore
        self.inference = InferenceOperations(self)  # type: ignore
        self._agents: Optional[AgentsClient] = None

    @property
    def agents(self) -> AgentsClient:  # type: ignore[name-defined]
        """Get the asynchronous AgentsClient associated with this AIProjectClient.
        The package azure.ai.agents must be installed to use this property.

        :return: The asynchronous AgentsClient associated with this AIProjectClient.
        :rtype: azure.ai.agents.aio.AgentsClient
        """
        if self._agents is None:
            self._agents = AgentsClient(
                endpoint=self._config.endpoint,
                credential=self._config.credential,
                user_agent=self._patched_user_agent,
                **self._kwargs,
            )
        return self._agents

    async def close(self) -> None:
        if self._agents:
            await self.agents.close()
        await super().close()

    async def __aenter__(self) -> Self:
        await super().__aenter__()
        if self._agents:
            await self.agents.__aenter__()
        return self

    async def __aexit__(self, *exc_details: Any) -> None:
        if self._agents:
            await self.agents.__aexit__(*exc_details)
        await super().__aexit__(*exc_details)


__all__: List[str] = ["AIProjectClient"]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
