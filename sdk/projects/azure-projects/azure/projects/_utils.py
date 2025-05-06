# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import collections
from concurrent.futures import ThreadPoolExecutor
import asyncio  # pylint: disable=do-not-import-asyncio
import threading
import importlib.util
import sys
import os
from typing import Coroutine, Any, Dict, Generator, List, Mapping, MutableMapping, Optional, Union, TYPE_CHECKING
from typing_extensions import TypeVar

from .resources import ResourceIdentifiers
from ._parameters import GLOBAL_PARAMS

if TYPE_CHECKING:
    from ._bicep.expressions import Parameter, ResourceSymbol, Expression
    from ._component import AzureInfrastructure
    from ._resource import FieldsType, FieldType, ExtensionResources


def import_from_path(file_path):
    full_path = os.path.abspath(file_path)
    module_name = os.path.basename(full_path)
    dirname = os.path.dirname(full_path)
    if os.path.isdir(full_path):
        full_path = os.path.join(full_path, "__init__.py")
    elif os.path.isfile(full_path):
        module_name = os.path.splitext(module_name)[0]
    else:
        raise ImportError(f"Module {module_name} not found at {file_path}")
    spec = importlib.util.spec_from_file_location(module_name, full_path)
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, dirname)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def lazy_import(name):
    spec = importlib.util.find_spec(name)
    loader = importlib.util.LazyLoader(spec.loader)
    spec.loader = loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    loader.exec_module(module)
    return module


T = TypeVar("T")


def run_coroutine_sync(coroutine: Coroutine[Any, Any, T], timeout: float = 30) -> T:
    # TODO: Found this on StackOverflow - needs further inspection
    # https://stackoverflow.com/questions/55647753/
    # call-async-function-from-sync-function-while-the-synchronous-function-continues

    def run_in_new_loop():
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        try:
            return new_loop.run_until_complete(coroutine)
        finally:
            new_loop.close()

    try:
        loop = asyncio.get_running_loop()
        if threading.current_thread() is threading.main_thread():
            if not loop.is_running():
                return loop.run_until_complete(coroutine)
            with ThreadPoolExecutor() as pool:
                future = pool.submit(run_in_new_loop)
                return future.result(timeout=timeout)
        else:
            return asyncio.run_coroutine_threadsafe(coroutine, loop).result()
    except RuntimeError:
        if "trio" in sys.modules:
            import trio  # pylint: disable=networking-import-outside-azure-core-transport, import-error

            # TODO: This needs testing - I think trio is different to asyncio in that it requires
            # the callable to be passed in rather than the awaitable.
            return trio.run(coroutine)
        return asyncio.run(coroutine)


def resolve_component(
    properties: Mapping,
    component: Optional["AzureInfrastructure"],
) -> Dict[Union[str, "Parameter"], Any]:
    # This method will only resolve ComponentFields, not Parameters.
    # It will also make a copy of the properties dict to prevent modifying the original.
    # TODO We also need to resolve resource references to a ResourceSymbol.id.
    from ._component import ComponentField

    new_props = {}
    for key, value in properties.items():
        if isinstance(value, ComponentField):
            if not component:
                raise ValueError(f"ComponentField {key} requires a component to resolve.")
            new_props[key] = value.get(component)
        elif isinstance(value, list):
            resolved_items = []
            for item in value:
                if isinstance(item, ComponentField):
                    if not component:
                        raise ValueError(f"ComponentField {key} requires a component to resolve.")
                    resolved_items.append(item.get(component))
                else:
                    try:
                        resolved_items.append(resolve_component(item, component))
                        continue
                    except (AttributeError, TypeError):
                        resolved_items.append(item)
            new_props[key] = resolved_items
        else:
            try:
                new_props[key] = resolve_component(value, component)
                continue
            except (AttributeError, TypeError):
                new_props[key] = value
    return new_props


def validate_parameter(
    parameter: "Parameter",
    parameters: Dict[str, "Parameter"],
    values: Dict[str, Any],
    *,
    replace: bool = False,
) -> Any:
    from ._bicep.expressions import MISSING

    if (
        parameter.name not in GLOBAL_PARAMS
        and parameter.public
        and parameter.default is MISSING
        and parameter.name not in values
        and not parameter.env_var
    ):
        raise ValueError(f"Parameter {parameter.name} not found in provided parameter values and has no default.")
    if replace:
        # This is only used for extension resources (like role assignments), where we need to know up
        # front what the values are in order to construct the resource definitions. This means there
        # shouldn't be any Outputs or Placeholders used. It's also unlikely to use env vars, but that may
        # need to be supported in the future.
        if parameter.default is MISSING and parameter.name not in values:
            raise ValueError(f"Parameter {parameter.name} must be provided in parameter values.")
        return values.get(parameter.name, parameter.default)

    if parameter.name in parameters:
        return parameters[parameter.name]
    parameters[parameter.name] = parameter
    return parameter


def resolve_parameters(
    properties: Mapping[Union[str, "Parameter"], Any],
    parameters: Dict[str, "Parameter"],
    values: Dict[str, Any],
    *,
    replace: bool = False,
) -> Dict[Union[str, "Parameter"], Any]:
    # TODO We also need to resolve resource references to a ResourceSymbol.id.
    # pylint: disable=protected-access
    from ._bicep.expressions import Parameter, Expression

    new_props: Dict[Union[str, "Parameter"], Any] = {}
    for key, value in properties.items():
        if isinstance(key, Parameter) and key.name:
            # This should only happen in unstructured dictionaries, like tags.
            key = validate_parameter(key, parameters, values, replace=replace)

        if isinstance(value, Parameter) and value.name:
            new_props[key] = validate_parameter(value, parameters, values, replace=replace)
        elif isinstance(value, Expression) and isinstance(value._value, Parameter):
            # This is currently here to support parameterized subscription scope - may need to be
            # expanded further.
            value._value = validate_parameter(value._value, parameters, values, replace=replace)
        elif isinstance(value, list):
            resolved_items = []
            for item in value:
                if isinstance(item, Parameter) and item.name:
                    resolved_items.append(validate_parameter(item, parameters, values, replace=replace))
                else:
                    try:
                        resolved_items.append(resolve_parameters(item, parameters, values, replace=replace))
                        continue
                    except (AttributeError, TypeError):
                        resolved_items.append(item)
            new_props[key] = resolved_items
        else:
            try:
                new_props[key] = resolve_parameters(value, parameters, values, replace=replace)
                continue
            except (AttributeError, TypeError):
                new_props[key] = value
    return new_props


def add_defaults(
    fields: "FieldsType",
    parameters: Dict[str, "Parameter"],
    values: Dict[str, Any],
    *,
    resource_defaults: Mapping[str, Any],
    local_access: bool = False
) -> None:
    # TODO: loads defaults from store.
    from ._bicep.expressions import PlaceholderParameter

    for field in fields.values():  # pylint: disable=too-many-nested-blocks
        if field.defaults:
            # field.defaults will be None if the field is an existing resource.
            yaml_defaults = resource_defaults.get(field.resource, {})
            for key, value in yaml_defaults.items():
                if field.properties.get(key):
                    if key in ["tags", "properties"]:
                        updated_default = value.copy()
                        updated_default.update(field.properties[key])
                        field.properties[key] = updated_default
                else:
                    field.properties[key] = value
            for key, value in field.defaults["resource"].items():
                if field.properties.get(key):
                    if key in ["tags", "properties"] and key not in yaml_defaults:
                        updated_default = value.copy()
                        updated_default.update(field.properties[key])
                        field.properties[key] = updated_default
                else:
                    field.properties[key] = value

            if "identity" in field.properties and field.properties["identity"] == {}:
                if not isinstance(parameters["managedIdentityId"], PlaceholderParameter):
                    field.properties["identity"] = {
                        "type": "UserAssigned",
                        "userAssignedIdentities": {
                            parameters["managedIdentityId"]: {}
                        }
                    }
                else:
                    field.properties.pop("identity")

            if "managed_identity_roles" not in field.extensions:
                field.extensions["managed_identity_roles"] = field.defaults["extensions"].get(
                    "managed_identity_roles", []
                )
            if local_access:
                if "user_roles" not in field.extensions:
                    field.extensions["user_roles"] = field.defaults["extensions"].get("user_roles", [])
            else:
                field.extensions.pop("user_roles", None)

        # field.properties is Dict[str, Any], but resolve properties supports Dict[Union[Parameter, str], Any] which
        # would only expect to show up in sub-dicts like tags.
        field.properties.update(resolve_parameters(field.properties, parameters, values))  # type: ignore[arg-type]

        # TODO: We're doing full parameter replacement here, which will potentially negate customers wanting
        # to parameterize specific values within their role definitions - something to explore further, but should
        # be uncommon, so not a priority.
        field.extensions.update(resolve_parameters(field.extensions, parameters, values, replace=True))  # type: ignore


def find_all_resource_match(
    fields: "FieldsType",
    *,
    resource_types: List[ResourceIdentifiers],
    resource_group: Optional["ResourceSymbol"] = None,
    parent: Optional["ResourceSymbol"] = None,
) -> Generator["FieldType", None, None]:
    for field in (f for f in reversed(list(fields.values())) if f.identifier in resource_types):
        if parent:
            if field.properties["parent"] == parent:
                yield field
        elif resource_group:
            if field.resource_group == resource_group:
                yield field
        else:
            yield field


def find_resource_match(
    fields: "FieldsType",
    *,
    resource: ResourceIdentifiers,
    name: Union[str, "Expression", None],
    resource_group: Optional["ResourceSymbol"] = None,
    parent: Optional["ResourceSymbol"] = None,
) -> Optional["FieldType"]:
    for match in find_all_resource_match(
        fields, resource_types=[resource], resource_group=resource_group, parent=parent
    ):
        if match.name == name:
            return match
    return None


def find_last_resource_match(
    fields: "FieldsType",
    *,
    resource: ResourceIdentifiers,
    resource_group: Optional["ResourceSymbol"] = None,
    parent: Optional["ResourceSymbol"] = None,
) -> Optional["FieldType"]:
    matches = find_all_resource_match(fields, resource_types=[resource], resource_group=resource_group, parent=parent)
    try:
        return next(matches)
    except StopIteration:
        return None


def find_resource_group(fields: "FieldsType") -> Optional["ResourceSymbol"]:
    # TODO: This might be no longer needed, always one resource group per deployment
    match = find_last_resource_match(fields, resource=ResourceIdentifiers.resource_group)
    if match:
        return match.symbol
    return None
