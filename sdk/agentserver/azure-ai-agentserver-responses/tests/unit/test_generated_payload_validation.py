"""Unit tests for generated payload validator integration in parse flow."""

from __future__ import annotations

import types
from pathlib import Path

import pytest

from azure.ai.agentserver.responses.hosting import _validation
from azure.ai.agentserver.responses.hosting._validation import parse_create_response
from azure.ai.agentserver.responses.models import RequestValidationError


class _StubCreateResponse:
    def __init__(self, payload: object) -> None:
        data = payload if isinstance(payload, dict) else {}
        self.model = data.get("model")


def _stub_validate_create_response(_payload: object) -> list[dict[str, str]]:
    return [{"path": "$.model", "message": "Required property 'model' is missing"}]


def _pass_validate_create_response(_payload: object) -> list[dict[str, str]]:
    return []


def _load_generated_validators_module() -> types.ModuleType:
    validators_path = (
        Path(__file__).resolve().parents[2] / "azure" / "ai" / "agentserver" / "responses" / "models" / "_generated" / "_validators.py"
    )
    module = types.ModuleType("generated_validators_runtime")
    exec(validators_path.read_text(encoding="utf-8"), module.__dict__)
    return module


def test_parse_create_response_uses_generated_payload_validator(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(_validation, "CreateResponse", _StubCreateResponse)
    monkeypatch.setattr(_validation, "validate_CreateResponse", _stub_validate_create_response)

    with pytest.raises(RequestValidationError) as exc_info:
        parse_create_response({})

    error = exc_info.value
    assert error.code == "invalid_request"
    assert error.debug_info is not None
    assert error.debug_info.get("errors") == [{"path": "$.model", "message": "Required property 'model' is missing"}]


def test_parse_create_response_allows_valid_payload_when_generated_checks_pass(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(_validation, "CreateResponse", _StubCreateResponse)
    monkeypatch.setattr(_validation, "validate_CreateResponse", _pass_validate_create_response)

    parsed = parse_create_response({"model": "gpt-4o"})
    assert parsed.model == "gpt-4o"


def test_parse_create_response_without_generated_module_still_parses(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(_validation, "CreateResponse", _StubCreateResponse)
    monkeypatch.setattr(_validation, "validate_CreateResponse", _pass_validate_create_response)
    parsed = parse_create_response({"model": "gpt-4o"})
    assert parsed.model == "gpt-4o"


def test_generated_create_response_validator_accepts_string_input() -> None:
    validators = _load_generated_validators_module()
    errors = validators.validate_CreateResponse(
        {
            "model": "gpt-4o",
            "input": "hello world",
        }
    )
    assert errors == []


def test_generated_create_response_validator_accepts_array_input_items() -> None:
    validators = _load_generated_validators_module()
    errors = validators.validate_CreateResponse(
        {
            "model": "gpt-4o",
            "input": [{"type": "message"}],
        }
    )
    assert errors == []


def test_generated_create_response_validator_rejects_non_string_non_array_input() -> None:
    validators = _load_generated_validators_module()
    errors = validators.validate_CreateResponse(
        {
            "model": "gpt-4o",
            "input": 123,
        }
    )
    assert any(e["path"] == "$.input" and "Expected one of: string, array" in e["message"] for e in errors)


def test_generated_create_response_validator_rejects_non_object_input_item() -> None:
    validators = _load_generated_validators_module()
    errors = validators.validate_CreateResponse(
        {
            "model": "gpt-4o",
            "input": [123],
        }
    )
    assert any(e["path"] == "$.input" and "Expected one of: string, array" in e["message"] for e in errors)


def test_generated_create_response_validator_rejects_input_item_missing_type() -> None:
    validators = _load_generated_validators_module()
    errors = validators.validate_CreateResponse(
        {
            "model": "gpt-4o",
            "input": [{}],
        }
    )
    assert any(e["path"] == "$.input" and "Expected one of: string, array" in e["message"] for e in errors)


def test_generated_create_response_validator_rejects_input_item_type_with_wrong_primitive() -> None:
    validators = _load_generated_validators_module()
    errors = validators.validate_CreateResponse(
        {
            "model": "gpt-4o",
            "input": [{"type": 1}],
        }
    )
    assert any(e["path"] == "$.input" and "Expected one of: string, array" in e["message"] for e in errors)


@pytest.mark.parametrize(
    "item_type",
    [
        "message",
        "item_reference",
        "function_call_output",
        "computer_call_output",
        "apply_patch_call_output",
    ],
)
def test_generated_create_response_validator_accepts_multiple_input_item_types(item_type: str) -> None:
    validators = _load_generated_validators_module()
    errors = validators.validate_CreateResponse(
        {
            "model": "gpt-4o",
            "input": [{"type": item_type}],
        }
    )
    assert errors == []


def test_generated_create_response_validator_accepts_mixed_input_item_types() -> None:
    validators = _load_generated_validators_module()
    errors = validators.validate_CreateResponse(
        {
            "model": "gpt-4o",
            "input": [
                {"type": "message"},
                {"type": "item_reference"},
                {"type": "function_call_output"},
            ],
        }
    )
    assert errors == []
