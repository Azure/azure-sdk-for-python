# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Unit tests for generated payload validator integration in parse flow."""
# cspell:ignore progo

from __future__ import annotations

import pytest

from azure.ai.agentserver.responses.hosting._validation import parse_create_response
from azure.ai.agentserver.responses.models._validators import (
    validate_create_response_payload,
)
from azure.ai.agentserver.responses.models._errors import RequestValidationError

# ---------------------------------------------------------------------------
# parse_create_response integration tests (real validator + real model)
# ---------------------------------------------------------------------------


def test_parse_create_response_rejects_invalid_payload() -> None:
    """A payload with a wrong-typed field is caught by the generated validator."""
    with pytest.raises(RequestValidationError) as exc_info:
        parse_create_response({"model": 123})

    error = exc_info.value
    assert error.code == "invalid_request"
    assert error.details is not None
    assert any(d["param"] == "$.model" for d in error.details)


def test_parse_create_response_allows_valid_payload() -> None:
    parsed = parse_create_response({"model": "gpt-4o"})
    assert parsed["model"] == "gpt-4o"


def test_parse_create_response_rejects_non_object_body() -> None:
    with pytest.raises(RequestValidationError) as exc_info:
        parse_create_response("not-a-dict")  # type: ignore[arg-type]

    assert exc_info.value.code == "invalid_request"


# ---------------------------------------------------------------------------
# Generated validator wrapper tests
# ---------------------------------------------------------------------------


def test_generated_create_response_validator_accepts_string_input() -> None:
    errors = validate_create_response_payload({"input": "hello world"})
    assert errors == []


def test_generated_create_response_validator_accepts_array_input_items() -> None:
    # ItemMessage requires role + content in addition to type (GAP-01: type is
    # optional on input, but role/content remain required by the spec).
    errors = validate_create_response_payload({"input": [{"type": "message", "role": "user", "content": "hello"}]})
    assert errors == []


def test_generated_create_response_validator_accepts_output_text_without_logprobs() -> None:
    errors = validate_create_response_payload(
        {
            "input": [
                {
                    "type": "message",
                    "role": "assistant",
                    "content": [{"type": "output_text", "text": "hello", "annotations": []}],
                }
            ]
        }
    )
    assert errors == []


def test_generated_create_response_validator_rejects_invalid_output_text_logprobs() -> None:
    errors = validate_create_response_payload(
        {
            "input": [
                {
                    "type": "message",
                    "role": "assistant",
                    "content": [
                        {
                            "type": "output_text",
                            "text": "hello",
                            "annotations": [],
                            "logprobs": "invalid",
                        }
                    ],
                }
            ]
        }
    )

    assert any(error["path"].endswith(".logprobs") and "array" in error["message"] for error in errors)


@pytest.mark.parametrize(
    "prompt_cache_options",
    [
        {"mode": 123},
        {"mode": "invalid"},
        {"ttl": "invalid"},
    ],
)
def test_generated_create_response_validator_rejects_invalid_prompt_cache_options(
    prompt_cache_options: dict,
) -> None:
    errors = validate_create_response_payload({"prompt_cache_options": prompt_cache_options})
    assert errors


@pytest.mark.parametrize(
    "caller",
    [
        {},
        {"type": "unknown"},
        {"type": "program"},
    ],
)
def test_generated_create_response_validator_rejects_invalid_tool_call_caller(
    caller: dict,
) -> None:
    errors = validate_create_response_payload(
        {
            "input": [
                {
                    "type": "function_call",
                    "call_id": "call_123",
                    "name": "get_weather",
                    "arguments": "{}",
                    "caller": caller,
                }
            ]
        }
    )
    assert errors


@pytest.mark.parametrize(
    "caller",
    [
        {"type": "direct"},
        {"type": "program", "caller_id": "program_123"},
    ],
)
def test_generated_create_response_validator_accepts_valid_tool_call_caller(
    caller: dict,
) -> None:
    errors = validate_create_response_payload(
        {
            "input": [
                {
                    "type": "function_call",
                    "call_id": "call_123",
                    "name": "get_weather",
                    "arguments": "{}",
                    "caller": caller,
                }
            ]
        }
    )
    assert errors == []


def test_generated_create_response_validator_accepts_scale_service_tier() -> None:
    errors = validate_create_response_payload({"input": "hello world", "service_tier": "scale"})
    assert errors == []


def test_generated_create_response_validator_accepts_nullable_literal_fields() -> None:
    errors = validate_create_response_payload(
        {
            "input": "hello world",
            "service_tier": None,
            "text": {"verbosity": None},
        }
    )
    assert errors == []


def test_generated_create_response_validator_rejects_unknown_service_tier() -> None:
    errors = validate_create_response_payload({"input": "hello world", "service_tier": "unknown"})
    assert any(
        e["path"] == "$.service_tier" and "Allowed: auto, default, flex, scale, priority" in e["message"]
        for e in errors
    )


def test_generated_create_response_validator_rejects_non_string_non_array_input() -> None:
    errors = validate_create_response_payload({"input": 123})
    assert any(e["path"] == "$.input" and "Expected one of: string, array" in e["message"] for e in errors)


def test_generated_create_response_validator_rejects_non_object_input_item() -> None:
    errors = validate_create_response_payload({"input": [123]})
    assert any(e["path"] == "$.input[0]" and "Expected object" in e["message"] for e in errors)


def test_generated_create_response_validator_rejects_input_item_missing_required_fields() -> None:
    errors = validate_create_response_payload({"input": [{}]})
    assert any(e["path"] == "$.input[0].role" for e in errors)


def test_generated_create_response_validator_rejects_input_item_type_with_wrong_primitive() -> None:
    errors = validate_create_response_payload({"input": [{"type": 1}]})
    assert any(e["path"] == "$.input[0].type" for e in errors)


@pytest.mark.parametrize(
    "payload,path",
    [
        ({"include": ["not_an_include"]}, "$.include[0]"),
        ({"input": [{"type": "not_an_item"}]}, "$.input[0].type"),
        ({"tool_choice": {"type": "not_a_tool_choice"}}, "$.tool_choice.type"),
        ({"text": {"format": {"type": "not_a_format"}}}, "$.text.format.type"),
    ],
)
def test_generated_create_response_validator_rejects_invalid_literal_values(payload: dict, path: str) -> None:
    errors = validate_create_response_payload(payload)
    assert any(e["path"] == path for e in errors)


# Minimal valid payloads per item type, satisfying each schema's required fields.
_VALID_INPUT_ITEMS: dict[str, dict] = {
    "message": {"type": "message", "role": "user", "content": "hello"},
    "item_reference": {"type": "item_reference", "id": "ref_123"},
    "function_call_output": {
        "type": "function_call_output",
        "call_id": "call_123",
        "output": "result",
    },
    "computer_call_output": {
        "type": "computer_call_output",
        "call_id": "call_123",
        "output": {"type": "computer_screenshot"},
    },
    "apply_patch_call_output": {
        "type": "apply_patch_call_output",
        "call_id": "call_123",
        "status": "completed",
    },
}


@pytest.mark.parametrize("item_type", list(_VALID_INPUT_ITEMS))
def test_generated_create_response_validator_accepts_multiple_input_item_types(
    item_type: str,
) -> None:
    errors = validate_create_response_payload({"input": [_VALID_INPUT_ITEMS[item_type]]})
    assert errors == []


def test_generated_create_response_validator_accepts_mixed_input_item_types() -> None:
    errors = validate_create_response_payload(
        {
            "input": [
                _VALID_INPUT_ITEMS["message"],
                _VALID_INPUT_ITEMS["item_reference"],
                _VALID_INPUT_ITEMS["function_call_output"],
            ]
        }
    )
    assert errors == []


@pytest.mark.parametrize(
    "item",
    [
        {
            "type": "program",
            "id": "prog_123",
            "call_id": "call_123",
            "code": "return 1;",
            "fingerprint": "fp_123",
        },
        {
            "type": "program_output",
            "id": "progo_123",
            "call_id": "call_123",
            "result": "1",
            "status": "completed",
        },
    ],
)
def test_generated_create_response_validator_accepts_program_items(
    item: dict[str, str],
) -> None:
    assert validate_create_response_payload({"input": [item]}) == []


@pytest.mark.parametrize(
    "item",
    [
        {
            "type": "program",
            "id": "prog_123",
            "call_id": "call_123",
            "code": "return 1;",
        },
        {
            "type": "program_output",
            "id": "progo_123",
            "call_id": "call_123",
            "status": "completed",
        },
    ],
)
def test_generated_create_response_validator_rejects_incomplete_program_items(
    item: dict[str, str],
) -> None:
    assert validate_create_response_payload({"input": [item]})
