# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from dataclasses import dataclass
from typing import Optional, Union

from langgraph.prebuilt import ToolRuntime
from langgraph.runtime import Runtime

from azure.ai.agentserver.core import AgentRunContext
from .tools._context import FoundryToolContext


@dataclass
class LanggraphRunContext:
    agent_run: AgentRunContext

    tools: FoundryToolContext

    @staticmethod
    def from_runtime(runtime: Union[Runtime, ToolRuntime]) -> Optional["LanggraphRunContext"]:
        context = runtime.context
        if isinstance(context, LanggraphRunContext):
            return context
        return None
