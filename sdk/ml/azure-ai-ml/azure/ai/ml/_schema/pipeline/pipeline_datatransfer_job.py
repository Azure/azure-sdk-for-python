# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

import logging
from typing import Any

from marshmallow import fields, post_load

from azure.ai.ml._schema.core.fields import NestedField, UnionField
from azure.ai.ml._schema.job.input_output_entry import OutputSchema
from azure.ai.ml._schema.pipeline.pipeline_job_io import OutputBindingStr
from azure.ai.ml._schema.job.data_transfer_job import (
    DataTransferCopyJobSchema,
    DataTransferImportJobSchema,
    DataTransferExportJobSchema,
)

module_logger = logging.getLogger(__name__)


class PipelineDataTransferCopyJobSchema(DataTransferCopyJobSchema):
    outputs = fields.Dict(
        keys=fields.Str(),
        values=UnionField([NestedField(OutputSchema), OutputBindingStr], allow_none=True),
    )

    @post_load
    def make(self, data: Any, **kwargs: Any):
        from azure.ai.ml.entities._job.data_transfer.data_transfer_job import DataTransferCopyJob

        return DataTransferCopyJob(**data)


class PipelineDataTransferImportJobSchema(DataTransferImportJobSchema):
    outputs = fields.Dict(
        keys=fields.Str(),
        values=UnionField([NestedField(OutputSchema), OutputBindingStr], allow_none=True),
    )

    @post_load
    def make(self, data: Any, **kwargs: Any):
        from azure.ai.ml.entities._job.data_transfer.data_transfer_job import DataTransferImportJob

        return DataTransferImportJob(**data)


class PipelineDataTransferExportJobSchema(DataTransferExportJobSchema):
    @post_load
    def make(self, data: Any, **kwargs: Any):
        from azure.ai.ml.entities._job.data_transfer.data_transfer_job import DataTransferExportJob

        return DataTransferExportJob(**data)
