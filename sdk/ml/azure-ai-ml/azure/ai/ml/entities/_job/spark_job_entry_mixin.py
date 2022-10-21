# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
import re
from pathlib import Path
from typing import Dict, Optional, Union

from azure.ai.ml._utils.utils import is_url
from azure.ai.ml.constants._common import ARM_ID_PREFIX, REGISTRY_URI_FORMAT
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

    def _validate_entry_exist(self):
        # validate whether component entry exists to ensure code path is correct, especially when code is default value
        if self.code is None:
            return
        is_remote_code = (
            self.code.startswith("git+")
            or self.code.startswith(REGISTRY_URI_FORMAT)
            or self.code.startswith(ARM_ID_PREFIX)
            or is_url(self.code)
            or self.CODE_ID_RE_PATTERN.match(self.code)
        )
        if isinstance(self.code, str) and is_remote_code:
            # skip validate when code is not a local path
            return

        if not os.path.isabs(self.code):
            code_path = Path(self.component.base_path) / self.code
            if code_path.exists():
                code_path = code_path.resolve().absolute()
            else:
                msg = "Code path doesn't exist."
                raise ValidationException(
                    message=msg,
                    no_personal_data_message=msg,
                    target=ErrorTarget.SPARK_JOB,
                    error_category=ErrorCategory.USER_ERROR,
                )
            entry_path = code_path / self.entry.entry
        else:
            entry_path = Path(self.code) / self.entry.entry

        if isinstance(self.entry, SparkJobEntry) and self.entry.entry_type == SparkJobEntryType.SPARK_JOB_FILE_ENTRY:
            if not entry_path.exists():
                msg = "Entry doesn't exist."
                raise ValidationException(
                    message=msg,
                    no_personal_data_message=msg,
                    target=ErrorTarget.SPARK_JOB,
                    error_category=ErrorCategory.USER_ERROR,
                )
