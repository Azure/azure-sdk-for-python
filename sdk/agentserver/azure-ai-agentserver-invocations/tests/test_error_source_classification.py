# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for error source classification on invocations endpoints.

Validates that every error response from the invocations protocol includes
``x-platform-error-source`` with the correct value (``user``, ``platform``,
or ``upstream``) and optionally ``x-platform-error-detail``.
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

import pytest
from azure.ai.agentserver.core._platform_headers import (
    ERROR_DETAIL,
    ERROR_SOURCE,
    PLATFORM_ERROR_TAG,
)
from httpx import ASGITransport, AsyncClient
from starlette.requests import Request
from starlette.responses import Response

from azure.ai.agentserver.invocations import InvocationAgentServerHost
from azure.ai.agentserver.invocations._invocation import (
    _ERROR_SOURCE_PLATFORM as ERROR_SOURCE_PLATFORM,
    _ERROR_SOURCE_UPSTREAM as ERROR_SOURCE_UPSTREAM,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


@asynccontextmanager
async def _make_client(app: InvocationAgentServerHost) -> AsyncIterator[AsyncClient]:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        yield client


def _make_no_handler_app() -> InvocationAgentServerHost:
    """App with no invoke handler registered → NotImplementedError."""
    return InvocationAgentServerHost()


def _make_upstream_error_app() -> InvocationAgentServerHost:
    """App whose invoke handler always raises a generic exception."""
    app = InvocationAgentServerHost()

    @app.invoke_handler
    async def handle(request: Request) -> Response:
        raise RuntimeError("handler bug")

    return app


def _make_platform_error_app() -> InvocationAgentServerHost:
    """App whose invoke handler raises an exception tagged as platform."""
    app = InvocationAgentServerHost()

    @app.invoke_handler
    async def handle(request: Request) -> Response:
        exc = RuntimeError("storage transport failure")
        setattr(exc, PLATFORM_ERROR_TAG, True)
        raise exc

    return app


def _make_echo_app() -> InvocationAgentServerHost:
    """App with a working echo handler."""
    app = InvocationAgentServerHost()

    @app.invoke_handler
    async def handle(request: Request) -> Response:
        body = await request.body()
        return Response(content=body, media_type="application/octet-stream")

    return app


# ---------------------------------------------------------------------------
# POST /invocations — success (no error headers)
# ---------------------------------------------------------------------------


class TestSuccessNoErrorHeaders:
    """Successful responses must NOT contain error source headers."""

    @pytest.mark.asyncio
    async def test_success_has_no_error_source(self) -> None:
        async with _make_client(_make_echo_app()) as client:
            resp = await client.post("/invocations", content=b"hello")
            assert resp.status_code == 200
            assert ERROR_SOURCE not in resp.headers
            assert ERROR_DETAIL not in resp.headers


# ---------------------------------------------------------------------------
# POST /invocations — NoImplementedError (501)
# ---------------------------------------------------------------------------


class TestNotImplementedUpstream:
    """NotImplementedError from missing handler → upstream."""

    @pytest.mark.asyncio
    async def test_not_implemented_classified_upstream(self) -> None:
        async with _make_client(_make_no_handler_app()) as client:
            resp = await client.post("/invocations", content=b"test")
            assert resp.status_code == 501
            assert resp.headers[ERROR_SOURCE] == ERROR_SOURCE_UPSTREAM

    @pytest.mark.asyncio
    async def test_not_implemented_has_invocation_id(self) -> None:
        async with _make_client(_make_no_handler_app()) as client:
            resp = await client.post("/invocations", content=b"test")
            assert "x-agent-invocation-id" in resp.headers

    @pytest.mark.asyncio
    async def test_not_implemented_no_error_detail(self) -> None:
        """upstream errors should NOT have x-platform-error-detail."""
        async with _make_client(_make_no_handler_app()) as client:
            resp = await client.post("/invocations", content=b"test")
            assert ERROR_DETAIL not in resp.headers


# ---------------------------------------------------------------------------
# POST /invocations — handler exception (500 upstream)
# ---------------------------------------------------------------------------


class TestHandlerExceptionUpstream:
    """Generic exception from developer handler → upstream."""

    @pytest.mark.asyncio
    async def test_handler_exception_classified_upstream(self) -> None:
        async with _make_client(_make_upstream_error_app()) as client:
            resp = await client.post("/invocations", content=b"test")
            assert resp.status_code == 500
            assert resp.headers[ERROR_SOURCE] == ERROR_SOURCE_UPSTREAM

    @pytest.mark.asyncio
    async def test_handler_exception_no_error_detail(self) -> None:
        """upstream errors should NOT have x-platform-error-detail."""
        async with _make_client(_make_upstream_error_app()) as client:
            resp = await client.post("/invocations", content=b"test")
            assert ERROR_DETAIL not in resp.headers


# ---------------------------------------------------------------------------
# POST /invocations — platform-tagged exception (500 platform)
# ---------------------------------------------------------------------------


class TestPlatformTaggedError:
    """Exception tagged with PLATFORM_ERROR_TAG → platform with detail."""

    @pytest.mark.asyncio
    async def test_platform_tagged_classified_platform(self) -> None:
        async with _make_client(_make_platform_error_app()) as client:
            resp = await client.post("/invocations", content=b"test")
            assert resp.status_code == 500
            assert resp.headers[ERROR_SOURCE] == ERROR_SOURCE_PLATFORM

    @pytest.mark.asyncio
    async def test_platform_tagged_has_error_detail(self) -> None:
        """platform errors MUST include x-platform-error-detail."""
        async with _make_client(_make_platform_error_app()) as client:
            resp = await client.post("/invocations", content=b"test")
            assert ERROR_DETAIL in resp.headers
            assert "storage transport failure" in resp.headers[ERROR_DETAIL]


# ---------------------------------------------------------------------------
# GET /invocations/{id} — no handler registered (404 upstream)
# ---------------------------------------------------------------------------


class TestGetDispatchNotImplemented:
    """Default dispatch_get_invocation (no handler) → 404 upstream."""

    @pytest.mark.asyncio
    async def test_get_not_implemented_upstream(self) -> None:
        async with _make_client(_make_echo_app()) as client:  # no get_invocation_handler
            resp = await client.get("/invocations/inv-123")
            assert resp.status_code == 404
            assert resp.headers[ERROR_SOURCE] == ERROR_SOURCE_UPSTREAM


# ---------------------------------------------------------------------------
# POST /invocations/{id}/cancel — no handler registered (404 upstream)
# ---------------------------------------------------------------------------


class TestCancelDispatchNotImplemented:
    """Default dispatch_cancel_invocation (no handler) → 404 upstream."""

    @pytest.mark.asyncio
    async def test_cancel_not_implemented_upstream(self) -> None:
        async with _make_client(_make_echo_app()) as client:  # no cancel_invocation_handler
            resp = await client.post("/invocations/inv-123/cancel")
            assert resp.status_code == 404
            assert resp.headers[ERROR_SOURCE] == ERROR_SOURCE_UPSTREAM


# ---------------------------------------------------------------------------
# GET /invocations/docs/openapi.json — no spec (404 upstream)
# ---------------------------------------------------------------------------


class TestOpenApiNotRegistered:
    """No OpenAPI spec registered → 404 upstream."""

    @pytest.mark.asyncio
    async def test_no_spec_upstream(self) -> None:
        async with _make_client(_make_echo_app()) as client:  # no openapi_spec
            resp = await client.get("/invocations/docs/openapi.json")
            assert resp.status_code == 404
            assert resp.headers[ERROR_SOURCE] == ERROR_SOURCE_UPSTREAM


# ---------------------------------------------------------------------------
# GET /invocations/{id} — handler raises (500, classified)
# ---------------------------------------------------------------------------


class TestGetHandlerException:
    """Exception in get_invocation_handler → upstream or platform."""

    @pytest.mark.asyncio
    async def test_get_handler_exception_upstream(self) -> None:
        app = InvocationAgentServerHost()

        @app.invoke_handler
        async def invoke(request: Request) -> Response:
            return Response(content=b"ok")

        @app.get_invocation_handler
        async def get_inv(request: Request) -> Response:
            raise RuntimeError("oops")

        async with _make_client(app) as client:
            resp = await client.get("/invocations/inv-123")
            assert resp.status_code == 500
            assert resp.headers[ERROR_SOURCE] == ERROR_SOURCE_UPSTREAM
            assert ERROR_DETAIL not in resp.headers

    @pytest.mark.asyncio
    async def test_get_handler_platform_error(self) -> None:
        app = InvocationAgentServerHost()

        @app.invoke_handler
        async def invoke(request: Request) -> Response:
            return Response(content=b"ok")

        @app.get_invocation_handler
        async def get_inv(request: Request) -> Response:
            exc = RuntimeError("infra failure")
            setattr(exc, PLATFORM_ERROR_TAG, True)
            raise exc

        async with _make_client(app) as client:
            resp = await client.get("/invocations/inv-123")
            assert resp.status_code == 500
            assert resp.headers[ERROR_SOURCE] == ERROR_SOURCE_PLATFORM
            assert "infra failure" in resp.headers[ERROR_DETAIL]


# ---------------------------------------------------------------------------
# POST /invocations/{id}/cancel — handler raises (500, classified)
# ---------------------------------------------------------------------------


class TestCancelHandlerException:
    """Exception in cancel_invocation_handler → upstream or platform."""

    @pytest.mark.asyncio
    async def test_cancel_handler_exception_upstream(self) -> None:
        app = InvocationAgentServerHost()

        @app.invoke_handler
        async def invoke(request: Request) -> Response:
            return Response(content=b"ok")

        @app.cancel_invocation_handler
        async def cancel_inv(request: Request) -> Response:
            raise ValueError("bad cancel")

        async with _make_client(app) as client:
            resp = await client.post("/invocations/inv-123/cancel")
            assert resp.status_code == 500
            assert resp.headers[ERROR_SOURCE] == ERROR_SOURCE_UPSTREAM

    @pytest.mark.asyncio
    async def test_cancel_handler_platform_error(self) -> None:
        app = InvocationAgentServerHost()

        @app.invoke_handler
        async def invoke(request: Request) -> Response:
            return Response(content=b"ok")

        @app.cancel_invocation_handler
        async def cancel_inv(request: Request) -> Response:
            exc = RuntimeError("platform cancel failure")
            setattr(exc, PLATFORM_ERROR_TAG, True)
            raise exc

        async with _make_client(app) as client:
            resp = await client.post("/invocations/inv-123/cancel")
            assert resp.status_code == 500
            assert resp.headers[ERROR_SOURCE] == ERROR_SOURCE_PLATFORM
            assert "platform cancel failure" in resp.headers[ERROR_DETAIL]
