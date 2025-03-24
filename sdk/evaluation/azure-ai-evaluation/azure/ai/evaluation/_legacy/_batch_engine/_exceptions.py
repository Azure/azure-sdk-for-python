# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from ..._exceptions import ErrorCategory, ErrorBlame, ErrorTarget, EvaluationException


class BatchEngineError(EvaluationException):
    """Exception class for batch engine errors.

    This exception is used to indicate that the error was caused by or in the batch engine.

    :param message: The error message.
    :type message: str
    """

    def __init__(self, message: str, **kwargs):
        kwargs.setdefault("category", ErrorCategory.FAILED_EXECUTION)
        kwargs.setdefault("target", ErrorTarget.EVAL_RUN)
        kwargs.setdefault("blame", ErrorBlame.UNKNOWN)

        super().__init__(message, **kwargs)


class BatchEngineValidationError(BatchEngineError):
    """Exception raised when validation fails

    :param message: The error message.
    :type message: str
    """

    def __init__(self, message: str, **kwargs):
        kwargs.setdefault("category", ErrorCategory.INVALID_VALUE)
        kwargs.setdefault("blame", ErrorBlame.USER_ERROR)
        super().__init__(message, **kwargs)


class BatchEngineTimeoutError(BatchEngineError):
    """Exception raised when a batch engine operation times out.

    :param message: The error message.
    :type message: str
    """

    def __init__(self, message: str, **kwargs):
        kwargs.setdefault("category", ErrorCategory.FAILED_EXECUTION)
        kwargs.setdefault("blame", ErrorBlame.SYSTEM_ERROR)
        super().__init__(message, **kwargs)


class BatchEngineCanceledError(BatchEngineError):
    """Exception raised when a batch engine operation is canceled.

    :param message: The error message.
    :type message: str
    """

    def __init__(self, message: str, **kwargs):
        kwargs.setdefault("category", ErrorCategory.FAILED_EXECUTION)
        kwargs.setdefault("blame", ErrorBlame.USER_ERROR)
        super().__init__(message, **kwargs)


class BatchEngineRunFailedError(BatchEngineError):
    """Exception raised when a batch engine run fails.

    :param message: The error message.
    :type message: str
    """

    def __init__(self, message: str, **kwargs):
        kwargs.setdefault("category", ErrorCategory.FAILED_EXECUTION)
        kwargs.setdefault("blame", ErrorBlame.SYSTEM_ERROR)
        super().__init__(message, **kwargs)


class BatchEnginePartialError(BatchEngineError):
    """Exception raised when a batch engine run has some successfull lines, mixed in
    with some failures.

    :param message: The error message.
    :type message: str
    """

    def __init__(self, message: str, **kwargs):
        kwargs.setdefault("category", ErrorCategory.FAILED_EXECUTION)
        kwargs.setdefault("blame", ErrorBlame.SYSTEM_ERROR)
        super().__init__(message, **kwargs)
