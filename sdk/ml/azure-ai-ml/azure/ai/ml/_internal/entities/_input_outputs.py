# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Dict, Optional, Union, overload

from ... import Input, Output
from ..._utils.utils import get_all_enum_values_iter
from ...constants import AssetTypes
from ...constants._common import InputTypes
from ...constants._component import ComponentParameterTypes, IOConstants
from .._schema.input_output import SUPPORTED_INTERNAL_PARAM_TYPES

_INPUT_TYPE_ENUM = "enum"
_INPUT_TYPE_ENUM_CAP = "Enum"
_INPUT_TYPE_FLOAT = "float"
_INPUT_TYPE_FLOAT_CAP = "Float"


class InternalInput(Input):
    """Internal input class for internal components only. Comparing to the public Input class, this class has additional
    primitive input types:

    - String
    - Integer
    - Float, float
    - Boolean
    - Enum, enum (new)
    """

    def __init__(self, *, datastore_mode=None, is_resource=None, **kwargs):
        self.datastore_mode = datastore_mode
        self.is_resource = is_resource
        super().__init__(**kwargs)

    @property
    def _allowed_types(self):
        if self._lower_type == _INPUT_TYPE_ENUM:
            return str
        if self._lower_type == _INPUT_TYPE_FLOAT:
            return float
        return IOConstants.PRIMITIVE_STR_2_TYPE.get(self._lower_type, None)

    @property
    def _lower_type(self) -> Optional[str]:
        if isinstance(self.type, str):
            return self.type.lower()
        if self._multiple_types:
            return None
        return self.type.__name__.lower()

    @property
    def _is_primitive_type(self):
        if self._lower_type in [_INPUT_TYPE_ENUM, _INPUT_TYPE_FLOAT]:
            return True
        if self._lower_type in IOConstants.PRIMITIVE_STR_2_TYPE:
            return True
        return super()._is_primitive_type

    def _simple_parse(self, value, _type=None):
        # simple parse is used to parse min, max & optional only, so we don't need to handle enum
        if _type is None:
            _type = self._lower_type
        if _type == _INPUT_TYPE_FLOAT:
            _type = ComponentParameterTypes.NUMBER
        return super()._simple_parse(value, _type)

    def _to_rest_object(self) -> Dict:
        rest_object = super()._to_rest_object()
        if self._lower_type == _INPUT_TYPE_ENUM:
            rest_object["type"] = _INPUT_TYPE_ENUM_CAP
        if self._lower_type == _INPUT_TYPE_FLOAT:
            rest_object["type"] = _INPUT_TYPE_FLOAT_CAP
        return rest_object

    @classmethod
    def _map_from_rest_type(cls, _type):
        mapping_dict = {
            _INPUT_TYPE_ENUM_CAP: _INPUT_TYPE_ENUM,
            _INPUT_TYPE_FLOAT_CAP: _INPUT_TYPE_FLOAT,
        }
        if isinstance(_type, str) and _type in mapping_dict:
            return mapping_dict[_type]
        return super()._map_from_rest_type(_type)

    @classmethod
    def _from_rest_object(cls, obj: Dict) -> "InternalInput":
        obj["type"] = cls._map_from_rest_type(obj["type"])
        return InternalInput(**obj)

    def _get_python_builtin_type_str(self) -> str:
        if self._lower_type in [_INPUT_TYPE_ENUM, _INPUT_TYPE_FLOAT]:
            return self._lower_type
        if self._is_primitive_type:
            return IOConstants.PRIMITIVE_STR_2_TYPE[self._lower_type].__name__  # type: ignore[index]
            # TODO: Bug 2881900
        return super()._get_python_builtin_type_str()

    @overload
    @classmethod
    def _from_base(cls, _input: None) -> None:  # type: ignore[misc]
        ...

    @overload
    @classmethod
    def _from_base(cls, _input: Union[Input, Dict]) -> "InternalInput": ...

    @classmethod
    def _from_base(cls, _input: Optional[Union[Input, Dict]]) -> Optional["InternalInput"]:
        """Cast from Input or Dict to InternalInput.

        Do not guarantee to create a new object.

        :param _input: The base input
        :type _input: Union[Input, Dict]
        :return:
          * None if _input is None
          * InternalInput
        :rtype: Optional["InternalInput"]
        """
        if _input is None:
            return None
        if isinstance(_input, InternalInput):
            return _input
        if isinstance(_input, Input):
            # do force cast directly as there is no new field added in InternalInput
            # need to change the logic if new field is added
            _input.__class__ = InternalInput
            return _input  # type: ignore[return-value]
        return InternalInput(**_input)


def _map_v1_io_type(output_type: str) -> str:
    """Map v1 IO type to v2.

    :param output_type: The v1 IO type
    :type output_type: str
    :return: The v2 IO type name
    :rtype: str
    """

    # TODO: put it in a common place
    def _map_primitive_type(_type: str) -> str:
        """Convert double and float to number type.

        :param _type: A primitive v1 IO type
        :type _type: str
        :return:
          * InputTypes.NUMBER if _type is "double" or "float"
          * The provided type otherwise
        :rtype: str
        """
        _type = _type.lower()
        if _type in ["double", "float"]:
            return InputTypes.NUMBER
        return _type

    if output_type in list(get_all_enum_values_iter(AssetTypes)):
        return output_type
    if output_type in SUPPORTED_INTERNAL_PARAM_TYPES:
        return _map_primitive_type(output_type)
    if output_type in ["AnyFile"]:
        return AssetTypes.URI_FILE
    # Handle AnyDirectory and the other types.
    return AssetTypes.URI_FOLDER


class InternalOutput(Output):
    def __init__(self, *, datastore_mode=None, is_link_mode=None, **kwargs):
        self.datastore_mode = datastore_mode
        self.is_link_mode = is_link_mode
        super().__init__(**kwargs)

    @classmethod
    def _from_base(cls, _output: Union[Output, Dict]) -> Optional["InternalOutput"]:
        if _output is None:
            return None
        if isinstance(_output, InternalOutput):
            return _output
        if isinstance(_output, Output):
            # do force cast directly as there is no new field added in InternalInput
            # need to change the logic if new field is added
            _output.__class__ = InternalOutput
            return _output  # type: ignore[return-value]
        return InternalOutput(**_output)

    def map_pipeline_output_type(self) -> str:
        """Map output type to pipeline output type.

        :return: The pipeline output type
        :rtype: str
        """
        # TODO: call this for node output
        return _map_v1_io_type(self.type)
