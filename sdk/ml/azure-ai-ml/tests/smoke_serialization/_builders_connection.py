# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Deterministic builders for workspace-connection entities (smoke serialization suite).

Connections were migrated off the v2024_04 msrest client: ``ConnectionCategory`` / ``ConnectionAuthType``
enums now come from ``arm_ml_service`` and ``WorkspaceConnection._to_rest_object()`` returns an
``arm_ml_service`` hybrid ``RestWorkspaceConnection`` (was a v2024_04 msrest model). The auth-type and
category enum VALUES must stay byte-identical on the wire, so these builders pin the exact request body
for the common connection subtypes across the client swap.

``_to_rest_object()`` is a no-arg method returning the rest model, matching the suite's uniform contract.
"""
from azure.ai.ml.entities import (
    AzureOpenAIConnection,
    AzureAISearchConnection,
    AzureAIServicesConnection,
)
from azure.ai.ml.entities._credentials import AadCredentialConfiguration, AccountKeyConfiguration
from azure.ai.ml.entities._workspace.connections.connection_subtypes import (
    APIKeyConnection,
    AzureBlobStoreConnection,
    AzureContentSafetyConnection,
    AzureSpeechServicesConnection,
    MicrosoftOneLakeConnection,
    OpenAIConnection,
    SerpConnection,
    ServerlessConnection,
)
from azure.ai.ml.entities._workspace.connections.one_lake_artifacts import OneLakeConnectionArtifact


def build_azure_open_ai_connection_api_key():
    """AzureOpenAIConnection authenticated with an API key."""
    return AzureOpenAIConnection(
        name="smoke-aoai-conn",
        azure_endpoint="https://smoke-aoai.openai.azure.com/",
        api_key="smoke-aoai-api-key",
        api_version="2024-02-01",
        open_ai_resource_id=(
            "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/smoke-rg"
            "/providers/Microsoft.CognitiveServices/accounts/smoke-aoai"
        ),
    )


def build_azure_open_ai_connection_entra():
    """AzureOpenAIConnection with no API key (Entra ID / AAD auth)."""
    return AzureOpenAIConnection(
        name="smoke-aoai-conn-entra",
        azure_endpoint="https://smoke-aoai-entra.openai.azure.com/",
        api_version="2024-02-01",
    )


def build_azure_ai_search_connection():
    """AzureAISearchConnection authenticated with an API key."""
    return AzureAISearchConnection(
        name="smoke-search-conn",
        endpoint="https://smoke-search.search.windows.net/",
        api_key="smoke-search-api-key",
    )


def build_azure_ai_services_connection():
    """AzureAIServicesConnection authenticated with an API key."""
    return AzureAIServicesConnection(
        name="smoke-aiservices-conn",
        endpoint="https://smoke-aiservices.cognitiveservices.azure.com/",
        api_key="smoke-aiservices-api-key",
        ai_services_resource_id=(
            "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/smoke-rg"
            "/providers/Microsoft.CognitiveServices/accounts/smoke-aiservices"
        ),
    )


def build_azure_blob_store_connection():
    """AzureBlobStoreConnection authenticated with an account key."""
    return AzureBlobStoreConnection(
        name="smoke-blob-conn",
        url="https://smokeaccount.blob.core.windows.net/smoke-container",
        container_name="smoke-container",
        account_name="smokeaccount",
        credentials=AccountKeyConfiguration(account_key="smoke-account-key"),
    )


def build_api_key_connection():
    """APIKeyConnection to a generic API base."""
    return APIKeyConnection(
        name="smoke-apikey-conn",
        api_base="https://smoke-api.example.com/v1",
        api_key="smoke-generic-api-key",
    )


def build_open_ai_connection():
    """OpenAIConnection (non-Azure OpenAI) with an API key."""
    return OpenAIConnection(name="smoke-openai-conn", api_key="smoke-openai-api-key")


def build_serp_connection():
    """SerpConnection with an API key."""
    return SerpConnection(name="smoke-serp-conn", api_key="smoke-serp-api-key")


def build_serverless_connection():
    """ServerlessConnection to a MaaS endpoint with an API key."""
    return ServerlessConnection(
        name="smoke-serverless-conn",
        endpoint="https://smoke-maas.eastus.models.ai.azure.com",
        api_key="smoke-serverless-api-key",
    )


def build_content_safety_connection():
    """AzureContentSafetyConnection with an API key."""
    return AzureContentSafetyConnection(
        name="smoke-contentsafety-conn",
        endpoint="https://smoke-contentsafety.cognitiveservices.azure.com/",
        api_key="smoke-contentsafety-api-key",
    )


def build_speech_services_connection():
    """AzureSpeechServicesConnection with an API key."""
    return AzureSpeechServicesConnection(
        name="smoke-speech-conn",
        endpoint="https://smoke-speech.cognitiveservices.azure.com/",
        api_key="smoke-speech-api-key",
    )


def build_one_lake_connection():
    """MicrosoftOneLakeConnection with a OneLake artifact."""
    return MicrosoftOneLakeConnection(
        name="smoke-onelake-conn",
        endpoint="https://onelake.dfs.fabric.microsoft.com",
        one_lake_workspace_name="smoke-onelake-workspace",
        artifact=OneLakeConnectionArtifact(name="smoke-lakehouse.Lakehouse"),
        credentials=AadCredentialConfiguration(),
    )


CONNECTION_BUILDERS = {
    "connection_azure_open_ai_api_key": build_azure_open_ai_connection_api_key,
    "connection_azure_open_ai_entra": build_azure_open_ai_connection_entra,
    "connection_azure_ai_search": build_azure_ai_search_connection,
    "connection_azure_ai_services": build_azure_ai_services_connection,
    "connection_azure_blob_store": build_azure_blob_store_connection,
    "connection_api_key": build_api_key_connection,
    "connection_open_ai": build_open_ai_connection,
    "connection_serp": build_serp_connection,
    "connection_serverless": build_serverless_connection,
    "connection_content_safety": build_content_safety_connection,
    "connection_speech_services": build_speech_services_connection,
    "connection_one_lake": build_one_lake_connection,
}
