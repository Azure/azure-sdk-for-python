# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

from marshmallow import fields

from azure.ai.ml._schema.core.fields import DumpableEnumField, UnionField
from azure.ai.ml._schema.core.schema import PatchedSchemaMeta
from azure.ai.ml.constants._common import AssetTypes, InputOutputModes, LegacyAssetTypes
from azure.ai.ml.constants._component import ComponentParameterTypes

# Here we use an adhoc way to collect all class constant attributes by checking if it's upper letter
# because making those constants enum will fail in string serialization in marshmallow
asset_type_obj = AssetTypes()
SUPPORTED_PORT_TYPES = [LegacyAssetTypes.PATH] + [
    getattr(asset_type_obj, k) for k in dir(asset_type_obj) if k.isupper()
]
param_obj = ComponentParameterTypes()
SUPPORTED_PARAM_TYPES = [getattr(param_obj, k) for k in dir(param_obj) if k.isupper()]

input_output_type_obj = InputOutputModes()
# Link mode is only supported in component level currently
SUPPORTED_INPUT_OUTPUT_MODES = [
    getattr(input_output_type_obj, k) for k in dir(input_output_type_obj) if k.isupper()
] + ["link"]


class InputPortSchema(metaclass=PatchedSchemaMeta):
    type = DumpableEnumField(
        allowed_values=SUPPORTED_PORT_TYPES,
        required=True,
    )
    description = fields.Str()
    optional = fields.Bool()
    default = fields.Str()
    mode = DumpableEnumField(
        allowed_values=SUPPORTED_INPUT_OUTPUT_MODES,
    )


class OutputPortSchema(metaclass=PatchedSchemaMeta):
    type = DumpableEnumField(
        allowed_values=SUPPORTED_PORT_TYPES,
        required=True,
    )
    description = fields.Str()
    mode = DumpableEnumField(
        allowed_values=SUPPORTED_INPUT_OUTPUT_MODES,
    )


class PrimitiveOutputSchema(OutputPortSchema):
    type = DumpableEnumField(
        allowed_values=SUPPORTED_PARAM_TYPES,
        required=True,
    )
    is_control = fields.Bool()


class ParameterSchema(metaclass=PatchedSchemaMeta):
    type = DumpableEnumField(
        allowed_values=SUPPORTED_PARAM_TYPES,
        required=True,
    )
    optional = fields.Bool()
    default = UnionField([fields.Str(), fields.Number(), fields.Bool()])
    description = fields.Str()
    max = UnionField([fields.Str(), fields.Number()])
    min = UnionField([fields.Str(), fields.Number()])
    enum = fields.List(fields.Str())
