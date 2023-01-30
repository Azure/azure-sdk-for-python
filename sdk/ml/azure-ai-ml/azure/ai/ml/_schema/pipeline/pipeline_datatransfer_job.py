# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

import logging
from typing import Any

from marshmallow import fields, post_load

from azure.ai.ml._schema.core.fields import NestedField, UnionField
from azure.ai.ml._schema.job.input_output_entry import OutputSchema
from azure.ai.ml._schema.job.data_transfer_job import DataTransferJobSchema
from azure.ai.ml.constants._component import DataTransferTaskType

module_logger = logging.getLogger(__name__)


class PipelineDataTransferJobSchema(DataTransferJobSchema):
    outputs = fields.Dict(
        keys=fields.Str(),
        values=UnionField([NestedField(OutputSchema), fields.Str()], allow_none=True),
    )

    @post_load
    def make(self, data: Any, **kwargs: Any):
        from azure.ai.ml.entities._job.data_transfer.data_transfer_job import DataTransferCopyJob, \
            DataTransferImportJob, DataTransferExportJob
        task = data.get("task", None)
        if task == DataTransferTaskType.COPY_DATA:
            return DataTransferCopyJob(**data)
        elif task == DataTransferTaskType.IMPORT_DATA:
            return DataTransferImportJob(**data)
        else:
            return DataTransferExportJob(**data)
