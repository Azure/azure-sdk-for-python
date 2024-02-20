# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

from marshmallow import fields, post_load

from azure.ai.ml._schema.core.schema import PatchedSchemaMeta


class FeatureTransformationCodeMetadataSchema(metaclass=PatchedSchemaMeta):
    path = fields.Str(required=False)
    transformer_class = fields.Str(required=False)

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._feature_set.feature_transformation_code_metadata import (
            FeatureTransformationCodeMetadata,
        )

        return FeatureTransformationCodeMetadata(**data)
