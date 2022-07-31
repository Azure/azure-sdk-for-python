# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
from typing import Any
from azure.ai.ml._schema.core.fields import NestedField, UnionField
from azure.ai.ml._schema.job.command_job import CommandJobSchema
from azure.ai.ml._schema.job.input_output_entry import OutputSchema
from azure.ai.ml.constants import AzureMLResourceType
from azure.ai.ml._schema.core.fields import ComputeField, ArmVersionedStr, RegistryStr
from azure.ai.ml._schema.assets.environment import AnonymousEnvironmentSchema
from marshmallow import fields, post_load

module_logger = logging.getLogger(__name__)


class PipelineCommandJobSchema(CommandJobSchema):
    compute = ComputeField()
    environment = UnionField(
        [
            RegistryStr(azureml_type=AzureMLResourceType.ENVIRONMENT),
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
        from azure.ai.ml.entities import CommandJob

        return CommandJob(**data)
