# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Unit tests for generated payload validator integration in parse flow."""

from __future__ import annotations

import pytest

from azure.ai.agentserver.responses.hosting._validation import parse_create_response
from azure.ai.agentserver.responses.models._generated._validators import validate_CreateResponse
from azure.ai.agentserver.responses.models.errors import RequestValidationError

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
    assert parsed.model == "gpt-4o"


def test_parse_create_response_rejects_non_object_body() -> None:
    with pytest.raises(RequestValidationError) as exc_info:
        parse_create_response("not-a-dict")  # type: ignore[arg-type]

    assert exc_info.value.code == "invalid_request"


# ---------------------------------------------------------------------------
# Generated validator tests (validate_CreateResponse directly)
# ---------------------------------------------------------------------------


def test_generated_create_response_validator_accepts_string_input() -> None:
    errors = validate_CreateResponse({"input": "hello world"})
    assert errors == []


def test_generated_create_response_validator_accepts_array_input_items() -> None:
    # ItemMessage requires role + content in addition to type (GAP-01: type is
    # optional on input, but role/content remain required by the spec).
    errors = validate_CreateResponse({"input": [{"type": "message", "role": "user", "content": "hello"}]})
    assert errors == []


def test_generated_create_response_validator_rejects_non_string_non_array_input() -> None:
    errors = validate_CreateResponse({"input": 123})
    assert any(e["path"] == "$.input" and "Expected one of: string, array" in e["message"] for e in errors)


def test_generated_create_response_validator_rejects_non_object_input_item() -> None:
    errors = validate_CreateResponse({"input": [123]})
    assert any(e["path"] == "$.input" and "Expected one of: string, array" in e["message"] for e in errors)


def test_generated_create_response_validator_rejects_input_item_missing_type() -> None:
    errors = validate_CreateResponse({"input": [{}]})
    assert any(e["path"] == "$.input" and "Expected one of: string, array" in e["message"] for e in errors)


def test_generated_create_response_validator_rejects_input_item_type_with_wrong_primitive() -> None:
    errors = validate_CreateResponse({"input": [{"type": 1}]})
    assert any(e["path"] == "$.input" and "Expected one of: string, array" in e["message"] for e in errors)


# Minimal valid payloads per item type, satisfying each schema's required fields.
_VALID_INPUT_ITEMS: dict[str, dict] = {
    "message": {"type": "message", "role": "user", "content": "hello"},
    "item_reference": {"type": "item_reference", "id": "ref_123"},
    "function_call_output": {"type": "function_call_output", "call_id": "call_123", "output": "result"},
    "computer_call_output": {
        "type": "computer_call_output",
        "call_id": "call_123",
        "output": {"type": "computer_screenshot"},
    },
    "apply_patch_call_output": {"type": "apply_patch_call_output", "call_id": "call_123", "status": "completed"},
}


@pytest.mark.parametrize("item_type", list(_VALID_INPUT_ITEMS))
def test_generated_create_response_validator_accepts_multiple_input_item_types(item_type: str) -> None:
    errors = validate_CreateResponse({"input": [_VALID_INPUT_ITEMS[item_type]]})
    assert errors == []


def test_generated_create_response_validator_accepts_mixed_input_item_types() -> None:
    errors = validate_CreateResponse(
        {
            "input": [
                _VALID_INPUT_ITEMS["message"],
                _VALID_INPUT_ITEMS["item_reference"],
                _VALID_INPUT_ITEMS["function_call_output"],
            ]
        }
    )
    assert errors == []
