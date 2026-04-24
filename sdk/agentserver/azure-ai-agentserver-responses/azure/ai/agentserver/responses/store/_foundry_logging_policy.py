# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Logging policy for Foundry storage HTTP calls.

Logs method, URI, status code, duration, and correlation headers for
each outbound storage request at the ``azure.ai.agentserver`` logger.

Provides consistent observability for storage operations.
"""

from __future__ import annotations

import logging
import time
import urllib.parse
from typing import cast

from azure.core.pipeline import PipelineRequest, PipelineResponse
from azure.core.pipeline.policies import AsyncHTTPPolicy
from azure.core.rest import HttpResponse

from .._platform_headers import (
    APIM_REQUEST_ID,
    CHAT_ISOLATION_KEY,
    CLIENT_REQUEST_ID,
    REQUEST_ID,
    TRACEPARENT,
    USER_ISOLATION_KEY,
)

logger = logging.getLogger("azure.ai.agentserver")


def _mask_storage_url(url: str) -> str:
    """Mask the sensitive portions of a Foundry storage URL.

    Everything before ``/storage`` (scheme, host, project path) is replaced
    with ``"***"`` because it contains the project endpoint and project
    name.  Only the ``/storage/...`` resource path is kept for debugging.
    The ``api-version`` query parameter is preserved; all other query
    parameters are stripped.

    Example::

        >>> _mask_storage_url(
        ...     "https://acct.services.ai.azure.com/api/projects/myproj"
        ...     "/storage/responses/resp_123?api-version=2025-01-01"
        ... )
        '***/storage/responses/resp_123?api-version=2025-01-01'

    :param url: The full storage URL.
    :type url: str
    :return: The masked URL with everything before ``/storage`` redacted.
    :rtype: str
    """
    try:
        if not url:
            return "(redacted)"
        parsed = urllib.parse.urlparse(url)
        path = parsed.path or ""
        # Find the /storage segment and keep only from there.
        idx = path.find("/storage")
        if idx < 0:
            return "(redacted)"
        masked = f"***{path[idx:]}"
        # Preserve api-version query param if present (safe and useful for debugging).
        qs = urllib.parse.parse_qs(parsed.query)
        api_version = qs.get("api-version")
        if api_version:
            masked += f"?api-version={api_version[0]}"
        return masked
    except Exception:  # pylint: disable=broad-exception-caught
        return "(redacted)"


class FoundryStorageLoggingPolicy(AsyncHTTPPolicy):  # type: ignore[type-arg]
    """Azure Core per-retry pipeline policy that logs Foundry storage calls.

    Logs the HTTP method, masked URI (host redacted, path preserved, query
    stripped), response status code, duration in milliseconds, and correlation
    headers (``x-ms-client-request-id``, ``traceparent``) for
    observability of storage operations.
    """

    async def send(self, request: PipelineRequest) -> PipelineResponse:
        """Send the request and log the operation details.

        :param request: The pipeline request.
        :type request: ~azure.core.pipeline.PipelineRequest
        :return: The pipeline response.
        :rtype: ~azure.core.pipeline.PipelineResponse
        """
        http_request = request.http_request
        method = http_request.method
        url = _mask_storage_url(str(http_request.url))

        client_request_id = http_request.headers.get(CLIENT_REQUEST_ID, "")
        traceparent = http_request.headers.get(TRACEPARENT, "")
        has_user_isolation_key = USER_ISOLATION_KEY in http_request.headers
        has_chat_isolation_key = CHAT_ISOLATION_KEY in http_request.headers

        logger.debug(
            "Foundry storage %s %s starting "
            "(x-ms-client-request-id=%s, traceparent=%s)",
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
                "Foundry storage %s %s transport failure after %.1fms "
                "(x-ms-client-request-id=%s, traceparent=%s)",
                method,
                url,
                elapsed_ms,
                client_request_id,
                traceparent,
                exc_info=True,
            )
            raise

        elapsed_ms = (time.monotonic() - start) * 1000
        http_response = cast(HttpResponse, response.http_response)
        status_code = http_response.status_code
        x_request_id = http_response.headers.get(REQUEST_ID, "")
        apim_request_id = http_response.headers.get(APIM_REQUEST_ID, "")

        log_level = logging.INFO if 200 <= status_code < 400 else logging.WARNING
        logger.log(
            log_level,
            "Foundry storage %s %s -> %d (%.1fms, "
            "x-ms-client-request-id=%s, traceparent=%s, "
            "x-request-id=%s, apim-request-id=%s, "
            "has_user_isolation_key=%s, has_chat_isolation_key=%s)",
            method,
            url,
            status_code,
            elapsed_ms,
            client_request_id,
            traceparent,
            x_request_id,
            apim_request_id,
            has_user_isolation_key,
            has_chat_isolation_key,
        )

        return response
