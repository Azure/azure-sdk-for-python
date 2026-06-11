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
        configure_observability,
        create_error_response,
        detach_context,
        end_span,
        flush_spans,
        record_error,
        set_current_span,
        trace_stream,
    )
"""
__path__ = __import__("pkgutil").extend_path(__path__, __name__)

from ._base import AgentServerHost
from ._config import AgentConfig
from ._errors import create_error_response
from ._middleware import InboundRequestLoggingMiddleware
from ._request_id import RequestIdMiddleware
from ._server_version import build_server_version
from ._tracing import (
    configure_observability,
    detach_context,
    end_span,
    flush_spans,
    record_error,
    set_current_span,
    trace_stream,
)
from ._version import VERSION

__all__ = [
    "AgentConfig",
    "AgentServerHost",
    "InboundRequestLoggingMiddleware",
    "RequestIdMiddleware",
    "build_server_version",
    "configure_observability",
    "create_error_response",
    "detach_context",
    "end_span",
    "flush_spans",
    "record_error",
    "set_current_span",
    "trace_stream",
]
__version__ = VERSION
