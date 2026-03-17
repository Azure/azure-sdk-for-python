"""Validation utilities for request and response models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from ._options import ResponsesServerOptions

try:
    from ._generated import ApiErrorResponse, CreateResponse, Error
except Exception:  # pragma: no cover - allows isolated unit testing when generated deps are unavailable.
    class _GeneratedUnavailable:
        def __init__(self, *_args: Any, **_kwargs: Any) -> None:
            raise ModuleNotFoundError(
                "generated contract models are unavailable; run generation to restore runtime dependencies"
            )

    ApiErrorResponse = _GeneratedUnavailable  # type: ignore[assignment]
    CreateResponse = _GeneratedUnavailable  # type: ignore[assignment]
    Error = _GeneratedUnavailable  # type: ignore[assignment]

try:
    from ._generated import _validators as _generated_validators
except Exception:  # pragma: no cover - optional until validator generation is integrated in all environments.
    _generated_validators = None


@dataclass(slots=True)
class RequestValidationError(ValueError):
    """Represents a client-visible request validation failure."""

    message: str
    code: str = "invalid_request"
    param: str | None = None
    error_type: str = "invalid_request_error"
    debug_info: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        """Initialize the parent :class:`ValueError` message."""
        ValueError.__init__(self, self.message)

    def to_error(self) -> Error:
        """Convert this validation error to the generated ``Error`` model."""
        return Error(
            code=self.code,
            message=self.message,
            param=self.param,
            type=self.error_type,
            debug_info=self.debug_info,
        )

    def to_api_error_response(self) -> ApiErrorResponse:
        """Convert this validation error to the generated API error envelope."""
        return ApiErrorResponse(error=self.to_error())


def parse_create_response(payload: Mapping[str, Any]) -> CreateResponse:
    """Parse incoming JSON payload into the generated ``CreateResponse`` model.

    :param payload: Raw request payload mapping.
    :returns: Parsed generated create response model.
    :raises RequestValidationError: If payload is not an object or cannot be parsed.
    """
    if not isinstance(payload, Mapping):
        raise RequestValidationError("request body must be a JSON object", code="invalid_json")

    validator = getattr(_generated_validators, "validate_CreateResponse", None) if _generated_validators else None
    if callable(validator):
        validation_errors = validator(payload)
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
            param="stream_options",
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


def to_api_error_response(error: Exception) -> ApiErrorResponse:
    """Map a Python exception to a generated API error envelope."""
    if isinstance(error, RequestValidationError):
        return error.to_api_error_response()

    return build_api_error_response(
        message="internal server error",
        code="internal_error",
        error_type="server_error",
        debug_info={"exception_type": type(error).__name__},
    )
