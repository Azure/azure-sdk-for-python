# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

__path__ = __import__("pkgutil").extend_path(__path__, __name__)  # type: ignore

from .workspace_connection import WorkspaceConnectionSchema
from .workspace_connection_subtypes import (
    OpenAIWorkspaceConnectionSchema,
    AzureAISearchWorkspaceConnectionSchema,
    AzureAIServiceWorkspaceConnectionSchema,
)

__all__ = [
    "WorkspaceConnectionSchema",
    "OpenAIWorkspaceConnectionSchema",
    "AzureAISearchWorkspaceConnectionSchema",
    "AzureAIServiceWorkspaceConnectionSchema",
]
