# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.ai.ml._schema.core.fields import NestedField
from azure.ai.ml._schema.job.input_output_fields_provider import InputsField, OutputsField
from azure.ai.ml._schema.job.input_output_entry import SourceSchema, SinkSchema
from azure.ai.ml.constants import JobType
from azure.ai.ml.constants._component import DataTransferTaskType, DataCopyMode

from ..core.fields import ComputeField, StringTransformedEnum, UnionField
from .base_job import BaseJobSchema


class DataTransferJobSchema(BaseJobSchema):
    type = StringTransformedEnum(required=True, allowed_values=JobType.DATA_TRANSFER)
    task = StringTransformedEnum(allowed_values=[DataTransferTaskType.COPY_DATA, DataTransferTaskType.IMPORT_DATA,
                                                 DataTransferTaskType.EXPORT_DATA])
    data_copy_mode = StringTransformedEnum(allowed_values=[DataCopyMode.MERGE_WITH_OVERWRITE,
                                                           DataCopyMode.FAIL_IF_CONFLICT])
    compute = ComputeField()
    inputs = InputsField()
    outputs = OutputsField()
    source = NestedField(SourceSchema)
    sink = NestedField(SinkSchema)
