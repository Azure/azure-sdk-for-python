# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

from marshmallow import fields, post_load

from azure.ai.ml._schema.core.schema import PatchedSchemaMeta


class DelayMetadataSchema(metaclass=PatchedSchemaMeta):
    days = fields.Int(required=False)
    hours = fields.Int(required=False)
    minutes = fields.Int(required=False)

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._feature_set.delay_metadata import DelayMetadata

        return DelayMetadata(**data)
