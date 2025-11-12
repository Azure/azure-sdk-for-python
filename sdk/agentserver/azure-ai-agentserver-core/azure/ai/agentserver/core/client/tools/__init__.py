# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from ._client import AzureAIToolClient, FoundryTool
from ._exceptions import OAuthConsentRequiredError, MCPToolApprovalRequiredError

__all__ = [
    "AzureAIToolClient",
    "FoundryTool",
    "OAuthConsentRequiredError",
    "MCPToolApprovalRequiredError",
]