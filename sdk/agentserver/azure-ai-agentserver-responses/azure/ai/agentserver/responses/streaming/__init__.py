# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Event streaming, SSE encoding, and output item builders."""

from ._builders import (
    OutputItemCodeInterpreterCallBuilder,
    OutputItemBuilder,
    OutputItemCustomToolCallBuilder,
    OutputItemFileSearchCallBuilder,
    OutputItemFunctionCallBuilder,
    OutputItemFunctionCallOutputBuilder,
    OutputItemImageGenCallBuilder,
    OutputItemMcpCallBuilder,
    OutputItemMcpListToolsBuilder,
    OutputItemMessageBuilder,
    OutputItemReasoningItemBuilder,
    OutputItemWebSearchCallBuilder,
    ReasoningSummaryPartBuilder,
    RefusalContentBuilder,
    TextContentBuilder,
)
from ._event_stream import ResponseEventStream
from ._helpers import (
    EVENT_TYPE,
    _apply_stream_event_defaults,
    _build_events,
    _coerce_handler_event,
    _encode_sse,
    _extract_response_snapshot_from_events,
)
from ._sse import encode_sse_event, encode_sse_payload, encode_keep_alive_comment
from ._state_machine import (
    LifecycleStateMachineError,
    normalize_lifecycle_events,
    validate_response_event_stream,
)

__all__ = [
    "EVENT_TYPE",
    "OutputItemBuilder",
    "OutputItemCodeInterpreterCallBuilder",
    "OutputItemCustomToolCallBuilder",
    "OutputItemFileSearchCallBuilder",
    "OutputItemFunctionCallBuilder",
    "OutputItemFunctionCallOutputBuilder",
    "OutputItemImageGenCallBuilder",
    "OutputItemMcpCallBuilder",
    "OutputItemMcpListToolsBuilder",
    "OutputItemMessageBuilder",
    "OutputItemReasoningItemBuilder",
    "OutputItemWebSearchCallBuilder",
    "ReasoningSummaryPartBuilder",
    "RefusalContentBuilder",
    "ResponseEventStream",
    "TextContentBuilder",
    "LifecycleStateMachineError",
    "encode_sse_event",
    "encode_sse_payload",
    "encode_keep_alive_comment",
    "normalize_lifecycle_events",
    "validate_response_event_stream",
]
