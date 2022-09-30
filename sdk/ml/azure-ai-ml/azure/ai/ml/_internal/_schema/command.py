# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from marshmallow import fields

from azure.ai.ml._internal._schema.node import InternalBaseNodeSchema, NodeType
from azure.ai.ml._schema import NestedField, StringTransformedEnum
from azure.ai.ml._schema.component.retry_settings import RetrySettingsSchema
from azure.ai.ml._schema.core.fields import DistributionField
from azure.ai.ml._schema.job.job_limits import CommandJobLimitsSchema
from azure.ai.ml._schema.job_resource_configuration import JobResourceConfigurationSchema


class CommandSchema(InternalBaseNodeSchema):
    type = StringTransformedEnum(allowed_values=[NodeType.COMMAND], casing_transform=lambda x: x)
    compute = fields.Str()
    environment = fields.Str()
    limits = NestedField(CommandJobLimitsSchema)
    resources = NestedField(JobResourceConfigurationSchema)


class DistributedSchema(CommandSchema):
    type = StringTransformedEnum(allowed_values=[NodeType.DISTRIBUTED], casing_transform=lambda x: x)
    distribution = DistributionField()


class ParallelSchema(CommandSchema):
    type = StringTransformedEnum(allowed_values=[NodeType.PARALLEL], casing_transform=lambda x: x)
    max_concurrency_per_instance = fields.Int()
    error_threshold = fields.Int()
    mini_batch_size = fields.Int()
    logging_level = StringTransformedEnum(
        allowed_values=["INFO", "WARNING", "DEBUG"], casing_transform=lambda x: x.upper()
    )
    retry_settings = NestedField(RetrySettingsSchema)
