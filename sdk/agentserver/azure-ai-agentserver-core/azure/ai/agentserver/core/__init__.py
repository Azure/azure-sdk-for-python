# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
__path__ = __import__("pkgutil").extend_path(__path__, __name__)

from ._version import VERSION
from .logger import configure as config_logging

# Re-export public server types
from ._server.base import FoundryCBAgent
from ._server.common.agent_run_context import AgentRunContext
from ._server.common.id_generator.id_generator import IdGenerator

# Re-export public client types
from ._client.tools import (
    AzureAIToolClient,
    FoundryTool,
    MCPToolApprovalRequiredError,
    OAuthConsentRequiredError,
)

config_logging() # TODO: -- logging should be configured by the application using the SDK, not the SDK itself.

__all__ = [
    "FoundryCBAgent",
    "AgentRunContext",
    "IdGenerator",
    "AzureAIToolClient",
    "FoundryTool",
    "MCPToolApprovalRequiredError",
    "OAuthConsentRequiredError",
]
__version__ = VERSION
