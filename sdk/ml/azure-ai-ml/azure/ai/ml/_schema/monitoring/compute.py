# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

from marshmallow import fields, post_load, validate
from azure.ai.ml._schema.core.schema import PatchedSchemaMeta


class ComputeConfigurationSchema(metaclass=PatchedSchemaMeta):
    compute_type = fields.Str(validate=validate.OneOf(["ServerlessSpark"]))


class ServerlessSparkComputeSchema(ComputeConfigurationSchema):
    runtime_version = fields.Str()
    instance_type = fields.Str()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.compute import ServerlessSparkCompute

        return ServerlessSparkCompute(**data)
