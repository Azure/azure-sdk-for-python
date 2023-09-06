# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import fields
from azure.ai.ml._schema.core.schema import YamlFileSchema
from .timestamp_column_metadata_schema import TimestampColumnMetadataSchema

class FeatureWindowSchema(YamlFileSchema):
    feature_window_end = fields.Str()
    feature_window_start = fields.Str()