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
        if type == "custom":
            # For custom feature source
            # Required: timestamp_column, dict and source_process_code.
            # Not support: path.
            if path:
                msg = "Cannot provide path for custom feature source."
                raise ValidationException(
                    message=msg,
                    no_personal_data_message=msg,
                    error_type=ValidationErrorType.INVALID_VALUE,
                    target=ErrorTarget.FEATURE_SET,
                    error_category=ErrorCategory.USER_ERROR,
                )
            if not (timestamp_column and dict and source_process_code):
                msg = f"You need to provide timestamp_column/dict/source_process_code for {type} feature source."
                raise ValidationException(
                    message=msg,
                    no_personal_data_message=msg,
                    error_type=ValidationErrorType.INVALID_VALUE,
                    target=ErrorTarget.FEATURE_SET,
                    error_category=ErrorCategory.USER_ERROR,
                )
        elif type == "featureset":
            # For featureset feature source
            # Required: path.
            # Not support: timestamp_column, source_delay and source_process_code.
            if timestamp_column or source_delay or source_process_code:
                msg = f"Cannot provide timestamp_column/source_delay/source_process_code for {type} feature source."
                raise ValidationException(
                    message=msg,
                    no_personal_data_message=msg,
                    error_type=ValidationErrorType.INVALID_VALUE,
                    target=ErrorTarget.FEATURE_SET,
                    error_category=ErrorCategory.USER_ERROR,
                )
            if not path:
                msg = f"You need to provide path for {type} feature source."
                raise ValidationException(
                    message=msg,
                    no_personal_data_message=msg,
                    error_type=ValidationErrorType.INVALID_VALUE,
                    target=ErrorTarget.FEATURE_SET,
                    error_category=ErrorCategory.USER_ERROR,
                )
        else:
            # For other type feature source
            # Required: timestamp_column, path.
            # Not support: source_process_code, dict
            if dict or source_process_code:
                msg = f"Cannot provide dict/source_process_code for {type} feature source."
                raise ValidationException(
                    message=msg,
                    no_personal_data_message=msg,
                    error_type=ValidationErrorType.INVALID_VALUE,
                    target=ErrorTarget.FEATURE_SET,
                    error_category=ErrorCategory.USER_ERROR,
                )
            if not (timestamp_column and path):
                msg = f"You need to provide timestamp_column/path for {type} feature source."
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
