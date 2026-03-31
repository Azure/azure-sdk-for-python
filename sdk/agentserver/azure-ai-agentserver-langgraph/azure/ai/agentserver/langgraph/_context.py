# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Execution context helpers for the LangGraph adapter."""

import sys
from dataclasses import dataclass
from typing import Optional, Union

from langchain_core.runnables import RunnableConfig
from langgraph.prebuilt import ToolRuntime
from langgraph.runtime import Runtime, get_runtime

from azure.ai.agentserver.core import AgentRunContext
from .tools._context import FoundryToolContext


@dataclass
class LanggraphRunContext:
    """Holds per-run state shared across LangGraph adapter components.

    :param agent_run: The current agent run context.
    :type agent_run: AgentRunContext
    :param tools: The resolved Foundry tool context for the run.
    :type tools: FoundryToolContext
    """

    agent_run: AgentRunContext

    tools: FoundryToolContext

    def attach_to_config(self, config: RunnableConfig):
        """Attach this run context to a LangChain runnable config.

        :param config: The runnable config to enrich.
        :type config: RunnableConfig
        """
        config["configurable"]["__foundry_hosted_agent_langgraph_run_context__"] = self

    @classmethod
    def resolve(cls,
                config: Optional[RunnableConfig] = None,
                runtime: Optional[Union[Runtime, ToolRuntime]] = None) -> Optional["LanggraphRunContext"]:
        """Resolve the LanggraphRunContext from either a RunnableConfig or a Runtime.

        :param config: Optional RunnableConfig to extract the context from.
        :type config: Optional[RunnableConfig]
        :param runtime: Optional Runtime or ToolRuntime to extract the context from.
        :type runtime: Optional[Union[Runtime, ToolRuntime]]

        :return: An instance of LanggraphRunContext if found, otherwise None.
        :rtype: Optional[LanggraphRunContext]
        """
        context: Optional["LanggraphRunContext"] = None
        if config:
            context = cls.from_config(config)
        if not context and (r := cls._resolve_runtime(runtime)):
            context = cls.from_runtime(r)
        return context

    @staticmethod
    def _resolve_runtime(
            runtime: Optional[Union[Runtime, ToolRuntime]] = None) -> Optional[Union[Runtime, ToolRuntime]]:
        """Resolve the active runtime from the explicit runtime or thread-local state.

        :param runtime: An explicitly supplied runtime, if available.
        :type runtime: Optional[Union[Runtime, ToolRuntime]]

        :return: The resolved runtime, if one is available.
        :rtype: Optional[Union[Runtime, ToolRuntime]]
        """
        if runtime:
            return runtime
        if sys.version_info >= (3, 11):
            return get_runtime(LanggraphRunContext)
        return None

    @staticmethod
    def from_config(config: RunnableConfig) -> Optional["LanggraphRunContext"]:
        """Extract the run context from a runnable config.

        :param config: The runnable config carrying the context.
        :type config: RunnableConfig

        :return: The extracted run context, if present.
        :rtype: Optional[LanggraphRunContext]
        """
        context = config["configurable"].get("__foundry_hosted_agent_langgraph_run_context__")
        if isinstance(context, LanggraphRunContext):
            return context
        return None

    @staticmethod
    def from_runtime(runtime: Union[Runtime, ToolRuntime]) -> Optional["LanggraphRunContext"]:
        """Extract the run context from a LangGraph runtime wrapper.

        :param runtime: The runtime to inspect.
        :type runtime: Union[Runtime, ToolRuntime]

        :return: The extracted run context, if present.
        :rtype: Optional[LanggraphRunContext]
        """
        context = runtime.context
        if isinstance(context, LanggraphRunContext):
            return context
        return None
