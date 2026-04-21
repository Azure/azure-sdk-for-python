# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Error model types for request validation failures."""

from __future__ import annotations

from typing import Any

from azure.ai.agentserver.responses.models._generated import ApiErrorResponse, Error


class RequestValidationError(ValueError):
    """Represents a client-visible request validation failure."""

    def __init__(
        self,
        message: str,
        *,
        code: str = "invalid_request_error",
        param: str | None = None,
        error_type: str = "invalid_request_error",
        debug_info: dict[str, Any] | None = None,
        details: list[dict[str, str]] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.param = param
        self.error_type = error_type
        self.debug_info = debug_info
        self.details = details

    def to_error(self) -> Error:
        """Convert this validation error to the generated ``Error`` model.

        :returns: An ``Error`` instance populated from this validation error's fields.
        :rtype: Error
        """
        detail_errors: list[Error] | None = None
        if self.details:
            detail_errors = [
                Error(
                    code=d.get("code", "invalid_value"),
                    message=d.get("message", ""),
                    param=d.get("param"),
                    type="invalid_request_error",
                )
                for d in self.details
            ]
        return Error(
            code=self.code,
            message=self.message,
            param=self.param,
            type=self.error_type,
            details=detail_errors,
        )

    def to_api_error_response(self) -> ApiErrorResponse:
        """Convert this validation error to the generated API error envelope.

        :returns: An ``ApiErrorResponse`` wrapping the generated ``Error``.
        :rtype: ApiErrorResponse
        """
        return ApiErrorResponse(error=self.to_error())
