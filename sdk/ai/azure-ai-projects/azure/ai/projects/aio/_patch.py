# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import os
import logging
from typing import List, Any, Optional, TYPE_CHECKING
from typing_extensions import Self
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.credentials_async import AsyncTokenCredential
from azure.ai.agents.aio import AgentsClient
from ._client import AIProjectClient as AIProjectClientGenerated
from .._patch import _patch_user_agent
from .operations import TelemetryOperations
from ..models._enums import ConnectionType
from ..models._models import ApiKeyCredentials, EntraIDCredentials
from .._patch import _get_aoai_inference_url

if TYPE_CHECKING:
    # pylint: disable=unused-import,ungrouped-imports
    from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

_console_logging_enabled: bool = os.environ.get("ENABLE_AZURE_AI_PROJECTS_CONSOLE_LOGGING", "False").lower() in (
    "true",
    "1",
    "yes",
)
if _console_logging_enabled:
    import sys

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
    :ivar telemetry: TelemetryOperations operations
    :vartype telemetry: azure.ai.projects.aio.operations.TelemetryOperations
    :ivar datasets: DatasetsOperations operations
    :vartype datasets: azure.ai.projects.aio.operations.DatasetsOperations
    :ivar indexes: IndexesOperations operations
    :vartype indexes: azure.ai.projects.aio.operations.IndexesOperations
    :ivar deployments: DeploymentsOperations operations
    :vartype deployments: azure.ai.projects.aio.operations.DeploymentsOperations
    :param endpoint: Project endpoint. In the form
     "https://your-ai-services-account-name.services.ai.azure.com/api/projects/_project"
     if your Foundry Hub has only one Project, or to use the default Project in your Hub. Or in the
     form "https://your-ai-services-account-name.services.ai.azure.com/api/projects/your-project-name"
     if you want to explicitly specify the Foundry Project name. Required.
    :type endpoint: str
    :param credential: Credential used to authenticate requests to the service. Required.
    :type credential: ~azure.core.credentials_async.AsyncTokenCredential
    :keyword api_version: The API version to use for this operation. Default value is
     "v1". Note that overriding this default value may result in unsupported
     behavior.
    :paramtype api_version: str
    """

    def __init__(self, endpoint: str, credential: AsyncTokenCredential, **kwargs: Any) -> None:

        kwargs.setdefault("logging_enable", _console_logging_enabled)

        self._kwargs = kwargs.copy()
        self._patched_user_agent = _patch_user_agent(self._kwargs.pop("user_agent", None))

        super().__init__(endpoint=endpoint, credential=credential, **kwargs)

        self.telemetry = TelemetryOperations(self)  # type: ignore
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

    @distributed_trace_async
    async def get_openai_client(
        self, *, api_version: Optional[str] = None, connection_name: Optional[str] = None, **kwargs
    ) -> "AsyncOpenAI":  # type: ignore[name-defined]
        """Get an authenticated AsyncAzureOpenAI client (from the `openai` package) to use with
        AI models deployed to your AI Foundry Project or connected Azure OpenAI services.

        .. note:: The package `openai` must be installed prior to calling this method.

        :keyword api_version: The Azure OpenAI api-version to use when creating the client. Optional.
         See "Data plane - Inference" row in the table at
         https://learn.microsoft.com/azure/ai-foundry/openai/reference#api-specs. If this keyword
         is not specified, you must set the environment variable `OPENAI_API_VERSION` instead.
        :paramtype api_version: Optional[str]
        :keyword connection_name: Optional. If specified, the connection named here must be of type Azure OpenAI.
         The returned AzureOpenAI client will use the inference URL specified by the connected Azure OpenAI
         service, and can be used with AI models deployed to that service. If not specified, the returned
         AzureOpenAI client will use the inference URL of the parent AI Services resource, and can be used
         with AI models deployed directly to your AI Foundry project.
        :paramtype connection_name: Optional[str]

        :return: An authenticated AsyncAzureOpenAI client
        :rtype: ~openai.AsyncAzureOpenAI

        :raises ~azure.core.exceptions.ResourceNotFoundError: if an Azure OpenAI connection
         does not exist.
        :raises ~azure.core.exceptions.ModuleNotFoundError: if the `openai` package
         is not installed.
        :raises ValueError: if the connection name is an empty string.
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        if connection_name is not None and not connection_name:
            raise ValueError("Connection name cannot be empty")

        try:
            from openai import AsyncAzureOpenAI
        except ModuleNotFoundError as e:
            raise ModuleNotFoundError(
                "OpenAI SDK is not installed. Please install it using 'pip install openai'"
            ) from e

        if connection_name:
            connection = await self.connections._get_with_credentials(  # pylint: disable=protected-access
                name=connection_name, **kwargs
            )
            if connection.type != ConnectionType.AZURE_OPEN_AI:
                raise ValueError(f"Connection `{connection_name}` is not of type Azure OpenAI.")

            azure_endpoint = connection.target[:-1] if connection.target.endswith("/") else connection.target

            if isinstance(connection.credentials, ApiKeyCredentials):

                logger.debug(
                    "[get_openai_client] Creating AsyncOpenAI client using API key authentication, on connection `%s`, endpoint `%s`, api_version `%s`",  # pylint: disable=line-too-long
                    connection_name,
                    azure_endpoint,
                    api_version,
                )
                api_key = connection.credentials.api_key
                client = AsyncAzureOpenAI(api_key=api_key, azure_endpoint=azure_endpoint, api_version=api_version)

            elif isinstance(connection.credentials, EntraIDCredentials):

                logger.debug(
                    "[get_openai_client] Creating AsyncOpenAI using Entra ID authentication, on connection `%s`, endpoint `%s`, api_version `%s`",  # pylint: disable=line-too-long
                    connection_name,
                    azure_endpoint,
                    api_version,
                )

                try:
                    from azure.identity.aio import get_bearer_token_provider
                except ModuleNotFoundError as e:
                    raise ModuleNotFoundError(
                        "azure.identity package not installed. Please install it using 'pip install azure.identity'"
                    ) from e

                client = AsyncAzureOpenAI(
                    # See https://learn.microsoft.com/python/api/azure-identity/azure.identity?view=azure-python#azure-identity-get-bearer-token-provider # pylint: disable=line-too-long
                    azure_ad_token_provider=get_bearer_token_provider(
                        self._config.credential,  # pylint: disable=protected-access
                        "https://cognitiveservices.azure.com/.default",  # pylint: disable=protected-access
                    ),
                    azure_endpoint=azure_endpoint,
                    api_version=api_version,
                )

            else:
                raise ValueError("Unsupported authentication type {connection.type}")

            return client

        try:
            from azure.identity.aio import get_bearer_token_provider
        except ModuleNotFoundError as e:
            raise ModuleNotFoundError(
                "azure.identity package not installed. Please install it using 'pip install azure.identity'"
            ) from e

        azure_endpoint = _get_aoai_inference_url(self._config.endpoint)  # pylint: disable=protected-access

        logger.debug(  # pylint: disable=specify-parameter-names-in-call
            "[get_openai_client] Creating AzureOpenAI client using Entra ID authentication, on parent AI Services resource, endpoint `%s`, api_version `%s`",  # pylint: disable=line-too-long
            azure_endpoint,
            api_version,
        )

        client = AsyncAzureOpenAI(
            # See https://learn.microsoft.com/python/api/azure-identity/azure.identity?view=azure-python#azure-identity-get-bearer-token-provider # pylint: disable=line-too-long
            azure_ad_token_provider=get_bearer_token_provider(
                self._config.credential,  # pylint: disable=protected-access
                "https://cognitiveservices.azure.com/.default",  # pylint: disable=protected-access
            ),
            azure_endpoint=azure_endpoint,
            api_version=api_version,
        )

        return client

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
