# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Validation utilities for request and response models."""

from __future__ import annotations

from typing import Any, Mapping

from starlette.responses import JSONResponse

from azure.ai.agentserver.responses._id_generator import IdGenerator
from azure.ai.agentserver.responses._options import ResponsesServerOptions
from azure.ai.agentserver.responses.models._generated import ApiErrorResponse, CreateResponse, Error
from azure.ai.agentserver.responses.models._generated._validators import validate_CreateResponse
from azure.ai.agentserver.responses.models.errors import RequestValidationError


def parse_create_response(payload: Mapping[str, Any]) -> CreateResponse:
    """Parse incoming JSON payload into the generated ``CreateResponse`` model.

    :param payload: Raw request payload mapping.
    :type payload: Mapping[str, Any]
    :returns: Parsed generated create response model.
    :rtype: CreateResponse
    :raises RequestValidationError: If payload is not an object or cannot be parsed.
    """
    if not isinstance(payload, Mapping):
        raise RequestValidationError("request body must be a JSON object", code="invalid_request")

    validation_errors = validate_CreateResponse(payload)
    if validation_errors:
        details = [
            {
                "code": "invalid_value",
                "message": e.get("message", ""),
                "param": ("$" + e.get("path", "")) if e.get("path", "").startswith(".") else e.get("path", ""),
            }
            for e in validation_errors
        ]
        raise RequestValidationError(
            "request body failed schema validation",
            code="invalid_request",
            details=details,
        )

    try:
        return CreateResponse(payload)
    except Exception as exc:  # pragma: no cover - generated model raises implementation-specific errors.
        raise RequestValidationError(
            "request body failed schema validation",
            code="invalid_request",
            debug_info={"exception_type": type(exc).__name__, "detail": str(exc)},
        ) from exc


def normalize_create_response(
    request: CreateResponse,
    options: ResponsesServerOptions | None,
) -> CreateResponse:
    """Apply server-side defaults to a parsed create request model.

    :param request: The parsed create response model to normalize.
    :type request: CreateResponse
    :param options: Server runtime options containing defaults, or ``None``.
    :type options: ResponsesServerOptions | None
    :return: The same model instance with defaults applied.
    :rtype: CreateResponse
    """
    if (request.model is None or (isinstance(request.model, str) and not request.model.strip())) and options:
        request.model = options.default_model

    if isinstance(request.model, str):
        request.model = request.model.strip() or ""
    elif request.model is None:
        request.model = ""

    return request


def validate_create_response(request: CreateResponse) -> None:
    """Validate create request semantics not enforced by generated model typing.

    :param request: The parsed create response model to validate.
    :type request: CreateResponse
    :raises RequestValidationError: If semantic preconditions are violated.
    """
    store_enabled = True if request.store is None else bool(request.store)

    if request.background and not store_enabled:
        raise RequestValidationError(
            "background=true requires store=true",
            code="unsupported_parameter",
            param="background",
        )

    if request.stream_options is not None and request.stream is not True:
        raise RequestValidationError(
            "stream_options requires stream=true",
            code="invalid_mode",
            param="stream",
        )

    # B22: model is optional — resolved to default in normalize_create_response()

    # Metadata constraints: ≤16 keys, key ≤64 chars, value ≤512 chars
    metadata = getattr(request, "metadata", None)
    if metadata is not None and hasattr(metadata, "items"):
        if len(metadata) > 16:
            raise RequestValidationError(
                "metadata must have at most 16 key-value pairs",
                code="invalid_request",
                param="metadata",
            )
        for key, value in metadata.items():
            if isinstance(key, str) and len(key) > 64:
                raise RequestValidationError(
                    f"metadata key '{key[:64]}...' exceeds maximum length of 64 characters",
                    code="invalid_request",
                    param="metadata",
                )
            if isinstance(value, str) and len(value) > 512:
                raise RequestValidationError(
                    f"metadata value for key '{key}' exceeds maximum length of 512 characters",
                    code="invalid_request",
                    param="metadata",
                )

    # Validate previous_response_id format (must be a valid caresp ID)
    prev_id = getattr(request, "previous_response_id", None)
    if isinstance(prev_id, str) and prev_id:
        is_valid, _ = IdGenerator.is_valid(prev_id, allowed_prefixes=["caresp"])
        if not is_valid:
            raise RequestValidationError(
                "Malformed identifier.",
                code="invalid_parameters",
                param="previous_response_id",
            )


def parse_and_validate_create_response(
    payload: Mapping[str, Any],
    *,
    options: ResponsesServerOptions | None = None,
) -> CreateResponse:
    """Parse, normalize, and validate a create request using generated models.

    :param payload: Raw request payload mapping.
    :type payload: Mapping[str, Any]
    :keyword options: Server runtime options for defaults, or ``None``.
    :keyword type options: ResponsesServerOptions | None
    :return: A fully validated ``CreateResponse`` model.
    :rtype: CreateResponse
    :raises RequestValidationError: If parsing or validation fails.
    """
    request = parse_create_response(payload)
    request = normalize_create_response(request, options)
    validate_create_response(request)
    return request


def build_api_error_response(
    message: str,
    *,
    code: str,
    param: str | None = None,
    error_type: str = "invalid_request_error",
    debug_info: dict[str, Any] | None = None,
) -> ApiErrorResponse:
    """Build a generated ``ApiErrorResponse`` envelope for client-visible failures.

    :param message: Human-readable error message.
    :type message: str
    :keyword code: Machine-readable error code.
    :keyword type code: str
    :keyword param: The request parameter that caused the error, or ``None``.
    :keyword type param: str | None
    :keyword error_type: Error type category (default ``"invalid_request_error"``).
    :keyword type error_type: str
    :keyword debug_info: Optional debug information dictionary.
    :keyword type debug_info: dict[str, Any] | None
    :return: A generated ``ApiErrorResponse`` envelope.
    :rtype: ApiErrorResponse
    """
    return ApiErrorResponse(
        error=Error(
            code=code,
            message=message,
            param=param,
            type=error_type,
            debug_info=debug_info,
        )
    )


def build_not_found_error_response(
    resource_id: str,
    *,
    param: str = "response_id",
    resource_name: str = "response",
) -> ApiErrorResponse:
    """Build a canonical generated not-found error envelope.

    :param resource_id: The ID of the resource that was not found.
    :type resource_id: str
    :keyword param: The parameter name to include in the error (default ``"response_id"``).
    :keyword type param: str
    :keyword resource_name: Display name for the resource type (default ``"response"``).
    :keyword type resource_name: str
    :return: A generated ``ApiErrorResponse`` envelope with not-found error.
    :rtype: ApiErrorResponse
    """
    return build_api_error_response(
        message=f"{resource_name} '{resource_id}' was not found",
        code="invalid_request_error",
        param=param,
        error_type="invalid_request_error",
    )


def build_invalid_mode_error_response(
    message: str,
    *,
    param: str | None = None,
) -> ApiErrorResponse:
    """Build a canonical generated invalid-mode error envelope.

    :param message: Human-readable error message.
    :type message: str
    :keyword param: The request parameter that caused the error, or ``None``.
    :keyword type param: str | None
    :return: A generated ``ApiErrorResponse`` envelope with invalid-mode error.
    :rtype: ApiErrorResponse
    """
    return build_api_error_response(
        message=message,
        code="invalid_request_error",
        param=param,
        error_type="invalid_request_error",
    )


def to_api_error_response(error: Exception) -> ApiErrorResponse:
    """Map a Python exception to a generated API error envelope.

    :param error: The exception to convert.
    :type error: Exception
    :return: A generated ``ApiErrorResponse`` envelope.
    :rtype: ApiErrorResponse
    """
    if isinstance(error, RequestValidationError):
        return error.to_api_error_response()

    if isinstance(error, ValueError):
        return build_api_error_response(
            message=str(error) or "invalid request",
            code="invalid_request_error",
            error_type="invalid_request_error",
        )

    return build_api_error_response(
        message="internal server error",
        code="server_error",
        error_type="server_error",
    )


# ---------------------------------------------------------------------------
# HTTP error response factories (moved from _http_errors.py)
# ---------------------------------------------------------------------------


def _json_payload(value: Any) -> Any:
    """Convert a value to a JSON-serializable form.

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
    request_id: str | None = None,
) -> JSONResponse:
    """Build a standard API error ``JSONResponse``.

    :keyword message: Human-readable error message.
    :keyword code: Machine-readable error code.
    :keyword headers: HTTP headers to include in the response.
    :keyword param: Optional parameter name associated with the error.
    :keyword status_code: HTTP status code for the response.
    :keyword error_type: The error type category.
    :keyword request_id: Resolved ``x-request-id`` value to embed in ``error.additionalInfo``.
    :return: A JSONResponse containing the error payload.
    :rtype: JSONResponse
    """
    payload = _json_payload(build_api_error_response(message=message, code=code, param=param, error_type=error_type))
    if request_id and isinstance(payload, dict):
        _enrich_error_payload(payload, request_id)
    return JSONResponse(payload, status_code=status_code, headers=headers)


def error_response(error: Exception, headers: dict[str, str], request_id: str | None = None) -> JSONResponse:
    """Map an exception to an appropriate HTTP error ``JSONResponse``.

    :param error: The exception to convert to an error response.
    :type error: Exception
    :param headers: HTTP headers to include in the response.
    :type headers: dict[str, str]
    :param request_id: Resolved ``x-request-id`` value to embed in ``error.additionalInfo``.
    :type request_id: str | None
    :return: A JSONResponse with the appropriate status code and error payload.
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
    if request_id and isinstance(payload, dict):
        _enrich_error_payload(payload, request_id)
    return JSONResponse(payload, status_code=status_code, headers=headers)


def not_found_response(
    response_id: str, headers: dict[str, str], request_id: str | None = None
) -> JSONResponse:
    """Build a 404 Not Found error response.

    :param response_id: The ID of the response that was not found.
    :type response_id: str
    :param headers: HTTP headers to include in the response.
    :type headers: dict[str, str]
    :param request_id: Resolved ``x-request-id`` value to embed in ``error.additionalInfo``.
    :type request_id: str | None
    :return: A 404 JSONResponse.
    :rtype: JSONResponse
    """
    return _api_error(
        message=f"Response with id '{response_id}' not found.",
        code="invalid_request_error",
        param="response_id",
        error_type="invalid_request_error",
        status_code=404,
        headers=headers,
        request_id=request_id,
    )


def invalid_request_response(
    message: str, headers: dict[str, str], *, param: str | None = None, request_id: str | None = None
) -> JSONResponse:
    """Build a 400 Bad Request error response.

    :param message: Human-readable error message.
    :type message: str
    :param headers: HTTP headers to include in the response.
    :type headers: dict[str, str]
    :keyword param: Optional parameter name associated with the error.
    :keyword request_id: Resolved ``x-request-id`` value to embed in ``error.additionalInfo``.
    :return: A 400 JSONResponse.
    :rtype: JSONResponse
    """
    return _api_error(
        message=message,
        code="invalid_request_error",
        param=param,
        error_type="invalid_request_error",
        status_code=400,
        headers=headers,
        request_id=request_id,
    )


def invalid_parameters_response(
    message: str, headers: dict[str, str], *, param: str | None = None, request_id: str | None = None
) -> JSONResponse:
    """Build a 400 Bad Request error response with ``code: "invalid_parameters"``.

    Used for malformed identifier validation (spec rule B40).

    :param message: Human-readable error message.
    :type message: str
    :param headers: HTTP headers to include in the response.
    :type headers: dict[str, str]
    :keyword param: Optional parameter name associated with the error.
    :keyword request_id: Resolved ``x-request-id`` value to embed in ``error.additionalInfo``.
    :return: A 400 JSONResponse.
    :rtype: JSONResponse
    """
    return _api_error(
        message=message,
        code="invalid_parameters",
        param=param,
        error_type="invalid_request_error",
        status_code=400,
        headers=headers,
        request_id=request_id,
    )


def invalid_mode_response(
    message: str, headers: dict[str, str], *, param: str | None = None, request_id: str | None = None
) -> JSONResponse:
    """Build a 400 Bad Request error response for an invalid mode combination.

    :param message: Human-readable error message.
    :type message: str
    :param headers: HTTP headers to include in the response.
    :type headers: dict[str, str]
    :keyword param: Optional parameter name associated with the error.
    :keyword request_id: Resolved ``x-request-id`` value to embed in ``error.additionalInfo``.
    :return: A 400 JSONResponse.
    :rtype: JSONResponse
    """
    payload = _json_payload(build_invalid_mode_error_response(message, param=param))
    if request_id and isinstance(payload, dict):
        _enrich_error_payload(payload, request_id)
    return JSONResponse(payload, status_code=400, headers=headers)


def service_unavailable_response(
    message: str, headers: dict[str, str], request_id: str | None = None
) -> JSONResponse:
    """Build a 503 Service Unavailable error response.

    :param message: Human-readable error message.
    :type message: str
    :param headers: HTTP headers to include in the response.
    :type headers: dict[str, str]
    :param request_id: Resolved ``x-request-id`` value to embed in ``error.additionalInfo``.
    :type request_id: str | None
    :return: A 503 JSONResponse.
    :rtype: JSONResponse
    """
    return _api_error(
        message=message,
        code="service_unavailable",
        param=None,
        error_type="server_error",
        status_code=503,
        headers=headers,
        request_id=request_id,
    )


def deleted_response(response_id: str, headers: dict[str, str], request_id: str | None = None) -> JSONResponse:
    """Build a 404 error response indicating the response has been deleted.

    Per spec, all endpoints treat deleted responses as not-found (HTTP 404).

    :param response_id: The ID of the deleted response.
    :type response_id: str
    :param headers: HTTP headers to include in the response.
    :type headers: dict[str, str]
    :param request_id: Resolved ``x-request-id`` value to embed in ``error.additionalInfo``.
    :type request_id: str | None
    :return: A 404 JSONResponse.
    :rtype: JSONResponse
    """
    return not_found_response(response_id, headers, request_id=request_id)


def _enrich_error_payload(payload: dict[str, Any], request_id: str) -> None:
    """Inject ``request_id`` into the ``error.additionalInfo`` of an error payload.

    Mutates the payload dict in-place.  If ``error.additionalInfo`` already
    contains a ``request_id`` key, it is left unchanged.

    :param payload: The error response payload dict.
    :type payload: dict[str, Any]
    :param request_id: The resolved request ID value.
    :type request_id: str
    """
    error = payload.get("error")
    if not isinstance(error, dict):
        return
    additional_info = error.get("additionalInfo")
    if not isinstance(additional_info, dict):
        additional_info = {}
        error["additionalInfo"] = additional_info
    if "request_id" not in additional_info:
        additional_info["request_id"] = request_id
