# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.ai.evaluation._exceptions import EvaluationException, ErrorBlame, ErrorCategory


class EvaluationSaveError(EvaluationException):
    """Custom exception for errors during the evaluation save process.
    
    :param str message: The error message."""

    def __init__(self, message: str, **kwargs) -> None:
        kwargs.setdefault("category", ErrorCategory.INVALID_VALUE)
        kwargs.setdefault("blame", ErrorBlame.USER_ERROR)
        super().__init__(message, **kwargs)


class EvaluationLoadError(EvaluationException):
    """Custom exception for errors during the evaluation load process.
    
    :param str message: The error message."""

    def __init__(self, message: str, **kwargs) -> None:
        kwargs.setdefault("category", ErrorCategory.INVALID_VALUE)
        kwargs.setdefault("blame", ErrorBlame.USER_ERROR)
        super().__init__(message or "evaluator must be a function or a callable class", **kwargs)