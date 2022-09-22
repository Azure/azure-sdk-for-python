# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=redefined-builtin

from typing import Optional, Union

from azure.ai.ml._restclient.v2022_06_01_preview.models import SparkJobPythonEntry, SparkJobScalaEntry


class SparkJobEntryType:
    SPARK_JOB_FILE_ENTRY = "SparkJobPythonEntry"
    SPARK_JOB_CLASS_ENTRY = "SparkJobScalaEntry"


class SparkJobEntry:
    """Entry for spark job.

    :param entry_type: Can be python or scala entry.
    :type entry_type: SparkJobEntryType
    :param entry: File or class entry point.
    :type entry: str
    """

    def __init__(self, *, entry: str, type: str = SparkJobEntryType.SPARK_JOB_FILE_ENTRY):
        self.entry_type = type
        self.entry = entry

    @classmethod
    def _from_rest_object(cls, data: Union[SparkJobPythonEntry, SparkJobScalaEntry]) -> Optional["SparkJobEntry"]:
        if data is None:
            return
        if data.spark_job_entry_type == SparkJobEntryType.SPARK_JOB_FILE_ENTRY:
            return SparkJobEntry(
                entry=data.__dict__.get("file", None),
                type=SparkJobEntryType.SPARK_JOB_FILE_ENTRY,
            )
        return SparkJobEntry(entry=data.class_name, type=SparkJobEntryType.SPARK_JOB_CLASS_ENTRY)

    def _to_rest_object(self) -> Union[SparkJobPythonEntry, SparkJobScalaEntry]:
        if self.entry_type == SparkJobEntryType.SPARK_JOB_FILE_ENTRY:
            return SparkJobPythonEntry(file=self.entry)
        return SparkJobScalaEntry(class_name=self.entry)
