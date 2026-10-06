# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Azure Core pipeline policies shared by Foundry storage clients.

Both the request User-Agent policy and the per-retry logging policy are
protocol-neutral and reused by every AgentServer storage client.
"""

# pylint: disable=docstring-missing-param,docstring-missing-return,docstring-missing-rtype

from __future__ import annotations

import logging
import time
import urllib.parse
from typing import Callable

from azure.ai.agentserver.core._platform_headers import (
    APIM_REQUEST_ID,
    CLIENT_REQUEST_ID,
    REQUEST_ID,
    TRACEPARENT,
)
from azure.core.pipeline import PipelineRequest, PipelineResponse
from azure.core.pipeline.policies import AsyncHTTPPolicy, SansIOHTTPPolicy
from azure.core.rest import AsyncHttpResponse, HttpRequest, HttpResponse

logger = logging.getLogger("azure.ai.agentserver.core")

_LOG_FMT_START = "Foundry storage %s %s starting (x-ms-client-request-id=%s, traceparent=%s)"
_LOG_FMT_TRANSPORT_FAILURE = (
    "Foundry storage %s %s transport failure after %.1fms (x-ms-client-request-id=%s, traceparent=%s)"
)
_LOG_FMT_RESPONSE = (
    "Foundry storage %s %s -> %d (%.1fms, "
    "x-ms-client-request-id=%s, traceparent=%s, x-request-id=%s, apim-request-id=%s)"
)


class ServerVersionUserAgentPolicy(SansIOHTTPPolicy[HttpRequest, HttpResponse]):
    """Pipeline policy that sets the ``User-Agent`` header lazily from a callback.

    Unlike :class:`~azure.core.pipeline.policies.UserAgentPolicy` which captures
    the value at construction time, this policy evaluates the callback on each
    request so it reflects segments registered after the pipeline was built
    (e.g. by cooperative ``__init__`` in a multi-protocol host).
    """

    def __init__(self, get_server_version: Callable[[], str]) -> None:
        super().__init__()
        self._get_server_version = get_server_version

    def on_request(self, request: PipelineRequest[HttpRequest]) -> None:
        """Set the ``User-Agent`` header before the request is sent."""
        request.http_request.headers["User-Agent"] = self._get_server_version()


def _mask_storage_url(url: str) -> str:
    """Mask the sensitive portions of a Foundry storage URL."""
    try:
        if not url:
            return "(redacted)"
        parsed = urllib.parse.urlparse(url)
        path = parsed.path or ""
        idx = path.find("/storage")
        if idx < 0:
            return "(redacted)"
        storage_path = path[idx:]
        masked = f"***{_redact_storage_path(storage_path)}"
        qs = urllib.parse.parse_qs(parsed.query)
        api_version = qs.get("api-version")
        if api_version:
            masked += f"?api-version={api_version[0]}"
        return masked
    except Exception:  # pylint: disable=broad-exception-caught
        return "(redacted)"


def _redact_storage_path(path: str) -> str:
    if not path.startswith("/storage/"):
        return "/storage"
    segments = path.split("/")
    redacted: list[str] = []
    for index, segment in enumerate(segments):
        if index < 3 or segment in {"items", "items:keys", "state_stores"} or not segment:
            redacted.append(segment)
        else:
            redacted.append("*")
    return "/".join(redacted)


class FoundryStorageLoggingPolicy(AsyncHTTPPolicy[HttpRequest, AsyncHttpResponse]):
    """Azure Core per-retry pipeline policy that logs Foundry storage calls."""

    async def send(self, request: PipelineRequest[HttpRequest]) -> PipelineResponse[HttpRequest, AsyncHttpResponse]:
        """Send the request and log the operation details."""
        http_request = request.http_request
        method = http_request.method
        url = _mask_storage_url(str(http_request.url))
        client_request_id = http_request.headers.get(CLIENT_REQUEST_ID, "")
        traceparent = http_request.headers.get(TRACEPARENT, "")

        logger.debug(
            _LOG_FMT_START,
            method,
            url,
            client_request_id,
            traceparent,
        )

        start = time.monotonic()
        try:
            response = await self.next.send(request)
        except Exception:
            elapsed_ms = (time.monotonic() - start) * 1000
            logger.error(
                _LOG_FMT_TRANSPORT_FAILURE,
                method,
                url,
                elapsed_ms,
                client_request_id,
                traceparent,
                exc_info=True,
            )
            raise

        elapsed_ms = (time.monotonic() - start) * 1000
        http_response = response.http_response
        status_code = http_response.status_code
        x_request_id = http_response.headers.get(REQUEST_ID, "")
        apim_request_id = http_response.headers.get(APIM_REQUEST_ID, "")

        log_level = logging.INFO if 200 <= status_code < 400 else logging.WARNING
        logger.log(
            log_level,
            _LOG_FMT_RESPONSE,
            method,
            url,
            status_code,
            elapsed_ms,
            client_request_id,
            traceparent,
            x_request_id,
            apim_request_id,
        )

        return response
