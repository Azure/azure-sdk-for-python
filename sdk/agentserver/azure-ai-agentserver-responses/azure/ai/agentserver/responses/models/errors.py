# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Error model types for request validation failures."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from azure.ai.agentserver.responses.models._generated import ApiErrorResponse, Error


@dataclass(slots=True)
class RequestValidationError(ValueError):
    """Represents a client-visible request validation failure."""

    message: str
    code: str = "invalid_request"
    param: str | None = None
    error_type: str = "invalid_request_error"
    debug_info: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        """Initialize the parent :class:`ValueError` message.

        Calls :meth:`ValueError.__init__` with the stored *message* so that
        ``str(err)`` returns the validation message.
        """
        ValueError.__init__(self, self.message)

    def to_error(self) -> Error:
        """Convert this validation error to the generated ``Error`` model.

        :returns: An ``Error`` instance populated from this validation error's fields.
        :rtype: Error
        """
        return Error(
            code=self.code,
            message=self.message,
            param=self.param,
            type=self.error_type,
            debug_info=self.debug_info,
        )

    def to_api_error_response(self) -> ApiErrorResponse:
        """Convert this validation error to the generated API error envelope.

        :returns: An ``ApiErrorResponse`` wrapping the generated ``Error``.
        :rtype: ApiErrorResponse
        """
        return ApiErrorResponse(error=self.to_error())
