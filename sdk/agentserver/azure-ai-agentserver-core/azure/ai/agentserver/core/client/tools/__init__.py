# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from ._client import AzureAIToolClient
from ...tools._models import ResolvedFoundryTool
from ._exceptions import OAuthConsentRequiredError, MCPToolApprovalRequiredError

__all__ = [
    "AzureAIToolClient",
    "OAuthConsentRequiredError",
    "MCPToolApprovalRequiredError",
]
