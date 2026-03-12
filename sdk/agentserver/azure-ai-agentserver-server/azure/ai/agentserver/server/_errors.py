# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Standardised error response builder for AgentServer.

Every error returned by the framework uses the shape::

    {
      "error": {
        "code": "...",            // required – machine-readable error code
        "message": "...",         // required – human-readable description
        "details": [ ... ]        // optional – child errors
      }
    }
"""
from __future__ import annotations

from typing import Any, Optional

from starlette.responses import JSONResponse


def error_response(
    code: str,
    message: str,
    *,
    status_code: int,
    details: Optional[list[dict[str, Any]]] = None,
    headers: Optional[dict[str, str]] = None,
) -> JSONResponse:
    """Build a ``JSONResponse`` with the standard error envelope.

    :param code: Machine-readable error code (e.g. ``"internal_error"``).
    :type code: str
    :param message: Human-readable error message.
    :type message: str
    :keyword status_code: HTTP status code for the response.
    :paramtype status_code: int
    :keyword details: Child error objects, each with at least ``code`` and
        ``message`` keys.
    :paramtype details: Optional[list[dict[str, Any]]]
    :keyword headers: Extra HTTP headers to include on the response.
    :paramtype headers: Optional[dict[str, str]]
    :return: A ready-to-send JSON error response.
    :rtype: JSONResponse
    """
    body: dict[str, Any] = {"code": code, "message": message}
    if details is not None:
        body["details"] = details
    return JSONResponse(
        {"error": body}, status_code=status_code, headers=headers
    )
