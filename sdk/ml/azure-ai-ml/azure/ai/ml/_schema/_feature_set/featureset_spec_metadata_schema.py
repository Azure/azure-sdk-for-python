# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

from typing import Dict

from marshmallow import fields, post_load

from azure.ai.ml._schema.core.fields import NestedField
from azure.ai.ml._schema.core.schema import YamlFileSchema
from azure.ai.ml._schema._feature_store_entity.data_column_schema import DataColumnSchema

from .source_metadata_schema import SourceMetadataSchema
from .delay_metadata_schema import DelayMetadataSchema
from .feature_schema import FeatureSchema
from .feature_transformation_code_metadata_schema import FeatureTransformationCodeMetadataSchema


class FeaturesetSpecMetadataSchema(YamlFileSchema):
    source = fields.Nested(SourceMetadataSchema, required=True)
    feature_transformation_code = fields.Nested(FeatureTransformationCodeMetadataSchema, required=False)
    features = fields.List(NestedField(FeatureSchema), required=True, allow_none=False)
    index_columns = fields.List(NestedField(DataColumnSchema), required=False)
    source_lookback = fields.Nested(DelayMetadataSchema, required=False)
    temporal_join_lookback = fields.Nested(DelayMetadataSchema, required=False)

    @post_load
    def make(self, data: Dict, **kwargs):
        from azure.ai.ml.entities._feature_set.featureset_spec_metadata import FeaturesetSpecMetadata

        return FeaturesetSpecMetadata(**data)
