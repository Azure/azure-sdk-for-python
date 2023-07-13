# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

from marshmallow import fields, post_dump, validate

from azure.ai.ml._schema import NestedField
from azure.ai.ml._schema.core.schema import YamlFileSchema

from .feature_set_specification_schema import FeatureSetSpecificationSchema
from .materialization_settings_schema import MaterializationSettingsSchema


class FeatureSetSchema(YamlFileSchema):
    name = fields.Str(required=True, allow_none=False)
    version = fields.Str(required=True, allow_none=False)
    latest_version = fields.Str(dump_only=True)
    specification = NestedField(FeatureSetSpecificationSchema, required=True, allow_none=False)
    entities = fields.List(fields.Str, required=True, allow_none=False)
    stage = fields.Str(validate=validate.OneOf(["Development", "Production", "Archived"]), dump_default="Development")
    description = fields.Str()
    tags = fields.Dict(keys=fields.Str(), values=fields.Str())
    materialization_settings = NestedField(MaterializationSettingsSchema)

    @post_dump
    def remove_empty_values(self, data, **kwargs):  # pylint: disable=unused-argument
        return {key: value for key, value in data.items() if value}
