# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Event streaming, SSE encoding, and output item builders."""

from ._helpers import (
    EVENT_TYPE,
)
from ._sse import encode_keep_alive_comment, encode_sse_event
from ._state_machine import (
    normalize_lifecycle_events,
    validate_response_event_stream,
)

__all__ = [
    "EVENT_TYPE",
    "encode_sse_event",
    "encode_keep_alive_comment",
    "normalize_lifecycle_events",
    "validate_response_event_stream",
]
