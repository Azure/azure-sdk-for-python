# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

from marshmallow import fields, post_load

from azure.ai.ml._schema.core.schema import PatchedSchemaMeta


class FeaturesetSpecificationSchema(metaclass=PatchedSchemaMeta):
    path = fields.Str(required=True, allow_none=False)

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._featureset.featureset_specification import FeaturesetSpecification

        return FeaturesetSpecification(**data)
