# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from marshmallow import fields, post_load
from azure.ai.ml._internal._schema.node import InternalBaseNodeSchema, NodeType
from azure.ai.ml._schema import StringTransformedEnum, NestedField
from azure.ai.ml._schema.job.job_limits import CommandJobLimitsSchema
from azure.ai.ml._schema.resource_configuration import ResourceConfigurationSchema


class CommandSchema(InternalBaseNodeSchema):
    type = StringTransformedEnum(allowed_values=[NodeType.COMMAND], casing_transform=lambda x: x)
    compute = fields.Str()
    environment = fields.Str()
    limits = NestedField(CommandJobLimitsSchema)
    resources = NestedField(ResourceConfigurationSchema)

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml._internal.entities.command import Command

        return Command(**data)


class DistributedSchema(InternalBaseNodeSchema):
    type = StringTransformedEnum(allowed_values=[NodeType.DISTRIBUTED], casing_transform=lambda x: x)

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml._internal.entities.command import Distributed

        return Distributed(**data)
