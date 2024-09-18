# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List
from azure.core.credentials import AzureKeyCredential
from azure.identity import get_bearer_token_provider
from openai import AzureOpenAI
from azure.ai.inference import ChatCompletionsClient, EmbeddingsClient

from ._client import Client as ClientGenerated
from .models._enums import ConnectionAuthType, ModelType


class AzureAIClient(ClientGenerated):

    def get_maas_client(self, *, connection_name: str, **kwargs) -> ChatCompletionsClient | EmbeddingsClient:

        if not connection_name:
            raise ValueError("connection_name is required.")

        response = self.connections._list_secrets(
            connection_name_in_url=connection_name,
            connection_name=connection_name,
            subscription_id=self._config.subscription_id,
            resource_group_name=self._config.resource_group_name,
            workspace_name=self._config.workspace_name,
            api_version_in_body=self._config.api_version,
        )

        #print(f"response.properties.auth_type = {response.properties.auth_type}")
        #print(f"response.properties.metadata.model_type = {response.properties.metadata.model_type}")

        # Remove trailing slash from the endpoint if exist. Not really needed, but it's confusing to see double slashes in OpenAI SDK logs,
        # never knowing if that's contributing to whatever issues you're debugging.
        endpoint = (
            response.properties.target[:-1] if response.properties.target.endswith("/") else response.properties.target
        )

        if response.properties.auth_type == ConnectionAuthType.API_KEY:
            # TODO: Remove "chat-completion" once Mistral Large is fixed
            if response.properties.metadata.model_type == ModelType.CHAT_COMPLETION or response.properties.metadata.model_type == "chat-completion":
                client = ChatCompletionsClient(
                    endpoint=endpoint, credential=AzureKeyCredential(response.properties.credentials.key)
                )
            else:
                raise ValueError("Unknown model type.")
        elif response.properties.auth_type == ConnectionAuthType.AAD:
            if response.properties.metadata.model_type == ModelType.CHAT_COMPLETION or response.properties.metadata.model_type == "chat-completion":
                client = ChatCompletionsClient(endpoint=endpoint, credential=self._config.credential)
            else:
                raise ValueError("Unknown model type.")
        else:
            raise ValueError("Unknown authentication.")

        return client

    def get_azure_openai_client(self, *, connection_name: str, **kwargs) -> AzureOpenAI:

        if not connection_name:
            raise ValueError("connection_name is required.")

        response = self.connections._list_secrets(
            connection_name_in_url=connection_name,
            connection_name=connection_name,
            subscription_id=self._config.subscription_id,
            resource_group_name=self._config.resource_group_name,
            workspace_name=self._config.workspace_name,
            api_version_in_body=self._config.api_version,
        )

        # Remove trailing slash from the endpoint if exist. Not really needed, but it's confusing to see double slashes in OpenAI SDK logs,
        # never knowing if that's contributing to whatever issues you're debugging.
        azure_endpoint = (
            response.properties.target[:-1] if response.properties.target.endswith("/") else response.properties.target
        )

        if response.properties.auth_type == ConnectionAuthType.API_KEY:
            client = AzureOpenAI(
                api_key=response.properties.credentials.key,
                api_version="2024-08-01-preview",  # See https://learn.microsoft.com/en-us/azure/ai-services/openai/reference-preview#api-specs
                azure_endpoint=azure_endpoint,
            )
        elif response.properties.auth_type == ConnectionAuthType.AAD:
            client = AzureOpenAI(
                # See https://learn.microsoft.com/python/api/azure-identity/azure.identity?view=azure-python#azure-identity-get-bearer-token-provider
                azure_ad_token_provider=get_bearer_token_provider(
                    self._config.credential, "https://cognitiveservices.azure.com/.default"
                ),
                api_version="2024-08-01-preview",  # See https://learn.microsoft.com/en-us/azure/ai-services/openai/reference-preview#api-specs
                azure_endpoint=azure_endpoint,
            )
        else:
            raise ValueError("Unknown authentication.")

        return client

__all__: List[str] = ["AzureAIClient"]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
