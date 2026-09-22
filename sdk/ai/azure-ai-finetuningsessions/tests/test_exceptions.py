# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Tests for typed SDK exceptions.

Verifies that:
1. Exception classes have the right inheritance hierarchy.
2. ``_classify_http_error`` correctly maps HTTP responses to typed exceptions.
3. ``_classify_poll_failure`` correctly maps poll envelope failures to typed exceptions.
4. Unknown errors fall through (return None) so generic handling still applies.
"""
from __future__ import annotations

import pytest
from azure.ai.finetuningsessions._exceptions import (
    BatchTooLargeError,
    ContentionError,
    FineTuningSessionsError,
    NoCapacityError,
    OperationResultUnavailableError,
    RequestRetryableError,
    RequestValidationError,
    TrainingEngineError,
    _classify_http_error,
    _classify_poll_failure,
)
from azure.core.exceptions import HttpResponseError


# ---------------------------------------------------------------------------
# Hierarchy
# ---------------------------------------------------------------------------
class TestHierarchy:
    def test_base_inherits_from_http_response_error(self) -> None:
        assert issubclass(FineTuningSessionsError, HttpResponseError)

    @pytest.mark.parametrize(
        "cls",
        [
            BatchTooLargeError,
            NoCapacityError,
            TrainingEngineError,
            OperationResultUnavailableError,
            RequestRetryableError,
            ContentionError,
            RequestValidationError,
        ],
    )
    def test_all_typed_inherit_from_base(self, cls: type) -> None:
        assert issubclass(cls, FineTuningSessionsError)

    @pytest.mark.parametrize(
        "cls",
        [BatchTooLargeError, NoCapacityError, TrainingEngineError, ContentionError, RequestValidationError],
    )
    def test_all_typed_catchable_as_http_response_error(self, cls: type) -> None:
        """Existing ``except HttpResponseError`` handlers still catch these."""
        assert issubclass(cls, HttpResponseError)


# ---------------------------------------------------------------------------
# _classify_http_error
# ---------------------------------------------------------------------------
class TestClassifyHttpError:
    def test_413_batch_too_large_structured(self) -> None:
        body = {
            "detail": {
                "type": "validation_error",
                "field": "forward_backward_input.data",
                "message": "Batch size (2048) exceeds the maximum allowed (1024)",
            }
        }
        exc = _classify_http_error(413, body)
        assert isinstance(exc, BatchTooLargeError)
        assert exc.max_batch_size == 1024
        assert exc.actual_batch_size == 2048
        assert "2048" in str(exc)

    def test_413_no_numbers(self) -> None:
        body = {"type": "validation_error", "field": "data", "message": "Too big"}
        exc = _classify_http_error(413, body)
        assert isinstance(exc, BatchTooLargeError)
        assert exc.max_batch_size is None

    def test_503_engine_busy_fastapi_detail_envelope(self) -> None:
        body = {
            "detail": {
                "reason": "engine_busy",
                "message": "No available engine capacity",
                "retry_after_sec": 5,
            }
        }
        exc = _classify_http_error(503, body)
        assert isinstance(exc, NoCapacityError)
        assert exc.retry_after_sec == 5.0
        assert exc.reason == "engine_busy"

    def test_503_engine_busy_flat_body_compatibility(self) -> None:
        body = {
            "reason": "engine_busy",
            "message": "No available engine capacity",
            "retry_after_sec": 5,
        }
        exc = _classify_http_error(503, body)
        assert isinstance(exc, NoCapacityError)
        assert exc.retry_after_sec == 5.0
        assert exc.reason == "engine_busy"

    def test_503_capacity_message_heuristic(self) -> None:
        body = {"detail": "No available engine capacity for model X"}
        exc = _classify_http_error(503, body)
        assert isinstance(exc, NoCapacityError)

    def test_503_generic_is_contention(self) -> None:
        body = {"reason": "throttled", "message": "slow down", "retry_after_sec": 10}
        exc = _classify_http_error(503, body)
        assert isinstance(exc, ContentionError)
        assert exc.retry_after_sec == 10.0

    def test_500_worker_crashed(self) -> None:
        body = {
            "error": "Engine crashed",
            "error_code": "worker_crashed",
            "debug_ref": "abc123def456",
        }
        exc = _classify_http_error(500, body, session_id="session_12345678")
        assert isinstance(exc, TrainingEngineError)
        assert exc.session_id == "session_12345678"
        assert exc.error_code == "worker_crashed"
        assert exc.debug_ref == "abc123def456"

    def test_500_engine_oom(self) -> None:
        body = {"error": "OOM", "error_code": "engine_oom"}
        exc = _classify_http_error(500, body)
        assert isinstance(exc, TrainingEngineError)
        assert exc.error_code == "engine_oom"

    def test_500_engine_timeout(self) -> None:
        body = {"error": "timed out", "error_code": "engine_timeout"}
        exc = _classify_http_error(500, body)
        assert isinstance(exc, TrainingEngineError)

    def test_500_heuristic_dead_engine(self) -> None:
        body = {"detail": "Engine died, LoRA weights lost"}
        exc = _classify_http_error(500, body)
        assert isinstance(exc, TrainingEngineError)

    def test_500_unknown_returns_none(self) -> None:
        body = {"error": "something unexpected"}
        exc = _classify_http_error(500, body)
        assert exc is None

    def test_409_engine_dead_structured(self) -> None:
        # Server (structured mode) returns 409 with the body nested under
        # FastAPI's "detail" key. Must classify as terminal TrainingEngineError.
        body = {
            "detail": {
                "reason": "engine_dead",
                "message": "Model 'model_x' failed because its engine died.",
                "error_code": "engine_dead",
                "failure_reason": "lease expired",
            }
        }
        exc = _classify_http_error(409, body, session_id="session_12345678")
        assert isinstance(exc, TrainingEngineError)
        assert exc.session_id == "session_12345678"
        assert exc.error_code == "engine_dead"

    def test_409_engine_dead_flat_body(self) -> None:
        body = {"reason": "engine_dead", "message": "engine died", "error_code": "engine_dead"}
        exc = _classify_http_error(409, body)
        assert isinstance(exc, TrainingEngineError)
        assert exc.error_code == "engine_dead"

    def test_409_engine_dead_message_heuristic(self) -> None:
        body = {"detail": "Model failed because its engine died. LoRA weights are lost."}
        exc = _classify_http_error(409, body)
        assert isinstance(exc, TrainingEngineError)

    def test_409_unrelated_returns_none(self) -> None:
        body = {"detail": "Some other conflict unrelated to that state"}
        exc = _classify_http_error(409, body)
        assert exc is None

    def test_500_internal_model_error_capacity_nested_detail(self) -> None:
        """Server returns 500 with type=internal_model_error and
        a capacity-related error_message. SDK should raise NoCapacityError."""
        body = {
            "detail": {
                "type": "internal_model_error",
                "error_message": "No available engine capacity for base_model 'qwen3-32b'",
                "error_code": "internal_error",
                "debug_ref": "abc123",
            }
        }
        exc = _classify_http_error(500, body)
        assert isinstance(exc, NoCapacityError)
        assert "capacity" in exc.message.lower()
        assert exc.reason == "internal_model_error"

    def test_500_capacity_in_flat_body(self) -> None:
        """Capacity message in a flat body (no nested detail)."""
        body = {
            "error_message": "No engine capacity available",
            "type": "internal_model_error",
        }
        exc = _classify_http_error(500, body)
        assert isinstance(exc, NoCapacityError)

    def test_500_capacity_in_plain_detail_string(self) -> None:
        """Capacity message as a plain string detail (legacy format)."""
        body = {"detail": "No available engine capacity for base_model 'qwen3-32b'"}
        exc = _classify_http_error(500, body)
        assert isinstance(exc, NoCapacityError)

    def test_500_capacity_case_insensitive(self) -> None:
        """Capacity detection is case-insensitive."""
        body = {"error_message": "NO ENGINE CAPACITY for model"}
        exc = _classify_http_error(500, body)
        assert isinstance(exc, NoCapacityError)

    def test_400_validation_error(self) -> None:
        body = {
            "type": "validation_error",
            "field": "forward_backward_input.data[3].model_input",
            "message": "tokens list must not be empty",
        }
        exc = _classify_http_error(400, body)
        assert isinstance(exc, RequestValidationError)
        assert exc.field == "forward_backward_input.data[3].model_input"
        assert exc.error_code == "invalid_request"

    def test_422_invalid_request_code(self) -> None:
        body = {"code": "invalid_request", "message": "bad shape"}
        exc = _classify_http_error(422, body)
        assert isinstance(exc, RequestValidationError)

    @pytest.mark.parametrize("status_code", [400, 422])
    def test_validation_error_nested_under_detail(self, status_code: int) -> None:
        body = {
            "detail": {
                "type": "validation_error",
                "field": "forward_backward_input.data[0].model_input",
                "message": "tokens list must not be empty",
                "code": "invalid_request",
                "debug_ref": "validation-ref",
            }
        }
        exc = _classify_http_error(status_code, body)
        assert isinstance(exc, RequestValidationError)
        assert exc.message == "tokens list must not be empty"
        assert exc.field == "forward_backward_input.data[0].model_input"
        assert exc.error_code == "invalid_request"
        assert exc.debug_ref == "validation-ref"

    def test_400_unknown_returns_none(self) -> None:
        body = {"type": "auth_error", "message": "unauthorized"}
        exc = _classify_http_error(400, body)
        assert exc is None

    def test_404_returns_none(self) -> None:
        exc = _classify_http_error(404, {"detail": "not found"})
        assert exc is None

    def test_none_body_413(self) -> None:
        exc = _classify_http_error(413, None)
        assert isinstance(exc, BatchTooLargeError)


# ---------------------------------------------------------------------------
# _classify_poll_failure
# ---------------------------------------------------------------------------
class TestClassifyPollFailure:
    @pytest.mark.parametrize(
        "error_code",
        [
            "request_timeout",
            "request_orphaned",
            "inference_request_rate_limited",
            "inference_unavailable",
            # Older services remain compatible with the code-agnostic retry contract.
            "request_read_timeout",
            "request_task_timeout",
            "external_inference_rate_limited",
            "external_inference_unavailable",
            "external_endpoints_exhausted",
        ],
    )
    def test_external_inference_retry_codes_use_generic_retry_contract(
        self,
        error_code: str,
    ) -> None:
        envelope = {
            "status": "failed",
            "error": "Retry the request.",
            "error_code": error_code,
            "should_retry": True,
            "retry_after_sec": 30,
            "debug_ref": "ref123",
        }

        exc = _classify_poll_failure(envelope)

        assert isinstance(exc, RequestRetryableError)
        assert exc.error_code == error_code
        assert exc.retry_after_sec == 30
        assert exc.debug_ref == "ref123"

    def test_engine_oom(self) -> None:
        envelope = {
            "status": "failed",
            "error": "The engine ran out of GPU memory",
            "error_code": "engine_oom",
            "debug_ref": "ref123",
        }
        exc = _classify_poll_failure(envelope, session_id="session_aabbccdd")
        assert isinstance(exc, BatchTooLargeError)
        assert "smaller batch" in str(exc).lower()

    def test_worker_crashed(self) -> None:
        envelope = {
            "status": "failed",
            "error": "Worker crashed",
            "error_code": "worker_crashed",
            "debug_ref": "deadbeef1234",
        }
        exc = _classify_poll_failure(envelope, session_id="session_aabbccdd")
        assert isinstance(exc, TrainingEngineError)
        assert exc.session_id == "session_aabbccdd"
        assert exc.debug_ref == "deadbeef1234"

    def test_engine_timeout(self) -> None:
        envelope = {"status": "failed", "error": "timeout", "error_code": "engine_timeout"}
        exc = _classify_poll_failure(envelope)
        assert isinstance(exc, TrainingEngineError)

    def test_engine_dead(self) -> None:
        """The orphan sweep fails requests for a lease-expired model with
        ``engine_dead``. Unmapped, that degrades to a bare RuntimeError in both
        pollers, so the caller cannot branch on the failure."""
        envelope = {
            "status": "failed",
            "error": (
                "Model 'model_abc' failed because its engine died. LoRA weights "
                "are lost. Re-create the model and reload from the last checkpoint."
            ),
            "error_code": "engine_dead",
            "debug_ref": "cafebabe9876",
        }
        exc = _classify_poll_failure(envelope, session_id="session_aabbccdd")
        assert isinstance(exc, TrainingEngineError)
        assert exc.error_code == "engine_dead"
        assert exc.session_id == "session_aabbccdd"
        assert exc.debug_ref == "cafebabe9876"

    def test_engine_dead_is_not_machine_retryable(self) -> None:
        """The weights are gone; resubmitting the same request cannot succeed.
        It must not classify as the retryable type that ``_post_and_poll``
        silently resubmits."""
        envelope = {"status": "failed", "error": "engine died", "error_code": "engine_dead"}
        exc = _classify_poll_failure(envelope)
        assert not isinstance(exc, RequestRetryableError)

    def test_engine_dead_agrees_across_the_409_and_poll_paths(self) -> None:
        """A client learns about one engine death either from a synchronous 409
        or by polling an LRO. Both must yield the same type and code, or the
        failure looks like two different events."""
        poll_exc = _classify_poll_failure(
            {"status": "failed", "error": "engine died", "error_code": "engine_dead"},
            session_id="session_aabbccdd",
        )
        http_exc = _classify_http_error(
            409,
            {"reason": "engine_dead", "message": "engine died", "error_code": "engine_dead"},
            session_id="session_aabbccdd",
        )
        assert type(poll_exc) is type(http_exc) is TrainingEngineError
        assert poll_exc.error_code == http_exc.error_code == "engine_dead"

    def test_invalid_request(self) -> None:
        envelope = {
            "status": "failed",
            "error": "The request was rejected as invalid.",
            "error_code": "invalid_request",
        }
        exc = _classify_poll_failure(envelope)
        assert isinstance(exc, RequestValidationError)
        assert exc.error_code == "invalid_request"

    def test_model_not_found(self) -> None:
        envelope = {
            "status": "failed",
            "error": "Model not loaded",
            "error_code": "model_not_found",
        }
        exc = _classify_poll_failure(envelope, session_id="session_deadbeef")
        assert isinstance(exc, TrainingEngineError)
        assert exc.error_code == "model_not_found"

    def test_completed_result_unavailable_is_non_retryable(self) -> None:
        envelope = {
            "status": "failed",
            "error": "Operation completed, but its result is unavailable.",
            "error_code": "operation_completed_result_unavailable",
            "debug_ref": "payload-ref",
            # The terminal payload-loss code must win over a malformed retry flag.
            "should_retry": True,
        }

        exc = _classify_poll_failure(envelope)

        assert isinstance(exc, OperationResultUnavailableError)
        assert exc.operation_completed is True
        assert exc.error_code == "operation_completed_result_unavailable"
        assert exc.debug_ref == "payload-ref"

    def test_failed_result_unavailable_preserves_failed_outcome(self) -> None:
        envelope = {
            "status": "failed",
            "error": "Operation failed, but its error details are unavailable.",
            "error_code": "operation_failed_result_unavailable",
            "debug_ref": "payload-ref",
        }

        exc = _classify_poll_failure(envelope)

        assert isinstance(exc, OperationResultUnavailableError)
        assert exc.operation_completed is False
        assert exc.error_code == "operation_failed_result_unavailable"
        assert exc.debug_ref == "payload-ref"

    def test_unknown_code_returns_none(self) -> None:
        envelope = {"status": "failed", "error": "something", "error_code": "new_code_2027"}
        exc = _classify_poll_failure(envelope)
        assert exc is None

    def test_internal_error_returns_none(self) -> None:
        envelope = {"status": "failed", "error": "oops", "error_code": "internal_error"}
        exc = _classify_poll_failure(envelope)
        assert exc is None


# ---------------------------------------------------------------------------
# Attributes & repr
# ---------------------------------------------------------------------------
class TestAttributes:
    def test_batch_too_large_attrs(self) -> None:
        e = BatchTooLargeError("too big", max_batch_size=1024, actual_batch_size=2048)
        assert e.max_batch_size == 1024
        assert e.actual_batch_size == 2048

    def test_no_capacity_attrs(self) -> None:
        e = NoCapacityError("busy", retry_after_sec=5.0, reason="engine_busy")
        assert e.retry_after_sec == 5.0
        assert e.reason == "engine_busy"

    def test_engine_dead_attrs(self) -> None:
        e = TrainingEngineError("dead", session_id="s1", error_code="worker_crashed", debug_ref="ref")
        assert e.session_id == "s1"
        assert e.error_code == "worker_crashed"
        assert e.debug_ref == "ref"

    def test_contention_attrs(self) -> None:
        e = ContentionError("slow", retry_after_sec=10.0, reason="throttled")
        assert e.retry_after_sec == 10.0
        assert e.reason == "throttled"

    def test_malformed_datum_attrs(self) -> None:
        e = RequestValidationError("bad", field="data[0]", error_code="invalid_request", debug_ref="x")
        assert e.field == "data[0]"
        assert e.error_code == "invalid_request"
        assert e.debug_ref == "x"


# ---------------------------------------------------------------------------
# Smart retry behavior: non-retryable vs retryable classification
# ---------------------------------------------------------------------------
class TestSmartRetryClassification:
    """Verify that the classification functions correctly identify errors
    that should NOT be retried (deterministic rejections) vs those that
    might be transient.
    """

    @pytest.mark.parametrize("status_code", [400, 413, 422])
    def test_non_retryable_codes_always_classify(self, status_code: int) -> None:
        """400/413/422 are deterministic — they should always produce a
        typed exception so the retry loop can exit immediately."""
        body = {"type": "validation_error", "field": "data", "message": "rejected"}
        exc = _classify_http_error(status_code, body)
        assert exc is not None
        assert isinstance(exc, FineTuningSessionsError)

    def test_503_classifies_for_early_exit_on_repeated(self) -> None:
        """After seeing the same 503 twice, the SDK should classify it.
        Verify the classifier produces a typed exception for a persistent 503."""
        body = {"reason": "engine_busy", "message": "No capacity", "retry_after_sec": 5}
        exc = _classify_http_error(503, body)
        assert isinstance(exc, NoCapacityError)
        assert exc.retry_after_sec == 5.0

    def test_500_with_known_code_classifies_for_early_exit(self) -> None:
        """A 500 with a known error code should produce a typed exception
        so repeated 500s don't waste retries."""
        body = {"error_code": "worker_crashed", "error": "crashed"}
        exc = _classify_http_error(500, body)
        assert isinstance(exc, TrainingEngineError)

    def test_500_without_known_code_returns_none(self) -> None:
        """A 500 with an unknown code — might be genuinely transient.
        Returns None so the retry loop continues."""
        body = {"error": "something unexpected", "error_code": "internal_error"}
        exc = _classify_http_error(500, body)
        assert exc is None

    def test_repeated_503_no_retry_after_means_contention(self) -> None:
        """503 without retry_after_sec or engine_busy reason is generic contention."""
        body = {"message": "service overloaded"}
        exc = _classify_http_error(503, body)
        assert isinstance(exc, ContentionError)
