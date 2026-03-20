# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Validation utilities for request and response models."""

from __future__ import annotations

from typing import Any, Mapping

from azure.ai.agentserver.responses._options import ResponsesServerOptions
from azure.ai.agentserver.responses.models._generated import ApiErrorResponse, CreateResponse, Error
from azure.ai.agentserver.responses.models._generated._validators import validate_CreateResponse
from azure.ai.agentserver.responses.models.errors import RequestValidationError


def parse_create_response(payload: Mapping[str, Any]) -> CreateResponse:
    """Parse incoming JSON payload into the generated ``CreateResponse`` model.

    :param payload: Raw request payload mapping.
    :returns: Parsed generated create response model.
    :raises RequestValidationError: If payload is not an object or cannot be parsed.
    """
    if not isinstance(payload, Mapping):
        raise RequestValidationError("request body must be a JSON object", code="invalid_request")

    validation_errors = validate_CreateResponse(payload)
    if validation_errors:
        raise RequestValidationError(
            "request body failed schema validation",
                code="invalid_request",
                debug_info={"errors": validation_errors},
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
    """Apply server-side defaults to a parsed create request model."""
    if (request.model is None or (isinstance(request.model, str) and not request.model.strip())) and options:
        request.model = options.default_model

    if isinstance(request.model, str):
        request.model = request.model.strip() or None

    return request


def validate_create_response(request: CreateResponse) -> None:
    """Validate create request semantics not enforced by generated model typing.

    :raises RequestValidationError: If semantic preconditions are violated.
    """
    store_enabled = True if request.store is None else bool(request.store)

    if request.background and not store_enabled:
        raise RequestValidationError(
            "background=true requires store=true",
            code="invalid_mode",
            param="store",
        )

    if request.stream_options is not None and request.stream is not True:
        raise RequestValidationError(
            "stream_options requires stream=true",
            code="invalid_mode",
            param="stream",
        )

    if request.model is None:
        raise RequestValidationError(
            "model is required",
            code="missing_required",
            param="model",
        )


def parse_and_validate_create_response(
    payload: Mapping[str, Any],
    *,
    options: ResponsesServerOptions | None = None,
) -> CreateResponse:
    """Parse, normalize, and validate a create request using generated models."""
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
    """Build a generated ``ApiErrorResponse`` envelope for client-visible failures."""
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
    """Build a canonical generated not-found error envelope."""
    return build_api_error_response(
        message=f"{resource_name} '{resource_id}' was not found",
        code="not_found",
        param=param,
        error_type="not_found_error",
    )


def build_invalid_mode_error_response(
    message: str,
    *,
    param: str | None = None,
) -> ApiErrorResponse:
    """Build a canonical generated invalid-mode error envelope."""
    return build_api_error_response(
        message=message,
        code="invalid_mode",
        param=param,
        error_type="invalid_request_error",
    )


def to_api_error_response(error: Exception) -> ApiErrorResponse:
    """Map a Python exception to a generated API error envelope."""
    if isinstance(error, RequestValidationError):
        return error.to_api_error_response()

    if isinstance(error, ValueError):
        return build_api_error_response(
            message=str(error) or "invalid request",
            code="invalid_request",
            error_type="invalid_request_error",
        )

    return build_api_error_response(
        message="internal server error",
        code="internal_error",
        error_type="server_error",
        debug_info={"exception_type": type(error).__name__},
    )
