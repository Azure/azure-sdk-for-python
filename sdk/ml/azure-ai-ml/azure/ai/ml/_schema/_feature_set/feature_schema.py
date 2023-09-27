# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

from marshmallow import fields, post_load

from azure.ai.ml._schema.core.schema import PatchedSchemaMeta


class FeatureSchema(metaclass=PatchedSchemaMeta):
    name = fields.Str(
        required=True,
        allow_none=False,
    )
    data_type = fields.Str(
        required=True,
        allow_none=False,
        data_key="type",
    )
    description = fields.Str(required=False)
    tags = fields.Dict(keys=fields.Str(), values=fields.Str(), required=False)

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._feature_set.feature import Feature

        return Feature(description=data.pop("description", None), **data)
