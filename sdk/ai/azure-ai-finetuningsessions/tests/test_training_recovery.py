# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Trainer interruption must offer CFT without replaying terminal work."""

from types import SimpleNamespace

import pytest

from azure.ai.finetuningsessions import EngineDeadError, TrainingEngineError
from azure.ai.finetuningsessions._exceptions import (
    RequestRetryableError,
    _classify_http_error,
    _classify_poll_failure,
)


def _assert_recovery_guidance(exc: TrainingEngineError) -> None:
    assert "continual fine-tuning (CFT)" in exc.message
    assert "new session" in exc.message
    assert "completed training checkpoint" in exc.message
    assert "no training checkpoint" in exc.message
    assert "Do not retry" in exc.message
    assert "weights are lost" not in str(exc).lower()
    assert "weights lost" not in str(exc).lower()


@pytest.mark.parametrize("status_code", [409, 500])
@pytest.mark.parametrize("nested", [False, True])
def test_http_engine_dead_offers_cft(status_code: int, nested: bool) -> None:
    detail = {
        "reason": "engine_dead",
        "error_code": "engine_dead",
        "message": "Model failed because its engine died. LoRA weights are lost.",
        "debug_ref": "support-ref",
    }
    body = {"detail": detail} if nested else detail
    exc = _classify_http_error(status_code, body, session_id="session_12345678")

    assert isinstance(exc, TrainingEngineError)
    assert isinstance(exc, EngineDeadError)
    assert exc.error_code == "engine_dead"
    assert exc.session_id == "session_12345678"
    assert exc.debug_ref == "support-ref"
    _assert_recovery_guidance(exc)


@pytest.mark.parametrize("status_code", [409, 500])
def test_legacy_string_engine_dead_offers_cft(status_code: int) -> None:
    exc = _classify_http_error(status_code, {"detail": "Engine died, LoRA weights lost"})
    assert isinstance(exc, TrainingEngineError)
    _assert_recovery_guidance(exc)


@pytest.mark.parametrize("code_field", ["error_code", "code"])
@pytest.mark.parametrize("message_field", ["message", "error_message"])
@pytest.mark.parametrize("nested", [False, True])
def test_http_engine_oom_preserves_exact_message(code_field: str, message_field: str, nested: bool) -> None:
    message = (
        "The engine ran out of GPU memory while processing this request. Try a smaller batch or shorter sequences."
    )
    detail = {code_field: "engine_oom", message_field: message, "debug_ref": "oom-ref"}
    body = {"detail": detail} if nested else detail
    response = SimpleNamespace(
        status_code=500,
        reason="Internal Server Error",
        headers={},
        json=lambda: body,
        text=lambda: str(body),
    )
    exc = _classify_http_error(500, body, response=response, session_id="session_12345678")

    # Keep the HTTP compatibility exception type; OOM does not imply engine death.
    assert type(exc) is TrainingEngineError
    assert exc.message == message
    assert str(exc) == message
    assert exc.args == (message,)
    assert exc.error_code == "engine_oom"
    assert exc.session_id == "session_12345678"
    assert exc.debug_ref == "oom-ref"
    assert exc.response is response
    assert exc.status_code == 500


@pytest.mark.parametrize("error_code", ["engine_oom", "engine_timeout", "model_not_found", None])
def test_nonterminal_engine_error_preserves_message(error_code: str | None) -> None:
    message = "The engine did not complete this request. Contact support for details."
    exc = TrainingEngineError(message, error_code=error_code)

    assert exc.message == message
    assert str(exc) == message


@pytest.mark.parametrize("error_code", ["engine_dead", "worker_crashed"])
def test_terminal_engine_error_still_offers_cft(error_code: str) -> None:
    exc = TrainingEngineError("Session unavailable.", error_code=error_code)
    _assert_recovery_guidance(exc)


@pytest.mark.parametrize("error_code", ["engine_dead", "worker_crashed"])
def test_terminal_recovery_message_is_not_duplicated(error_code: str) -> None:
    message = "You can resume using continual fine-tuning (CFT) in a new session from a completed training checkpoint."
    exc = TrainingEngineError(message, error_code=error_code)

    assert exc.message == message
    assert str(exc) == message


@pytest.mark.parametrize("message", ["Engine died.", "The model's engine has died."])
def test_legacy_uncoded_engine_death_still_offers_cft(message: str) -> None:
    exc = _classify_http_error(500, {"detail": message})
    assert isinstance(exc, TrainingEngineError)
    _assert_recovery_guidance(exc)


@pytest.mark.parametrize("code_field", ["error_code", "code"])
@pytest.mark.parametrize("retry_flag", [None, False, True])
def test_poll_engine_dead_is_terminal_even_with_retry_flag(code_field: str, retry_flag: bool | None) -> None:
    exc = _classify_poll_failure(
        {
            "status": "failed",
            "error": "Engine died, LoRA weights lost",
            code_field: "engine_dead",
            "debug_ref": "support-ref",
            "should_retry": retry_flag,
            "retry_after_sec": 1,
        },
        session_id="session_12345678",
    )

    assert isinstance(exc, TrainingEngineError)
    assert not isinstance(exc, RequestRetryableError)
    assert exc.error_code == "engine_dead"
    assert exc.session_id == "session_12345678"
    assert exc.debug_ref == "support-ref"
    _assert_recovery_guidance(exc)


def test_exception_display_does_not_append_legacy_response_body() -> None:
    body = {"detail": "Engine died, LoRA weights lost"}
    response = SimpleNamespace(
        status_code=500,
        reason="Internal Server Error",
        headers={},
        json=lambda: body,
        text=lambda: '{"detail": "Engine died, LoRA weights lost"}',
    )
    exc = _classify_http_error(500, body, response=response)

    assert isinstance(exc, TrainingEngineError)
    assert exc.response is response
    assert exc.status_code == 500
    assert str(exc) == exc.message
    _assert_recovery_guidance(exc)


def test_retryable_inference_contract_is_unchanged() -> None:
    exc = _classify_poll_failure(
        {"status": "failed", "error": "Try again", "error_code": "request_timeout", "should_retry": True}
    )
    assert isinstance(exc, RequestRetryableError)
