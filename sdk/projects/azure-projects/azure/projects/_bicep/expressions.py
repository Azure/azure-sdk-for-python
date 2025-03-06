# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import json
from typing import Dict, List, Type, Generic, Literal, Optional, Any, Union
from typing_extensions import TypeVar
from enum import Enum

from .utils import resolve_value, serialize

BicepDataTypes = Literal["string", "array", "object", "int", "bool"]
_type = type


class Default(Enum):
    MISSING = "NoDefault"


MISSING = Default.MISSING


class Expression:
    def __init__(self, value: Union["Expression", str], /) -> None:
        self._value = value

    def __eq__(self, value: Any) -> bool:
        try:
            return self.value == value.value
        except AttributeError:
            return False

    def __ne__(self, value: Any) -> bool:
        return not self.__eq__(value)

    def __repr__(self) -> str:
        return str(self._resolve_expression(self._value))

    def __hash__(self):
        return hash(self.value)

    def _resolve_expression(self, expression: Union["Expression", str]):
        try:
            return expression.value
        except AttributeError:
            return expression

    def _resolve_obj(self, value: Union["Expression", Any]):
        try:
            return value.value
        except AttributeError:
            return serialize(value)

    @property
    def value(self) -> str:
        return self._resolve_expression(self._value)

    def format(self, format_str: Optional[str] = None, /) -> str:
        if format_str:
            return format_str.format(f"${{{self.value}}}")
        return f"${{{self.value}}}"


class Subscription(Expression):
    def __init__(self, subscription: Optional[Union[Expression, str]] = None, /):
        self._sub = subscription

    def __repr__(self) -> str:
        sub = self._sub or "<default>"
        return f"subscription({sub})"

    @property
    def value(self) -> str:
        if self._sub:
            return f"subscription({resolve_value(self._sub)})"
        return f"subscription()"

    @property
    def subscription_id(self) -> Expression:
        return Expression(f"{self.value}.subscriptionId")

    @property
    def tenant_id(self) -> Expression:
        return Expression(f"{self.value}.tenantId")


class ResourceGroup(Expression):
    def __init__(self, resource_group: Optional[Union[Expression, str]] = None, /):
        self._rg = resource_group

    def __repr__(self) -> str:
        sub = self._rg or "<default>"
        return f"resourcegroup({sub})"

    @property
    def value(self) -> str:
        if self._rg:
            return f"resourceGroup({resolve_value(self._rg)})"
        return f"resourceGroup()"

    @property
    def name(self) -> Union[str, Expression]:
        if self._rg:
            return self._rg
        return Expression(f"{self.value}.name")

    @property
    def id(self) -> Expression:
        return Expression(f"{self.value}.id")


class ResourceSymbol(Expression):
    def __init__(
        self,
        value: str,
        *,
        principal_id: bool = False,
    ) -> None:
        self._value = value
        self._principal_id_output = principal_id

    def __repr__(self) -> str:
        return f"resource({self._value})"

    @property
    def value(self) -> str:
        return self._value

    @property
    def name(self) -> "Output[str]":
        return Output(None, "name", self)

    @property
    def id(self) -> "Output[str]":
        return Output(None, "id", self)

    @property
    def principal_id(self) -> "Output[str]":
        if not self._principal_id_output:
            raise ValueError("Module has no principal ID output.")
        return Output(None, "properties.principalId", self)


ParameterType = TypeVar("ParameterType", str, int, bool, dict, list, default=str)


class Parameter(Expression, Generic[ParameterType]):
    name: str
    type: str
    module: str
    default: Union[ParameterType, Literal[Default.MISSING]]

    def __init__(
        self,
        name: str,
        *,
        type: Optional[Type[ParameterType]] = None,
        default: ParameterType = MISSING,
        secure: bool = False,
        description: Optional[str] = None,
        varname: Optional[str] = None,
        allowed: Optional[List[int]] = None,
        max_value: Optional[int] = None,
        min_value: Optional[int] = None,
        max_length: Optional[int] = None,
        min_length: Optional[int] = None,
        module: str = "main",
    ):
        self.name = name
        self.default = default
        self.module = module
        if type:
            self._type = type
        elif default and default is not MISSING:
            self._type = _type(default)
        else:
            self._type = str
        self._secure = secure
        self._description = description
        self._varname = varname
        self._allowed = allowed
        self._max_value = max_value
        self._min_value = min_value
        self._max_length = max_length
        self._min_length = min_length

    @property
    def value(self) -> str:
        return self.name

    @property
    def type(self) -> str:
        if self._type is str:
            return "string"
        if self._type is bool:
            return "boolean"
        if self._type is list:
            return "array"
        if self._type is int:
            return "int"
        return "object"

    def __repr__(self) -> str:
        if self.default not in (None, MISSING, ""):
            return f"parameter({self.name}={self.default})"
        return f"parameter({self.name})"

    def __bicep__(self, default: Optional[ParameterType] = None, /) -> str:
        declaration = ""
        if self._secure:
            declaration += "@sys.secure()\n"
        if self._description:
            declaration += f"@sys.description('{self._description}')\n"
        if self._allowed:
            declaration += "@sys.allowed([\n"
            for value in self._allowed:
                if isinstance(value, str):
                    clean_value = "'" + json.dumps(value).strip('"') + "'"
                else:
                    clean_value = json.dumps(value)
                declaration += f"  {clean_value}\n"
            declaration += "])\n"
        if self._max_value is not None:
            declaration += f"@sys.maxValue({self._max_value})\n"
        if self._min_value is not None:
            declaration += f"@sys.minValue({self._min_value})\n"
        if self._max_length is not None:
            declaration += f"@sys.maxLength({self._max_length})\n"
        if self._min_length is not None:
            declaration += f"@sys.minLength({self._min_length})\n"
        declaration += f"param {self.name} {self.type}"
        if default or self.default is not MISSING:
            declaration += " = "
            declaration += serialize(default or self.default)
        declaration += "\n\n"
        return declaration

    def __obj__(self) -> Dict[str, Dict[str, str]]:
        if not self._varname:
            return {}
        if self.default not in (None, MISSING, ""):
            value = f"${{{self._varname}={self.default}}}"
        else:
            value = f"${{{self._varname}}}"
        return {self.name: {"value": value}}


class Variable(Parameter[ParameterType]):
    def __init__(
        self,
        name: str,
        value: ParameterType,
        *,
        description: Optional[str] = None,
        module: str = "main",
    ):
        self._value = value
        super().__init__(name=name, type=type(value), description=description, module=module)

    def __repr__(self) -> str:
        return f"var({self.name})"

    def __bicep__(self, default: Optional[ParameterType] = None, /) -> str:
        declaration = ""
        if self._description:
            declaration += f"@sys.description('{self._description}')\n"
        declaration += f"var {self.name} = "
        declaration += serialize(default or self._value)
        declaration += "\n"
        return declaration


class Output(Parameter[ParameterType]):
    def __init__(
        self,
        name: str,
        value: Union[Expression, str],
        symbol: Optional[ResourceSymbol] = None,
        *,
        type: Type[ParameterType] = str,
        description: Optional[str] = None,
    ) -> None:
        self.symbol = symbol
        self._path = value
        super().__init__(name=name, type=type, description=description, module="")

    def __repr__(self) -> str:
        return f"output({self.value})"

    @property
    def value(self) -> str:
        if self.symbol:
            return f"{self.symbol.value}.{self._path}"
        value = resolve_value(self._path)
        return value

    def __bicep__(self, *args) -> str:
        declaration = ""
        if self._description:
            declaration += f"@sys.description('{self._description}')\n"
        declaration += f"output {self.name} {self.type} = {self.value}\n"
        return declaration


class Guid(Expression):
    def __init__(
        self,
        basestr: Union[Expression, str],
        *args: Union[Expression, str],
    ) -> None:
        self._args = [basestr] + list(args)

    def __repr__(self):
        return self.value

    @property
    def value(self) -> str:
        arg_str = ", ".join([resolve_value(a) for a in self._args])
        return f"guid({arg_str})"


class UniqueString(Expression):
    def __init__(
        self,
        basestr: Union[Expression, str],
        *args: Union[Expression, str],
    ) -> None:
        self._args = [basestr] + list(args)

    def __repr__(self):
        return self.value

    @property
    def value(self) -> str:
        arg_str = ", ".join([resolve_value(a) for a in self._args])
        return f"uniqueString({arg_str})"


class RoleDefinition(Expression):
    def __init__(self, guid: str) -> None:
        self._guid = guid
        self.description: Optional[str] = None

    def __repr__(self):
        return f"roleDefinition({self._guid})"

    @property
    def value(self) -> str:
        return (
            f"subscriptionResourceId(\n      'Microsoft.Authorization/roleDefinitions',\n      '{self._guid}'\n    )\n"
        )
