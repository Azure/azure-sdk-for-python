# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import fields, pre_load, post_dump

from azure.ai.ml._schema.component.input_output import InputPortSchema, OutputPortSchema, ParameterSchema
from azure.ai.ml._schema.core.fields import ArmVersionedStr, NestedField, PythonFuncNameStr, UnionField
from azure.ai.ml.constants._common import AzureMLResourceType

from ..assets.asset import AssetSchema
from ..core.fields import RegistryStr


class ComponentNameStr(PythonFuncNameStr):
    def _get_field_name(self):
        return "Component"


class ComponentSchema(AssetSchema):
    schema = fields.Str(data_key="$schema", attribute="_schema")
    name = ComponentNameStr(required=True)
    id = UnionField(
        [
            RegistryStr(dump_only=True),
            ArmVersionedStr(azureml_type=AzureMLResourceType.COMPONENT, dump_only=True),
        ]
    )
    display_name = fields.Str()
    description = fields.Str()
    tags = fields.Dict(keys=fields.Str(), values=fields.Str())
    is_deterministic = fields.Bool()
    inputs = fields.Dict(
        keys=fields.Str(),
        values=UnionField(
            [
                NestedField(ParameterSchema),
                NestedField(InputPortSchema),
            ]
        ),
    )
    outputs = fields.Dict(
        keys=fields.Str(),
        values=NestedField(OutputPortSchema),
    )

    def __init__(self, *args, **kwargs):
        # Remove schema_ignored to enable serialize and deserialize schema.
        self._declared_fields.pop("schema_ignored", None)  # pylint: disable=no-member
        super().__init__(*args, **kwargs)

    @pre_load
    def convert_version_to_str(self, data, **kwargs):  # pylint: disable=unused-argument, no-self-use
        if isinstance(data, dict) and data.get("version", None):
            data["version"] = str(data["version"])
        return data

    @post_dump
    def convert_input_value_to_str(self, data, **kwargs):
        if isinstance(data, dict) and data.get("inputs", None):
            input_dict = data["inputs"]
            for name, input in input_dict.items():
                input_type = input.get("type", None)
                if isinstance(input_type, str) and input_type.lower() == "float":
                    # Convert number to string to avoid precision issue
                    for key in ["default", "min", "max"]:
                        if input.get(key, None) is not None:
                            input[key] = str(input[key])
        return data
