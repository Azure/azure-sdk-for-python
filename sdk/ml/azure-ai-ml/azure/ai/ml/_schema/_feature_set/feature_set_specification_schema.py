# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

from marshmallow import fields, post_load

from azure.ai.ml._schema.core.schema import PatchedSchemaMeta


class FeatureSetSpecificationSchema(metaclass=PatchedSchemaMeta):
    path = fields.Str(required=True, allow_none=False)

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._feature_set.feature_set_specification import FeatureSetSpecification

        return FeatureSetSpecification(**data)
