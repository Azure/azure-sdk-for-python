# The MIT License (MIT)
# Copyright (c) 2023 Microsoft Corporation

from typing import Any
try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal


class BatchOperationResponse:
    operation: dict
    """Operation that was sent as part of the batch request."""
    operation_response: dict
    """The operation response."""
    kind: Literal["BatchOperationResponse"] = "BatchOperationResponse"
    """Error kind - "BatchOperationResponse"."""

    def __init__(self, **kwargs: Any) -> None:
        self.operation = kwargs.get("operation", None)
        self.operation_response = kwargs.get("operation_response", None)
        self.kind: Literal["BatchOperationResponse"] = "BatchOperationResponse"

    def __repr__(self) -> str:
        return (
            f"OperationResult(operation={self.operation}, "
            f"operation_response={self.operation_response}, "
            f"kind={self.kind})"[:1024]
        )


class BatchOperationError:
    operation: dict
    """Operation that was sent as part of the batch request."""
    operation_response: dict
    """The operation response."""
    error: str
    """The error message for the operation."""
    kind: Literal["BatchOperationError"] = "BatchOperationError"
    """Error kind - "BatchOperationError"."""

    def __init__(self, **kwargs: Any) -> None:
        self.operation = kwargs.get("operation", None)
        self.operation_response = kwargs.get("operation_response", None)
        self.error = kwargs.get("error", None)
        self.kind: Literal["BatchOperationError"] = "BatchOperationError"

    def __repr__(self) -> str:
        return (
            f"OperationResult(operation={self.operation}, "
            f"operation_response={self.operation_response}, "
            f"error={self.error}, "
            f"kind={self.kind})"[:1024]
        )