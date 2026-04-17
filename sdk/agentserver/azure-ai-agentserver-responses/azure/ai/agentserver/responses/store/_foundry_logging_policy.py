# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Logging policy for Foundry storage HTTP calls.

Logs method, URI, status code, duration, and correlation headers for
each outbound storage request at the ``azure.ai.agentserver`` logger.

This mirrors the .NET ``FoundryStorageLoggingPolicy`` and provides
consistent observability for storage operations.
"""

from __future__ import annotations

import logging
import time
from typing import cast

from azure.core.pipeline import PipelineRequest, PipelineResponse
from azure.core.pipeline.policies import AsyncHTTPPolicy
from azure.core.rest import HttpResponse

logger = logging.getLogger("azure.ai.agentserver")

# Correlation headers to extract and log
_CLIENT_REQUEST_ID_HEADER = "x-ms-client-request-id"
_SERVER_REQUEST_ID_HEADER = "x-ms-request-id"


class FoundryStorageLoggingPolicy(AsyncHTTPPolicy[PipelineRequest, PipelineResponse]):
    """Azure Core per-retry pipeline policy that logs Foundry storage calls.

    Logs the HTTP method, URI, response status code, duration in milliseconds,
    and correlation headers (``x-ms-client-request-id``, ``x-ms-request-id``)
    for observability of storage operations.
    """

    async def send(self, request: PipelineRequest) -> PipelineResponse:  # type: ignore[override]
        """Send the request and log the operation details.

        :param request: The pipeline request.
        :type request: ~azure.core.pipeline.PipelineRequest
        :return: The pipeline response.
        :rtype: ~azure.core.pipeline.PipelineResponse
        """
        http_request = request.http_request
        method = http_request.method
        url = http_request.url

        client_request_id = http_request.headers.get(_CLIENT_REQUEST_ID_HEADER, "")

        start = time.monotonic()
        try:
            response = await self.next.send(request)
        except Exception:
            elapsed_ms = (time.monotonic() - start) * 1000
            logger.warning(
                "Foundry storage %s %s failed after %.1fms (client-request-id=%s)",
                method,
                url,
                elapsed_ms,
                client_request_id,
            )
            raise

        elapsed_ms = (time.monotonic() - start) * 1000
        http_response = cast(HttpResponse, response.http_response)
        status_code = http_response.status_code
        server_request_id = http_response.headers.get(_SERVER_REQUEST_ID_HEADER, "")

        log_level = logging.INFO if 200 <= status_code < 400 else logging.WARNING
        logger.log(
            log_level,
            "Foundry storage %s %s -> %d (%.1fms, client-request-id=%s, request-id=%s)",
            method,
            url,
            status_code,
            elapsed_ms,
            client_request_id,
            server_request_id,
        )

        return response
