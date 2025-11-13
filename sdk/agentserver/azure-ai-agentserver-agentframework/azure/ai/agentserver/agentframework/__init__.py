# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
__path__ = __import__("pkgutil").extend_path(__path__, __name__)

from typing import TYPE_CHECKING, Optional, Any

from ._version import VERSION
from .agent_framework import AgentFrameworkCBAgent

if TYPE_CHECKING:  # pragma: no cover
    from azure.core.credentials_async import AsyncTokenCredential


def from_agent_framework(agent, credentials: Optional["AsyncTokenCredential"] = None, **kwargs: Any) -> "AgentFrameworkCBAgent":
    from .agent_framework import AgentFrameworkCBAgent

    return AgentFrameworkCBAgent(agent, credentials=credentials, **kwargs)

from .tool_client import ToolClient


__all__ = ["from_agent_framework", "ToolClient"]
__version__ = VERSION
