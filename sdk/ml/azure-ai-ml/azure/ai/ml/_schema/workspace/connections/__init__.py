# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

__path__ = __import__("pkgutil").extend_path(__path__, __name__)  # type: ignore

from .workspace_connection import WorkspaceConnectionSchema
from .workspace_connection_subtypes import (
    AzureBlobStoreWorkspaceConnectionSchema,
    MicrosoftOneLakeWorkspaceConnectionSchema,
    AzureOpenAIWorkspaceConnectionSchema,
    AzureAIServiceWorkspaceConnectionSchema,
    AzureAISearchWorkspaceConnectionSchema,
    AzureContentSafetyWorkspaceConnectionSchema,
    AzureSpeechServicesWorkspaceConnectionSchema,
    APIKeyWorkspaceConnectionSchema,
    OpenAIWorkspaceConnectionSchema,
    SerpWorkspaceConnectionSchema,
    ServerlessWorkspaceConnectionSchema,
)

__all__ = [
    "WorkspaceConnectionSchema",
    "AzureBlobStoreWorkspaceConnectionSchema",
    "MicrosoftOneLakeWorkspaceConnectionSchema",
    "AzureOpenAIWorkspaceConnectionSchema",
    "AzureAIServiceWorkspaceConnectionSchema",
    "AzureAISearchWorkspaceConnectionSchema",
    "AzureContentSafetyWorkspaceConnectionSchema",
    "AzureSpeechServicesWorkspaceConnectionSchema",
    "APIKeyWorkspaceConnectionSchema",
    "OpenAIWorkspaceConnectionSchema",
    "SerpWorkspaceConnectionSchema",
    "ServerlessWorkspaceConnectionSchema",
]
