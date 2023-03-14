# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

from marshmallow import fields, post_load

from azure.ai.ml._schema.core.schema import PatchedSchemaMeta


class FeatureTransformationCodeSchema(metaclass=PatchedSchemaMeta):
    path = fields.Str(required=False)
    transformer_class = fields.Str(required=False)

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._feature_set.delay_metadata import DelayMetadata

        return DelayMetadata(**data)
