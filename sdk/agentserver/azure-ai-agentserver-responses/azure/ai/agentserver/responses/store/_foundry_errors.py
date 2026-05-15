# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Exception hierarchy for Foundry storage API errors."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from azure.ai.agentserver.core._platform_headers import PLATFORM_ERROR_TAG  # pylint: disable=import-error,no-name-in-module

if TYPE_CHECKING:
    from azure.core.rest import HttpResponse


class FoundryStorageError(Exception):
    """Base class for errors returned by the Foundry storage API."""

    def __init__(
        self,
        message: str,
        *,
        response_body: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.response_body = response_body


class FoundryResourceNotFoundError(FoundryStorageError):
    """Raised when the requested resource does not exist (HTTP 404)."""


class FoundryBadRequestError(FoundryStorageError):
    """Raised for invalid-request or conflict errors (HTTP 400, 409)."""


class FoundryApiError(FoundryStorageError):
    """Raised for all other non-success HTTP responses."""


def raise_for_storage_error(response: "HttpResponse") -> None:
    """Raise an appropriate :class:`FoundryStorageError` subclass if *response* is not successful.

    :param response: The HTTP response to inspect.
    :type response: ~azure.core.rest.HttpResponse
    :raises FoundryResourceNotFoundError: For HTTP 404.
    :raises FoundryBadRequestError: For HTTP 400 or 409.
    :raises FoundryApiError: For all other non-2xx responses.
    """
    status = response.status_code
    if 200 <= status < 300:
        return

    message, body = _extract_error_message(response, status)

    if status == 404:
        raise FoundryResourceNotFoundError(message, response_body=body)
    if status in (400, 409):
        raise FoundryBadRequestError(message, response_body=body)
    exc = FoundryApiError(message, response_body=body)
    # Tag non-client storage errors as platform errors so the error source
    # classification in response headers correctly reports "platform".
    setattr(exc, PLATFORM_ERROR_TAG, True)
    raise exc


def _extract_error_message(response: "HttpResponse", status: int) -> tuple[str, dict[str, Any] | None]:
    """Extract an error message and raw body from *response*.

    Returns a ``(message, body_dict)`` tuple.  *body_dict* is the parsed
    JSON body when it matches the Foundry error envelope shape, or ``None``
    when the body cannot be parsed.  This allows callers to forward the
    original Foundry error payload to clients without re-wrapping it.

    :param response: The HTTP response whose body is inspected.
    :type response: ~azure.core.rest.HttpResponse
    :param status: The HTTP status code of the response.
    :type status: int
    :returns: A ``(message, body_dict)`` tuple.
    :rtype: tuple[str, dict[str, Any] | None]
    """
    try:
        body = response.text()
        if body:
            data = json.loads(body)
            error = data.get("error")
            if isinstance(error, dict):
                msg = error.get("message")
                if msg:
                    return str(msg), data
    except Exception:  # pylint: disable=broad-except
        pass
    return f"Foundry storage request failed with HTTP {status}.", None
