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
    """Build a standard API error ``JSONResponse`` from individual fields."""
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
    return _api_error(
        message=f"Response with id '{response_id}' not found.",
        code="invalid_request",
        param="response_id",
        error_type="invalid_request_error",
        status_code=404,
        headers=headers,
    )


def _invalid_request(message: str, headers: dict[str, str], *, param: str | None = None) -> JSONResponse:
    return _api_error(
        message=message,
        code="invalid_request",
        param=param,
        error_type="invalid_request_error",
        status_code=400,
        headers=headers,
    )


def _invalid_mode(message: str, headers: dict[str, str], *, param: str | None = None) -> JSONResponse:
    payload = _json_payload(build_invalid_mode_error_response(message, param=param))
    return JSONResponse(payload, status_code=400, headers=headers)


def _service_unavailable(message: str, headers: dict[str, str]) -> JSONResponse:
    return _api_error(
        message=message,
        code="service_unavailable",
        param=None,
        error_type="server_error",
        status_code=503,
        headers=headers,
    )


def _deleted_response(response_id: str, headers: dict[str, str]) -> JSONResponse:
    return _invalid_request(
        f"Response with id '{response_id}' has been deleted.",
        headers,
        param="response_id",
    )
