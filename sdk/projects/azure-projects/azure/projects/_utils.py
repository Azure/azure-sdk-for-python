# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from concurrent.futures import ThreadPoolExecutor
import asyncio  # pylint: disable=do-not-import-asyncio
import threading
import importlib.util
import sys
import os
from typing import Coroutine, Any, Dict, Generator, List, Mapping, Optional, Union, TYPE_CHECKING
from typing_extensions import TypeVar

from .resources import ResourceIdentifiers

if TYPE_CHECKING:
    from ._bicep.expressions import Parameter, ResourceSymbol, Expression
    from ._component import AzureInfrastructure
    from ._resource import FieldsType, FieldType


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
    # https://stackoverflow.com/questions/55647753/call-async-function-from-sync-function-while-the-synchronous-function-continues

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


def resolve_properties(
    properties: Mapping[Union[str, "Parameter"], Any],
    parameters: Dict[str, "Parameter"],
    component: Optional["AzureInfrastructure"] = None,
) -> Dict[Union[str, "Parameter"], Any]:
    # TODO: Better design here? We need to gather Parameters both
    # with and without resolving ComponentFields.
    # TODO We also need to resolve resource references to a ResourceSymbol.id.
    from ._component import ComponentField
    from ._bicep.expressions import Parameter

    new_props: Dict[Union[str, "Parameter"], Any] = {}
    for key, value in properties.items():
        if isinstance(key, Parameter) and key.name:
            if key.name in parameters:
                key = parameters[key.name]
            else:
                parameters[key.name] = value

        if component and isinstance(value, ComponentField):
            new_props[key] = value.get(component)
        elif isinstance(value, Parameter) and value.name:
            if value.name in parameters:
                value = parameters[value.name]
            else:
                parameters[value.name] = value
            new_props[key] = value
        elif isinstance(value, list):
            resolved_items = []
            for item in value:
                if component and isinstance(item, ComponentField):
                    resolved_items.append(item.get(component))
                elif isinstance(item, Parameter) and item.name:
                    if item.name in parameters:
                        item = parameters[item.name]
                    else:
                        parameters[item.name] = item
                    resolved_items.append(item)
                else:
                    try:
                        resolved_items.append(resolve_properties(item, parameters, component))
                        continue
                    except (AttributeError, TypeError):
                        resolved_items.append(item)
            new_props[key] = resolved_items
        else:
            try:
                new_props[key] = resolve_properties(value, parameters, component)
                continue
            except (AttributeError, TypeError):
                new_props[key] = value
    return new_props


def find_all_resource_match(
    fields: "FieldsType",
    *,
    resource_types: List[ResourceIdentifiers],
    resource_group: Optional["ResourceSymbol"] = None,
    name: Optional[Union[str, "Expression"]] = None,
    parent: Optional["ResourceSymbol"] = None,
) -> Generator["FieldType", None, None]:
    for field in (f for f in reversed(list(fields.values())) if f.identifier in resource_types):
        if name and resource_group:
            if field.name == name and field.resource_group == resource_group:
                yield field
        elif name and parent:
            if field.name == name and field.properties["parent"] == parent:
                yield field
        elif resource_group:
            if field.resource_group == resource_group:
                yield field
        elif parent:
            if field.properties["parent"] == parent:
                yield field
        elif name:
            if field.name == name:
                yield field
        else:
            yield field


def find_last_resource_match(
    fields: "FieldsType",
    *,
    resource: ResourceIdentifiers,
    resource_group: Optional["ResourceSymbol"] = None,
    name: Optional[Union[str, "Expression"]] = None,
    parent: Optional["ResourceSymbol"] = None,
) -> Optional["FieldType"]:
    matches = find_all_resource_match(
        fields, resource_types=[resource], resource_group=resource_group, name=name, parent=parent
    )
    try:
        return next(matches)
    except StopIteration:
        return None


def find_resource_group(
    fields: "FieldsType",
    *,
    name: Optional[str] = None,
) -> Optional["ResourceSymbol"]:
    # TODO: This might be no longer needed, always one resource group per deployment
    match = find_last_resource_match(fields, resource=ResourceIdentifiers.resource_group, name=name)
    if match:
        return match.symbol
    return None


def add_defaults(fields: "FieldsType", parameters: Dict[str, "Parameter"]):
    # TODO: loads defaults from store.
    from ._bicep.expressions import PlaceholderParameter

    for field in fields.values():  # pylint: disable=too-many-nested-blocks
        if field.defaults:
            for key, value in field.defaults["resource"].items():
                if key == "identity" and isinstance(parameters["managedIdentityId"], PlaceholderParameter):
                    # This indicates that no managed identity is being deployed, so skip it.
                    continue
                if field.properties.get(key):
                    if key in ["tags", "properties"]:
                        try:
                            updated_default = value.copy()
                            updated_default.update(field.properties[key])
                            field.properties[key] = updated_default
                        except AttributeError:
                            # We probably got an Expression
                            # TODO: support bicep union operation?
                            pass
                else:
                    field.properties[key] = value
            # TODO: This is making a copy of the properties, very slow...
            # field.properties is Dict[str, Any], but resolve properties supports Dict[Union[Parameter, str], Any] which
            # would only expect to show up in sub-dicts like tags.
            field.properties.update(resolve_properties(field.properties, parameters))  # type: ignore[arg-type]
            if "managed_identity_roles" not in field.extensions:
                field.extensions["managed_identity_roles"] = field.defaults["extensions"].get(
                    "managed_identity_roles", []
                )
            if "user_roles" not in field.extensions:
                field.extensions["user_roles"] = field.defaults["extensions"].get("user_roles", [])
