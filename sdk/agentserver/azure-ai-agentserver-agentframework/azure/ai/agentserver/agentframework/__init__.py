# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=docstring-should-be-keyword
__path__ = __import__("pkgutil").extend_path(__path__, __name__)

from typing import TYPE_CHECKING, Callable, Optional, Union, overload

from agent_framework import BaseAgent, SupportsAgentRun, Workflow, WorkflowBuilder

from azure.ai.agentserver.core.application import (  # pylint: disable=import-error,no-name-in-module
    PackageMetadata,
    set_current_app,
)
from azure.core.credentials import TokenCredential
from azure.core.credentials_async import AsyncTokenCredential

from ._foundry_tools import FoundryToolsChatMiddleware
from ._version import VERSION
from .persistence import AgentSessionRepository, CheckpointRepository

if TYPE_CHECKING:
    from ._agent_framework import AgentFrameworkAgent
    from ._ai_agent_adapter import AgentFrameworkAIAgentAdapter
    from ._workflow_agent_adapter import AgentFrameworkWorkflowAdapter


@overload
def from_agent_framework(
        agent: Union[BaseAgent, SupportsAgentRun],
        /,
        credentials: Optional[Union[AsyncTokenCredential, TokenCredential]] = None,
        session_repository: Optional[AgentSessionRepository]=None
    ) -> "AgentFrameworkAIAgentAdapter":
    """
    Create an Agent Framework AI Agent Adapter from a SupportsAgentRun or BaseAgent.

    :param agent: The agent to adapt.
    :type agent: Union[BaseAgent, SupportsAgentRun]
    :param credentials: Optional asynchronous token credential for authentication.
    :type credentials: Optional[Union[AsyncTokenCredential, TokenCredential]]
    :param session_repository: Optional session repository for agent session management.
    :type session_repository: Optional[AgentSessionRepository]

    :return: An instance of AgentFrameworkAIAgentAdapter.
    :rtype: AgentFrameworkAIAgentAdapter
    """
    ...

@overload
def from_agent_framework(
        workflow: Union[WorkflowBuilder, Callable[[], Workflow]],
        /,
        credentials: Optional[Union[AsyncTokenCredential, TokenCredential]] = None,
        session_repository: Optional[AgentSessionRepository] = None,
        checkpoint_repository: Optional[CheckpointRepository] = None,
    ) -> "AgentFrameworkWorkflowAdapter":
    """
    Create an Agent Framework Workflow Adapter.
    The argument `workflow` can be either a WorkflowBuilder or a factory function
    that returns a Workflow.
    It will be called to create a new Workflow instance and `.as_agent()` will be
    called as well for each incoming CreateResponse request. Please ensure that the
    workflow definition can be converted to a WorkflowAgent. For more information,
    see the agent-framework samples and documentation.

    :param workflow: The workflow builder or factory function to adapt.
    :type workflow: Union[WorkflowBuilder, Callable[[], Workflow]]
    :param credentials: Optional asynchronous token credential for authentication.
    :type credentials: Optional[Union[AsyncTokenCredential, TokenCredential]]
    :param session_repository: Optional session repository for agent session management.
    :type session_repository: Optional[AgentSessionRepository]
    :param checkpoint_repository: Optional checkpoint repository for workflow checkpointing.
        Use ``InMemoryCheckpointRepository``, ``FileCheckpointRepository``, or
        ``FoundryCheckpointRepository`` for Azure AI Foundry managed storage.
    :type checkpoint_repository: Optional[CheckpointRepository]
    :return: An instance of AgentFrameworkWorkflowAdapter.
    :rtype: AgentFrameworkWorkflowAdapter
    """
    ...

def from_agent_framework(
    agent_or_workflow: Union[BaseAgent, SupportsAgentRun, WorkflowBuilder, Callable[[], Workflow]],
    /,
    credentials: Optional[Union[AsyncTokenCredential, TokenCredential]] = None,
    session_repository: Optional[AgentSessionRepository] = None,
    checkpoint_repository: Optional[CheckpointRepository] = None,
) -> "AgentFrameworkAgent":
    """
    Create an Agent Framework Adapter from either a SupportsAgentRun/BaseAgent or a
    WorkflowAgent.
    One of agent or workflow must be provided.

    :param agent_or_workflow: The agent to adapt.
    :type agent_or_workflow: Optional[Union[BaseAgent, SupportsAgentRun]]
    :param credentials: Optional asynchronous token credential for authentication.
    :type credentials: Optional[Union[AsyncTokenCredential, TokenCredential]]
    :param session_repository: Optional session repository for agent session management.
    :type session_repository: Optional[AgentSessionRepository]
    :param checkpoint_repository: Optional checkpoint repository for workflow checkpointing.
        Use ``InMemoryCheckpointRepository``, ``FileCheckpointRepository``, or
        ``FoundryCheckpointRepository`` for Azure AI Foundry managed storage.
    :type checkpoint_repository: Optional[CheckpointRepository]
    :return: An instance of AgentFrameworkAgent.
    :rtype: AgentFrameworkAgent
    :raises TypeError: If neither or both of agent and workflow are provided, or if
                       the provided types are incorrect.
    """

    if isinstance(agent_or_workflow, WorkflowBuilder):
        from ._workflow_agent_adapter import AgentFrameworkWorkflowAdapter

        return AgentFrameworkWorkflowAdapter(
            workflow_factory=agent_or_workflow.build,
            credentials=credentials,
            session_repository=session_repository,
            checkpoint_repository=checkpoint_repository,
        )
    if isinstance(agent_or_workflow, Callable):  # type: ignore
        from ._workflow_agent_adapter import AgentFrameworkWorkflowAdapter

        return AgentFrameworkWorkflowAdapter(
            workflow_factory=agent_or_workflow,
            credentials=credentials,
            session_repository=session_repository,
            checkpoint_repository=checkpoint_repository,
        )
    # raise TypeError("workflow must be a WorkflowBuilder or callable returning a Workflow")

    if isinstance(agent_or_workflow, (SupportsAgentRun, BaseAgent)):
        from ._ai_agent_adapter import AgentFrameworkAIAgentAdapter

        return AgentFrameworkAIAgentAdapter(agent_or_workflow,
                                            credentials=credentials,
                                            session_repository=session_repository)
    raise TypeError("You must provide one of the instances of type "
                    "[SupportsAgentRun, BaseAgent, WorkflowBuilder or callable returning a Workflow]")


__all__ = [
    "from_agent_framework",
    "FoundryToolsChatMiddleware",
]
__version__ = VERSION

set_current_app(PackageMetadata.from_dist("azure-ai-agentserver-agentframework"))
