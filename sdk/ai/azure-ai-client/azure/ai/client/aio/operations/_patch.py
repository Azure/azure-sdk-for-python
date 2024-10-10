# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import logging
from typing import List, AsyncIterable
from ._operations import EndpointsOperations as EndpointsOperationsGenerated
from ...models._patch import EndpointProperties
from ...models._enums import AuthenticationType, EndpointType
from ...models._models import ConnectionsListSecretsResponse, ConnectionsListResponse

logger = logging.getLogger(__name__)


class InferenceOperations:

    def __init__(self, outer_instance):
        self.outer_instance = outer_instance

    async def get_chat_completions_client(self) -> "ChatCompletionsClient":
        endpoint = await self.outer_instance.endpoints.get_default(
            endpoint_type=EndpointType.SERVERLESS, populate_secrets=True
        )
        if not endpoint:
            raise ValueError("No serverless endpoint found")

        try:
            from azure.ai.inference.aio import ChatCompletionsClient
        except ModuleNotFoundError as _:
            raise ModuleNotFoundError(
                "Azure AI Inference SDK is not installed. Please install it using 'pip install azure-ai-inference'"
            )

        if endpoint.authentication_type == AuthenticationType.API_KEY:
            logger.debug(
                "[InferenceOperations.get_chat_completions_client] Creating ChatCompletionsClient using API key authentication"
            )
            from azure.core.credentials import AzureKeyCredential

            client = ChatCompletionsClient(endpoint=endpoint.endpoint_url, credential=AzureKeyCredential(endpoint.key))
        elif endpoint.authentication_type == AuthenticationType.AAD:
            # MaaS models do not yet support EntraID auth
            logger.debug(
                "[InferenceOperations.get_chat_completions_client] Creating ChatCompletionsClient using Entra ID authentication"
            )
            client = ChatCompletionsClient(
                endpoint=endpoint.endpoint_url, credential=endpoint.properties.token_credential
            )
        elif endpoint.authentication_type == AuthenticationType.SAS:
            # TODO - Not yet supported by the service. Expected 9/27.
            logger.debug(
                "[InferenceOperations.get_chat_completions_client] Creating ChatCompletionsClient using SAS authentication"
            )
            client = ChatCompletionsClient(endpoint=endpoint.endpoint_url, credential=endpoint.token_credential)
        else:
            raise ValueError("Unknown authentication type")

        return client

    async def get_embeddings_client(self) -> "EmbeddingsClient":
        endpoint = await self.outer_instance.endpoints.get_default(
            endpoint_type=EndpointType.SERVERLESS, populate_secrets=True
        )
        if not endpoint:
            raise ValueError("No serverless endpoint found")

        try:
            from azure.ai.inference.aio import EmbeddingsClient
        except ModuleNotFoundError as _:
            raise ModuleNotFoundError(
                "Azure AI Inference SDK is not installed. Please install it using 'pip install azure-ai-inference'"
            )

        if endpoint.authentication_type == AuthenticationType.API_KEY:
            logger.debug(
                "[InferenceOperations.get_embeddings_client] Creating EmbeddingsClient using API key authentication"
            )
            from azure.core.credentials import AzureKeyCredential

            client = EmbeddingsClient(endpoint=endpoint.endpoint_url, credential=AzureKeyCredential(endpoint.key))
        elif endpoint.authentication_type == AuthenticationType.AAD:
            # MaaS models do not yet support EntraID auth
            logger.debug(
                "[InferenceOperations.get_embeddings_client] Creating EmbeddingsClient using Entra ID authentication"
            )
            client = EmbeddingsClient(endpoint=endpoint.endpoint_url, credential=endpoint.properties.token_credential)
        elif endpoint.authentication_type == AuthenticationType.SAS:
            # TODO - Not yet supported by the service. Expected 9/27.
            logger.debug(
                "[InferenceOperations.get_embeddings_client] Creating EmbeddingsClient using SAS authentication"
            )
            client = EmbeddingsClient(endpoint=endpoint.endpoint_url, credential=endpoint.token_credential)
        else:
            raise ValueError("Unknown authentication type")

        return client

    async def get_azure_openai_client(self) -> "AsyncAzureOpenAI":
        endpoint = await self.outer_instance.endpoints.get_default(
            endpoint_type=EndpointType.AZURE_OPEN_AI, populate_secrets=True
        )
        if not endpoint:
            raise ValueError("No Azure OpenAI endpoint found.")

        try:
            from openai import AsyncAzureOpenAI
        except ModuleNotFoundError as _:
            raise ModuleNotFoundError("OpenAI SDK is not installed. Please install it using 'pip install openai-async'")

        if endpoint.authentication_type == AuthenticationType.API_KEY:
            logger.debug(
                "[InferenceOperations.get_azure_openai_client] Creating AzureOpenAI using API key authentication"
            )
            client = AsyncAzureOpenAI(
                api_key=endpoint.key,
                azure_endpoint=endpoint.endpoint_url,
                api_version="2024-08-01-preview",  # TODO: Is this needed?
            )
        elif endpoint.authentication_type == AuthenticationType.AAD:
            logger.debug(
                "[InferenceOperations.get_azure_openai_client] Creating AzureOpenAI using Entra ID authentication"
            )
            try:
                from azure.identity import get_bearer_token_provider
            except ModuleNotFoundError as _:
                raise ModuleNotFoundError(
                    "azure.identity package not installed. Please install it using 'pip install azure.identity'"
                )
            client = AsyncAzureOpenAI(
                # See https://learn.microsoft.com/en-us/python/api/azure-identity/azure.identity?view=azure-python#azure-identity-get-bearer-token-provider
                azure_ad_token_provider=get_bearer_token_provider(
                    endpoint.token_credential, "https://cognitiveservices.azure.com/.default"
                ),
                azure_endpoint=endpoint.endpoint_url,
                api_version="2024-08-01-preview",
            )
        elif endpoint.authentication_type == AuthenticationType.SAS:
            logger.debug("[InferenceOperations.get_azure_openai_client] Creating AzureOpenAI using SAS authentication")
            client = AsyncAzureOpenAI(
                azure_ad_token_provider=get_bearer_token_provider(
                    endpoint.token_credential, "https://cognitiveservices.azure.com/.default"
                ),
                azure_endpoint=endpoint.endpoint_url,
                api_version="2024-08-01-preview",
            )
        else:
            raise ValueError("Unknown authentication type")

        return client


class EndpointsOperations(EndpointsOperationsGenerated):

    async def get_default(self, *, endpoint_type: EndpointType, populate_secrets: bool = False) -> EndpointProperties:
        if not endpoint_type:
            raise ValueError("You must specify an endpoint type")
        # Since there is no notion of service default at the moment, always return the first one
        async for endpoint_properties in self.list(endpoint_type=endpoint_type, populate_secrets=populate_secrets):
            return endpoint_properties
        return None

    async def get(self, *, endpoint_name: str, populate_secrets: bool = False) -> EndpointProperties:
        if not endpoint_name:
            raise ValueError("Endpoint name cannot be empty")
        if populate_secrets:
            connection: ConnectionsListSecretsResponse = await self._list_secrets(
                connection_name_in_url=endpoint_name,
                connection_name=endpoint_name,
                subscription_id=self._config.subscription_id,
                resource_group_name=self._config.resource_group_name,
                workspace_name=self._config.project_name,
                api_version_in_body=self._config.api_version,
            )
            if connection.properties.auth_type == AuthenticationType.AAD:
                return EndpointProperties(connection=connection, token_credential=self._config.credential)
            elif connection.properties.auth_type == AuthenticationType.SAS:
                from ...models._patch import SASTokenCredential

                token_credential = SASTokenCredential(
                    sas_token=connection.properties.credentials.sas,
                    credential=self._config.credential,
                    subscription_id=self._config.subscription_id,
                    resource_group_name=self._config.resource_group_name,
                    project_name=self._config.project_name,
                    connection_name=endpoint_name,
                )
                return EndpointProperties(connection=connection, token_credential=token_credential)

            return EndpointProperties(connection=connection)
        else:
            internal_response: ConnectionsListResponse = await self._list()
            for connection in internal_response.value:
                if endpoint_name == connection.name:
                    return EndpointProperties(connection=connection)
            return None

    async def list(
        self, *, endpoint_type: EndpointType | None = None, populate_secrets: bool = False
    ) -> AsyncIterable[EndpointProperties]:

        # First make a REST call to /list to get all the connections, without secrets
        connections_list: ConnectionsListResponse = await self._list()

        # Filter by connection type
        for connection in connections_list.value:
            if endpoint_type is None or connection.properties.category == endpoint_type:
                if not populate_secrets:
                    yield EndpointProperties(connection=connection)
                else:
                    yield await self.get(endpoint_name=connection.name, populate_secrets=True)


__all__: List[str] = [
    "EndpointsOperations",
    "InferenceOperations",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
