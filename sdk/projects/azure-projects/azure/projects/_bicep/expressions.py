# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import json
from typing import Dict, Iterable, List, Literal, Mapping, Optional, Any, Union, cast
from enum import Enum

from .utils import resolve_value, serialize


class Default(Enum):
    MISSING = "NoDefault"


MISSING = Default.MISSING


class Expression:
    def __init__(self, value: Union["Expression", str, None], /) -> None:
        self._value = value or ""

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

    def _resolve_expression(self, expression: Union["Expression", str]) -> str:
        if isinstance(expression, Expression):
            return expression.value
        return expression

    @property
    def value(self) -> str:
        return self._resolve_expression(self._value)

    def format(self, format_str: Optional[str] = None, /) -> str:
        if format_str:
            return format_str.format(f"${{{self.value}}}")
        return f"${{{self.value}}}"


class Subscription(Expression):
    def __init__(self, subscription: Optional[Union[Expression, str]] = None, /):
        super().__init__(subscription)

    def __repr__(self) -> str:
        sub = self._value or "<default>"
        return f"subscription({sub})"

    @property
    def value(self) -> str:
        if self._value:
            return f"subscription({resolve_value(self._value)})"
        return "subscription()"

    @property
    def subscription_id(self) -> Expression:
        return Expression(f"{self.value}.subscriptionId")

    @property
    def tenant_id(self) -> Expression:
        return Expression(f"{self.value}.tenantId")


class ResourceGroup(Expression):
    def __init__(self, resource_group: Optional[Union[Expression, str]] = None, /):
        super().__init__(resource_group)

    def __repr__(self) -> str:
        rg = self._value or "<default>"
        return f"resourcegroup({rg})"

    @property
    def value(self) -> str:
        if self._value:
            return f"resourceGroup({resolve_value(self._value)})"
        return "resourceGroup()"

    @property
    def name(self) -> Union[str, Expression]:
        if self._value:
            return self._value
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
        super().__init__(value)
        self._principal_id_output = principal_id

    def __repr__(self) -> str:
        return f"resource({self._value})"

    @property
    def value(self) -> str:
        return cast(str, self._value)

    @property
    def name(self) -> "Output":
        return Output(None, "name", self)

    @property
    def id(self) -> "Output":
        return Output(None, "id", self)

    @property
    def principal_id(self) -> "Output":
        if not self._principal_id_output:
            raise ValueError("Module has no principal ID output.")
        return Output(None, "properties.principalId", self)


class Parameter(Expression):
    env_var: Optional[str]
    default: Any

    def __init__(
        self,
        name: str,
        *,
        default: Any = MISSING,
        secure: bool = False,
        type: Optional[Literal["string", "int", "boolean", "array", "object"]] = None,
        description: Optional[str] = None,
        env_var: Optional[str] = None,
        allowed: Optional[List[int]] = None,
        max_value: Optional[int] = None,
        min_value: Optional[int] = None,
        max_length: Optional[int] = None,
        min_length: Optional[int] = None,
    ):
        super().__init__(name)
        self.env_var = env_var
        self.default = default
        self._type = type
        self._secure = secure
        self._description = description
        self._allowed = allowed
        self._max_value = max_value
        self._min_value = min_value
        self._max_length = max_length
        self._min_length = min_length

    @property
    def name(self) -> str:
        return cast(str, self._value)

    @property
    def value(self) -> str:
        return cast(str, self._value)

    @property
    def type(self) -> str:
        return self._get_type(self.default)

    def _get_type(self, value: Any) -> str:
        if self._type:
            return self._type
        if value is MISSING or isinstance(value, str):
            return "string"
        if value in [True, False]:
            return "boolean"
        if isinstance(value, int):
            return "int"
        if isinstance(value, Mapping):
            return "object"
        if isinstance(value, Iterable):
            return "array"
        raise TypeError("Parameter value incompatible with supported parameter types.")

    def __repr__(self) -> str:
        if self.default not in (None, MISSING, ""):
            return f"parameter({self.name}={self.default})"
        return f"parameter({self.name})"

    def __bicep__(self, default: Any = MISSING, /) -> str:
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
        value = default if default is not MISSING else self.default
        param_type = self._get_type(value)
        declaration += f"param {self.name} {param_type}"
        # TODO: What happens with when value=None? What's the correct bicep?
        if value is not MISSING:
            declaration += " = "
            declaration += serialize(value)
        declaration += "\n\n"
        return declaration

    def __obj__(self) -> Dict[str, Dict[str, str]]:
        if self.env_var:
            # if self.default not in (None, MISSING, ""):
            #     # TODO: Is this correct formatting for different default types? Objects?
            #     value = f"${{{self.env_var}={self.default}}}"
            # else:
            value = f"${{{self.env_var}}}"
            return {self.name: {"value": value}}
        if self.default is not MISSING:
            return {self.name: {"value": self.default}}
        return {}


class PlaceholderParameter(Parameter): ...


# TODO:
# class RequiredParameter(Parameter):
#     ...


class Variable(Parameter):
    def __init__(
        self,
        name: str,
        value: Any,
        *,
        description: Optional[str] = None,
    ):
        super().__init__(name=name, default=value, description=description)

    def __repr__(self) -> str:
        return f"var({self.name})"

    def __bicep__(self, value: Any = MISSING, /) -> str:
        declaration = ""
        if self._description:
            declaration += f"@sys.description('{self._description}')\n"
        declaration += f"var {self.name} = "
        declaration += serialize(value if value is not MISSING else self.default)
        declaration += "\n"
        return declaration

    def __obj__(self) -> Dict[str, Dict[str, str]]:
        return {}


class Output(Parameter):
    def __init__(
        self,
        name: Optional[str],
        value: Union[Expression, str],
        symbol: Optional[ResourceSymbol] = None,
        *,
        description: Optional[str] = None,
    ) -> None:
        self.symbol = symbol
        self._path = value
        super().__init__(name=name or "", description=description, type="string")

    def __repr__(self) -> str:
        return f"output({self.value})"

    def __eq__(self, value: Any) -> bool:
        try:
            return self.value == value.value and self.name == value.name
        except AttributeError:
            return False

    def __ne__(self, value: Any) -> bool:
        return not self.__eq__(value)

    def __lt__(self, value: Any) -> bool:
        try:
            return self.name < value.name
        except AttributeError:
            return False

    def __hash__(self):
        return hash(self.value + self.name)

    @property
    def value(self) -> str:
        if self.symbol:
            return f"{self.symbol.value}.{self._path}"
        value = resolve_value(self._path)
        return value

    def __bicep__(self, *args) -> str:  # pylint: disable=arguments-differ, unused-argument
        declaration = ""
        if self._description:
            declaration += f"@sys.description('{self._description}')\n"
        # TODO: We're only supporting string outputs for now....
        declaration += f"output {self.name} string = {self.value}\n"
        return declaration

    def __obj__(self) -> Dict[str, Dict[str, str]]:
        return {}


class Guid(Expression):
    def __init__(
        self,
        basestr: Union[Expression, str],
        *args: Union[Expression, str],
    ) -> None:
        super().__init__(basestr)
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
        super().__init__(basestr)
        self._args = [basestr] + list(args)

    def __repr__(self):
        return self.value

    @property
    def value(self) -> str:
        arg_str = ", ".join([resolve_value(a) for a in self._args])
        return f"uniqueString({arg_str})"


class RoleDefinition(Expression):
    def __init__(self, guid: str) -> None:
        super().__init__(guid)
        self.description: Optional[str] = None

    def __repr__(self):
        return f"roleDefinition({self._value})"

    @property
    def value(self) -> str:
        return (
            f"subscriptionResourceId(\n      'Microsoft.Authorization/roleDefinitions',\n      '{self._value}'\n    )\n"
        )
