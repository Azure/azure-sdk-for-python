# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=redefined-builtin

from typing import Optional, Union

from azure.ai.ml._restclient.v2023_04_01_preview.models import SparkJobEntry as RestSparkJobEntry
from azure.ai.ml._restclient.v2023_04_01_preview.models import SparkJobPythonEntry, SparkJobScalaEntry
from azure.ai.ml.entities._mixins import RestTranslatableMixin


class SparkJobEntryType:
    SPARK_JOB_FILE_ENTRY = "SparkJobPythonEntry"
    SPARK_JOB_CLASS_ENTRY = "SparkJobScalaEntry"


class SparkJobEntry(RestTranslatableMixin):
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
    def _from_rest_object(cls, obj: Union[SparkJobPythonEntry, SparkJobScalaEntry]) -> Optional["SparkJobEntry"]:
        if obj is None:
            return
        if isinstance(obj, dict):
            obj = RestSparkJobEntry.from_dict(obj)
        if obj.spark_job_entry_type == SparkJobEntryType.SPARK_JOB_FILE_ENTRY:
            return SparkJobEntry(
                entry=obj.__dict__.get("file", None),
                type=SparkJobEntryType.SPARK_JOB_FILE_ENTRY,
            )
        return SparkJobEntry(entry=obj.class_name, type=SparkJobEntryType.SPARK_JOB_CLASS_ENTRY)

    def _to_rest_object(self) -> Union[SparkJobPythonEntry, SparkJobScalaEntry]:
        if self.entry_type == SparkJobEntryType.SPARK_JOB_FILE_ENTRY:
            return SparkJobPythonEntry(file=self.entry)
        return SparkJobScalaEntry(class_name=self.entry)
