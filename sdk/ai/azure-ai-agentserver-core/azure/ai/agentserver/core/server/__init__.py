__path__ = __import__("pkgutil").extend_path(__path__, __name__)

from typing import TYPE_CHECKING, Optional

from .base import FoundryCBAgent

if TYPE_CHECKING:  # pragma: no cover
    from .langgraph_models import LanggraphStateConverter


def from_agent_framework(agent):
    from .agent_framework import AgentFrameworkCBAgent

    return AgentFrameworkCBAgent(agent)


def from_langgraph(agent, state_converter: Optional["LanggraphStateConverter"] = None):
    from .langgraph import LangGraphAdapter

    return LangGraphAdapter(agent, state_converter=state_converter)


__all__ = ["FoundryCBAgent", "from_agent_framework", "from_langgraph"]
