# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Azure AI AgentServer core framework.

Provides the :class:`AgentServer` host and shared utilities for
building Azure AI Hosted Agent containers.

Public API::

    from azure.ai.agentserver.core import (
        AgentLogger,
        AgentServer,
        Constants,
        ErrorResponse,
        TracingHelper,
    )
"""
__path__ = __import__("pkgutil").extend_path(__path__, __name__)

from ._base import AgentServer
from ._constants import Constants
from ._errors import ErrorResponse
from ._logger import AgentLogger
from ._tracing import TracingHelper
from ._version import VERSION

__all__ = [
    "AgentLogger",
    "AgentServer",
    "Constants",
    "ErrorResponse",
    "TracingHelper",
]
__version__ = VERSION
