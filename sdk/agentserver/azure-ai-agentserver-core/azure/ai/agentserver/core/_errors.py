# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Standardized error response builder for AgentHost.

Every error returned by the framework uses the shape::

    {
      "error": {
        "code": "...",            // required – machine-readable error code
        "message": "...",         // required – human-readable description
        "type": "...",            // optional – error type classification
        "details": [ ... ]        // optional – child errors
      }
    }

Usage::

    from azure.ai.agentserver.core import create_error_response

    return create_error_response("not_found", "Resource missing", status_code=404)
"""
from typing import Any, Optional

from starlette.responses import JSONResponse


def create_error_response(
    code: str,
    message: str,
    *,
    status_code: int,
    error_type: Optional[str] = None,
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
    :keyword error_type: Optional error type classification string.  When
        provided, included as ``"type"`` in the error body.
    :paramtype error_type: Optional[str]
    :keyword details: Child error objects, each with at least ``code`` and
        ``message`` keys.
    :paramtype details: Optional[list[dict[str, Any]]]
    :keyword headers: Extra HTTP headers to include on the response.
    :paramtype headers: Optional[dict[str, str]]
    :return: A ready-to-send JSON error response.
    :rtype: JSONResponse
    """
    body: dict[str, Any] = {"code": code, "message": message}
    if error_type is not None:
        body["type"] = error_type
    if details is not None:
        body["details"] = details
    return JSONResponse(
        {"error": body}, status_code=status_code, headers=headers
    )
