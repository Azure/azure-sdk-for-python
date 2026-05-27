# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Unit tests for error source classification helpers and header application."""

from __future__ import annotations

import pytest
from azure.ai.agentserver.core._platform_headers import (
    ERROR_DETAIL,
    ERROR_SOURCE,
)

from azure.ai.agentserver.responses.hosting._validation import (
    ERROR_SOURCE_PLATFORM,
    ERROR_SOURCE_UPSTREAM,
    ERROR_SOURCE_USER,
    MAX_ERROR_DETAIL_LENGTH,
    PLATFORM_ERROR_TAG,
    _apply_error_source_headers,
    error_response,
    format_error_detail,
    invalid_mode_response,
    invalid_parameters_response,
    invalid_request_response,
    is_platform_error,
    not_found_response,
    service_unavailable_response,
    tag_platform_error,
)
from azure.ai.agentserver.responses.models.errors import RequestValidationError

# ---------------------------------------------------------------------------
# is_platform_error / tag_platform_error
# ---------------------------------------------------------------------------


class TestPlatformErrorTagging:
    """Tests for is_platform_error and tag_platform_error."""

    def test_untagged_exception_is_not_platform(self) -> None:
        exc = RuntimeError("boom")
        assert is_platform_error(exc) is False

    def test_tagged_exception_is_platform(self) -> None:
        exc = RuntimeError("storage down")
        tag_platform_error(exc)
        assert is_platform_error(exc) is True

    def test_tag_platform_error_sets_attribute(self) -> None:
        exc = Exception("oops")
        tag_platform_error(exc)
        assert getattr(exc, PLATFORM_ERROR_TAG) is True

    def test_double_tagging_is_idempotent(self) -> None:
        exc = RuntimeError("retry")
        tag_platform_error(exc)
        tag_platform_error(exc)
        assert is_platform_error(exc) is True


# ---------------------------------------------------------------------------
# format_error_detail
# ---------------------------------------------------------------------------


class TestFormatErrorDetail:
    """Tests for format_error_detail."""

    def test_short_detail_not_truncated(self) -> None:
        exc = ValueError("short message")
        detail = format_error_detail(exc)
        assert detail == "ValueError: short message"
        assert len(detail) <= MAX_ERROR_DETAIL_LENGTH

    def test_long_detail_truncated_to_max_length(self) -> None:
        exc = ValueError("x" * (MAX_ERROR_DETAIL_LENGTH + 500))
        detail = format_error_detail(exc)
        assert len(detail) <= MAX_ERROR_DETAIL_LENGTH
        assert detail.endswith("...[truncated]")

    def test_truncated_detail_preserves_prefix(self) -> None:
        msg = "A" * 5000
        exc = RuntimeError(msg)
        detail = format_error_detail(exc)
        # Must start with the type name prefix
        assert detail.startswith("RuntimeError: ")


# ---------------------------------------------------------------------------
# _apply_error_source_headers
# ---------------------------------------------------------------------------


class TestApplyErrorSourceHeaders:
    """Tests for _apply_error_source_headers."""

    def test_adds_error_source_header(self) -> None:
        headers = {"x-platform-server": "test/1.0"}
        result = _apply_error_source_headers(headers, ERROR_SOURCE_USER)
        assert result[ERROR_SOURCE] == "user"
        # Original dict is unmodified
        assert ERROR_SOURCE not in headers

    def test_adds_error_detail_when_provided(self) -> None:
        headers = {}
        result = _apply_error_source_headers(headers, ERROR_SOURCE_PLATFORM, error_detail="disk full")
        assert result[ERROR_SOURCE] == "platform"
        assert result[ERROR_DETAIL] == "disk full"

    def test_omits_error_detail_when_none(self) -> None:
        headers = {}
        result = _apply_error_source_headers(headers, ERROR_SOURCE_UPSTREAM)
        assert result[ERROR_SOURCE] == "upstream"
        assert ERROR_DETAIL not in result

    def test_preserves_existing_headers(self) -> None:
        headers = {"x-custom": "value", "x-platform-server": "v1"}
        result = _apply_error_source_headers(headers, ERROR_SOURCE_USER)
        assert result["x-custom"] == "value"
        assert result["x-platform-server"] == "v1"
        assert result[ERROR_SOURCE] == "user"

    def test_returns_new_dict(self) -> None:
        headers = {"a": "1"}
        result = _apply_error_source_headers(headers, ERROR_SOURCE_USER)
        assert result is not headers


# ---------------------------------------------------------------------------
# error_response auto-classification
# ---------------------------------------------------------------------------


class TestErrorResponseClassification:
    """Tests for error_response auto-classification of error source."""

    def test_request_validation_error_classified_as_user(self) -> None:
        exc = RequestValidationError("bad input", code="invalid_request")
        resp = error_response(exc, {})
        assert resp.headers[ERROR_SOURCE] == "user"
        assert ERROR_DETAIL not in resp.headers

    def test_value_error_classified_as_user(self) -> None:
        exc = ValueError("not a number")
        resp = error_response(exc, {})
        assert resp.headers[ERROR_SOURCE] == "user"
        assert ERROR_DETAIL not in resp.headers

    def test_tagged_exception_classified_as_platform(self) -> None:
        exc = RuntimeError("storage timeout")
        tag_platform_error(exc)
        resp = error_response(exc, {})
        assert resp.headers[ERROR_SOURCE] == "platform"
        assert ERROR_DETAIL in resp.headers

    def test_platform_error_detail_contains_exception_repr(self) -> None:
        exc = ConnectionError("refused")
        tag_platform_error(exc)
        resp = error_response(exc, {})
        detail = resp.headers[ERROR_DETAIL]
        assert "ConnectionError" in detail
        assert "refused" in detail

    def test_untagged_exception_classified_as_upstream(self) -> None:
        exc = RuntimeError("handler bug")
        resp = error_response(exc, {})
        assert resp.headers[ERROR_SOURCE] == "upstream"
        assert ERROR_DETAIL not in resp.headers

    def test_explicit_error_source_overrides_classification(self) -> None:
        exc = RuntimeError("whatever")
        resp = error_response(exc, {}, error_source=ERROR_SOURCE_PLATFORM)
        assert resp.headers[ERROR_SOURCE] == "platform"

    def test_preserves_session_headers(self) -> None:
        headers = {"x-agent-session-id": "session1", "x-platform-server": "v1"}
        exc = ValueError("err")
        resp = error_response(exc, headers)
        assert resp.headers["x-agent-session-id"] == "session1"
        assert resp.headers["x-platform-server"] == "v1"
        assert resp.headers[ERROR_SOURCE] == "user"


# ---------------------------------------------------------------------------
# Factory function error source headers
# ---------------------------------------------------------------------------


class TestFactoryFunctionErrorSource:
    """Tests that all error factory functions set the expected error source."""

    def test_not_found_response_is_user(self) -> None:
        resp = not_found_response("resp_123abc", {})
        assert resp.headers[ERROR_SOURCE] == "user"
        assert ERROR_DETAIL not in resp.headers
        assert resp.status_code == 404

    def test_invalid_request_response_is_user(self) -> None:
        resp = invalid_request_response("bad param", {})
        assert resp.headers[ERROR_SOURCE] == "user"
        assert ERROR_DETAIL not in resp.headers
        assert resp.status_code == 400

    def test_invalid_parameters_response_is_user(self) -> None:
        resp = invalid_parameters_response("bad temperature", {})
        assert resp.headers[ERROR_SOURCE] == "user"
        assert ERROR_DETAIL not in resp.headers
        assert resp.status_code == 400

    def test_invalid_mode_response_is_user(self) -> None:
        resp = invalid_mode_response("not streamable", {})
        assert resp.headers[ERROR_SOURCE] == "user"
        assert ERROR_DETAIL not in resp.headers
        assert resp.status_code == 400

    def test_service_unavailable_response_is_platform(self) -> None:
        resp = service_unavailable_response("shutting down", {})
        assert resp.headers[ERROR_SOURCE] == "platform"
        assert resp.status_code == 503


# ---------------------------------------------------------------------------
# FoundryApiError platform tagging
# ---------------------------------------------------------------------------


class TestFoundryErrorTagging:
    """Tests that FoundryApiError from raise_for_storage_error is tagged as platform."""

    def test_foundry_api_error_tagged_as_platform(self) -> None:
        from azure.ai.agentserver.responses.store._foundry_errors import (
            FoundryApiError,
            raise_for_storage_error,
        )

        class _FakeResponse:
            status_code = 502
            def text(self) -> str:
                return '{"error": {"message": "bad gateway"}}'

        with pytest.raises(FoundryApiError) as exc_info:
            raise_for_storage_error(_FakeResponse())  # type: ignore[arg-type]

        assert is_platform_error(exc_info.value) is True

    def test_foundry_not_found_error_not_tagged(self) -> None:
        from azure.ai.agentserver.responses.store._foundry_errors import (
            FoundryResourceNotFoundError,
            raise_for_storage_error,
        )

        class _FakeResponse:
            status_code = 404
            def text(self) -> str:
                return '{"error": {"message": "not found"}}'

        with pytest.raises(FoundryResourceNotFoundError) as exc_info:
            raise_for_storage_error(_FakeResponse())  # type: ignore[arg-type]

        assert is_platform_error(exc_info.value) is False

    def test_foundry_bad_request_error_not_tagged(self) -> None:
        from azure.ai.agentserver.responses.store._foundry_errors import (
            FoundryBadRequestError,
            raise_for_storage_error,
        )

        class _FakeResponse:
            status_code = 400
            def text(self) -> str:
                return '{"error": {"message": "bad request"}}'

        with pytest.raises(FoundryBadRequestError) as exc_info:
            raise_for_storage_error(_FakeResponse())  # type: ignore[arg-type]

        assert is_platform_error(exc_info.value) is False


# ---------------------------------------------------------------------------
# Platform header constant values
# ---------------------------------------------------------------------------


class TestErrorSourceConstants:
    """Ensure error source header constants match the container spec wire values."""

    def test_error_source_header_name(self) -> None:
        assert ERROR_SOURCE == "x-platform-error-source"

    def test_error_detail_header_name(self) -> None:
        assert ERROR_DETAIL == "x-platform-error-detail"

    def test_error_source_user_value(self) -> None:
        assert ERROR_SOURCE_USER == "user"

    def test_error_source_platform_value(self) -> None:
        assert ERROR_SOURCE_PLATFORM == "platform"

    def test_error_source_upstream_value(self) -> None:
        assert ERROR_SOURCE_UPSTREAM == "upstream"

    def test_max_error_detail_length(self) -> None:
        assert MAX_ERROR_DETAIL_LENGTH == 2048

    def test_platform_error_tag_value(self) -> None:
        assert PLATFORM_ERROR_TAG == "Azure.AI.AgentServer.PlatformError"
