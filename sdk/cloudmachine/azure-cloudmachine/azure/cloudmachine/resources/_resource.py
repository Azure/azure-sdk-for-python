# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from enum import Enum
import json
import os
import re
import random
import string
import itertools
from typing import IO, Any, List, Optional, Dict, Literal, Self, ClassVar
from dataclasses import InitVar, dataclass, field, fields, is_dataclass

dataclass_model = dataclass(kw_only=True)
split_camelcase = re.compile('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)')
resource_prefix = "antisch"


def resolve_value(value: Any) -> str:
    try:
        return value.resolve()
    except AttributeError:
        if isinstance(value, Resource):
            return f"{value._symbolicname}.id"
        return json.dumps(value).replace('"', "'")


def resolve_key(key: Any) -> str:
    if isinstance(key, Resource):
        return f"'${{{key._symbolicname}.id}}'"
    if key[0].isalpha() or key[0] == '_':
        if not any(not c.isalnum() for c in key[1:]):
            return key
    return f"'{key}'"


class BicepResolver:
    def resolve(self) -> str:
        raise NotImplementedError()


class DefaultLocation(BicepResolver):
    def resolve(self) -> str:
        return "location"


class ResourceId(BicepResolver):
    def __init__(self, resource: 'Resource') -> None:
        self._resource = resource

    def resolve(self) -> str:
        return f"{self._resource._symbolicname}.id"


class CloudMachineName(BicepResolver):
    def resolve(self) -> str:
        return "cloudmachineName"


class PrincipalId(BicepResolver):
    def __init__(self, resource: Optional['LocatedResource'] = None) -> None:
        self._resource = resource

    def resolve(self) -> str:
        if self._resource:
            return f"{self._resource._symbolicname}.properties.principalId"
        return "principalId"


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
    def resolve(self):
        return f"'{resource_prefix}${{cloudmachineId}}'"


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
    for field in fields(dataclass_value):
        client_name = field.name
        if client_name.startswith('_'):
            continue
        value = getattr(dataclass_value, client_name)
        try:
            rest_name = field.metadata['rest']
        except KeyError:
            continue
        if value is _UNSET or rest_name is _SKIP:
            continue
        yield rest_name, value
        
def _serialize_resource(bicep: IO[str], model_val: 'Resource') -> None:
    indent: str = '  '
    bicep.write(f"resource {model_val._symbolicname} '{model_val._resource}@{model_val._version}' = {{\n")
    if model_val._parent:
        bicep.write(f"{indent}parent: {model_val._parent._symbolicname}\n")
    elif model_val._scope:
        bicep.write(f"{indent}scope: {model_val._scope._symbolicname}\n")

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


@dataclass_model
class Resource:
    _resource: ClassVar[str]
    _version: ClassVar[str]
    _symbolicname: str
    name: str = field(metadata={'rest': 'name'})
    _parent: Optional['Resource'] = field(init=False, default=None)
    _scope: Optional['Resource'] = field(init=False, default=None)
    _outputs: List[str] = field(default_factory=list, init=False)

    def write(self, bicep: IO[str]) -> None:
        _serialize_resource(bicep, self)

    @classmethod
    def existing(self, scope: Optional['ResourceGroup'] = None) -> Self:
        raise NotImplementedError()

    def write(self, bicep: IO[str]) -> None:
        _serialize_resource(bicep, self)


@dataclass_model
class LocatedResource(Resource):
    friendly_name: InitVar[Optional[str]] = None
    name: str = field(init=False, default_factory=ResourceName, metadata={'rest': 'name'})
    location: str = field(default_factory=DefaultLocation, metadata={'rest': 'location'})
    tags: Dict[str, str] = field(default_factory=dict, metadata={'rest': 'tags'})
    _fname: Optional[str] = None

    def __post_init__(self, friendly_name: Optional[str] = None):
        self._fname = friendly_name
        if self._fname:
            self.tags['cloudmachine-friendlyname'] = self._fname


@dataclass_model
class ResourceGroup(LocatedResource):
    name: str = field(init=False, default_factory=ResourceName, metadata={'rest': 'name'})
    _resources: List['LocatedResource'] = field(default_factory=list, init=False, repr=False)
    _resource: ClassVar[Literal['Microsoft.Resources/resourceGroups']] = 'Microsoft.Resources/resourceGroups'
    _version: ClassVar[str] = '2021-04-01'
    _parent: ClassVar[None] = None
    _scope: ClassVar[None] = None
    _symbolicname: str = field(default_factory=lambda: generate_symbol("resourceGroup"), init=False, repr=False)

    
    def add(self, resource: 'Resource') -> None:
        self._resources.append(resource)

    def write(self, bicep: IO[str]) -> None:
        _serialize_resource(bicep, self)

        indent: str = '  '
        outputs = {}
        cloudmachine_module = os.path.join(os.path.dirname(bicep.name), "cloudmachine.bicep")
        with open(cloudmachine_module, 'w') as cm_bicep:
            cm_bicep.write("param location string = resourceGroup().location\n")
            cm_bicep.write("param principalId string\n")
            cm_bicep.write("param cloudmachineId string\n")
            cm_bicep.write("param tags object\n\n")
            for resource in self._resources:
                resource.write(cm_bicep)
                for output in resource._outputs:
                    outputs[f"{generate_envvar(output)}"] = f"cloudmachine.outputs.{output}"

        bicep.write(f"module cloudmachine 'cloudmachine.bicep' = {{\n")
        bicep.write(f"{indent}name: 'cloudmachine'\n")
        bicep.write(f"{indent}scope: {self._symbolicname}\n")
        bicep.write(f"{indent}params: {{\n")
        bicep.write(f"{indent}  location: location\n")
        bicep.write(f"{indent}  tags: tags\n")
        bicep.write(f"{indent}  principalId: principalId\n")
        bicep.write(f"{indent}  cloudmachineId: cloudmachineId\n")
        bicep.write(f"{indent}}}\n")
        bicep.write(f"}}\n\n")

        for key, value in outputs.items():
            bicep.write(f"output AZURE_{key} string = {value}\n")
