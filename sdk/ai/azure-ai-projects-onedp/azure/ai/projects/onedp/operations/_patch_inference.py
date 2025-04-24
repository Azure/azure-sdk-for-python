# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import logging
from typing import Optional, Iterable
from urllib.parse import urlparse
from azure.core.exceptions import ResourceNotFoundError
from azure.core.tracing.decorator import distributed_trace
from ..models._models import Connection, ApiKeyCredentials, EntraIDCredentials
from ..models._enums import CredentialType, ConnectionType

logger = logging.getLogger(__name__)


class InferenceOperations:
    """
    .. warning::
        **DO NOT** instantiate this class directly.

        Instead, you should access the following operations through
        :class:`~azure.ai.projects.onedp.AIProjectClient`'s
        :attr:`inference` attribute.
    """

    def __init__(self, outer_instance: "azure.ai.projects.onedp.AIProjectClient") -> None:  # type: ignore[name-defined]

        # All returned inference clients will have this application id set on their user-agent.
        # For more info on user-agent HTTP header, see:
        # https://azure.github.io/azure-sdk/general_azurecore.html#telemetry-policy
        USER_AGENT_APP_ID = "AIProjectClient"

        if hasattr(outer_instance, "_user_agent") and outer_instance._user_agent:
            # If the calling application has set "user_agent" when constructing the AIProjectClient,
            # take that value and prepend it to USER_AGENT_APP_ID.
            self._user_agent = f"{outer_instance._user_agent}-{USER_AGENT_APP_ID}"
        else:
            self._user_agent = USER_AGENT_APP_ID

        self._outer_instance = outer_instance

    @classmethod
    def _get_inference_url(cls, input_url: str) -> str:
        """
        Converts an input URL in the format:
        https://<host-name>/<some-path>
        to:
        https://<host-name>/api/models

        :param input_url: The input endpoint URL used to construct AIProjectClient.
        :type input_url: str

        :return: The endpoint URL required to construct inference clients from the azure-ai-inference package.
        :rtype: str
        """
        parsed = urlparse(input_url)
        if parsed.scheme != "https" or not parsed.netloc:
            raise ValueError("Invalid endpoint URL format. Must be an https URL with a host.")
        new_url = f"https://{parsed.netloc}/api/models"
        return new_url

    @distributed_trace
    def get_chat_completions_client(self, **kwargs) -> "ChatCompletionsClient":  # type: ignore[name-defined]
        """Get an authenticated ChatCompletionsClient (from the package azure-ai-inference) to use with
        AI models deployed to your AI Foundry Project. Keyword arguments are passed to the constructor of
        ChatCompletionsClient.

        At least one AI model that supports chat completions must be deployed.

        .. note:: The package `azure-ai-inference` must be installed prior to calling this method.

        :return: An authenticated chat completions client.
        :rtype: ~azure.ai.inference.ChatCompletionsClient

        :raises ~azure.core.exceptions.ModuleNotFoundError: if the `azure-ai-inference` package
         is not installed.
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        try:
            from azure.ai.inference import ChatCompletionsClient
        except ModuleNotFoundError as e:
            raise ModuleNotFoundError(
                "Azure AI Inference SDK is not installed. Please install it using 'pip install azure-ai-inference'"
            ) from e

        endpoint = self._get_inference_url(self._outer_instance._config.endpoint)  # pylint: disable=protected-access
        # TODO: Remove this before //build?
        # Older Inference SDK versions use ml.azure.com as the scope. Make sure to set the correct value here. This
        # is only relevent of course if EntraID auth is used.
        credential_scopes = ["https://cognitiveservices.azure.com/.default"]

        client = ChatCompletionsClient(
            endpoint=endpoint,
            credential=self._outer_instance._config.credential,  # pylint: disable=protected-access
            credential_scopes=credential_scopes,
            user_agent=kwargs.pop("user_agent", self._user_agent),
            **kwargs,
        )

        return client

    @distributed_trace
    def get_embeddings_client(self, **kwargs) -> "EmbeddingsClient":  # type: ignore[name-defined]
        """Get an authenticated EmbeddingsClient (from the package azure-ai-inference) to use with
        AI models deployed to your AI Foundry Project. Keyword arguments are passed to the constructor of
        ChatCompletionsClient.

        At least one AI model that supports text embeddings must be deployed.

        .. note:: The package `azure-ai-inference` must be installed prior to calling this method.

        :return: An authenticated Embeddings client.
        :rtype: ~azure.ai.inference.EmbeddingsClient

        :raises ~azure.core.exceptions.ModuleNotFoundError: if the `azure-ai-inference` package
         is not installed.
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        try:
            from azure.ai.inference import EmbeddingsClient
        except ModuleNotFoundError as e:
            raise ModuleNotFoundError(
                "Azure AI Inference SDK is not installed. Please install it using 'pip install azure-ai-inference'"
            ) from e

        endpoint = self._get_inference_url(self._outer_instance._config.endpoint)  # pylint: disable=protected-access
        # Older Inference SDK versions use ml.azure.com as the scope. Make sure to set the correct value here. This
        # is only relevent of course if EntraID auth is used.
        credential_scopes = ["https://cognitiveservices.azure.com/.default"]

        client = EmbeddingsClient(
            endpoint=endpoint,
            credential=self._outer_instance._config.credential,  # pylint: disable=protected-access
            credential_scopes=credential_scopes,
            user_agent=kwargs.pop("user_agent", self._user_agent),
            **kwargs,
        )

        return client

    @distributed_trace
    def get_image_embeddings_client(self, **kwargs) -> "ImageEmbeddingsClient":  # type: ignore[name-defined]
        """Get an authenticated ImageEmbeddingsClient (from the package azure-ai-inference) to use with
        AI models deployed to your AI Foundry Project. Keyword arguments are passed to the constructor of
        ChatCompletionsClient.

        At least one AI model that supports image embeddings must be deployed.

        .. note:: The package `azure-ai-inference` must be installed prior to calling this method.

        :return: An authenticated Image Embeddings client.
        :rtype: ~azure.ai.inference.ImageEmbeddingsClient

        :raises ~azure.core.exceptions.ModuleNotFoundError: if the `azure-ai-inference` package
         is not installed.
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        try:
            from azure.ai.inference import ImageEmbeddingsClient
        except ModuleNotFoundError as e:
            raise ModuleNotFoundError(
                "Azure AI Inference SDK is not installed. Please install it using 'pip install azure-ai-inference'"
            ) from e

        endpoint = self._get_inference_url(self._outer_instance._config.endpoint)  # pylint: disable=protected-access
        # Older Inference SDK versions use ml.azure.com as the scope. Make sure to set the correct value here. This
        # is only relevent of course if EntraID auth is used.
        credential_scopes = ["https://cognitiveservices.azure.com/.default"]

        client = ImageEmbeddingsClient(
            endpoint=endpoint,
            credential=self._outer_instance._config.credential,  # pylint: disable=protected-access
            credential_scopes=credential_scopes,
            user_agent=kwargs.pop("user_agent", self._user_agent),
            **kwargs,
        )

        return client

    @distributed_trace
    def get_azure_openai_client(
        self, *, api_version: Optional[str] = None, connection_name: Optional[str] = None, **kwargs
    ) -> "AzureOpenAI":  # type: ignore[name-defined]
        """Get an authenticated AzureOpenAI client (from the `openai` package) for the default
        Azure OpenAI connection (if `connection_name` is not specificed), or from the Azure OpenAI
        resource given by its connection name.

        .. note:: The package `openai` must be installed prior to calling this method.

        :keyword api_version: The Azure OpenAI api-version to use when creating the client. Optional.
         See "Data plane - Inference" row in the table at
         https://learn.microsoft.com/azure/ai-services/openai/reference#api-specs. If this keyword
         is not specified, you must set the environment variable `OPENAI_API_VERSION` instead.
        :paramtype api_version: str
        :keyword connection_name: The name of a connection to an Azure OpenAI resource in your AI Foundry project.
         resource. Optional. If not provided, the default Azure OpenAI connection will be used.
        :type connection_name: str

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

        connection = Connection()
        if connection_name:
            connection = self._outer_instance.connections.get(name=connection_name, **kwargs)
            if connection.type != ConnectionType.AZURE_OPEN_AI:
                raise ValueError(f"Connection `{connection_name}` is not of type Azure OpenAI.")
        else:
            # If connection name was not specified, try to get the default Azure OpenAI connection.
            connections: Iterable[Connection] = self._outer_instance.connections.list(
                connection_type=ConnectionType.AZURE_OPEN_AI, default_connection=True, **kwargs
            )
            try:
                connection = next(iter(connections))
            except StopAsyncIteration as exc:
                raise ResourceNotFoundError("No default Azure OpenAI connection found.") from exc
            connection_name = connection.name

            # TODO: if there isn't a default openai connection, we would have to by convention
            # use https://{resource-name}.openai.azure.com where {resource-name} is the same as the
            # foundry API endpoint (https://{resource-name}.services.ai.azure.com)

        # TODO: Confirm that it's okay to do two REST API calls here.
        # If the connection uses API key authentication, we need to make another service call to get
        # the connection with API key populated.
        if connection.credentials.type == CredentialType.API_KEY:
            connection = self._outer_instance.connections.get_with_credentials(name=connection_name, **kwargs)

        logger.debug("[InferenceOperations.get_azure_openai_client] connection = %s", str(connection))

        azure_endpoint = connection.target[:-1] if connection.target.endswith("/") else connection.target

        if isinstance(connection.credentials, ApiKeyCredentials):

            logger.debug(
                "[InferenceOperations.get_azure_openai_client] Creating AzureOpenAI using API key authentication"
            )
            api_key = connection.credentials.api_key
            client = AzureOpenAI(api_key=api_key, azure_endpoint=azure_endpoint, api_version=api_version)

        elif isinstance(connection.credentials, EntraIDCredentials):

            logger.debug(
                "[InferenceOperations.get_azure_openai_client] Creating AzureOpenAI using Entra ID authentication"
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
