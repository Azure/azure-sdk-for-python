"""Error model types for request validation failures."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .._generated import ApiErrorResponse as ApiErrorResponseType
    from .._generated import Error as ErrorType
else:
    ApiErrorResponseType = Any
    ErrorType = Any

try:
    from .._generated import ApiErrorResponse, Error
except Exception:  # pragma: no cover - allows isolated unit testing when generated deps are unavailable.
    class _GeneratedUnavailable:
        def __init__(self, *_args: Any, **_kwargs: Any) -> None:
            raise ModuleNotFoundError(
                "generated contract models are unavailable; run generation to restore runtime dependencies"
            )

    ApiErrorResponse = _GeneratedUnavailable  # type: ignore[assignment]
    Error = _GeneratedUnavailable  # type: ignore[assignment]


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

    def to_error(self) -> ErrorType:
        """Convert this validation error to the generated ``Error`` model."""
        return Error(
            code=self.code,
            message=self.message,
            param=self.param,
            type=self.error_type,
            debug_info=self.debug_info,
        )

    def to_api_error_response(self) -> ApiErrorResponseType:
        """Convert this validation error to the generated API error envelope."""
        return ApiErrorResponse(error=self.to_error())
