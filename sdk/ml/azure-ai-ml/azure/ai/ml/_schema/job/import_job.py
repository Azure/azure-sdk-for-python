# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

from marshmallow import fields, post_load

from azure.ai.ml._schema.core.fields import NestedField, StringTransformedEnum, UnionField
from azure.ai.ml._schema.core.schema_meta import PatchedSchemaMeta
from azure.ai.ml._schema.job.input_output_entry import OutputSchema
from azure.ai.ml.constants import ImportSourceType, JobType

from .base_job import BaseJobSchema


class DatabaseImportSourceSchema(metaclass=PatchedSchemaMeta):
    type = StringTransformedEnum(
        allowed_values=[
            ImportSourceType.AZURESQLDB,
            ImportSourceType.AZURESYNAPSEANALYTICS,
            ImportSourceType.SNOWFLAKE,
        ],
        required=True,
    )
    connection = fields.Str(required=True)
    query = fields.Str(required=True)

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._job.import_job import DatabaseImportSource

        return DatabaseImportSource(**data)


class FileImportSourceSchema(metaclass=PatchedSchemaMeta):
    type = StringTransformedEnum(allowed_values=[ImportSourceType.S3], required=True)
    connection = fields.Str(required=True)
    path = fields.Str(required=True)

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._job.import_job import FileImportSource

        return FileImportSource(**data)


class ImportJobSchema(BaseJobSchema):
    class Meta:
        exclude = ["compute"]  # compute property not applicable to import job

    type = StringTransformedEnum(allowed_values=JobType.IMPORT)
    source = UnionField([NestedField(DatabaseImportSourceSchema), NestedField(FileImportSourceSchema)], required=True)
    output = NestedField(OutputSchema, required=True)
