# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

from marshmallow import fields, post_load

from azure.ai.ml._schema.core.fields import UnionField
from azure.ai.ml._schema.core.schema_meta import PatchedSchemaMeta


class SparkResourceConfigurationSchema(metaclass=PatchedSchemaMeta):
    instance_type = fields.Str(metadata={"description": "Optional type of VM used as supported by the compute target."})
    runtime_version = UnionField([fields.Str(), fields.Number()])

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities import SparkResourceConfiguration

        return SparkResourceConfiguration(**data)
