# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
__path__ = __import__("pkgutil").extend_path(__path__, __name__)

from ._version import VERSION
from .logger import configure as config_logging
from ._server.base import FoundryCBAgent
from ._server.common.agent_run_context import AgentRunContext

config_logging()

__all__ = ["FoundryCBAgent", "AgentRunContext"]
__version__ = VERSION
