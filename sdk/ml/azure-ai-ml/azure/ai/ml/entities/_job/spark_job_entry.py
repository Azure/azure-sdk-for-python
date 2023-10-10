# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=redefined-builtin

from typing import Optional, Union

from azure.ai.ml._restclient.v2023_04_01_preview.models import SparkJobEntry as RestSparkJobEntry
from azure.ai.ml._restclient.v2023_04_01_preview.models import SparkJobPythonEntry, SparkJobScalaEntry
from azure.ai.ml.entities._mixins import RestTranslatableMixin


class SparkJobEntryType:
    """Type of Spark job entry. Possibilities are Python file entry or Scala class entry."""

    SPARK_JOB_FILE_ENTRY = "SparkJobPythonEntry"
    SPARK_JOB_CLASS_ENTRY = "SparkJobScalaEntry"


class SparkJobEntry(RestTranslatableMixin):
    """Entry for Spark job.

    :keyword entry: The file or class entry point.
    :paramtype entry: str
    :keyword type: The entry type. Accepted values are SparkJobEntryType.SPARK_JOB_FILE_ENTRY or
        SparkJobEntryType.SPARK_JOB_CLASS_ENTRY. Defaults to SparkJobEntryType.SPARK_JOB_FILE_ENTRY.
    :paramtype type: ~azure.ai.ml.entities.SparkJobEntryType

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_spark_configurations.py
            :start-after: [START spark_component_definition]
            :end-before: [END spark_component_definition]
            :language: python
            :dedent: 8
            :caption: Creating SparkComponent.
    """

    def __init__(self, *, entry: str, type: str = SparkJobEntryType.SPARK_JOB_FILE_ENTRY) -> None:
        self.entry_type = type
        self.entry = entry

    @classmethod
    def _from_rest_object(cls, obj: Union[SparkJobPythonEntry, SparkJobScalaEntry]) -> Optional["SparkJobEntry"]:
        if obj is None:
            return None
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
