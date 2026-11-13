# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""A2A protocol host for Azure AI Hosted Agents."""

__path__ = __import__("pkgutil").extend_path(__path__, __name__)

from ._host import A2AAgentServerHost
from ._foundry_task_store import FoundryTaskStore
from ._version import VERSION

__all__ = ["A2AAgentServerHost", "FoundryTaskStore"]
__version__ = VERSION
