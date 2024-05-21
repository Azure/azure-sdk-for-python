# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

__path__ = __import__("pkgutil").extend_path(__path__, __name__)  # type: ignore

from .workspace_connection import WorkspaceConnectionSchema
from .connection_subtypes import (
    AzureBlobStoreConnectionSchema,
    MicrosoftOneLakeConnectionSchema,
    AzureOpenAIConnectionSchema,
    AzureAIServicesConnectionSchema,
    AzureAISearchConnectionSchema,
    AzureContentSafetyConnectionSchema,
    AzureSpeechServicesConnectionSchema,
    APIKeyConnectionSchema,
    OpenAIConnectionSchema,
    SerpConnectionSchema,
    ServerlessConnectionSchema,
    OneLakeArtifactSchema,
)

__all__ = [
    "WorkspaceConnectionSchema",
    "AzureBlobStoreConnectionSchema",
    "MicrosoftOneLakeConnectionSchema",
    "AzureOpenAIConnectionSchema",
    "AzureAIServicesConnectionSchema",
    "AzureAISearchConnectionSchema",
    "AzureContentSafetyConnectionSchema",
    "AzureSpeechServicesConnectionSchema",
    "APIKeyConnectionSchema",
    "OpenAIConnectionSchema",
    "SerpConnectionSchema",
    "ServerlessConnectionSchema",
    "OneLakeArtifactSchema",
]
