# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Dict, Optional, Union

from azure.ai.ml import Input, Output
from azure.ai.ml.constants._component import ComponentParameterTypes, IOConstants

_INPUT_TYPE_ENUM = "enum"
_INPUT_TYPE_ENUM_CAP = "Enum"
_INPUT_TYPE_FLOAT = "float"
_INPUT_TYPE_FLOAT_CAP = "Float"


class InternalInput(Input):
    """Internal input class for internal components only.
    Comparing to the public Input class, this class has additional primitive
    input types:
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
            return IOConstants.PRIMITIVE_STR_2_TYPE[self._lower_type].__name__
        return super()._get_python_builtin_type_str()

    @classmethod
    def _from_base(cls, _input: Union[Input, Dict]) -> Optional["InternalInput"]:
        """Cast from Input or Dict to InternalInput. Do not guarantee to create a new object."""
        if _input is None:
            return None
        if isinstance(_input, InternalInput):
            return _input
        if isinstance(_input, Input):
            # do force cast directly as there is no new field added in InternalInput
            # need to change the logic if new field is added
            _input.__class__ = InternalInput
            return _input
        return InternalInput(**_input)


class InternalOutput(Output):
    def __init__(self, *, datastore_mode=None, **kwargs):
        self.datastore_mode = datastore_mode
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
            return _output
        return InternalOutput(**_output)
