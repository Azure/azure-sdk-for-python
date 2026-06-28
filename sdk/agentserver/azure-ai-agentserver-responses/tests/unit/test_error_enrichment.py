# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Tests for error response request_id enrichment in additionalInfo."""

from __future__ import annotations

import json

import pytest

from azure.ai.agentserver.responses.hosting._validation import (
    _enrich_error_payload,
    error_response,
    invalid_request_response,
    not_found_response,
    service_unavailable_response,
)


class TestEnrichErrorPayload:
    """Tests for _enrich_error_payload helper."""

    def test_adds_request_id_to_additional_info(self) -> None:
        payload: dict = {"error": {"code": "test", "message": "msg"}}
        _enrich_error_payload(payload, "req-123")
        assert payload["error"]["additionalInfo"]["request_id"] == "req-123"

    def test_does_not_overwrite_existing_request_id(self) -> None:
        payload: dict = {"error": {"code": "test", "message": "msg", "additionalInfo": {"request_id": "existing"}}}
        _enrich_error_payload(payload, "new-id")
        assert payload["error"]["additionalInfo"]["request_id"] == "existing"

    def test_preserves_existing_additional_info_fields(self) -> None:
        payload: dict = {"error": {"code": "test", "message": "msg", "additionalInfo": {"foo": "bar"}}}
        _enrich_error_payload(payload, "req-456")
        assert payload["error"]["additionalInfo"]["foo"] == "bar"
        assert payload["error"]["additionalInfo"]["request_id"] == "req-456"

    def test_noop_when_no_error_key(self) -> None:
        payload: dict = {"other": "stuff"}
        _enrich_error_payload(payload, "req-789")
        assert "additionalInfo" not in payload

    def test_noop_when_error_is_not_dict(self) -> None:
        payload: dict = {"error": "string-error"}
        _enrich_error_payload(payload, "req-000")
        assert payload["error"] == "string-error"


class TestErrorResponseEnrichment:
    """Test that error response builders include request_id in additional_info."""

    def test_not_found_includes_request_id(self) -> None:
        resp = not_found_response("resp_123", {}, request_id="test-req-id")
        body = json.loads(resp.body)
        assert body["error"]["additionalInfo"]["request_id"] == "test-req-id"

    def test_not_found_without_request_id_has_no_additional_info(self) -> None:
        resp = not_found_response("resp_123", {})
        body = json.loads(resp.body)
        assert "additionalInfo" not in body.get("error", {})

    def test_invalid_request_includes_request_id(self) -> None:
        resp = invalid_request_response("bad request", {}, request_id="req-456")
        body = json.loads(resp.body)
        assert body["error"]["additionalInfo"]["request_id"] == "req-456"

    def test_error_response_includes_request_id(self) -> None:
        resp = error_response(ValueError("test error"), {}, request_id="req-789")
        body = json.loads(resp.body)
        assert body["error"]["additionalInfo"]["request_id"] == "req-789"

    def test_service_unavailable_includes_request_id(self) -> None:
        resp = service_unavailable_response("shutting down", {}, request_id="req-svc")
        body = json.loads(resp.body)
        assert body["error"]["additionalInfo"]["request_id"] == "req-svc"

    @pytest.mark.parametrize(
        "builder_fn,args",
        [
            (not_found_response, ("resp_1", {})),
            (invalid_request_response, ("msg", {})),
            (error_response, (RuntimeError("err"), {})),
            (service_unavailable_response, ("msg", {})),
        ],
    )
    def test_no_request_id_means_no_additional_info(self, builder_fn, args) -> None:
        resp = builder_fn(*args)
        body = json.loads(resp.body)
        assert "additionalInfo" not in body.get("error", {})
