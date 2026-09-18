# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Starlette CloudAdapter for the Activity protocol host.

A framework adapter modelled on the M365 Agents SDK per-framework adapters
small request adapter maps the Starlette request onto ``HttpRequestProtocol``,
and the CloudAdapter delegates a turn to the shared
:meth:`HttpAdapterBase.process_request` pipeline and converts the returned
framework-agnostic ``HttpResponse`` back to a Starlette response.

This module contains *only* the framework adapter. Outbound-auth/claims and the
M365 stack build live in :mod:`._m365_bridge`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from ._constants import ErrorCode

if TYPE_CHECKING:  # pragma: no cover - type-only imports (M365 SDK is optional)
    from microsoft_agents.hosting.core import Agent, ClaimsIdentity, HttpAdapterBase
    from microsoft_agents.hosting.core.http import HttpResponse


class _StarletteRequestAdapter:
    """Adapter to make a Starlette ``Request`` compatible with ``HttpRequestProtocol``."""

    def __init__(self, request: Request) -> None:
        self._request = request

    @property
    def method(self) -> str:
        return self._request.method

    @property
    def headers(self) -> Any:
        return self._request.headers

    async def json(self) -> dict:
        return self._request.state.activity

    def get_claims_identity(self) -> Optional[ClaimsIdentity]:
        return getattr(self._request.state, "claims_identity", None)

    def get_path_param(self, name: str) -> str:
        return self._request.path_params.get(name, "")


class StarletteCloudAdapter:
    """CloudAdapter for the Starlette web framework."""

    def __init__(self, adapter: HttpAdapterBase) -> None:
        """Initialize the CloudAdapter.

        :param adapter: The HTTP adapter providing the shared ``process_request``
            pipeline.
        :type adapter: ~microsoft_agents.hosting.core.HttpAdapterBase
        """
        self._adapter = adapter

    async def process(self, request: Request, agent: Agent) -> Response:
        """Process a Starlette request.

        :param request: The Starlette request.
        :type request: ~starlette.requests.Request
        :param agent: The agent to handle the request.
        :type agent: ~microsoft_agents.hosting.core.Agent
        :return: The Starlette response.
        :rtype: ~starlette.responses.Response
        """
        # Adapt request to protocol
        adapted_request = _StarletteRequestAdapter(request)

        # Process using the shared base implementation
        http_response = await self._adapter.process_request(adapted_request, agent)

        # Convert HttpResponse to a Starlette response
        return self._to_starlette_response(http_response)

    @staticmethod
    def _to_starlette_response(http_response: HttpResponse) -> Response:
        """Convert an M365 ``HttpResponse`` to a Starlette response.

        Errors (status >= 400) are re-wrapped into the Foundry error envelope
        (``{"error": {"code", "message"}}``); success bodies pass through; any
        headers on the ``HttpResponse`` are preserved.

        :param http_response: The framework-agnostic response from ``process_request``.
        :type http_response: ~microsoft_agents.hosting.core.http.HttpResponse
        :return: The equivalent Starlette response.
        :rtype: ~starlette.responses.Response
        """
        status_code = http_response.status_code
        body = http_response.body
        headers = dict(http_response.headers) if http_response.headers else None

        if status_code >= 400:
            message = body.get("error") if isinstance(body, dict) else None
            code = ErrorCode.INVALID_REQUEST if status_code == 400 else ErrorCode.INTERNAL_ERROR
            return JSONResponse(
                status_code=status_code,
                content={"error": {"code": code, "message": message or "Request failed"}},
                headers=headers,
            )
        if body is not None:
            return JSONResponse(content=body, status_code=status_code, headers=headers)
        return Response(status_code=status_code, headers=headers)
