# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import re
from typing import Dict, Optional, Union

from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationException

from .spark_job_entry import SparkJobEntry, SparkJobEntryType


class SparkJobEntryMixin:
    CODE_ID_RE_PATTERN = re.compile(
        (
            r"\/subscriptions\/(?P<subscription>[\w,-]+)\/resourceGroups\/(?P<resource_group>[\w,-]+)"
            r"\/providers\/Microsoft\.MachineLearningServices\/workspaces\/(?P<workspace>[\w,-]+)"
            r"\/codes\/(?P<code_id>[\w,-]+)"  # fmt: skip
        )
    )

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
        if self.entry is None:
            # Entry is a required field for local component and when we load a remote job, component now is an arm_id,
            # entry is from node level returned from service. Entry is only None when we reference an existing
            # component with a function and the referenced component is in remote with name and version.
            return
        if not isinstance(self.entry, SparkJobEntry):
            msg = f'Unsupported type {type(self.entry)} detected when validate entry, entry should be SparkJobEntry.'
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
