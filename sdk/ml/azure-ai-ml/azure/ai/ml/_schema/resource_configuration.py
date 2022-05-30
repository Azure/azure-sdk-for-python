# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.ai.ml._schema.core.schema_meta import PatchedSchemaMeta
from marshmallow import fields, post_load


class ResourceConfigurationSchema(metaclass=PatchedSchemaMeta):
    instance_count = fields.Int()
    instance_type = fields.Str(metadata={"description": "The instance type to make available to this job."})
    properties = fields.Dict(keys=fields.Str())

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities import ResourceConfiguration

        return ResourceConfiguration(**data)
