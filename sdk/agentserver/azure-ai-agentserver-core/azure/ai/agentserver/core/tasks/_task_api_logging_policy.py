# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Task-API logging policy for the hosted task-store pipeline.

, this policy logs request/response metadata for the
``HostedTaskProvider`` ``azure.core.AsyncPipelineClient`` chain. The
policy:

- Logs an allow-listed set of operational headers (`x-ms-client-request-id`,
  `x-ms-request-id`, `etag`, `if-match`, `retry-after`, standard Azure
  operational headers like `x-ms-correlation-request-id`).
- NEVER logs the `Authorization` header (or any header whose name matches
  a credential-bearing pattern).
- NEVER logs request or response bodies above DEBUG.
- Logs status codes and methods at INFO for successful responses, WARNING
  for client errors (4xx), ERROR for server errors (5xx).

Reference: spec.md,  (the classifier funnels errors but does
NOT log them — that's this policy's job).
"""

from __future__ import annotations

import logging
from typing import Any

from azure.core.pipeline import PipelineRequest, PipelineResponse
from azure.core.pipeline.policies import SansIOHTTPPolicy

logger = logging.getLogger("azure.ai.agentserver.tasks.taskapi")


# Allow-listed operational headers. Logging anything else risks leaking
# auth, internal correlation IDs, or large payloads.
_ALLOWED_REQUEST_HEADERS: frozenset[str] = frozenset(
    h.lower()
    for h in (
        "x-ms-client-request-id",
        "x-ms-correlation-request-id",
        "if-match",
        "if-none-match",
        "content-type",
        "content-length",
        "user-agent",
        "api-version",
    )
)
_ALLOWED_RESPONSE_HEADERS: frozenset[str] = frozenset(
    h.lower()
    for h in (
        "x-ms-client-request-id",
        "x-ms-request-id",
        "x-ms-correlation-request-id",
        "etag",
        "retry-after",
        "content-type",
        "content-length",
        "date",
    )
)


def _redact_headers(headers: Any, allowed: frozenset[str]) -> dict[str, str]:
    """Return a copy of ``headers`` keeping only the allow-listed keys.

    Defensive: ``headers`` may be a real Mapping or a custom HeaderDict.
    Anything not in the allow-list is replaced with ``"<redacted>"``
    so the log line still shows the header was present without exposing
    the value.

    :param headers: Header collection to copy (any mapping-like object).
    :type headers: Any
    :param allowed: Lower-cased header names that may be logged in full.
    :type allowed: frozenset[str]
    :return: A redacted copy of the headers.
    :rtype: dict[str, str]
    """
    if not headers:
        return {}
    out: dict[str, str] = {}
    try:
        items = list(headers.items())
    except Exception:  # pylint: disable=broad-exception-caught  # noqa: BLE001
        return {}
    for name, value in items:
        try:
            key = str(name).lower()
        except Exception:  # pylint: disable=broad-exception-caught  # noqa: BLE001
            continue
        if key in allowed:
            out[name] = str(value)
        else:
            out[name] = "<redacted>"
    return out


class TaskApiLoggingPolicy(SansIOHTTPPolicy):
    """Sans-I/O logging policy for the task-store pipeline.

    Sits late in the chain (after retries and credential injection) so
    each emitted line reflects what actually went over the wire.
    """

    def on_request(self, request: PipelineRequest) -> None:
        if not logger.isEnabledFor(logging.INFO):
            return
        http_request = request.http_request
        method = http_request.method
        url = str(http_request.url)
        headers = _redact_headers(http_request.headers, _ALLOWED_REQUEST_HEADERS)
        logger.info("task-store request: %s %s headers=%s", method, url, headers)

    def on_response(self, request: PipelineRequest, response: PipelineResponse) -> None:
        http_response = response.http_response
        status = getattr(http_response, "status_code", 0)
        if status >= 500:
            level = logging.ERROR
        elif status >= 400:
            level = logging.WARNING
        else:
            level = logging.INFO
        if not logger.isEnabledFor(level):
            return
        method = request.http_request.method
        url = str(request.http_request.url)
        resp_headers = _redact_headers(getattr(http_response, "headers", {}), _ALLOWED_RESPONSE_HEADERS)
        logger.log(
            level,
            "task-store response: %s %s -> %d headers=%s",
            method,
            url,
            status,
            resp_headers,
        )
