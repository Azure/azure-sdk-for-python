# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Public API surface for the Azure AI Agent Server core framework."""
__path__ = __import__("pkgutil").extend_path(__path__, __name__)

from ._base import AgentServerHost
from ._config import AgentConfig
from ._errors import create_error_response
from ._middleware import InboundRequestLoggingMiddleware
from ._request_context import (
    FoundryAgentRequestContext,
    get_request_context,
    reset_request_context,
    set_request_context,
)
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
    "FoundryAgentRequestContext",
    "RequestIdMiddleware",
    "build_server_version",
    "configure_observability",
    "create_error_response",
    "detach_context",
    "end_span",
    "flush_spans",
    "get_request_context",
    "record_error",
    "reset_request_context",
    "set_current_span",
    "set_request_context",
    "trace_stream",
]
__version__ = VERSION
