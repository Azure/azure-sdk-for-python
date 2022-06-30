# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import copy
from typing import Dict, Type, Union

from azure.ai.ml.entities._mixins import RestTranslatableMixin


class ComponentIOItem(dict, RestTranslatableMixin):
    """Component input/output. Inherit from dictionary for flexibility."""

    def __init__(self, port_dict: Dict):
        self._type = port_dict["type"]
        self._default = port_dict.get("default", None)
        super().__init__(port_dict)

    @property
    def type(self) -> str:
        return self._type

    @property
    def default(self):
        return self._default


class ComponentInput(ComponentIOItem):
    # map from yaml type to rest object type
    DATA_TYPE_MAPPING = {
        "string": "String",
        "integer": "Integer",
        "number": "Number",
        "boolean": "Boolean",
    }
    # map from yaml type to python built in type
    PYTHON_BUILT_IN_TYPE_MAPPING = {
        "string": str,
        "integer": int,
        "number": float,
        "boolean": bool,
    }
    PARAM_PARSERS = {
        "float": float,
        "integer": lambda v: int(float(v)),  # backend returns 10.0 for integer, parse it to float before int
        "boolean": lambda v: str(v).lower() == "true",
        "number": lambda v: str(v),
    }

    def __init__(self, port_dict: Dict):
        # parse value from string to it's original type. eg: "false" -> False
        if isinstance(port_dict["type"], str) and port_dict["type"] in self.PARAM_PARSERS.keys():
            for key in ["default", "min", "max"]:
                if key in port_dict.keys():
                    port_dict[key] = self.PARAM_PARSERS[port_dict["type"]](port_dict[key])
        self._optional = self.PARAM_PARSERS["boolean"](port_dict.get("optional", "false"))
        super().__init__(port_dict)

    @property
    def python_builtin_type(self) -> Type[Union[int, str, float, bool]]:
        """Return python builtin type of the input."""
        return self.PYTHON_BUILT_IN_TYPE_MAPPING[self.type]

    def get_python_builtin_type_str(self) -> str:
        """Get python builtin type for current input in string, eg: str. Return yaml type if not available."""
        try:
            return self.python_builtin_type.__name__
        except KeyError:
            return self._type

    def _to_rest_object(self) -> Dict:
        result = copy.deepcopy(self)
        # parse string -> String, integer -> Integer, etc.
        if result["type"] in result.DATA_TYPE_MAPPING.keys():
            result["type"] = result.DATA_TYPE_MAPPING[result["type"]]
        return result

    @classmethod
    def _from_rest_object(cls, rest_dict: Dict) -> "ComponentInput":
        reversed_data_type_mapping = {v: k for k, v in cls.DATA_TYPE_MAPPING.items()}
        # parse String -> string, Integer -> integer, etc
        if rest_dict["type"] in reversed_data_type_mapping.keys():
            rest_dict["type"] = reversed_data_type_mapping[rest_dict["type"]]
        return ComponentInput(rest_dict)

    def _is_literal(self) -> bool:
        """Returns True if this input is literal input."""
        return self._type in ["number", "integer", "boolean", "string"]

    def _is_path(self) -> bool:
        """Returns True if this input is path input."""
        return self._type == "path"


class ComponentOutput(ComponentIOItem):
    def _to_rest_object(self) -> Dict:
        result = copy.deepcopy(self)
        return result

    @classmethod
    def _from_rest_object(cls, rest_dict: Dict) -> "ComponentOutput":
        return ComponentOutput(rest_dict)
