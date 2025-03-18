# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.ai.evaluation._exceptions import ErrorCategory, ErrorBlame, ErrorTarget, EvaluationException


class PromptyException(EvaluationException):
    """Exception class for Prompty related errors.

    This exception is used to indicate that the error was caused by Prompty execution.

    :param message: The error message.
    :type message: str
    """

    def __init__(self, message: str, **kwargs):
        kwargs.setdefault("category", ErrorCategory.INVALID_VALUE)
        kwargs.setdefault("target", ErrorTarget.UNKNOWN)
        kwargs.setdefault("blame", ErrorBlame.USER_ERROR)

        super().__init__(message, **kwargs)


class MissingRequiredInputError(PromptyException):
    """Exception raised when missing required input"""

    def __init__(self, message: str, **kwargs):
        kwargs.setdefault("category", ErrorCategory.MISSING_FIELD)
        kwargs.setdefault("target", ErrorTarget.EVAL_RUN)
        super().__init__(message, **kwargs)


class InvalidInputError(PromptyException):
    """Exception raised when an input is invalid, could not be loaded, or is not the expected format."""

    def __init__(self, message: str, **kwargs):
        kwargs.setdefault("category", ErrorCategory.INVALID_VALUE)
        kwargs.setdefault("target", ErrorTarget.EVAL_RUN)
        super().__init__(message, **kwargs)


class JinjaTemplateError(PromptyException):
    """Exception raised when the Jinja template is invalid or could not be rendered."""

    def __init__(self, message: str, **kwargs):
        kwargs.setdefault("category", ErrorCategory.INVALID_VALUE)
        kwargs.setdefault("target", ErrorTarget.EVAL_RUN)
        super().__init__(message, **kwargs)


class NotSupportedError(PromptyException):
    """Exception raised when the operation is not supported."""

    def __init__(self, message: str, **kwargs):
        kwargs.setdefault("category", ErrorCategory.INVALID_VALUE)
        kwargs.setdefault("target", ErrorTarget.UNKNOWN)
        kwargs.setdefault("blame", ErrorBlame.SYSTEM_ERROR)
        super().__init__(message, **kwargs)
