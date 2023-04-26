# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

from marshmallow import fields, INCLUDE, pre_dump

from azure.ai.ml._schema.core.fields import DumpableEnumField, ExperimentalField, UnionField, NestedField
from azure.ai.ml._schema.core.schema import PatchedSchemaMeta
from azure.ai.ml._utils.utils import is_private_preview_enabled
from azure.ai.ml.constants._common import AssetTypes, InputOutputModes, LegacyAssetTypes
from azure.ai.ml.constants._component import ComponentParameterTypes
from azure.ai.ml._schema.core.intellectual_property import ProtectionLevelSchema

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
    # hide in private preview
    if is_private_preview_enabled():
        # only protection_level is allowed for inputs
        intellectual_property = ExperimentalField(NestedField(ProtectionLevelSchema))

    @pre_dump
    def add_private_fields_to_dump(self, data, **kwargs):  # pylint: disable=unused-argument,no-self-use
        # The ipp field is set on the output object as "_intellectual_property".
        # We need to set it as "intellectual_property" before dumping so that Marshmallow
        # can pick up the field correctly on dump and show it back to the user.
        if hasattr(data, "_intellectual_property"):
            ipp_field = data._intellectual_property  # pylint: disable=protected-access
            if ipp_field:
                setattr(data, "intellectual_property", ipp_field)
        return data


class OutputPortSchema(metaclass=PatchedSchemaMeta):
    type = DumpableEnumField(
        allowed_values=SUPPORTED_PORT_TYPES,
        required=True,
    )
    description = fields.Str()
    mode = DumpableEnumField(
        allowed_values=SUPPORTED_INPUT_OUTPUT_MODES,
    )
    # hide in private preview
    if is_private_preview_enabled():
        # only protection_level is allowed for outputs
        intellectual_property = ExperimentalField(NestedField(ProtectionLevelSchema))

    @pre_dump
    def add_private_fields_to_dump(self, data, **kwargs):  # pylint: disable=unused-argument,no-self-use
        # The ipp field is set on the output object as "_intellectual_property".
        # We need to set it as "intellectual_property" before dumping so that Marshmallow
        # can pick up the field correctly on dump and show it back to the user.
        if hasattr(data, "_intellectual_property"):
            ipp_field = data._intellectual_property  # pylint: disable=protected-access
            if ipp_field:
                setattr(data, "intellectual_property", ipp_field)
        return data


class PrimitiveOutputSchema(OutputPortSchema):
    # Note: according to marshmallow doc on Handling Unknown Fields:
    # https://marshmallow.readthedocs.io/en/stable/quickstart.html#handling-unknown-fields
    # specify unknown at instantiation time will not take effect;
    # still add here just for explicitly declare this behavior:
    # primitive type output used in environment that private preview flag is not enabled.
    class Meta:
        unknown = INCLUDE

    type = DumpableEnumField(
        allowed_values=SUPPORTED_PARAM_TYPES,
        required=True,
    )
    # hide is_control and early_available in spec
    if is_private_preview_enabled():
        is_control = fields.Bool()
        early_available = fields.Bool()

    def _serialize(self, obj, *, many: bool = False):
        """Override to add private preview hidden fields"""
        from azure.ai.ml.entities._job.pipeline._attr_dict import has_attr_safe  # pylint: disable=protected-access

        ret = super()._serialize(obj, many=many)  # pylint: disable=no-member
        if has_attr_safe(obj, "is_control") and obj.is_control is not None and "is_control" not in ret:
            ret["is_control"] = obj.is_control
        if has_attr_safe(obj, "early_available") and obj.early_available is not None and "early_available" not in ret:
            ret["early_available"] = obj.early_available
        return ret


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
