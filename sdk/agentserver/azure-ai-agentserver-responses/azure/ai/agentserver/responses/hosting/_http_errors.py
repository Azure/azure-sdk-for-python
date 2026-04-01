# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""HTTP error response factory functions for the Responses server."""

from __future__ import annotations

from typing import Any

from starlette.responses import JSONResponse

from ._validation import (
    build_api_error_response,
    build_invalid_mode_error_response,
    to_api_error_response,
)


def _json_payload(value: Any) -> Any:
    """Convert a value to a JSON-serializable form.

    If the value has an ``as_dict`` method (e.g. generated models), it is called;
    otherwise the value is returned as-is.

    :param value: The value to convert.
    :type value: Any
    :return: A JSON-serializable representation of the value.
    :rtype: Any
    """
    if hasattr(value, "as_dict"):
        return value.as_dict()  # type: ignore[no-any-return]
    return value


def _api_error(
    *,
    message: str,
    code: str,
    param: str | None = None,
    error_type: str = "invalid_request_error",
    status_code: int,
    headers: dict[str, str],
) -> JSONResponse:
    """Build a standard API error ``JSONResponse`` from individual fields.

    :keyword message: Human-readable error message.
    :keyword type message: str
    :keyword code: Machine-readable error code.
    :keyword type code: str
    :keyword param: The request parameter that caused the error, or ``None``.
    :keyword type param: str | None
    :keyword error_type: Error type category (default ``"invalid_request_error"``).
    :keyword type error_type: str
    :keyword status_code: HTTP status code for the response.
    :keyword type status_code: int
    :keyword headers: Response headers to include.
    :keyword type headers: dict[str, str]
    :return: A ``JSONResponse`` with the error envelope.
    :rtype: JSONResponse
    """
    payload = _json_payload(
        build_api_error_response(
            message=message,
            code=code,
            param=param,
            error_type=error_type,
        )
    )
    return JSONResponse(payload, status_code=status_code, headers=headers)


def _error_response(error: Exception, headers: dict[str, str]) -> JSONResponse:
    """Map an exception to an appropriate HTTP error ``JSONResponse``.

    The HTTP status code is inferred from the error type field in the envelope.

    :param error: The exception to convert.
    :type error: Exception
    :param headers: Response headers to include.
    :type headers: dict[str, str]
    :return: A ``JSONResponse`` with the mapped error and status code.
    :rtype: JSONResponse
    """
    envelope = to_api_error_response(error)
    payload = _json_payload(envelope)
    error_type = payload.get("error", {}).get("type") if isinstance(payload, dict) else None

    status_code = 500
    if error_type == "invalid_request_error":
        status_code = 400
    elif error_type == "not_found_error":
        status_code = 404

    return JSONResponse(payload, status_code=status_code, headers=headers)


def _not_found(response_id: str, headers: dict[str, str]) -> JSONResponse:
    """Build a 404 Not Found error response for a missing response ID.

    :param response_id: The response ID that was not found.
    :type response_id: str
    :param headers: Response headers to include.
    :type headers: dict[str, str]
    :return: A 404 ``JSONResponse``.
    :rtype: JSONResponse
    """
    return _api_error(
        message=f"Response with id '{response_id}' not found.",
        code="invalid_request",
        param="response_id",
        error_type="invalid_request_error",
        status_code=404,
        headers=headers,
    )


def _invalid_request(message: str, headers: dict[str, str], *, param: str | None = None) -> JSONResponse:
    """Build a 400 Bad Request error response for an invalid request.

    :param message: Human-readable error message.
    :type message: str
    :param headers: Response headers to include.
    :type headers: dict[str, str]
    :keyword param: The request parameter that caused the error, or ``None``.
    :keyword type param: str | None
    :return: A 400 ``JSONResponse``.
    :rtype: JSONResponse
    """
    return _api_error(
        message=message,
        code="invalid_request",
        param=param,
        error_type="invalid_request_error",
        status_code=400,
        headers=headers,
    )


def _invalid_mode(message: str, headers: dict[str, str], *, param: str | None = None) -> JSONResponse:
    """Build a 400 Bad Request error response for an invalid mode combination.

    :param message: Human-readable error message.
    :type message: str
    :param headers: Response headers to include.
    :type headers: dict[str, str]
    :keyword param: The request parameter that caused the error, or ``None``.
    :keyword type param: str | None
    :return: A 400 ``JSONResponse`` with an ``invalid_mode`` error code.
    :rtype: JSONResponse
    """
    payload = _json_payload(build_invalid_mode_error_response(message, param=param))
    return JSONResponse(payload, status_code=400, headers=headers)


def _service_unavailable(message: str, headers: dict[str, str]) -> JSONResponse:
    """Build a 503 Service Unavailable error response.

    :param message: Human-readable error message.
    :type message: str
    :param headers: Response headers to include.
    :type headers: dict[str, str]
    :return: A 503 ``JSONResponse``.
    :rtype: JSONResponse
    """
    return _api_error(
        message=message,
        code="service_unavailable",
        param=None,
        error_type="server_error",
        status_code=503,
        headers=headers,
    )


def _deleted_response(response_id: str, headers: dict[str, str]) -> JSONResponse:
    """Build a 400 error response indicating the response has been deleted.

    :param response_id: The response ID that was deleted.
    :type response_id: str
    :param headers: Response headers to include.
    :type headers: dict[str, str]
    :return: A 400 ``JSONResponse``.
    :rtype: JSONResponse
    """
    return _invalid_request(
        f"Response with id '{response_id}' has been deleted.",
        headers,
        param="response_id",
    )
