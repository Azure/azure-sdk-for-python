# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Exception hierarchy for Foundry storage API errors."""

# pylint: disable=docstring-missing-param,docstring-missing-return,docstring-missing-rtype

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, Union

from azure.ai.agentserver.core._platform_headers import PLATFORM_ERROR_TAG

if TYPE_CHECKING:
    from azure.core.rest import AsyncHttpResponse, HttpResponse

    _AnyHttpResponse = Union[HttpResponse, AsyncHttpResponse]


class FoundryStorageError(Exception):
    """Base class for errors returned by the Foundry storage API."""

    def __init__(
        self,
        message: str,
        *,
        response_body: dict[str, Any] | None = None,
        status_code: int | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.response_body = response_body
        self.status_code = status_code


class FoundryStorageNotFoundError(FoundryStorageError):
    """Raised when the requested resource does not exist (HTTP 404)."""


class FoundryStorageBadRequestError(FoundryStorageError):
    """Raised for invalid-request errors (HTTP 400)."""

    def __init__(
        self,
        message: str,
        *,
        response_body: dict[str, Any] | None = None,
        status_code: int | None = None,
        param: str | None = None,
    ) -> None:
        super().__init__(message, response_body=response_body, status_code=status_code)
        self.param = param


class FoundryStorageConflictError(FoundryStorageBadRequestError):
    """Raised when the requested create/update conflicts with an existing resource (HTTP 409)."""


class FoundryStoragePreconditionError(FoundryStorageError):
    """Raised when an ``If-Match`` precondition fails on a single-item write."""

    def __init__(
        self,
        message: str,
        *,
        response_body: dict[str, Any] | None = None,
        status_code: int | None = None,
        current_etag: str | None = None,
    ) -> None:
        super().__init__(message, response_body=response_body, status_code=status_code)
        self.current_etag = current_etag


class FoundryStorageApiError(FoundryStorageError):
    """Raised for all other non-success HTTP responses."""


def raise_for_storage_error(response: "_AnyHttpResponse") -> None:
    """Raise an appropriate :class:`FoundryStorageError` subclass for non-2xx responses."""
    status = response.status_code
    if 200 <= status < 300:
        return

    message, body = _extract_error_message(response, status)

    if status == 404:
        raise FoundryStorageNotFoundError(message, response_body=body, status_code=status)
    if status == 412:
        raise FoundryStoragePreconditionError(
            message,
            response_body=body,
            status_code=status,
            current_etag=response.headers.get("ETag"),
        )
    if status == 400:
        param = None
        if isinstance(body, dict):
            error = body.get("error")
            if isinstance(error, dict):
                raw_param = error.get("param")
                param = str(raw_param) if raw_param is not None else None
        raise FoundryStorageBadRequestError(message, response_body=body, status_code=status, param=param)
    if status == 409:
        raise FoundryStorageConflictError(message, response_body=body, status_code=status)
    exc = FoundryStorageApiError(message, response_body=body, status_code=status)
    setattr(exc, PLATFORM_ERROR_TAG, True)
    raise exc


def _extract_error_message(response: "_AnyHttpResponse", status: int) -> tuple[str, dict[str, Any] | None]:
    """Extract a Foundry error-envelope message from *response* when possible."""
    try:
        body = response.text()
        if body:
            data = json.loads(body)
            error = data.get("error")
            if isinstance(error, dict):
                message = error.get("message")
                if message:
                    return str(message), data
    except Exception:  # pylint: disable=broad-exception-caught
        pass
    return f"Foundry storage request failed with HTTP {status}.", None
