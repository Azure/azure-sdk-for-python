# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""HTTP hosting, routing, and request orchestration for the Responses server."""

from ._observability import (
    CreateSpan,
    CreateSpanHook,
    InMemoryCreateSpanHook,
    RecordedSpan,
    build_create_span_tags,
    build_platform_server_header,
    start_create_span,
)
from ._routing import ResponsesAgentServerHost
from ._validation import (
    build_api_error_response,
    build_invalid_mode_error_response,
    build_not_found_error_response,
    parse_and_validate_create_response,
    parse_create_response,
    to_api_error_response,
    validate_create_response,
)

__all__ = [
    "ResponsesAgentServerHost",
    "CreateSpan",
    "CreateSpanHook",
    "InMemoryCreateSpanHook",
    "RecordedSpan",
    "build_api_error_response",
    "build_create_span_tags",
    "build_invalid_mode_error_response",
    "build_not_found_error_response",
    "build_platform_server_header",
    "parse_and_validate_create_response",
    "parse_create_response",
    "start_create_span",
    "to_api_error_response",
    "validate_create_response",
]
