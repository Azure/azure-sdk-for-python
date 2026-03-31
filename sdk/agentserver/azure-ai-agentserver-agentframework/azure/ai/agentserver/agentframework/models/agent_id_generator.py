# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Helper for constructing AgentId model instances from request context."""

from __future__ import annotations

from typing import Optional

from azure.ai.agentserver.core import AgentRunContext
from azure.ai.agentserver.core.models import projects


def generate_agent_id(context: AgentRunContext) -> Optional[projects.AgentId]:
    """Build an AgentId model from the request agent object in the provided context.

    :param context: The agent run context containing the request.
    :type context: AgentRunContext
    """
    agent = context.request.get("agent")
    if not agent:
        return None

    return projects.AgentId(
        {
            "type": agent.type,
            "name": agent.name,
            "version": agent.version,
        }
    )
