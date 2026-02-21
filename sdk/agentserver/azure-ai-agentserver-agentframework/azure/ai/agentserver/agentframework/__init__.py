# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
__path__ = __import__("pkgutil").extend_path(__path__, __name__)

from ._version import VERSION


def from_agent_framework(agent):
    from .agent_framework import AgentFrameworkCBAgent

    return AgentFrameworkCBAgent(agent)


__all__ = ["from_agent_framework"]
__version__ = VERSION
