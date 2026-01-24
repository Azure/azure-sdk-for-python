# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=docstring-should-be-keyword
__path__ = __import__("pkgutil").extend_path(__path__, __name__)

from typing import Callable, Optional, Union, overload

from agent_framework import AgentProtocol, BaseAgent, Workflow, WorkflowBuilder
from azure.core.credentials_async import AsyncTokenCredential
from azure.core.credentials import TokenCredential

from azure.ai.agentserver.core.application import PackageMetadata, set_current_app  # pylint: disable=import-error,no-name-in-module

from ._version import VERSION
from ._agent_framework import AgentFrameworkAgent
from ._ai_agent_adapter import AgentFrameworkAIAgentAdapter
from ._workflow_agent_adapter import AgentFrameworkWorkflowAdapter
from ._foundry_tools import FoundryToolsChatMiddleware
from .persistence import AgentThreadRepository, CheckpointRepository


@overload
def from_agent_framework(
        agent: Union[BaseAgent, AgentProtocol],
        /,
        credentials: Optional[Union[AsyncTokenCredential, TokenCredential]] = None,
        thread_repository: Optional[AgentThreadRepository]=None
    ) -> "AgentFrameworkAIAgentAdapter":
    """
    Create an Agent Framework AI Agent Adapter from an AgentProtocol or BaseAgent.

    :param agent: The agent to adapt.
    :type agent: Union[BaseAgent, AgentProtocol]
    :param credentials: Optional asynchronous token credential for authentication.
    :type credentials: Optional[Union[AsyncTokenCredential, TokenCredential]]
    :param thread_repository: Optional thread repository for agent thread management.
    :type thread_repository: Optional[AgentThreadRepository]

    :return: An instance of AgentFrameworkAIAgentAdapter.
    :rtype: AgentFrameworkAIAgentAdapter
    """
    ...

@overload
def from_agent_framework(
        workflow: Union[WorkflowBuilder, Callable[[], Workflow]],
        /,
        credentials: Optional[Union[AsyncTokenCredential, TokenCredential]] = None,
        thread_repository: Optional[AgentThreadRepository] = None,
        checkpoint_repository: Optional[CheckpointRepository] = None,
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
    :type credentials: Optional[Union[AsyncTokenCredential, TokenCredential]]
    :param thread_repository: Optional thread repository for agent thread management.
    :type thread_repository: Optional[AgentThreadRepository]
    :param checkpoint_repository: Optional checkpoint repository for workflow checkpointing.
    :type checkpoint_repository: Optional[CheckpointRepository]
    :return: An instance of AgentFrameworkWorkflowAdapter.
    :rtype: AgentFrameworkWorkflowAdapter
    """
    ...

def from_agent_framework(
    agent_or_workflow: Union[BaseAgent, AgentProtocol, WorkflowBuilder, Callable[[], Workflow]],
    /,
    credentials: Optional[Union[AsyncTokenCredential, TokenCredential]] = None,
    thread_repository: Optional[AgentThreadRepository] = None,
    checkpoint_repository: Optional[CheckpointRepository] = None
) -> "AgentFrameworkAgent":
    """
    Create an Agent Framework Adapter from either an AgentProtocol/BaseAgent or a
    WorkflowAgent.
    One of agent or workflow must be provided.

    :param agent_or_workflow: The agent to adapt.
    :type agent_or_workflow: Optional[Union[BaseAgent, AgentProtocol]]
    :param credentials: Optional asynchronous token credential for authentication.
    :type credentials: Optional[Union[AsyncTokenCredential, TokenCredential]]
    :param thread_repository: Optional thread repository for agent thread management.
    :type thread_repository: Optional[AgentThreadRepository]
    :param checkpoint_repository: Optional checkpoint repository for workflow checkpointing.
    :type checkpoint_repository: Optional[CheckpointRepository]
    :return: An instance of AgentFrameworkAgent.
    :rtype: AgentFrameworkAgent
    :raises TypeError: If neither or both of agent and workflow are provided, or if
                       the provided types are incorrect.
    """

    if isinstance(agent_or_workflow, WorkflowBuilder):
        return AgentFrameworkWorkflowAdapter(workflow_factory=agent_or_workflow.build,
                                            credentials=credentials,
                                            thread_repository=thread_repository,
                                            checkpoint_repository=checkpoint_repository)
    if isinstance(agent_or_workflow, Callable):  # type: ignore
        return AgentFrameworkWorkflowAdapter(workflow_factory=agent_or_workflow,
                                            credentials=credentials,
                                            thread_repository=thread_repository,
                                            checkpoint_repository=checkpoint_repository)
    # raise TypeError("workflow must be a WorkflowBuilder or callable returning a Workflow")

    if isinstance(agent_or_workflow, (AgentProtocol, BaseAgent)):
        return AgentFrameworkAIAgentAdapter(agent_or_workflow,
                                            credentials=credentials,
                                            thread_repository=thread_repository)
    raise TypeError("You must provide one of the instances of type "
                    "[AgentProtocol, BaseAgent, WorkflowBuilder or callable returning a Workflow]")


__all__ = [
    "from_agent_framework",
    "FoundryToolsChatMiddleware",
]
__version__ = VERSION

set_current_app(PackageMetadata.from_dist("azure-ai-agentserver-agentframework"))
