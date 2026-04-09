# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Event streaming, SSE encoding, and output item builders."""

from ._builders import (
    OutputItemBuilder,
    OutputItemCodeInterpreterCallBuilder,
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
from ._helpers import (
    EVENT_TYPE,
)
from ._sse import encode_keep_alive_comment, encode_sse_event
from ._state_machine import (
    EventStreamValidator,
    LifecycleStateMachineError,
    normalize_lifecycle_events,
    validate_response_event_stream,
)

__all__ = [
    "EVENT_TYPE",
    "EventStreamValidator",
    "LifecycleStateMachineError",
    "encode_sse_event",
    "encode_keep_alive_comment",
    "normalize_lifecycle_events",
    "validate_response_event_stream",
    # Builders
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
    "TextContentBuilder",
]
