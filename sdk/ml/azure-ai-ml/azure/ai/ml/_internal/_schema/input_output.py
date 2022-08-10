# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from marshmallow import fields, post_dump, post_load

from azure.ai.ml._schema import StringTransformedEnum, UnionField
from azure.ai.ml._schema.component.input_output import InputPortSchema, OutputPortSchema, ParameterSchema


class InternalInputPortSchema(InputPortSchema):
    # skip client-side validate for type enum & support list
    type = UnionField(
        [
            fields.Str(),
            # TODO 1856980: support [AnyFile, AnyDirectory] for component creation
            fields.List(fields.Str()),
        ],
        required=True,
        data_key="type",
    )
    is_resource = fields.Bool()
    datastore_mode = fields.Str()


class InternalOutputPortSchema(OutputPortSchema):
    # skip client-side validate for type enum
    type = fields.Str(
        required=True,
        data_key="type",
    )
    is_link_mode = fields.Bool()
    datastore_mode = fields.Str()


class InternalParameterSchema(ParameterSchema):
    type = StringTransformedEnum(
        allowed_values=["number", "integer", "boolean", "string", "object", "float"],
        casing_transform=lambda x: x,
        required=True,
        data_key="type",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_skip_fields(self):
        return []

    @post_dump(pass_original=True)
    def resolve_input_specific_field(self, data, original_data, **kwargs):
        for attr_name, value in original_data.items():
            if not attr_name.startswith("_") and attr_name not in self.get_skip_fields() and attr_name not in data:
                data[attr_name] = value
        return data


class InternalEnumParameterSchema(ParameterSchema):
    type = StringTransformedEnum(
        allowed_values=["enum"],
        required=True,
        data_key="type",
    )
    enum = fields.List(UnionField([fields.Str(), fields.Number(), fields.Bool()]))

    @post_dump
    @post_load
    def enum_value_to_string(self, data, **kwargs):
        if "enum" in data:
            data["enum"] = list(map(str, data["enum"]))
        if "default" in data:
            data["default"] = str(data["default"])
        return data
