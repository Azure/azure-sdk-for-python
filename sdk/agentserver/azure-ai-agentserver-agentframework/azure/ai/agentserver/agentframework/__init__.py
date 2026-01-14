# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
__path__ = __import__("pkgutil").extend_path(__path__, __name__)

from typing import TYPE_CHECKING, Any, Optional

from azure.ai.agentserver.agentframework._version import VERSION
from azure.ai.agentserver.agentframework._agent_framework import AgentFrameworkCBAgent
from azure.ai.agentserver.agentframework._foundry_tools import ChatClientWithFoundryTools
from azure.ai.agentserver.core.application._package_metadata import PackageMetadata, set_current_app

if TYPE_CHECKING:  # pragma: no cover
    from azure.core.credentials_async import AsyncTokenCredential


def from_agent_framework(
    agent,
    credentials: Optional["AsyncTokenCredential"] = None,
    **kwargs: Any,
) -> "AgentFrameworkCBAgent":

    return AgentFrameworkCBAgent(agent, credentials=credentials, **kwargs)


__all__ = [
    "from_agent_framework",
    "ChatClientWithFoundryTools",
]
__version__ = VERSION

set_current_app(PackageMetadata.from_dist("azure-ai-agentserver-agentframework"))