# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

import logging
from typing import Any

from marshmallow import fields, post_load

from azure.ai.ml._schema.assets.environment import AnonymousEnvironmentSchema
from azure.ai.ml._schema.core.fields import ArmVersionedStr, ComputeField, NestedField, RegistryStr, UnionField
from azure.ai.ml._schema.job.command_job import CommandJobSchema
from azure.ai.ml._schema.job.input_output_entry import OutputSchema
from azure.ai.ml.constants import AzureMLResourceType

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
