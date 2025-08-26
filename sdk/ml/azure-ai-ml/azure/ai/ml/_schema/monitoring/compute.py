# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

from marshmallow import fields, post_load
from azure.ai.ml._schema.core.schema import PatchedSchemaMeta
from azure.ai.ml._schema.core.fields import StringTransformedEnum


class ComputeConfigurationSchema(metaclass=PatchedSchemaMeta):
    compute_type = StringTransformedEnum(allowed_values=["ServerlessSpark"])


class ServerlessSparkComputeSchema(ComputeConfigurationSchema):
    runtime_version = fields.Str()
    instance_type = fields.Str()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.compute import ServerlessSparkCompute

        return ServerlessSparkCompute(**data)
