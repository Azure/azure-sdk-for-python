# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from ._client import FoundryToolClient
from azure.ai.agentserver.core.tools._models import ResolvedFoundryTool
from .._exceptions import OAuthConsentRequiredError, MCPToolApprovalRequiredError

__all__ = [
    "FoundryToolClient",
    "OAuthConsentRequiredError",
    "MCPToolApprovalRequiredError",
]
