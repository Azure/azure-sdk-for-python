# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from enum import Enum
import json
import re
import random
import string
import itertools
from typing import IO, Any, List, Optional, Dict, Literal, ClassVar, Union
from dataclasses import InitVar, dataclass, field, fields, is_dataclass


split_camelcase = re.compile('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)')
resource_prefix = "antisch"


def resolve_value(value: Any) -> str:
    try:
        return value.resolve()
    except AttributeError:
        if isinstance(value, Resource):
            return f"{value._symbolicname}.id"  # pylint: disable=protected-access
        return json.dumps(value).replace('"', "'")


def resolve_key(key: Any) -> str:
    if isinstance(key, Resource):
        return f"'${{{key._symbolicname}.id}}'"  # pylint: disable=protected-access
    if key.isidentifier():
        return key
    return f"'{key}'"


class BicepResolver:
    def resolve(self) -> str:
        raise NotImplementedError()

BicepStr = Union[str, BicepResolver]
BicepInt = Union[int, BicepResolver]
BicepBool = Union[bool, BicepResolver]


class Output(BicepResolver):
    def __init__(self, value: str) -> None:
        self._value = value

    def resolve(self) -> str:
        return self._value


class DefaultLocation(BicepResolver):
    def resolve(self) -> str:
        return "location"


class ResourceId(BicepResolver):
    def __init__(self, resource: 'Resource') -> None:
        self._resource = resource

    def resolve(self) -> str:
        return f"{self._resource._symbolicname}.id"  # pylint: disable=protected-access


class CloudMachineId(BicepResolver):
    def resolve(self) -> str:
        return "cloudmachineId"


class PrincipalId(BicepResolver):
    def __init__(self, resource: Optional['LocatedResource'] = None) -> None:
        self._resource = resource

    def resolve(self) -> str:
        if self._resource:
            return f"{self._resource._symbolicname}.properties.principalId"  # pylint: disable=protected-access
        return "principalId"


class BoolLogic(BicepResolver):
    def __init__(self, a_value, b_value, operator: Literal['==', '!=', '<', '>', '<=', '>=']):
        self._a = a_value
        self._b = b_value
        self._op = operator

    def resolve(self) -> str:
        return f"{resolve_value(self._a)} {self._op} {resolve_value(self._b)}"


class UniqueName(BicepResolver):
    def __init__(self, prefix: str, length: int, basestr: Optional[Any] = None) -> None:
        self._prefix = prefix
        self._length = length
        if basestr:
            self._basestr = resolve_value(basestr)
        else:
            self._basestr = "resourceGroup().id"

    def resolve(self) -> str:
        return f"take('{self._prefix}${{uniqueString({self._basestr})}}', {self._length})"


class ResourceName(BicepResolver):
    def __init__(self, suffix: Optional[str] = None):
        self._suffix = suffix or ""

    def resolve(self):
        return f"'{resource_prefix}${{cloudmachineId}}{self._suffix}'"


class GuidName(BicepResolver):
    def __init__(self, basestr: str, *args: str) -> None:
        self._args = [basestr] + list(args)

    def resolve(self) -> str:
        arg_str = ", ".join([resolve_value(a) for a in self._args])
        return f"guid({arg_str})"


class SubscriptionResourceId(BicepResolver):
    def __init__(self, resourcetype: str, name: Enum) -> None:
        self._resource = resourcetype
        self._name = name.value

    def resolve(self) -> str:
        return f"subscriptionResourceId('{self._resource}', '{self._name}')"


class SubscriptionScopeProperty(BicepResolver):
    def __init__(self, property_name: str = 'id'):
        self._property_name = property_name

    def resolve(self) -> str:
        return f"subscription().{self._property_name}"


class _SKIP:
    ...


class _UNSET:
    ...


def generate_symbol(prefix: str, n: int = 5) -> str:
    return prefix + '_' + ''.join(
        random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(n)
    ).lower()


def generate_envvar(identifier):
    matches = split_camelcase.finditer(identifier)
    return "_".join([m.group(0).upper() for m in matches])


def generate_name(n=itertools.count()) -> str:
    return f"${{resourceToken}}{next(n):03}"


def iter_fields(dataclass_value):
    for datafield in fields(dataclass_value):
        client_name = datafield.name
        if client_name.startswith('_'):
            continue
        value = getattr(dataclass_value, client_name)
        try:
            rest_name = datafield.metadata['rest']
        except KeyError:
            continue
        if value is _UNSET or rest_name is _SKIP:
            continue
        yield rest_name, value

def _serialize_resource(bicep: IO[str], model_val: 'Resource') -> None:
    # pylint: disable=protected-access
    indent: str = '  '
    bicep.write(f"resource {model_val._symbolicname} '{model_val._resource}@{model_val._version}' = {{\n")
    if model_val.parent:
        bicep.write(f"{indent}parent: {model_val.parent._symbolicname}\n")
    elif model_val.scope:
        bicep.write(f"{indent}scope: {model_val.scope._symbolicname}\n")

    for rest_name, value in iter_fields(model_val):
        if is_dataclass(value):
            bicep.write(f"{indent}{rest_name}: {{\n")
            _serialize_dataclass(bicep, value, indent + '  ')
            bicep.write(f"{indent}}}\n")
        elif isinstance(value, dict):
            if rest_name == 'tags':
                if not value:
                    bicep.write(f"{indent}{rest_name}: tags\n")
                    continue
                bicep.write(f"{indent}{rest_name}: union(\n")
                bicep.write(f"{indent}  tags, {{\n")
                _serialize_dict(bicep, value, indent + '    ')
                bicep.write(f"{indent}  }}\n")
                bicep.write(f"{indent})\n")
            else:
                if not value:
                    continue
                bicep.write(f"{indent}{rest_name}: {{\n")
                _serialize_dict(bicep, value, indent + '  ')
                bicep.write(f"{indent}}}\n")
        elif isinstance(value, list):
            if not value:
                continue
            bicep.write(f"{indent}{rest_name}: [\n")
            _serialize_list(bicep, value, indent + '  ')
            bicep.write(f"{indent}]\n")
        else:
            bicep.write(f"{indent}{rest_name}: {resolve_value(value)}\n")
    if model_val.dependson:
        bicep.write(f"{indent}dependsOn: [\n")
        for dependency in model_val.dependson:
            bicep.write(f"{indent}{indent}{dependency._symbolicname}\n")
        bicep.write(f"{indent}]\n")
    bicep.write("}\n\n")


def _serialize_dataclass(bicep: IO[str], data_val: dataclass, indent: str) -> None:
    for rest_name, value in iter_fields(data_val):
        if is_dataclass(value):
            bicep.write(f"{indent}{rest_name}: {{\n")
            _serialize_dataclass(bicep, value, indent + '  ')
            bicep.write(f"{indent}}}\n")
        elif isinstance(value, dict):
            if not value:
                continue
            bicep.write(f"{indent}{rest_name}: {{\n")
            _serialize_dict(bicep, value, indent + '  ')
            bicep.write(f"{indent}}}\n")
        elif isinstance(value, list):
            if not value:
                continue
            bicep.write(f"{indent}{rest_name}: [\n")
            _serialize_list(bicep, value, indent + '  ')
            bicep.write(f"{indent}]\n")
        else:
            bicep.write(f"{indent}{rest_name}: {resolve_value(value)}\n")


def _serialize_dict(bicep: IO[str], dict_val: Dict[str, Any], indent: str) -> None:
    for key, value in dict_val.items():
        if is_dataclass(value):
            bicep.write(f"{indent}{key}: {{\n")
            _serialize_dataclass(bicep, value, indent + '  ')
            bicep.write(f"{indent}}}\n")
        elif isinstance(value, dict) and value:
            bicep.write(f"{indent}{key}: {{\n")
            _serialize_dict(bicep, value, indent + '  ')
            bicep.write(f"{indent}}}\n")
        elif isinstance(value, list) and value:
            bicep.write(f"{indent}{key}: [\n")
            _serialize_list(bicep, value, indent + '  ')
            bicep.write(f"{indent}]\n")
        else:
            bicep.write(f"{indent}{resolve_key(key)}: {resolve_value(value)}\n")


def _serialize_list(bicep: IO[str], list_val: List[Any], indent: str) -> None:
    for item in list_val:
        if is_dataclass(item):
            bicep.write(f"{indent} {{\n")
            _serialize_dataclass(bicep, item, indent + '  ')
            bicep.write(f"{indent} }}\n")
        elif isinstance(item, dict):
            bicep.write(f"{indent} {{\n")
            _serialize_dict(bicep, item, indent + '  ')
            bicep.write(f"{indent} }}\n")
        elif isinstance(item, list):
            bicep.write(f"{indent} [\n")
            _serialize_list(bicep, item, indent + '  ')
            bicep.write(f"{indent} ]\n")
        else:
            bicep.write(f"{indent}{resolve_value(item)}\n")


@dataclass(kw_only=True)
class Resource:
    _resource: ClassVar[str]
    _version: ClassVar[str]
    _symbolicname: str
    name: str = field(metadata={'rest': 'name'})
    parent: Optional['Resource'] = field(init=False, default=None)
    scope: Optional['Resource'] = field(init=False, default=None)
    dependson: Optional[List['Resource']] = field(default_factory=list)
    _outputs: Dict[str, Any] = field(default_factory=dict, init=False)

    def write(self, bicep: IO[str]) -> Dict[str, str]:
        _serialize_resource(bicep, self)
        return self._outputs

    # @classmethod
    # def existing(self, scope: Optional['ResourceGroup'] = None) -> Self:
    #     raise NotImplementedError()

    # @classmethod
    # def from_json(self, resource: Dict[str, Any]) -> Self:
    #     raise NotImplementedError()


@dataclass(kw_only=True)
class LocatedResource(Resource):
    friendly_name: InitVar[Optional[str]] = None
    name: BicepStr = field(init=False, default_factory=ResourceName, metadata={'rest': 'name'})
    location: BicepStr = field(default_factory=DefaultLocation, metadata={'rest': 'location'})
    tags: Dict[BicepStr, BicepStr] = field(default_factory=dict, metadata={'rest': 'tags'})
    _fname: Optional[BicepStr] = None

    def __post_init__(self, friendly_name: Optional[str] = None):
        self._fname = friendly_name
        if self._fname:
            self.tags['cloudmachine-friendlyname'] = self._fname


@dataclass(kw_only=True)
class ResourceGroup(LocatedResource):
    _resource: ClassVar[Literal['Microsoft.Resources/resourceGroups']] = 'Microsoft.Resources/resourceGroups'
    _version: ClassVar[str] = '2021-04-01'
    parent: ClassVar[None] = None
    scope: ClassVar[None] = None
    name: BicepStr = field(init=False, default_factory=ResourceName, metadata={'rest': 'name'})
    resources: Dict[str, List['LocatedResource']] = field(
        default_factory=dict, init=False, repr=False, metadata={'rest': _SKIP}
    )
    _symbolicname: str = field(default_factory=lambda: generate_symbol("resourceGroup"), init=False, repr=False)

    def add(self, resource: 'Resource') -> None:
        # pylint: disable=protected-access
        try:
            self.resources[resource._resource].append(resource)
        except KeyError:
            self.resources[resource._resource] = [resource]

    def write(self, bicep: IO[str]) -> Dict[str, str]:
        bicep.write("param location string = resourceGroup().location\n")
        bicep.write("param principalId string\n")
        bicep.write("param cloudmachineId string\n")
        bicep.write("param tags object\n\n")
        for resources in self.resources.values():
            for resource in resources:
                self._outputs.update(resource.write(bicep))
        return self._outputs
