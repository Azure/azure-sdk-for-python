# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Unit tests for validation helpers."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from azure.ai.agentserver.responses.hosting._validation import parse_create_response, to_api_error_response, validate_create_response
from azure.ai.agentserver.responses.models import RequestValidationError


@dataclass
class _FakeCreateRequest:
    store: bool | None = True
    background: bool = False
    stream: bool | None = False
    stream_options: object | None = None
    model: str | None = "gpt-4o-mini"


def test_validation__non_object_payload_returns_invalid_request() -> None:
    with pytest.raises(RequestValidationError) as exc_info:
        parse_create_response(["not", "an", "object"])  # type: ignore[arg-type]

    assert exc_info.value.code == "invalid_request"


def test_validation__cross_field_stream_options_requires_stream_flag() -> None:
    request = _FakeCreateRequest(stream=False, stream_options={"foo": "bar"})

    with pytest.raises(RequestValidationError) as exc_info:
        validate_create_response(request)  # type: ignore[arg-type]

    assert exc_info.value.param == "stream"


def test_validation__unexpected_exception_maps_to_bad_request_category() -> None:
    error = ValueError("bad payload")
    envelope = to_api_error_response(error)

    assert envelope.error.type == "invalid_request_error"
