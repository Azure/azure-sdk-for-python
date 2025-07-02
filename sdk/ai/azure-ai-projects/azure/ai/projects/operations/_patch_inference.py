# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import logging
from typing import Optional, TYPE_CHECKING
from urllib.parse import urlparse
from azure.core.tracing.decorator import distributed_trace
from ..models._models import ApiKeyCredentials, EntraIDCredentials
from ..models._enums import ConnectionType

if TYPE_CHECKING:
    # pylint: disable=unused-import,ungrouped-imports
    from openai import AzureOpenAI

logger = logging.getLogger(__name__)


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


class InferenceOperations:
    """
    .. warning::
        **DO NOT** instantiate this class directly.

        Instead, you should access the following operations through
        :class:`~azure.ai.projects.AIProjectClient`'s
        :attr:`inference` attribute.
    """

    def __init__(self, outer_instance: "azure.ai.projects.AIProjectClient") -> None:  # type: ignore[name-defined]
        self._outer_instance = outer_instance

    @distributed_trace
    def get_azure_openai_client(
        self, *, api_version: Optional[str] = None, connection_name: Optional[str] = None, **kwargs
    ) -> "AzureOpenAI":  # type: ignore[name-defined]
        """Get an authenticated AzureOpenAI client (from the `openai` package) to use with
        AI models deployed to your AI Foundry Project or connected Azure OpenAI services.

        .. note:: The package `openai` must be installed prior to calling this method.

        :keyword api_version: The Azure OpenAI api-version to use when creating the client. Optional.
         See "Data plane - Inference" row in the table at
         https://learn.microsoft.com/azure/ai-services/openai/reference#api-specs. If this keyword
         is not specified, you must set the environment variable `OPENAI_API_VERSION` instead.
        :paramtype api_version: Optional[str]
        :keyword connection_name: Optional. If specified, the connection named here must be of type Azure OpenAI.
         The returned AzureOpenAI client will use the inference URL specified by the connected Azure OpenAI
         service, and can be used with AI models deployed to that service. If not specified, the returned
         AzureOpenAI client will use the inference URL of the parent AI Services resource, and can be used
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
            connection = self._outer_instance.connections._get_with_credentials(  # pylint: disable=protected-access
                name=connection_name, **kwargs
            )
            if connection.type != ConnectionType.AZURE_OPEN_AI:
                raise ValueError(f"Connection `{connection_name}` is not of type Azure OpenAI.")

            azure_endpoint = connection.target[:-1] if connection.target.endswith("/") else connection.target

            if isinstance(connection.credentials, ApiKeyCredentials):

                logger.debug(
                    "[InferenceOperations.get_azure_openai_client] Creating AzureOpenAI client using API key authentication, on connection `%s`, endpoint `%s`, api_version `%s`",
                    connection_name,
                    azure_endpoint,
                    api_version,
                )
                api_key = connection.credentials.api_key
                client = AzureOpenAI(api_key=api_key, azure_endpoint=azure_endpoint, api_version=api_version)

            elif isinstance(connection.credentials, EntraIDCredentials):

                logger.debug(
                    "[InferenceOperations.get_azure_openai_client] Creating AzureOpenAI using Entra ID authentication, on connection `%s`, endpoint `%s`, api_version `%s`",
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
                        self._outer_instance._config.credential,  # pylint: disable=protected-access
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

        azure_endpoint = _get_aoai_inference_url(
            self._outer_instance._config.endpoint  # pylint: disable=protected-access
        )

        logger.debug(
            "[InferenceOperations.get_azure_openai_client] Creating AzureOpenAI client using Entra ID authentication, on parent AI Services resource, endpoint `%s`, api_version `%s`",
            azure_endpoint,
            api_version,
        )

        client = AzureOpenAI(
            # See https://learn.microsoft.com/python/api/azure-identity/azure.identity?view=azure-python#azure-identity-get-bearer-token-provider # pylint: disable=line-too-long
            azure_ad_token_provider=get_bearer_token_provider(
                self._outer_instance._config.credential,  # pylint: disable=protected-access
                "https://cognitiveservices.azure.com/.default",  # pylint: disable=protected-access
            ),
            azure_endpoint=azure_endpoint,
            api_version=api_version,
        )

        return client
