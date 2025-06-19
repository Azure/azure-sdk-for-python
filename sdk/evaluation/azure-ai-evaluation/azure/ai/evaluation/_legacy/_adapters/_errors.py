# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Any
from typing_extensions import TypeAlias


try:
    from promptflow.core._errors import MissingRequiredPackage
except ImportError:
    from azure.ai.evaluation._exceptions import ErrorBlame, ErrorCategory, ErrorTarget, EvaluationException

    class MissingRequiredPackage(EvaluationException):
        """Raised when a required package is missing.

        :param message: A message describing the error. This is the error message the user will see.
        :type message: str
        """

        def __init__(self, message: str, **kwargs: Any):
            kwargs.setdefault("category", ErrorCategory.MISSING_PACKAGE)
            kwargs.setdefault("blame", ErrorBlame.SYSTEM_ERROR)
            kwargs.setdefault("target", ErrorTarget.EVALUATE)
            kwargs.setdefault("internal_message", "Missing required package.")
            super().__init__(message=message, **kwargs)
