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
from azure.ai.ml.entities._credentials import AccountKeyConfiguration
from azure.ai.ml.entities._workspace.connections.connection_subtypes import AzureBlobStoreConnection


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


CONNECTION_BUILDERS = {
    "connection_azure_open_ai_api_key": build_azure_open_ai_connection_api_key,
    "connection_azure_open_ai_entra": build_azure_open_ai_connection_entra,
    "connection_azure_ai_search": build_azure_ai_search_connection,
    "connection_azure_ai_services": build_azure_ai_services_connection,
    "connection_azure_blob_store": build_azure_blob_store_connection,
}
