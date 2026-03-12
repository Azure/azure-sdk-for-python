# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Internal server context shared across protocol implementations."""
from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ._tracing import TracingHelper


@dataclasses.dataclass(frozen=True)
class _ServerContext:
    """Shared server state passed to protocol implementations.

    Internal — not part of the public API.  Each protocol receives this
    at construction time so it can access tracing, error handling, and
    timeout configuration without coupling to the ``AgentServer`` class.
    """

    tracing: Optional[TracingHelper]
    debug_errors: bool
    request_timeout: int
