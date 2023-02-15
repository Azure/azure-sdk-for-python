# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# hack: map internal component output type to valid v2 output type
from azure.ai.ml._internal._schema.input_output import SUPPORTED_INTERNAL_PARAM_TYPES
from azure.ai.ml._utils.utils import get_all_enum_values_iter
from azure.ai.ml.constants import AssetTypes
from azure.ai.ml.constants._common import InputTypes


def _map_internal_output_type(_meta):
    """Map component output type to valid pipeline output type."""
    def _map_primitive_type(_type):
        """Convert double and float to number type."""
        _type = _type.lower()
        if _type in ["double", "float"]:
            return InputTypes.NUMBER
        return _type

    if type(_meta).__name__ != "InternalOutput":
        return _meta.type
    if _meta.type in list(get_all_enum_values_iter(AssetTypes)):
        return _meta.type
    if _meta.type in SUPPORTED_INTERNAL_PARAM_TYPES:
        return _map_primitive_type(_meta.type)
    if _meta.type in ["AnyFile"]:
        return AssetTypes.URI_FILE
    # Handle AnyDirectory and the other types.
    return AssetTypes.URI_FOLDER
