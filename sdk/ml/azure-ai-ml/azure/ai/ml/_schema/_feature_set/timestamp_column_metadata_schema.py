# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

from marshmallow import fields, post_load

from azure.ai.ml._schema.core.schema import PatchedSchemaMeta


class TimestampColumnMetadataSchema(metaclass=PatchedSchemaMeta):
    name = fields.Str(required=True)
    format = fields.Str(required=False)

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._feature_set.timestamp_column_metadata import TimestampColumnMetadata

        return TimestampColumnMetadata(**data)
