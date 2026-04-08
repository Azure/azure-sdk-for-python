# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Azure AI AgentServerHost core framework.

Provides the :class:`AgentServerHost` base class and shared utilities for
building Azure AI Hosted Agent containers.

Public API::

    from azure.ai.agentserver.core import (
        AgentConfig,
        AgentServerHost,
        create_error_response,
        end_span,
        flush_spans,
        record_error,
        trace_stream,
    )
"""
__path__ = __import__("pkgutil").extend_path(__path__, __name__)

from ._base import AgentServerHost
from ._config import AgentConfig
from ._errors import create_error_response
from ._tracing import end_span, flush_spans, record_error, trace_stream
from ._version import VERSION

__all__ = [
    "AgentConfig",
    "AgentServerHost",
    "create_error_response",
    "end_span",
    "flush_spans",
    "record_error",
    "trace_stream",
]
__version__ = VERSION
