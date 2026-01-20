# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from dataclasses import dataclass

from langgraph.runtime import get_runtime
from azure.ai.agentserver.core import AgentRunContext

from .tools._context import FoundryToolContext


@dataclass
class LanggraphRunContext:
    agent_run: AgentRunContext

    tools: FoundryToolContext

    @classmethod
    def get_current(cls) -> "LanggraphRunContext":
        lg_runtime = get_runtime(cls)
        return lg_runtime.context
