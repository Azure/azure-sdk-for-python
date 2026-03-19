"""Compatibility module for runtime response server models.

Canonical non-generated type definitions now live in ``azure.ai.agentserver.responses.models``.
"""

from .models.runtime import (
    ResponseExecution,
    ResponseModeFlags,
    ResponseSession,
    ResponseStatus,
    StreamEventRecord,
    StreamReplayState,
    TerminalResponseStatus,
)

__all__ = [
    "ResponseExecution",
    "ResponseModeFlags",
    "ResponseSession",
    "ResponseStatus",
    "StreamEventRecord",
    "StreamReplayState",
    "TerminalResponseStatus",
]
