# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Tests for RequestIdMiddleware — x-request-id response header."""

from __future__ import annotations

import pytest
from azure.ai.agentserver.core._request_id import RequestIdMiddleware
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.testclient import TestClient

# Internal well-known key — not public API, shared across sibling packages.
_REQUEST_ID_STATE_KEY = "agentserver.request_id"


def _build_app() -> Starlette:
    """Build a minimal Starlette app with RequestIdMiddleware."""

    async def _ok(request: Request) -> JSONResponse:
        # Return the scope-stored request_id in the body for assertion
        request_id = request.scope.get("state", {}).get(_REQUEST_ID_STATE_KEY)
        return JSONResponse({"request_id": request_id})

    async def _error_plain(request: Request) -> JSONResponse:
        """Structured JSON error response with an ``error`` key."""
        return JSONResponse({"error": "internal"}, status_code=500)

    return Starlette(
        routes=[
            Route("/test", _ok, methods=["GET"]),
            Route("/error", _error_plain, methods=["GET"]),
        ],
        middleware=[
            Middleware(RequestIdMiddleware),  # type: ignore[arg-type]
        ],
    )


class TestRequestIdMiddleware:
    """Test the x-request-id response header middleware."""

    def test_response_includes_x_request_id_header(self) -> None:
        """Every response should include an x-request-id header."""
        client = TestClient(_build_app())
        response = client.get("/test")
        assert response.status_code == 200
        assert "x-request-id" in response.headers
        assert response.headers["x-request-id"]  # non-empty

    def test_incoming_x_request_id_is_used_as_fallback(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """When client sends x-request-id and no OTEL trace, it should be used."""
        # Force _get_trace_id to return None so the fallback path is exercised.
        from azure.ai.agentserver.core import _request_id as _rid_mod

        monkeypatch.setattr(_rid_mod, "_get_trace_id", lambda *_args, **_kwargs: None)
        client_request_id = "client-provided-123"
        client = TestClient(_build_app())
        response = client.get("/test", headers={"x-request-id": client_request_id})
        assert response.status_code == 200
        header_value = response.headers["x-request-id"]
        assert header_value == client_request_id

    def test_request_id_stored_in_scope_state(self) -> None:
        """The resolved request_id should be stored in scope state AND match the header."""
        client = TestClient(_build_app())
        response = client.get("/test")
        assert response.status_code == 200
        body = response.json()
        header_value = response.headers["x-request-id"]
        assert body["request_id"] == header_value

    def test_error_responses_include_x_request_id(self) -> None:
        """Error responses (500) should also have x-request-id header."""
        client = TestClient(_build_app())
        response = client.get("/error")
        assert response.status_code == 500
        assert "x-request-id" in response.headers
        assert response.headers["x-request-id"]

    def test_different_requests_get_different_ids(self) -> None:
        """Two requests should get different x-request-id values."""
        client = TestClient(_build_app())
        r1 = client.get("/test")
        r2 = client.get("/test")
        id1 = r1.headers["x-request-id"]
        id2 = r2.headers["x-request-id"]
        # They're different requests so should get different IDs.
        assert id1 and id2
        assert id1 != id2

    @pytest.mark.parametrize("path", ["/test", "/error"])
    def test_header_present_on_all_paths(self, path: str) -> None:
        """x-request-id header should be present regardless of path or status."""
        client = TestClient(_build_app())
        response = client.get(path)
        assert "x-request-id" in response.headers
