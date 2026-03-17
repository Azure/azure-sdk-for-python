"""Unit tests for generated payload validator integration in parse flow."""

from __future__ import annotations

import types

import pytest

from azure.ai.responses.server import _validation
from azure.ai.responses.server._validation import RequestValidationError, parse_create_response


class _StubCreateResponse:
    def __init__(self, payload: object) -> None:
        data = payload if isinstance(payload, dict) else {}
        self.model = data.get("model")


class _StubGeneratedValidators:
    @staticmethod
    def validate_CreateResponse(_payload: object) -> list[dict[str, str]]:
        return [{"path": "$.model", "message": "Required property 'model' is missing"}]


class _PassGeneratedValidators:
    @staticmethod
    def validate_CreateResponse(_payload: object) -> list[dict[str, str]]:
        return []


def test_parse_create_response_uses_generated_payload_validator(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(_validation, "CreateResponse", _StubCreateResponse)
    monkeypatch.setattr(_validation, "_generated_validators", _StubGeneratedValidators)

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
    monkeypatch.setattr(_validation, "_generated_validators", _PassGeneratedValidators)

    parsed = parse_create_response({"model": "gpt-4o"})
    assert parsed.model == "gpt-4o"


def test_parse_create_response_without_generated_module_still_parses() -> None:
    module = _validation._generated_validators
    original_create_response = _validation.CreateResponse
    try:
        _validation.CreateResponse = _StubCreateResponse
        _validation._generated_validators = None
        parsed = parse_create_response({"model": "gpt-4o"})
        assert parsed.model == "gpt-4o"
    finally:
        _validation.CreateResponse = original_create_response
        _validation._generated_validators = module
