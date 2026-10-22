# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

from marshmallow import fields, post_load

from azure.ai.ml._schema.core.schema_meta import PatchedSchemaMeta


class JobResourcesSchema(metaclass=PatchedSchemaMeta):
    instance_types = fields.List(
        fields.Str(), metadata={"description": "The instance type to make available to this job."}
    )

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities import JobResources

        return JobResources(**data)
