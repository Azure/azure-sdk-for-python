# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
from typing import Any
from marshmallow import fields, post_load, INCLUDE
from azure.ai.ml._schema.core.fields import NestedField, UnionField
from azure.ai.ml._schema.job.input_output_entry import OutputSchema

from azure.ai.ml._schema.job.parallel_job import ParallelJobSchema
from azure.ai.ml._schema._deployment.batch.batch_deployment_settings import BatchRetrySettingsSchema
from azure.ai.ml._schema.core.fields import ComputeField, ArmVersionedStr
from azure.ai.ml._schema.assets.environment import AnonymousEnvironmentSchema
from azure.ai.ml.constants import AzureMLResourceType

module_logger = logging.getLogger(__name__)


class PipelineParallelJobSchema(ParallelJobSchema):
    compute = ComputeField()
    environment = UnionField(
        [
            NestedField(AnonymousEnvironmentSchema),
            ArmVersionedStr(azureml_type=AzureMLResourceType.ENVIRONMENT, allow_default_version=True),
        ],
    )
    outputs = fields.Dict(
        keys=fields.Str(),
        values=UnionField([NestedField(OutputSchema), fields.Str()], allow_none=True),
    )

    @post_load
    def make(self, data: Any, **kwargs: Any):
        from azure.ai.ml.entities import ParallelJob

        return ParallelJob(**data)
