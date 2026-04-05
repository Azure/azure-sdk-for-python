# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Azure AI AgentServerHost core framework.

Provides the :class:`AgentServerHost` base class and shared utilities for
building Azure AI Hosted Agent containers.

Public API::

    from azure.ai.agentserver.core import (
        get_logger,
        AgentServerHost,
        Constants,
        create_error_response,
        TracingHelper,
    )
"""
__path__ = __import__("pkgutil").extend_path(__path__, __name__)

from ._base import AgentServerHost
from ._constants import Constants
from ._errors import create_error_response
from ._logger import get_logger
from ._tracing import TracingHelper
from ._version import VERSION

__all__ = [
    "AgentServerHost",
    "Constants",
    "create_error_response",
    "get_logger",
    "TracingHelper",
]
__version__ = VERSION
