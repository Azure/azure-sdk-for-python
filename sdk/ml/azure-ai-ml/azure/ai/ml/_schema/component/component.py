# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from marshmallow import fields, post_load, pre_load

from azure.ai.ml._schema.core.fields import VersionField, PythonFuncNameStr
from azure.ai.ml.constants import AzureMLResourceType, BASE_PATH_CONTEXT_KEY
from azure.ai.ml._schema import PathAwareSchema, UnionField, NestedField, ArmVersionedStr
from azure.ai.ml._schema.component.input_output import InputPortSchema, ParameterSchema, OutputPortSchema
from azure.ai.ml._schema.job.creation_context import CreationContextSchema
from ..core.fields import RegistryStr


class ComponentNameStr(PythonFuncNameStr):
    def _get_field_name(self):
        return "Component"


class BaseComponentSchema(PathAwareSchema):
    schema = fields.Str(data_key="$schema", attribute="_schema")
    name = ComponentNameStr(required=True)
    id = UnionField(
        [
            RegistryStr(dump_only=True),
            ArmVersionedStr(azureml_type=AzureMLResourceType.COMPONENT, dump_only=True),
        ]
    )
    version = VersionField()
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
    creation_context = NestedField(CreationContextSchema, dump_only=True)

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
