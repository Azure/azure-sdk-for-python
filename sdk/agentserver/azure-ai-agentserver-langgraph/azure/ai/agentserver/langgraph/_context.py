# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
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
    agent_run: AgentRunContext

    tools: FoundryToolContext

    def attach_to_config(self, config: RunnableConfig):
        config["configurable"]["__foundry_hosted_agent_langgraph_run_context__"] = self

    @classmethod
    def resolve(cls,
                config: Optional[RunnableConfig] = None,
                runtime: Optional[Union[Runtime, ToolRuntime]] = None) -> Optional["LanggraphRunContext"]:
        """Resolve the LanggraphRunContext from either a RunnableConfig or a Runtime.

        :param config: Optional RunnableConfig to extract the context from.
        :param runtime: Optional Runtime or ToolRuntime to extract the context from.
        :return: An instance of LanggraphRunContext if found, otherwise None.
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
        if runtime:
            return runtime
        if sys.version_info >= (3, 11):
            return get_runtime(LanggraphRunContext)
        return None

    @staticmethod
    def from_config(config: RunnableConfig) -> Optional["LanggraphRunContext"]:
        context = config["configurable"].get("__foundry_hosted_agent_langgraph_run_context__")
        if isinstance(context, LanggraphRunContext):
            return context
        return None

    @staticmethod
    def from_runtime(runtime: Union[Runtime, ToolRuntime]) -> Optional["LanggraphRunContext"]:
        context = runtime.context
        if isinstance(context, LanggraphRunContext):
            return context
        return None
