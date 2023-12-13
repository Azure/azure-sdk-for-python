# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument


from marshmallow import fields

from azure.ai.ml._schema.core.fields import NestedField
from azure.ai.ml._schema.core.schema import PatchedSchemaMeta, YamlFileSchema

from .source_process_code_metadata_schema import SourceProcessCodeSchema
from .timestamp_column_metadata_schema import TimestampColumnMetadataSchema


# pylint: disable-next=name-too-long
class FeatureTransformationCodePropertiesSchema(metaclass=PatchedSchemaMeta):
    path = fields.Str(data_key="Path")
    transformer_class = fields.Str(data_key="TransformerClass")


class DelayMetadataPropertiesSchema(metaclass=PatchedSchemaMeta):
    days = fields.Int(data_key="Days")
    hours = fields.Int(data_key="Hours")
    minutes = fields.Int(data_key="Minutes")


class FeaturePropertiesSchema(metaclass=PatchedSchemaMeta):
    name = fields.Str(data_key="FeatureName")
    data_type = fields.Str(data_key="DataType")
    description = fields.Str(data_key="Description")
    tags = fields.Dict(keys=fields.Str(), values=fields.Str(), data_key="Tags")


class ColumnPropertiesSchema(metaclass=PatchedSchemaMeta):
    name = fields.Str(data_key="ColumnName")
    type = fields.Str(data_key="DataType")


class SourcePropertiesSchema(metaclass=PatchedSchemaMeta):
    type = fields.Str(required=True)
    path = fields.Str(required=False)
    timestamp_column = fields.Nested(TimestampColumnMetadataSchema, data_key="timestampColumn")
    source_delay = fields.Nested(DelayMetadataPropertiesSchema, data_key="sourceDelay")
    source_process_code = fields.Nested(SourceProcessCodeSchema)
    dict = fields.Dict(keys=fields.Str(), values=fields.Str(), data_key="kwargs")


class FeaturesetSpecPropertiesSchema(YamlFileSchema):
    source = fields.Nested(SourcePropertiesSchema, data_key="source")
    feature_transformation_code = fields.Nested(
        FeatureTransformationCodePropertiesSchema, data_key="featureTransformationCode"
    )
    features = fields.List(NestedField(FeaturePropertiesSchema), data_key="features")
    index_columns = fields.List(NestedField(ColumnPropertiesSchema), data_key="indexColumns")
    source_lookback = fields.Nested(DelayMetadataPropertiesSchema, data_key="sourceLookback")
    temporal_join_lookback = fields.Nested(DelayMetadataPropertiesSchema, data_key="temporalJoinLookback")
