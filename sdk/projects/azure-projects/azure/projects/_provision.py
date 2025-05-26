# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from collections import ChainMap
from typing import (
    IO,
    Any,
    List,
    Mapping,
    Optional,
    Tuple,
    Dict,
    Union,
)
import os
import json
from io import StringIO
import subprocess

import yaml  # type: ignore[import-untyped]
from dotenv import dotenv_values

from ._version import VERSION
from ._utils import add_defaults
from ._component import AzureApp, AzureInfrastructure
from ._parameters import GLOBAL_PARAMS
from ._bicep.utils import resolve_value, serialize_dict
from ._bicep.expressions import MISSING, Output, Parameter, PlaceholderParameter, ResourceSymbol
from ._resource import FieldType, Resource, FieldsType, _load_dev_environment
from .resources._extension import add_extensions
from .resources import ResourceIdentifiers
from .resources.appconfig.setting import ConfigSetting
from .resources.appservice.site import AppSite


_BICEP_PARAMS = {
    "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentParameters.json#",
    "contentVersion": "1.0.0.0",
}


def get_settings() -> Dict[str, Any]:
    args = ["azd", "env", "get-values"]
    try:
        output = subprocess.run(args, check=False, capture_output=True, text=True)
        if output.returncode == 0:
            config = StringIO(output.stdout)
            return dotenv_values(stream=config)
    except Exception:  # pylint: disable=broad-except
        pass
    return {}


def _deploy_project(name: str, label: Optional[str] = None) -> int:
    project_name = name + (f"-{label}" if label else "")
    args = ["azd", "deploy", project_name, "-e", project_name]
    print("Running: ", args)
    output = subprocess.run(args, check=False)
    print(output)
    return output.returncode


def _deprovision_project(name: str, label: Optional[str] = None, purge: bool = False) -> int:
    project_name = name + (f"-{label}" if label else "")
    args = ["azd", "down", "-e", project_name, "--force"]
    if purge:
        args.append("--purge")
    print("Running: ", args)
    output = subprocess.run(args, check=False)
    print(output)
    return output.returncode


def _provision_project(name: str, label: Optional[str] = None) -> int:
    project_name = name + (f"-{label}" if label else "")
    args = ["azd", "provision", "-e", project_name]
    print("Running: ", args)
    output = subprocess.run(args, check=False)
    print(output)
    return output.returncode


def _init_project(
    *,
    root_path: str,
    name: str,
    infra_dir: str,
    main_bicep: str,
    location: Optional[str] = None,
    label: Optional[str] = None,
    host: Optional[AppSite] = None,
) -> int:
    azure_dir = os.path.join(root_path, ".azure")
    azure_yaml = os.path.join(root_path, "azure.yaml")
    project_name = name + (f"-{label}" if label else "")
    project_dir = os.path.join(azure_dir, project_name)

    # TODO: Needs to properly set code root
    if os.path.isfile(azure_yaml):
        with open(azure_yaml, "r", encoding="utf-8") as config:
            yaml_doc = yaml.safe_load(config)
    else:
        yaml_doc = {}

    yaml_doc["name"] = project_name
    yaml_doc["metadata"] = {
        "azprojects": VERSION,
    }
    yaml_doc["infra"] = {
        "path": infra_dir,
        "module": main_bicep,
    }
    if host:
        if label:
            service_name = f"{project_name}-{label}"
        else:
            service_name = project_name
        if "services" not in yaml_doc:
            yaml_doc["services"] = {}
        yaml_doc["services"][service_name] = {
            "project": ".",
            "language": "py",
            "host": "appservice",
        }
    with open(azure_yaml, "w", encoding="utf-8") as config:
        config.write(
            "# yaml-language-server: $schema=https://raw.githubusercontent.com/Azure/azure-dev/main/schemas/v1.0/azure.yaml.json\n\n"  # pylint: disable=line-too-long
        )
        config.write(yaml.dump(yaml_doc, indent=2, sort_keys=False))

    returncode = 0
    if not os.path.isdir(azure_dir) or not os.path.isdir(project_dir):
        print(f"Adding environment: {project_name}.")
        output = subprocess.run(["azd", "env", "new", project_name], check=False)
        print(output)
        returncode = output.returncode
    if location:
        output = subprocess.run(["azd", "env", "set", "AZURE_LOCATION", location, "-e", project_name], check=False)
        print(output)
        returncode = output.returncode
    print("Finished environment setup.")
    return returncode


def _get_component_resources(component: AzureInfrastructure) -> Dict[str, Union[Resource, AzureInfrastructure]]:
    return {k: v for k, v in component.__dict__.items() if isinstance(v, (Resource, AzureInfrastructure))}


def deploy(deployment: AzureInfrastructure) -> None:
    returncode = _deploy_project(deployment.__class__.__name__)
    if returncode != 0:
        raise RuntimeError()


def deprovision(deployment: Union[str, AzureInfrastructure, AzureApp], /, *, purge: bool = False) -> None:
    if isinstance(deployment, str):
        deployment_name = deployment
    else:
        deployment_name = deployment.__class__.__name__
    returncode = _deprovision_project(deployment_name, purge=purge)
    if returncode != 0:
        raise RuntimeError()


def provision(
    deployment: AzureInfrastructure,
    /,
    infra_dir: str = "infra",
    main_bicep: str = "main",
    output_dir: str = ".",
    user_access: bool = True,
    location: Optional[str] = None,
    parameters: Optional[Mapping[str, Any]] = None,
) -> Mapping[str, Any]:
    deployment_name = deployment.__class__.__name__
    parameters = parameters or {}
    working_dir = os.path.abspath(output_dir)
    export(
        deployment,
        infra_dir=infra_dir,
        main_bicep=main_bicep,
        output_dir=output_dir,
        user_access=user_access,
        location=location,
        parameters=parameters,
    )
    returncode = _init_project(
        root_path=working_dir,
        name=deployment_name,
        infra_dir=infra_dir,
        main_bicep=main_bicep,
        location=location,
        host=deployment.host,
    )
    if returncode != 0:
        raise RuntimeError()
    returncode = _provision_project(deployment_name)
    if returncode != 0:
        raise RuntimeError()
    env_config = _load_dev_environment(deployment_name)
    return ChainMap(env_config)


def export(
    deployment: AzureInfrastructure,
    /,
    infra_dir: str = "infra",
    main_bicep: str = "main",
    output_dir: str = ".",
    user_access: bool = True,
    location: Optional[str] = None,
    parameters: Optional[Mapping[str, Any]] = None,
) -> None:
    deployment_name = deployment.__class__.__name__
    parameter_values = parameters or {}
    # TODO: Replace print statements with logging
    print("Building bicep...")
    working_dir = os.path.abspath(output_dir)
    infra_dir = os.path.join(working_dir, infra_dir)
    # Not sure why a TypedDict is incompatible with SupportsKeysAndGetItem
    export_parameters: Dict[str, Parameter] = dict(GLOBAL_PARAMS)  # type: ignore[arg-type]
    if not user_access:
        # If we don't want any local access, simply remove the parameter.
        export_parameters.pop("principalId")
    if location:
        export_parameters["location"].default = location

    fields: FieldsType = {}
    _parse_module(
        parameters=export_parameters,
        parent_component=deployment,
        component=deployment,
        component_resources=_get_component_resources(deployment),
        component_fields=fields,
    )
    add_defaults(fields, export_parameters)
    add_extensions(fields, export_parameters)

    try:
        os.makedirs(infra_dir)
    except FileExistsError:
        pass
    bicep_main = os.path.join(infra_dir, f"{main_bicep}.bicep")
    with open(bicep_main, "w", encoding="utf-8") as main:
        main.write("targetScope = 'subscription'\n\n")
        for parameter in export_parameters.values():
            # TODO: Maybe add a "public: bool" attribute to Outputs and Placeholders?
            if parameter.name and not isinstance(parameter, (Output, PlaceholderParameter)):
                main.write(parameter.__bicep__(parameter_values.get(parameter.name, MISSING)))
        _write_resources(
            bicep=main,
            fields=list(fields.values()),
            parameters=export_parameters,
            deployment_name=deployment_name,
            infra_dir=infra_dir,
        )
        main.write("\n")
    # TODO: Full parameters file
    main_parameters = os.path.join(infra_dir, f"{main_bicep}.parameters.json")
    params_content: Dict[str, Any] = dict(_BICEP_PARAMS)
    params_content["parameters"] = {}
    for parameter in export_parameters.values():
        if parameter.name and parameter.env_var:
            params_content["parameters"].update(parameter.__obj__())
    with open(main_parameters, "w", encoding="utf-8") as params_json:
        json.dump(params_content, params_json, indent=4)


def _parse_module(
    *,
    parameters: Dict[str, Parameter],
    parent_component: AzureInfrastructure,
    component: AzureInfrastructure,
    component_resources: Dict[str, Union[Resource, AzureInfrastructure]],
    component_fields: FieldsType,
) -> None:
    for attr, resource in component_resources.items():
        if isinstance(resource, Resource):
            resource.__bicep__(
                component_fields,
                parameters=parameters,
                infra_component=component,
                attrname=attr[8:] if attr.startswith("_field__") else attr,
            )
        else:
            _parse_module(
                parameters=parameters,
                parent_component=parent_component,
                component=resource,
                component_resources=_get_component_resources(resource),
                component_fields=component_fields,
            )
    if component.config_store:
        outputs = [o for f in component_fields.values() for o in f.outputs.values()]
        for output_type in outputs:
            for output in sorted(output_type):
                new_setting = ConfigSetting(
                    name=output.name,  # f"{output.name}$azprojects",
                    value=output,
                    store=component.config_store,
                )
                new_setting.__bicep__(component_fields, parameters=parameters, infra_component=component)


def _write_resources(  # pylint: disable=too-many-statements
    *,
    bicep: IO[str],
    fields: List[FieldType],
    parameters: Dict[str, Parameter],
    infra_dir: str,
    deployment_name: str,
    resource_group_scope: Optional[ResourceSymbol] = None,
) -> List[Tuple[str, str]]:
    all_outputs = []
    for index, field in enumerate(fields):
        if field.identifier == ResourceIdentifiers.resource_group:
            if field.existing:
                bicep.write(f"resource {field.symbol.value} '{field.resource}@{field.version}' existing = {{\n")
                bicep.write(f"  name: {resolve_value(field.properties['name'])}\n")
                if "scope" in field.properties:
                    bicep.write(f"  scope: {field.properties['scope'].value}\n")
                elif resource_group_scope:
                    bicep.write("  scope: subscription()\n")
                bicep.write("}\n\n")
                if resource_group_scope:
                    continue
            elif not resource_group_scope:
                bicep.write(f"resource {field.symbol.value} '{field.resource}@{field.version}' = {{\n")
                bicep.write(serialize_dict(field.properties, "  "))
                bicep.write("}\n\n")
            else:
                # TODO Currently only supporting the creation of a single resource group,
                # however other existing resources may continue to reference other resource groups
                # by name
                raise ValueError("Cannot create additional resource group in deployment.")
            if fields[index + 1 :]:
                bicep.write(f"module {deployment_name}_module '{deployment_name}.bicep' = {{\n")
                bicep.write(f"  name: '${{deployment().name}}_{deployment_name}'\n")
                bicep.write(f"  scope: {field.symbol.value}\n")
                bicep.write("  params: {\n")
                for parameter in parameters.values():
                    if parameter.name and not isinstance(parameter, (Output, PlaceholderParameter)):
                        bicep.write(f"    {parameter.name}: {parameter.value}\n")
                bicep.write("  }\n")
                bicep.write("}\n")
                bicep_module = os.path.join(infra_dir, f"{deployment_name}.bicep")
                with open(bicep_module, "w", encoding="utf-8") as module:
                    for parameter in parameters.values():
                        if parameter.name and not isinstance(parameter, (Output, PlaceholderParameter)):
                            # TODO: This will default to type "string" which may not be true.
                            module.write(f"param {parameter.name} {parameter.type}\n")

                    module.write("\n")
                    outputs = _write_resources(
                        bicep=module,
                        fields=fields[index + 1 :],
                        parameters=parameters,
                        infra_dir=infra_dir,
                        resource_group_scope=field.symbol,
                        deployment_name="",  # TODO: support submodules/resource groups
                    )
                    for output_name, type in outputs:
                        bicep.write(f"output {output_name} {type} = {deployment_name}_module.outputs.{output_name}\n")
                    bicep.write("\n")
                break
        elif field.existing:
            bicep.write(f"resource {field.symbol.value} '{field.resource}@{field.version}' existing = {{\n")
            bicep.write(f"  name: {resolve_value(field.properties['name'])}\n")
            if "parent" in field.properties:
                bicep.write(f"  parent: {resolve_value(field.properties['parent'])}\n")
            elif field.resource_group is not None and field.resource_group != resource_group_scope:
                bicep.write(f"  scope: {field.resource_group.value}\n")
            bicep.write("}\n")
        else:
            bicep.write(f"resource {field.symbol.value} '{field.resource}@{field.version}' = {{\n")
            bicep.write(serialize_dict(field.properties, "  "))
            bicep.write("}\n")
        bicep.write("\n")
        # TODO: Only output the values for config store, then everything can be retrieved from there.
        for output_type in field.outputs.values():
            for output in sorted(output_type):
                all_outputs.append((output.name, output.type))
                bicep.write(output.__bicep__())
        bicep.write("\n\n")
    return all_outputs
