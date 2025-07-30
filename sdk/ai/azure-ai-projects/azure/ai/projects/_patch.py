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
from urllib.parse import urlparse
from typing import List, Any, Optional, TYPE_CHECKING
from typing_extensions import Self
from azure.core.tracing.decorator import distributed_trace
from azure.core.credentials import TokenCredential
from azure.ai.agents import AgentsClient
from ._client import AIProjectClient as AIProjectClientGenerated
from .operations import TelemetryOperations
from .models._enums import ConnectionType
from .models._models import ApiKeyCredentials, EntraIDCredentials

if TYPE_CHECKING:
    # pylint: disable=unused-import,ungrouped-imports
    from openai import OpenAI

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


def _get_aoai_inference_url(input_url: str) -> str:
    """
    Converts an input URL in the format:
    https://<host-name>/<some-path>
    to:
    https://<host-name>

    :param input_url: The input endpoint URL used to construct AIProjectClient.
    :type input_url: str

    :return: The endpoint URL required to construct an AzureOpenAI client from the `openai` package.
    :rtype: str
    """
    parsed = urlparse(input_url)
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError("Invalid endpoint URL format. Must be an https URL with a host.")
    new_url = f"https://{parsed.netloc}"
    return new_url


class AIProjectClient(AIProjectClientGenerated):  # pylint: disable=too-many-instance-attributes
    """AIProjectClient.

    :ivar agents: The AgentsClient associated with this AIProjectClient.
    :vartype agents: azure.ai.agents.AgentsClient
    :ivar connections: ConnectionsOperations operations
    :vartype connections: azure.ai.projects.operations.ConnectionsOperations
    :ivar telemetry: TelemetryOperations operations
    :vartype telemetry: azure.ai.projects.operations.TelemetryOperations
    :ivar datasets: DatasetsOperations operations
    :vartype datasets: azure.ai.projects.operations.DatasetsOperations
    :ivar indexes: IndexesOperations operations
    :vartype indexes: azure.ai.projects.operations.IndexesOperations
    :ivar deployments: DeploymentsOperations operations
    :vartype deployments: azure.ai.projects.operations.DeploymentsOperations
    :param endpoint: Project endpoint. In the form
     "https://your-ai-services-account-name.services.ai.azure.com/api/projects/_project"
     if your Foundry Hub has only one Project, or to use the default Project in your Hub. Or in the
     form "https://your-ai-services-account-name.services.ai.azure.com/api/projects/your-project-name"
     if you want to explicitly specify the Foundry Project name. Required.
    :type endpoint: str
    :param credential: Credential used to authenticate requests to the service. Required.
    :type credential: ~azure.core.credentials.TokenCredential
    :keyword api_version: The API version to use for this operation. Default value is
     "v1". Note that overriding this default value may result in unsupported
     behavior.
    :paramtype api_version: str
    """

    def __init__(self, endpoint: str, credential: TokenCredential, **kwargs: Any) -> None:

        kwargs.setdefault("logging_enable", _console_logging_enabled)

        self._kwargs = kwargs.copy()
        self._patched_user_agent = _patch_user_agent(self._kwargs.pop("user_agent", None))

        super().__init__(endpoint=endpoint, credential=credential, **kwargs)

        self.telemetry = TelemetryOperations(self)  # type: ignore
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

    @distributed_trace
    def get_openai_client(
        self, *, api_version: Optional[str] = None, connection_name: Optional[str] = None, **kwargs
    ) -> "OpenAI":  # type: ignore[name-defined]
        """Get an authenticated AzureOpenAI client (from the `openai` package) to use with
        AI models deployed to your AI Foundry Project or connected Azure OpenAI services.

        .. note:: The package `openai` must be installed prior to calling this method.

        :keyword api_version: The Azure OpenAI api-version to use when creating the client. Optional.
         See "Data plane - Inference" row in the table at
         https://learn.microsoft.com/azure/ai-foundry/openai/reference#api-specs. If this keyword
         is not specified, you must set the environment variable `OPENAI_API_VERSION` instead.
        :paramtype api_version: Optional[str]
        :keyword connection_name: Optional. If specified, the connection named here must be of type Azure OpenAI.
         The returned OpenAI client will use the inference URL specified by the connected Azure OpenAI
         service, and can be used with AI models deployed to that service. If not specified, the returned
         OpenAI client will use the inference URL of the parent AI Services resource, and can be used
         with AI models deployed directly to your AI Foundry project.
        :paramtype connection_name: Optional[str]

        :return: An authenticated AzureOpenAI client
        :rtype: ~openai.AzureOpenAI

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
            from openai import AzureOpenAI
        except ModuleNotFoundError as e:
            raise ModuleNotFoundError(
                "OpenAI SDK is not installed. Please install it using 'pip install openai'"
            ) from e

        if connection_name:
            connection = self.connections._get_with_credentials(  # pylint: disable=protected-access
                name=connection_name, **kwargs
            )
            if connection.type != ConnectionType.AZURE_OPEN_AI:
                raise ValueError(f"Connection `{connection_name}` is not of type Azure OpenAI.")

            azure_endpoint = connection.target[:-1] if connection.target.endswith("/") else connection.target

            if isinstance(connection.credentials, ApiKeyCredentials):

                logger.debug(
                    "[get_openai_client] Creating OpenAI client using API key authentication, on connection `%s`, endpoint `%s`, api_version `%s`",  # pylint: disable=line-too-long
                    connection_name,
                    azure_endpoint,
                    api_version,
                )
                api_key = connection.credentials.api_key
                client = AzureOpenAI(api_key=api_key, azure_endpoint=azure_endpoint, api_version=api_version)

            elif isinstance(connection.credentials, EntraIDCredentials):

                logger.debug(
                    "[get_openai_client] Creating OpenAI using Entra ID authentication, on connection `%s`, endpoint `%s`, api_version `%s`",  # pylint: disable=line-too-long
                    connection_name,
                    azure_endpoint,
                    api_version,
                )

                try:
                    from azure.identity import get_bearer_token_provider
                except ModuleNotFoundError as e:
                    raise ModuleNotFoundError(
                        "azure.identity package not installed. Please install it using 'pip install azure.identity'"
                    ) from e

                client = AzureOpenAI(
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
            from azure.identity import get_bearer_token_provider
        except ModuleNotFoundError as e:
            raise ModuleNotFoundError(
                "azure.identity package not installed. Please install it using 'pip install azure.identity'"
            ) from e

        azure_endpoint = _get_aoai_inference_url(self._config.endpoint)  # pylint: disable=protected-access

        logger.debug(  # pylint: disable=specify-parameter-names-in-call
            "[get_openai_client] Creating OpenAI client using Entra ID authentication, on parent AI Services resource, endpoint `%s`, api_version `%s`",  # pylint: disable=line-too-long
            azure_endpoint,
            api_version,
        )

        client = AzureOpenAI(
            # See https://learn.microsoft.com/python/api/azure-identity/azure.identity?view=azure-python#azure-identity-get-bearer-token-provider # pylint: disable=line-too-long
            azure_ad_token_provider=get_bearer_token_provider(
                self._config.credential,  # pylint: disable=protected-access
                "https://cognitiveservices.azure.com/.default",  # pylint: disable=protected-access
            ),
            azure_endpoint=azure_endpoint,
            api_version=api_version,
        )

        return client

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
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
