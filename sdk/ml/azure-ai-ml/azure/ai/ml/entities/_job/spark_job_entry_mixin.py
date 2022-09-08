# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


from typing import Dict, Optional, Union

from azure.ai.ml._ml_exceptions import ErrorCategory, ErrorTarget, ValidationException

from .spark_job_entry import SparkJobEntry, SparkJobEntryType


class SparkJobEntryMixin:
    @property
    def entry(self) -> Optional[SparkJobEntry]:
        return self._entry

    @entry.setter
    def entry(self, value: Union[Dict[str, str], SparkJobEntry, None]):
        if isinstance(value, dict):
            if value.get("file", None):
                self._entry = SparkJobEntry(entry=value.get("file"), type=SparkJobEntryType.SPARK_JOB_FILE_ENTRY)
                return
            if value.get("class_name", None):
                self._entry = SparkJobEntry(entry=value.get("class_name"), type=SparkJobEntryType.SPARK_JOB_CLASS_ENTRY)
                return
        self._entry = value

    def _validate_entry(self):
        if not isinstance(self.entry, SparkJobEntry):
            msg = "Entry is a required field."
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.SPARK_JOB,
                error_category=ErrorCategory.USER_ERROR,
            )
        if self.entry.entry_type == SparkJobEntryType.SPARK_JOB_CLASS_ENTRY:
            msg = "Classpath is not supported, please use 'file' to define the entry file."
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.SPARK_JOB,
                error_category=ErrorCategory.USER_ERROR,
            )
