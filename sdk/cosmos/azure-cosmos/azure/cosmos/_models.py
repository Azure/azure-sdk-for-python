# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# pylint: disable=unused-argument
from typing import Any
from typing_extensions import Literal


class OperationResult:
    """OperationResult is a result object which contains
    the response of an individual document operation.
    """
    operation: dict
    """Operation that was sent as part of the bulk request."""
    operation_response: dict
    """The bulk operation response."""
    is_error: Literal[False] = False
    """Boolean check for error item when iterating over list of
        results. Always False for an instance of a OperationResult."""
    kind: Literal["OperationResult"] = "OperationResult"
    """The operation result kind - "OperationResult"."""

    def __init__(self, **kwargs: Any) -> None:
        self.operation = kwargs.get("operation", None)
        self.operation_response = kwargs.get("operation_response", None)
        self.is_error: Literal[False] = False
        self.kind: Literal["OperationResult"] = "OperationResult"

    def __repr__(self) -> str:
        return (
            f"OperationResult(operation={self.operation}, "
            f"operation_response={self.operation_response}, "
            f"is_error={self.is_error}, "
            f"kind={self.kind})"[:1024]
        )


class OperationError:
    """OperationError is an error object which represents an error on
    the individual document operation.
    """
    operation: dict  # pylint: disable=redefined-builtin
    """Operation that was sent as part of the bulk request."""
    operation_response: dict
    """The bulk operation response."""
    is_error: Literal[True] = True
    """Boolean check for error item when iterating over list of
        results. Always True for an instance of a OperationError."""
    error_status: str
    """The string representation of the returned error code."""
    kind: Literal["OperationError"] = "OperationError"
    """Error kind - "OperationError"."""

    def __init__(self, **kwargs: Any) -> None:
        self.operation = kwargs.get("operation", None)
        self.operation_response = kwargs.get("operation_response", None)
        self.is_error: Literal[True] = True
        self.error_status = kwargs.get("error_status")
        self.kind: Literal["OperationError"] = "OperationError"

    def __getattr__(self, attr: str) -> Any:
        result_set = set()
        result_set.update(
            RecognizeEntitiesResult().keys()  # type: ignore[operator]
        )
        result_attrs = result_set.difference(OperationError().keys())
        if attr in result_attrs:
            raise AttributeError(
                "'DocumentError' object has no attribute '{}'. The service was unable to process this document:\n"
                "Document Id: {}\nError: {} - {}\n".format(
                    attr, self.id, self.error.code, self.error.message
                )
            )
        raise AttributeError(
            f"'DocumentError' object has no attribute '{attr}'"
        )

    def __repr__(self) -> str:
        return f"DocumentError(operation={self.operation}, error={repr(self.error)}, " \
               f"is_error={self.is_error}, kind={self.kind})"[:1024]
