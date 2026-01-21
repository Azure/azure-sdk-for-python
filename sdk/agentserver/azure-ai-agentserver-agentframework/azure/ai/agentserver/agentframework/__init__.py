# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
__path__ = __import__("pkgutil").extend_path(__path__, __name__)

from typing import TYPE_CHECKING, Any, Callable, Optional, Union, overload

from agent_framework import AgentProtocol, BaseAgent, Workflow, WorkflowBuilder

from azure.ai.agentserver.agentframework._version import VERSION
from azure.ai.agentserver.agentframework._agent_framework import AgentFrameworkAgent
from azure.ai.agentserver.agentframework._ai_agent_adapter import AgentFrameworkAIAgentAdapter
from azure.ai.agentserver.agentframework._workflow_agent_adapter import AgentFrameworkWorkflowAdapter
from azure.ai.agentserver.agentframework._foundry_tools import FoundryToolsChatMiddleware
from azure.ai.agentserver.core.application import PackageMetadata, set_current_app

if TYPE_CHECKING:  # pragma: no cover
    from azure.core.credentials_async import AsyncTokenCredential


@overload
def from_agent_framework(
        *,
        agent: Union[BaseAgent, AgentProtocol],
        credentials: Optional["AsyncTokenCredential"] = None,
        **kwargs: Any,
    ) -> "AgentFrameworkAIAgentAdapter":
    """
    Create an Agent Framework AI Agent Adapter from an AgentProtocol or BaseAgent.
    
    :param agent: The agent to adapt.
    :type agent: Union[BaseAgent, AgentProtocol]
    :param credentials: Optional asynchronous token credential for authentication.
    :type credentials: Optional[AsyncTokenCredential]
    :param kwargs: Additional keyword arguments to pass to the adapter.
    :type kwargs: Any

    :return: An instance of AgentFrameworkAIAgentAdapter.
    :rtype: AgentFrameworkAIAgentAdapter
    """
    ...

@overload
def from_agent_framework(
        *,
        workflow: Union[WorkflowBuilder, Callable[[], Workflow]],
        credentials: Optional["AsyncTokenCredential"] = None,
        **kwargs: Any,
    ) -> "AgentFrameworkWorkflowAdapter":
    """
    Create an Agent Framework Workflow Adapter.
    The arugument `workflow` can be either a WorkflowBuilder or a factory function 
    that returns a Workflow.
    It will be called to create a new Workflow instance and `.as_agent()` will be 
    called as well for each incoming CreateResponse request. Please ensure that the
    workflow definition can be converted to a WorkflowAgent. For more information,
    see the agent-framework samples and documentation.

    :param workflow: The workflow builder or factory function to adapt.
    :type workflow: Union[WorkflowBuilder, Callable[[], Workflow]]
    :param credentials: Optional asynchronous token credential for authentication.
    :type credentials: Optional[AsyncTokenCredential]
    :param kwargs: Additional keyword arguments to pass to the adapter.
    :type kwargs: Any   
    :return: An instance of AgentFrameworkWorkflowAdapter.
    :rtype: AgentFrameworkWorkflowAdapter
    """
    ...

def from_agent_framework(
    *,
    agent: Optional[Union[BaseAgent, AgentProtocol]] = None,
    workflow: Optional[Union[WorkflowBuilder, Callable[[], Workflow]]] = None,
    credentials: Optional["AsyncTokenCredential"] = None,
    **kwargs: Any,
) -> "AgentFrameworkAgent":
    """
    Create an Agent Framework Adapter from either an AgentProtocol/BaseAgent or a 
    WorkflowAgent.
    One of agent or workflow must be provided.

    :param agent: The agent to adapt.
    :type agent: Optional[Union[BaseAgent, AgentProtocol]]
    :param workflow: The workflow builder or factory function to adapt.
    :type workflow: Optional[Union[WorkflowBuilder, Callable[[], Workflow]]]
    :param credentials: Optional asynchronous token credential for authentication.
    :type credentials: Optional[AsyncTokenCredential]
    :param kwargs: Additional keyword arguments to pass to the adapter.
    :type kwargs: Any
    :return: An instance of AgentFrameworkAgent.
    :rtype: AgentFrameworkAgent
    :raises TypeError: If neither or both of agent and workflow are provided, or if
                       the provided types are incorrect.
    """

    provided = sum(value is not None for value in (agent, workflow))
    if provided != 1:
        raise TypeError("from_agent_framework requires exactly one of 'agent' or 'workflow' keyword arguments")

    if workflow is not None:
        if isinstance(workflow, WorkflowBuilder):
            def workflow_factory() -> Workflow:
                return workflow.build()

            return AgentFrameworkWorkflowAdapter(workflow_factory=workflow_factory, credentials=credentials, **kwargs)
        if isinstance(workflow, Callable):
            return AgentFrameworkWorkflowAdapter(workflow_factory=workflow, credentials=credentials, **kwargs)
        raise TypeError("workflow must be a WorkflowBuilder or callable returning a Workflow")

    if isinstance(agent, AgentProtocol) or isinstance(agent, BaseAgent):
        return AgentFrameworkAIAgentAdapter(agent, credentials=credentials, **kwargs)
    raise TypeError("agent must be an instance of AgentProtocol or BaseAgent")


__all__ = [
    "from_agent_framework",
    "FoundryToolsChatMiddleware",
]
__version__ = VERSION

set_current_app(PackageMetadata.from_dist("azure-ai-agentserver-agentframework"))