# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Contract tests for malformed response ID validation.

All endpoints that accept a response_id path parameter must reject
malformed IDs with 400 (``code: "invalid_parameters"``,
``param: "responseId{<value>}"``).

Malformed ``previous_response_id`` in the POST body must be rejected
with 400 (``code: "invalid_parameters"``, ``param: "previous_response_id"``).
"""

from __future__ import annotations

from typing import Any

import pytest
from starlette.testclient import TestClient

from azure.ai.agentserver.responses import ResponsesAgentServerHost
from azure.ai.agentserver.responses._id_generator import IdGenerator


def _noop_handler(request: Any, context: Any, cancellation_signal: Any):
    async def _events():
        if False:  # pragma: no cover
            yield None

    return _events()


def _make_client() -> TestClient:
    host = ResponsesAgentServerHost()
    host.response_handler(_noop_handler)
    return TestClient(host)


# ── Path parameter ID validation ──────────────────────────


class TestMalformedPathId:
    """Path parameter ``response_id`` validation on all endpoints (B40)."""

    MALFORMED_IDS = [
        "totally-invalid",
        "resp_abc123",  # wrong prefix
        "caresp_tooshort",  # correct prefix but too short
    ]

    @pytest.mark.parametrize("bad_id", MALFORMED_IDS)
    def test_get_malformed_id_returns_400(self, bad_id: str) -> None:
        client = _make_client()
        r = client.get(f"/responses/{bad_id}")
        assert r.status_code == 400
        body = r.json()
        assert body["error"]["code"] == "invalid_parameters"
        assert body["error"]["param"] == f"responseId{{{bad_id}}}"

    @pytest.mark.parametrize("bad_id", MALFORMED_IDS)
    def test_get_sse_malformed_id_returns_400(self, bad_id: str) -> None:
        client = _make_client()
        r = client.get(f"/responses/{bad_id}", params={"stream": "true"})
        assert r.status_code == 400

    @pytest.mark.parametrize("bad_id", MALFORMED_IDS)
    def test_cancel_malformed_id_returns_400(self, bad_id: str) -> None:
        client = _make_client()
        r = client.post(f"/responses/{bad_id}/cancel")
        assert r.status_code == 400

    @pytest.mark.parametrize("bad_id", MALFORMED_IDS)
    def test_delete_malformed_id_returns_400(self, bad_id: str) -> None:
        client = _make_client()
        r = client.delete(f"/responses/{bad_id}")
        assert r.status_code == 400

    @pytest.mark.parametrize("bad_id", MALFORMED_IDS)
    def test_input_items_malformed_id_returns_400(self, bad_id: str) -> None:
        client = _make_client()
        r = client.get(f"/responses/{bad_id}/input_items")
        assert r.status_code == 400

    def test_valid_format_unknown_id_returns_404_not_400(self) -> None:
        """A well-formed but non-existent ID should return 404, not 400."""
        client = _make_client()
        unknown_id = IdGenerator.new_response_id()
        r = client.get(f"/responses/{unknown_id}")
        assert r.status_code == 404


# ── Body field ``previous_response_id`` validation ─────────


class TestMalformedPreviousResponseId:
    """``previous_response_id`` in POST body must be valid ``caresp`` format."""

    def test_malformed_previous_response_id_returns_400(self) -> None:
        """Malformed previous_response_id returns 400 with invalid_parameters code and param."""
        client = _make_client()
        r = client.post(
            "/responses",
            json={
                "model": "m",
                "input": [{"role": "user", "content": "hi"}],
                "previous_response_id": "totally-invalid",
            },
        )
        assert r.status_code == 400
        body = r.json()
        error = body["error"]
        assert error["code"] == "invalid_parameters"
        assert error["type"] == "invalid_request_error"
        assert "previous_response_id" in error.get("param", "")

    def test_wrong_prefix_previous_response_id_returns_400(self) -> None:
        client = _make_client()
        r = client.post(
            "/responses",
            json={
                "model": "m",
                "input": [{"role": "user", "content": "hi"}],
                "previous_response_id": "resp_abc123xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            },
        )
        assert r.status_code == 400

    def test_valid_format_nonexistent_previous_response_id_not_rejected_by_format(self) -> None:
        """A valid-format previous_response_id that doesn't exist should pass
        format validation — it must NOT be rejected with the format-validation
        error shape (code=invalid_parameters, Malformed message)."""
        client = _make_client()
        valid_id = IdGenerator.new_response_id()
        r = client.post(
            "/responses",
            json={
                "model": "m",
                "input": [{"role": "user", "content": "hi"}],
                "previous_response_id": valid_id,
            },
        )
        # If the server returns 400, it must NOT be the format-validation shape.
        if r.status_code == 400:
            error = r.json().get("error", {})
            assert error.get("code") != "invalid_parameters", (
                "Valid-format previous_response_id was rejected by format validation"
            )
            assert "Malformed" not in error.get("message", ""), (
                "Valid-format previous_response_id was rejected with Malformed message"
            )
