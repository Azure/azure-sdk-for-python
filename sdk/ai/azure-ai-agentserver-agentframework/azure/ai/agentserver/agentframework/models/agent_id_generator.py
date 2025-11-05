"""Helper utilities for constructing AgentId model instances.

Centralizes logic for safely building a `models.AgentId` from a request agent
object. We intentionally do not allow overriding the generated model's fixed
`type` literal ("agent_id"). If the provided object lacks a name, `None` is
returned so callers can decide how to handle absence.
"""

from __future__ import annotations

from typing import Optional

from azure.ai.agentserver.core import AgentRunContext
from azure.ai.agentserver.core.models import projects


class AgentIdGenerator:
    @staticmethod
    def generate(context: AgentRunContext) -> Optional[projects.AgentId]:
        """Builds an AgentId model from the request agent object in the provided context."""
        agent = context.request.get("agent")
        if not agent:
            return None

        agent_id = projects.AgentId(
            {
                "type": agent.type,
                "name": agent.name,
                "version": agent.version,
            }
        )

        return agent_id
