# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

from marshmallow import fields

from azure.ai.ml._schema import NestedField
from azure.ai.ml._schema.core.schema import YamlFileSchema

from .materialization_settings_schema import MaterializationSettingsSchema
from .featureset_specification_schema import FeaturesetSpecificationSchema


class FeatureSetSchema(YamlFileSchema):
    name = fields.Str(required=True, allow_none=False)
    version = fields.Str(required=True, allow_none=False)
    specification = NestedField(FeaturesetSpecificationSchema, required=True, allow_none=False)
    entities = fields.List(fields.Str, required=True, allow_none=False)
    stage = fields.Str()
    description = fields.Str()
    tags = fields.Dict(keys=fields.Str(), values=fields.Str())
    materialization_settings = NestedField(MaterializationSettingsSchema)
