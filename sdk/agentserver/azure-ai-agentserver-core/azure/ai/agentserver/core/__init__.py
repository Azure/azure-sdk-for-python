# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Azure AI AgentServerHost core framework.

Provides the :class:`AgentServerHost` base class and shared utilities for
building Azure AI Hosted Agent containers.

Public API::

    from azure.ai.agentserver.core import (
        AgentServerHost,
        Constants,
        create_error_response,
    )
"""
__path__ = __import__("pkgutil").extend_path(__path__, __name__)

from ._base import AgentServerHost
from ._constants import Constants
from ._errors import create_error_response
from ._version import VERSION

__all__ = [
    "AgentServerHost",
    "Constants",
    "create_error_response",
]
__version__ = VERSION
