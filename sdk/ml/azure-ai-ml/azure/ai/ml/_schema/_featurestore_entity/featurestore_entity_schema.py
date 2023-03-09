# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


from marshmallow import fields

from azure.ai.ml._schema import NestedField
from azure.ai.ml._schema.core.schema import YamlFileSchema

from .data_column_schema import DataColumnSchema


class FeaturestoreEntitySchema(YamlFileSchema):
    name = fields.Str(required=True, allow_none=False)
    version = fields.Str(required=True, allow_none=False)
    index_columns = fields.List(NestedField(DataColumnSchema), required=True, allow_none=False)
    description = fields.Str()
    tags = fields.Dict(keys=fields.Str(), values=fields.Str())
    properties = fields.Dict(keys=fields.Str(), values=fields.Str())
