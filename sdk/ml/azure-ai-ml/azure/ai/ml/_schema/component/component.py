# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from pathlib import Path

from marshmallow import ValidationError, fields, post_dump, pre_dump, pre_load
from marshmallow.fields import Field

from azure.ai.ml._schema.component.input_output import InputPortSchema, OutputPortSchema, ParameterSchema
from azure.ai.ml._schema.core.fields import (
    ArmVersionedStr,
    ExperimentalField,
    NestedField,
    PythonFuncNameStr,
    UnionField,
)
from azure.ai.ml._schema.core.intellectual_property import IntellectualPropertySchema
from azure.ai.ml._utils.utils import is_private_preview_enabled, load_yaml
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, AzureMLResourceType

from .._utils.utils import _resolve_group_inputs_for_component
from ..assets.asset import AssetSchema
from ..core.fields import RegistryStr


class ComponentNameStr(PythonFuncNameStr):
    def _get_field_name(self):
        return "Component"


class ComponentYamlRefField(Field):
    """Allows you to nest a :class:`Schema <marshmallow.Schema>`
    inside a yaml ref field.
    """

    def _jsonschema_type_mapping(self):
        schema = {"type": "string"}
        if self.name is not None:
            schema["title"] = self.name
        if self.dump_only:
            schema["readonly"] = True
        return schema

    def _deserialize(self, value, attr, data, **kwargs):
        if not isinstance(value, str):
            raise ValidationError(f"Nested yaml ref field expected a string but got {type(value)}.")

        base_path = Path(self.context[BASE_PATH_CONTEXT_KEY])

        source_path = Path(value)
        # raise if the string is not a valid path, like "azureml:xxx"
        try:
            source_path.resolve()
        except OSError as ex:
            raise ValidationError(f"Nested file ref field expected a local path but got {value}.") from ex

        if not source_path.is_absolute():
            source_path = base_path / source_path

        if not source_path.is_file():
            raise ValidationError(
                f"Nested yaml ref field expected a local path but can't find {value} based on {base_path.as_posix()}."
            )

        loaded_value = load_yaml(source_path)

        # local import to avoid circular import
        from azure.ai.ml.entities import Component

        component = Component._load(data=loaded_value, yaml_path=source_path)  # pylint: disable=protected-access
        return component

    def _serialize(self, value, attr, obj, **kwargs):
        raise ValidationError("Serialize on RefField is not supported.")


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
    # hide in private preview
    if is_private_preview_enabled():
        intellectual_property = ExperimentalField(NestedField(IntellectualPropertySchema))

    def __init__(self, *args, **kwargs):
        # Remove schema_ignored to enable serialize and deserialize schema.
        self._declared_fields.pop("schema_ignored", None)  # pylint: disable=no-member
        super().__init__(*args, **kwargs)

    @pre_load
    def convert_version_to_str(self, data, **kwargs):  # pylint: disable=unused-argument
        if isinstance(data, dict) and data.get("version", None):
            data["version"] = str(data["version"])
        return data

    @pre_dump
    def add_private_fields_to_dump(self, data, **kwargs):  # pylint: disable=unused-argument
        # The ipp field is set on the component object as "_intellectual_property".
        # We need to set it as "intellectual_property" before dumping so that Marshmallow
        # can pick up the field correctly on dump and show it back to the user.
        ipp_field = data._intellectual_property  # pylint: disable=protected-access
        if ipp_field:
            setattr(data, "intellectual_property", ipp_field)
        return data

    @post_dump
    def convert_input_value_to_str(self, data, **kwargs):  # pylint:disable=unused-argument
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

    @pre_dump
    def flatten_group_inputs(self, data, **kwargs):  # pylint: disable=unused-argument
        return _resolve_group_inputs_for_component(data)
