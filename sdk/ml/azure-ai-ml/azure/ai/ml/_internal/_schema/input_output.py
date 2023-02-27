# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import fields, post_dump, post_load

from azure.ai.ml._schema import PatchedSchemaMeta, StringTransformedEnum, UnionField
from azure.ai.ml._schema.component.input_output import InputPortSchema, ParameterSchema
from azure.ai.ml._schema.core.fields import DumpableEnumField, PrimitiveValueField

SUPPORTED_INTERNAL_PARAM_TYPES = [
    "integer",
    "Integer",
    "boolean",
    "Boolean",
    "string",
    "String",
    "float",
    "Float",
    "double",
    "Double",
]


class InternalInputPortSchema(InputPortSchema):
    # skip client-side validate for type enum & support list
    type = UnionField(
        [
            fields.Str(),
            fields.List(fields.Str()),
        ],
        required=True,
        data_key="type",
    )
    is_resource = fields.Bool()
    datastore_mode = fields.Str()

    @post_dump(pass_original=True)
    def resolve_list_type(self, data, original_data, **kwargs):  # pylint: disable=unused-argument, no-self-use
        if isinstance(original_data.type, list):
            data["type"] = original_data.type
        return data


class InternalOutputPortSchema(metaclass=PatchedSchemaMeta):
    # skip client-side validate for type enum
    type = fields.Str(
        required=True,
        data_key="type",
    )
    description = fields.Str()
    is_link_mode = fields.Bool()
    datastore_mode = fields.Str()


class InternalPrimitiveOutputSchema(metaclass=PatchedSchemaMeta):
    type = DumpableEnumField(
        allowed_values=SUPPORTED_INTERNAL_PARAM_TYPES,
        required=True,
    )
    description = fields.Str()
    is_control = fields.Bool()


class InternalParameterSchema(ParameterSchema):
    type = DumpableEnumField(
        allowed_values=SUPPORTED_INTERNAL_PARAM_TYPES,
        required=True,
        data_key="type",
    )


class InternalEnumParameterSchema(ParameterSchema):
    type = StringTransformedEnum(
        allowed_values=["enum"],
        required=True,
        data_key="type",
    )
    default = PrimitiveValueField()
    enum = fields.List(
        PrimitiveValueField(),
        required=True,
    )

    @post_dump
    @post_load
    def enum_value_to_string(self, data, **kwargs):  # pylint: disable=unused-argument, disable=no-self-use
        if "enum" in data:
            data["enum"] = list(map(str, data["enum"]))
        if "default" in data and data["default"] is not None:
            data["default"] = str(data["default"])
        return data
