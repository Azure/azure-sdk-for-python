# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=redefined-builtin,disable=unused-argument

from typing import Any, Dict, Optional

from azure.ai.ml.entities._feature_set.source_process_code_metadata import SourceProcessCodeMetadata
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationErrorType, ValidationException

from .delay_metadata import DelayMetadata
from .timestamp_column_metadata import TimestampColumnMetadata


class SourceMetadata(object):
    def __init__(
        self,
        *,
        type: str,
        timestamp_column: Optional[TimestampColumnMetadata] = None,
        path: Optional[str] = None,
        source_delay: Optional[DelayMetadata] = None,
        source_process_code: Optional[SourceProcessCodeMetadata] = None,
        dict: Optional[Dict] = None,
        **kwargs: Any,
    ):
        if type != "featureset":
            if not timestamp_column:
                msg = f"You need to provide timestamp_column for {type} feature source."
                raise ValidationException(
                    message=msg,
                    no_personal_data_message=msg,
                    error_type=ValidationErrorType.INVALID_VALUE,
                    target=ErrorTarget.FEATURE_SET,
                    error_category=ErrorCategory.USER_ERROR,
                )

        if type != "custom":
            if type == "featureset":
                if not path:
                    msg = f"You need to provide path for {type} feature source."
                    raise ValidationException(
                        message=msg,
                        no_personal_data_message=msg,
                        error_type=ValidationErrorType.INVALID_VALUE,
                        target=ErrorTarget.FEATURE_SET,
                        error_category=ErrorCategory.USER_ERROR,
                    )
                if timestamp_column:
                    msg = f"Cannot provide timestamp_column for {type} feature source."
                    raise ValidationException(
                        message=msg,
                        no_personal_data_message=msg,
                        error_type=ValidationErrorType.INVALID_VALUE,
                        target=ErrorTarget.FEATURE_SET,
                        error_category=ErrorCategory.USER_ERROR,
                    )
            if not (path and not dict and not source_process_code):
                msg = f"Cannot provide source_process_code or kwargs for {type} feature source."
                raise ValidationException(
                    message=msg,
                    no_personal_data_message=msg,
                    error_type=ValidationErrorType.INVALID_VALUE,
                    target=ErrorTarget.FEATURE_SET,
                    error_category=ErrorCategory.USER_ERROR,
                )
        else:
            if not (dict and source_process_code and not path):
                msg = "You cannot provide path for custom feature source."
                raise ValidationException(
                    message=msg,
                    no_personal_data_message=msg,
                    error_type=ValidationErrorType.INVALID_VALUE,
                    target=ErrorTarget.FEATURE_SET,
                    error_category=ErrorCategory.USER_ERROR,
                )
        self.type = type
        self.path = path
        self.timestamp_column = timestamp_column
        self.source_delay = source_delay
        self.source_process_code = source_process_code
        self.kwargs = dict
