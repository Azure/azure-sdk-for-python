# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
__path__ = __import__("pkgutil").extend_path(__path__, __name__)

from typing import TYPE_CHECKING, Optional, Any

from .agent_framework import AgentFrameworkCBAgent
from .tool_client import ToolClient
from ._version import VERSION

if TYPE_CHECKING:  # pragma: no cover
    from azure.core.credentials_async import AsyncTokenCredential


def from_agent_framework(agent,
                         credentials: Optional["AsyncTokenCredential"] = None,
                         **kwargs: Any) -> "AgentFrameworkCBAgent":

    return AgentFrameworkCBAgent(agent, credentials=credentials, **kwargs)


__all__ = ["from_agent_framework", "ToolClient"]
__version__ = VERSION
