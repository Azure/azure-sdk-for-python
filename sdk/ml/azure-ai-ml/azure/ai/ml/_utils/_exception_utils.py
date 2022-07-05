# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.ai.ml._ml_exceptions import MlException, ErrorTarget, ErrorCategory


class EmptyDirectoryError(MlException):
    def __init__(
        self,
        message: str,
        no_personal_data_message: str,
        target: ErrorTarget = ErrorTarget.UNKNOWN,
        error_category: ErrorCategory = ErrorCategory.UNKNOWN,
    ):
        self.message = message
        super(EmptyDirectoryError, self).__init__(
            message=self.message,
            no_personal_data_message=no_personal_data_message,
            target=target,
            error_category=error_category,
        )
