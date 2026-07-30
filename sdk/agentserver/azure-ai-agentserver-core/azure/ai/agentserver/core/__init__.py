# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Azure AI AgentServerHost core framework: base :class:`AgentServerHost` and shared utilities for Hosted Agents."""

# NOTE: keep this module docstring on a SINGLE line. The apiview-stub-generator
# (apistub, pinned via eng/apiview_reqs.txt) namespace detector mis-parses a
# multi-line module docstring in a package __init__ — a closing triple-quote on
# its own line leaves its parser stuck in "docstring" mode, so the package
# namespace resolves to "" and api.md generation breaks (and can crash). The
# public API is enumerated in ``__all__`` below.

__path__ = __import__("pkgutil").extend_path(__path__, __name__)

from ._base import AgentServerHost
from ._config import AgentConfig, resolve_state_subdir
from ._errors import create_error_response
from ._middleware import InboundRequestLoggingMiddleware
from ._request_context import (
    FoundryAgentRequestContext,
    get_request_context,
    reset_request_context,
    set_request_context,
)
from ._request_id import RequestIdMiddleware, read_request_id
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
from ._types import MiddlewareFactory, StreamContent
from ._version import VERSION

__all__ = [
    "AgentConfig",
    "AgentServerHost",
    "MiddlewareFactory",
    "StreamContent",
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
    "read_request_id",
    "reset_request_context",
    "resolve_state_subdir",
    "set_current_span",
    "set_request_context",
    "trace_stream",
]
__version__ = VERSION
