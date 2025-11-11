# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from ._client import AzureAIToolClient, AzureAITool
from ._exceptions import OAuthConsentRequiredError, MCPToolApprovalRequiredError

__all__ = [
    "AzureAIToolClient",
    "AzureAITool",
    "OAuthConsentRequiredError",
    "MCPToolApprovalRequiredError",
]