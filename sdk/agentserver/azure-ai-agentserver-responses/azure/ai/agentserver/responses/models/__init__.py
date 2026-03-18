"""Canonical non-generated model types for the response server."""

from .errors import RequestValidationError
try:
    from .runtime import (
        ResponseExecution,
        ResponseModeFlags,
        ResponseSession,
        ResponseStatus,
        StreamEventRecord,
        StreamReplayState,
        TerminalResponseStatus,
    )
except Exception:  # pragma: no cover - allows importing lightweight model errors in isolated test envs.
    pass

__all__ = [
    "RequestValidationError",
]

if "ResponseExecution" in globals():
    __all__.extend(
        [
            "ResponseExecution",
            "ResponseModeFlags",
            "ResponseSession",
            "ResponseStatus",
            "StreamEventRecord",
            "StreamReplayState",
            "TerminalResponseStatus",
        ]
    )
