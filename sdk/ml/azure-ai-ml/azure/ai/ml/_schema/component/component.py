# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import fields, post_dump, pre_load, pre_dump

from azure.ai.ml._schema.component.input_output import InputPortSchema, OutputPortSchema, ParameterSchema
from azure.ai.ml._schema.core.fields import (
    ArmVersionedStr,
    ExperimentalField,
    NestedField,
    PythonFuncNameStr,
    UnionField,
)
from azure.ai.ml._schema.core.intellectual_property import IntellectualPropertySchema
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
    intellectual_property = ExperimentalField(NestedField(IntellectualPropertySchema))

    def __init__(self, *args, **kwargs):
        # Remove schema_ignored to enable serialize and deserialize schema.
        self._declared_fields.pop("schema_ignored", None)  # pylint: disable=no-member
        super().__init__(*args, **kwargs)

    @pre_load
    def convert_version_to_str(self, data, **kwargs):  # pylint: disable=unused-argument, no-self-use
        if isinstance(data, dict) and data.get("version", None):
            data["version"] = str(data["version"])
        return data

    @pre_dump
    def add_private_fields_to_dump(self, data, **kwargs):  # pylint: disable=unused-argument,no-self-use
        # The ipp field is set on the component object as "_intellectual_property".
        # We need to set it as "intellectual_property" before dumping so that Marshmallow
        # can pick up the field correctly on dump and show it back to the user.
        ipp_field = data._intellectual_property # pylint: disable=protected-access
        if ipp_field:
            setattr(data, "intellectual_property", ipp_field)
        return data

    @post_dump
    def convert_input_value_to_str(self, data, **kwargs):  # pylint:disable=unused-argument, no-self-use
        if isinstance(data, dict) and data.get("inputs", None):
            input_dict = data["inputs"]
            for input_value in input_dict.values():
                input_type = input_value.get("type", None)
                if isinstance(input_type, str) and input_type.lower() == "float":
                    # Convert number to string to avoid precision issue
                    for key in ["default", "min", "max"]:
                        if input_value.get(key, None) is not None:
                            input_value[key] = str(input_value[key])
        return data
