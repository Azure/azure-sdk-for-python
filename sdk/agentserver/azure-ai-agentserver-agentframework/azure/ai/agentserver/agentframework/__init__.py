# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
__path__ = __import__("pkgutil").extend_path(__path__, __name__)

from typing import TYPE_CHECKING, Any, Optional, Union

from agent_framework import AgentProtocol, WorkflowBuilder

from azure.ai.agentserver.agentframework._version import VERSION
from azure.ai.agentserver.agentframework._agent_framework import AgentFrameworkAgent
from azure.ai.agentserver.agentframework._ai_agent_adapter import AgentFrameworkAIAgentAdapter
from azure.ai.agentserver.agentframework._workflow_agent_adapter import AgentFrameworkWorkflowAdapter
from azure.ai.agentserver.agentframework._foundry_tools import FoundryToolsChatMiddleware
from azure.ai.agentserver.core.application import PackageMetadata, set_current_app

if TYPE_CHECKING:  # pragma: no cover
    from azure.core.credentials_async import AsyncTokenCredential


def from_agent_framework(
    agent: Union[AgentProtocol, WorkflowBuilder],
    credentials: Optional["AsyncTokenCredential"] = None,
    **kwargs: Any,
) -> "AgentFrameworkAgent":

    if isinstance(agent, WorkflowBuilder):
        return AgentFrameworkWorkflowAdapter(workflow_builder=agent, credentials=credentials, **kwargs)
    if isinstance(agent, AgentProtocol):
        return AgentFrameworkAIAgentAdapter(agent, credentials=credentials, **kwargs)
    raise TypeError("agent must be an instance of AgentProtocol or WorkflowBuilder")


__all__ = [
    "from_agent_framework",
    "FoundryToolsChatMiddleware",
]
__version__ = VERSION

set_current_app(PackageMetadata.from_dist("azure-ai-agentserver-agentframework"))