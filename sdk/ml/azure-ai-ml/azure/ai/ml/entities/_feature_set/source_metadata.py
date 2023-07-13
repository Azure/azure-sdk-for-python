# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=redefined-builtin,disable=unused-argument

from typing import Dict

from azure.ai.ml.entities._feature_set.source_process_code_metadata import SourceProcessCodeMetadata
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationErrorType, ValidationException

from .delay_metadata import DelayMetadata
from .timestamp_column_metadata import TimestampColumnMetadata


class SourceMetadata(object):
    def __init__(
        self,
        *,
        type: str,
        timestamp_column: TimestampColumnMetadata,
        path: str = None,
        source_delay: DelayMetadata = None,
        source_process_code: SourceProcessCodeMetadata = None,
        dict: Dict = None,
        **kwargs,
    ):
        if type != "custom":
            if not (path and not dict and not source_process_code):
                msg = f"Only path should be provided when source type is {type}"
                raise ValidationException(
                    message=msg,
                    no_personal_data_message=msg,
                    error_type=ValidationErrorType.INVALID_VALUE,
                    target=ErrorTarget.FEATURE_SET,
                    error_category=ErrorCategory.USER_ERROR,
                )
        else:
            if not (dict and source_process_code and not path):
                msg = f"Only kwargs and source_process_code should be provided when source type is {type}"
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
        self.dict = dict
