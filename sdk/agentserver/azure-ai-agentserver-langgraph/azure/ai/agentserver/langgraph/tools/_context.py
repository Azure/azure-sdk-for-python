# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from dataclasses import dataclass, field

from langgraph.runtime import get_runtime

from azure.ai.agentserver.langgraph.tools._resolver import ResolvedTools


@dataclass
class FoundryToolContext:
    """Context for tool resolution.

    :param resolved_tools: The resolved tools of all registered foundry tools.
    :type resolved_tools: ResolvedTools
    """
    resolved_tools: ResolvedTools = field(default_factory=lambda: ResolvedTools([]))

    @classmethod
    def get_current(cls) -> "FoundryToolContext":
        lg_runtime = get_runtime(cls)
        return lg_runtime.context
