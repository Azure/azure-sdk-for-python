# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

from typing import Dict

from marshmallow import fields, post_load

from azure.ai.ml._schema.core.fields import NestedField
from azure.ai.ml._schema.core.schema import YamlFileSchema
from azure.ai.ml._schema._featurestore_entity.data_column_schema import DataColumnSchema

from .source_schema import SourceSchema
from .delay_schema import DelaySchema
from .feature_schema import FeatureSchema


class FeaturesetSpecSchema(YamlFileSchema):
    source = NestedField(SourceSchema)
    features = fields.List(NestedField(FeatureSchema), required=True, allow_none=False)
    index_columns = fields.List(NestedField(DataColumnSchema), required=True, allow_none=False)
    temporal_join_lookback = NestedField(DelaySchema)

    @post_load
    def make(self, data: Dict, **kwargs):
        from azure.ai.ml.entities._featureset.featureset_spec import FeaturesetSpec

        return FeaturesetSpec(**data)
