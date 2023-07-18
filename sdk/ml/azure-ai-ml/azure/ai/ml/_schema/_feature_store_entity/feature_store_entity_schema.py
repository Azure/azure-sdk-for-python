# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


from marshmallow import fields, post_dump, validate

from azure.ai.ml._schema import NestedField
from azure.ai.ml._schema.core.schema import YamlFileSchema

from .data_column_schema import DataColumnSchema


class FeatureStoreEntitySchema(YamlFileSchema):
    name = fields.Str(required=True, allow_none=False)
    version = fields.Str(required=True, allow_none=False)
    latest_version = fields.Str(dump_only=True)
    index_columns = fields.List(NestedField(DataColumnSchema), required=True, allow_none=False)
    stage = fields.Str(validate=validate.OneOf(["Development", "Production", "Archived"]), dump_default="Development")
    description = fields.Str()
    tags = fields.Dict(keys=fields.Str(), values=fields.Str())
    properties = fields.Dict(keys=fields.Str(), values=fields.Str())

    @post_dump
    def remove_empty_values(self, data, **kwargs):  # pylint: disable=unused-argument
        return {key: value for key, value in data.items() if value}
