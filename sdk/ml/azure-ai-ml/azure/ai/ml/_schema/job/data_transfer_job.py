# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import validates, ValidationError, fields
from azure.ai.ml._schema.core.fields import NestedField
from azure.ai.ml._schema.job.input_output_fields_provider import InputsField, OutputsField
from azure.ai.ml._schema.job.input_output_entry import DatabaseSchema, FileSystemSchema, OutputSchema
from azure.ai.ml.constants import JobType
from azure.ai.ml.constants._component import DataTransferTaskType, DataCopyMode

from ..core.fields import ComputeField, StringTransformedEnum, UnionField
from .base_job import BaseJobSchema


class DataTransferCopyJobSchema(BaseJobSchema):
    type = StringTransformedEnum(required=True, allowed_values=JobType.DATA_TRANSFER)
    task = StringTransformedEnum(allowed_values=[DataTransferTaskType.COPY_DATA], required=True)
    data_copy_mode = StringTransformedEnum(
        allowed_values=[DataCopyMode.MERGE_WITH_OVERWRITE, DataCopyMode.FAIL_IF_CONFLICT]
    )
    compute = ComputeField()
    inputs = InputsField()
    outputs = OutputsField()


class DataTransferImportJobSchema(BaseJobSchema):
    type = StringTransformedEnum(required=True, allowed_values=JobType.DATA_TRANSFER)
    task = StringTransformedEnum(allowed_values=[DataTransferTaskType.IMPORT_DATA], required=True)
    compute = ComputeField()
    outputs = fields.Dict(
        keys=fields.Str(),
        values=NestedField(nested=OutputSchema, allow_none=False),
        metadata={"description": "Outputs of a data transfer job."},
    )
    source = UnionField([NestedField(DatabaseSchema), NestedField(FileSystemSchema)], required=True, allow_none=False)

    @validates("outputs")
    def outputs_key(self, value):
        if len(value) != 1 or list(value.keys())[0] != "sink":
            raise ValidationError(
                f"outputs field only support one output called sink in task type "
                f"{DataTransferTaskType.IMPORT_DATA}."
            )


class DataTransferExportJobSchema(BaseJobSchema):
    type = StringTransformedEnum(required=True, allowed_values=JobType.DATA_TRANSFER)
    task = StringTransformedEnum(allowed_values=[DataTransferTaskType.EXPORT_DATA], required=True)
    compute = ComputeField()
    inputs = InputsField(allow_none=False)
    sink = UnionField([NestedField(DatabaseSchema), NestedField(FileSystemSchema)], required=True, allow_none=False)

    @validates("inputs")
    def inputs_key(self, value):
        if len(value) != 1 or list(value.keys())[0] != "source":
            raise ValidationError(
                f"inputs field only support one input called source in task type "
                f"{DataTransferTaskType.EXPORT_DATA}."
            )
