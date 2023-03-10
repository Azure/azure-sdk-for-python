# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use


from marshmallow import fields

from azure.ai.ml._schema.core.fields import NestedField
from azure.ai.ml._schema.core.schema import YamlFileSchema, PatchedSchemaMeta
from azure.ai.ml._schema._feature_store_entity.data_column_schema import DataColumnSchema

from .source_metadata_schema import SourceMetadataSchema


class FeatureTransformationCodePropertiesSchema(metaclass=PatchedSchemaMeta):
    Path = fields.Str()
    TransformerClass = fields.Str()


class DelayMetadataPropertiesSchema(metaclass=PatchedSchemaMeta):
    Days = fields.Int()
    Hours = fields.Int()
    Minutes = fields.Int()


class FeaturePropertiesSchema(metaclass=PatchedSchemaMeta):
    FeatureName = fields.Str()
    DataType = fields.Str()
    Description = fields.Str()
    Tags = fields.Dict(keys=fields.Str(), values=fields.Str())


class FeaturesetSpecPropertiesSchema(YamlFileSchema):
    source = fields.Nested(SourceMetadataSchema)
    featureTransformationCode = fields.Nested(FeatureTransformationCodePropertiesSchema)
    features = fields.List(NestedField(FeaturePropertiesSchema))
    indexColumns = fields.List(NestedField(DataColumnSchema))
    sourceLookback = fields.Nested(DelayMetadataPropertiesSchema)
    temporalJoinLookback = fields.Nested(DelayMetadataPropertiesSchema)
