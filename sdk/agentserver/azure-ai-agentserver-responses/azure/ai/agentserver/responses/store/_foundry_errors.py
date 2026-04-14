# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Exception hierarchy for Foundry storage API errors."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from azure.core.rest import HttpResponse


class FoundryStorageError(Exception):
    """Base class for errors returned by the Foundry storage API."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class FoundryResourceNotFoundError(FoundryStorageError):
    """Raised when the requested resource does not exist (HTTP 404)."""


class FoundryBadRequestError(FoundryStorageError):
    """Raised for invalid-request or conflict errors (HTTP 400, 409)."""


class FoundryApiError(FoundryStorageError):
    """Raised for all other non-success HTTP responses."""

    def __init__(self, message: str, status_code: int) -> None:
        super().__init__(message)
        self.status_code = status_code


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

    message = _extract_error_message(response, status)

    if status == 404:
        raise FoundryResourceNotFoundError(message)
    if status in (400, 409):
        raise FoundryBadRequestError(message)
    raise FoundryApiError(message, status)


def _extract_error_message(response: "HttpResponse", status: int) -> str:
    """Extract an error message from *response*, falling back to a generic string.

    :param response: The HTTP response whose body is inspected.
    :type response: ~azure.core.rest.HttpResponse
    :param status: The HTTP status code of the response.
    :type status: int
    :returns: A human-readable error message string.
    :rtype: str
    """
    try:
        body = response.text()
        if body:
            data = json.loads(body)
            error = data.get("error")
            if isinstance(error, dict):
                msg = error.get("message")
                if msg:
                    return str(msg)
    except Exception:  # pylint: disable=broad-except
        pass
    return f"Foundry storage request failed with HTTP {status}."
