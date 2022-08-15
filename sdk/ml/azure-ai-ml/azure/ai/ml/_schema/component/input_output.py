# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

from marshmallow import fields, pre_load, validate

from azure.ai.ml._schema.core.fields import UnionField
from azure.ai.ml._schema.core.schema import PatchedSchemaMeta
from azure.ai.ml.constants import AssetTypes, ComponentParameterTypes, LegacyAssetTypes

# Here we use an adhoc way to collect all class constant attributes by checking if it's upper letter
# because making those constants enum will fail in string serialization in marshmallow
asset_type_obj = AssetTypes()
SUPPORTED_PORT_TYPES = [LegacyAssetTypes.PATH] + [
    getattr(asset_type_obj, k) for k in dir(asset_type_obj) if k.isupper()
]
param_obj = ComponentParameterTypes()
SUPPORTED_PARAM_TYPES = [getattr(param_obj, k) for k in dir(param_obj) if k.isupper()]


class InputPortSchema(metaclass=PatchedSchemaMeta):
    type = fields.Str(
        validate=validate.OneOf(SUPPORTED_PORT_TYPES),
        required=True,
        data_key="type",
    )
    description = fields.Str()
    optional = fields.Bool()
    default = fields.Str()

    @pre_load
    def trim_input(self, data, **kwargs):
        if isinstance(data, dict):
            if "mode" in data:
                data.pop("mode")
        return data


class OutputPortSchema(metaclass=PatchedSchemaMeta):
    type = fields.Str(
        validate=validate.OneOf(SUPPORTED_PORT_TYPES),
        required=True,
        data_key="type",
    )
    description = fields.Str()

    @pre_load
    def trim_output(self, data, **kwargs):
        if isinstance(data, dict):
            if "mode" in data:
                data.pop("mode")
        return data


class ParameterSchema(metaclass=PatchedSchemaMeta):
    type = fields.Str(
        validate=validate.OneOf(SUPPORTED_PARAM_TYPES),
        required=True,
        data_key="type",
    )
    optional = fields.Bool()
    default = UnionField([fields.Str(), fields.Number(), fields.Bool()])
    description = fields.Str()
    max = UnionField([fields.Str(), fields.Number()])
    min = UnionField([fields.Str(), fields.Number()])
    enum = fields.List(fields.Str())
