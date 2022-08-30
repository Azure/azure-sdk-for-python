# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

from marshmallow import fields, post_load, pre_load

from azure.ai.ml._schema.core.fields import ArmVersionedStr, NestedField, UnionField
from azure.ai.ml._schema.component.input_output import InputPortSchema, OutputPortSchema, ParameterSchema
from azure.ai.ml._schema.core.fields import PythonFuncNameStr
from azure.ai.ml.constants import BASE_PATH_CONTEXT_KEY, AzureMLResourceType

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
    outputs = fields.Dict(keys=fields.Str(), values=NestedField(OutputPortSchema))

    def __init__(self, *args, **kwargs):
        # Remove schema_ignored to enable serialize and deserialize schema.
        self._declared_fields.pop("schema_ignored", None)
        super().__init__(*args, **kwargs)

    @post_load
    def make(self, data, **kwargs):
        data[BASE_PATH_CONTEXT_KEY] = self.context[BASE_PATH_CONTEXT_KEY]
        return data

    @pre_load
    def convert_version_to_str(self, data, **kwargs):
        if isinstance(data, dict) and data.get("version", None):
            data["version"] = str(data["version"])
        return data
