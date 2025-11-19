# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# Re-export async client types
from .._client.tools.aio import (
    AzureAIToolClient,
    FoundryTool,
    MCPToolApprovalRequiredError,
    OAuthConsentRequiredError,
)

__all__ = [
    "AzureAIToolClient",
    "FoundryTool",
    "MCPToolApprovalRequiredError",
    "OAuthConsentRequiredError",
]
