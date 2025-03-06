# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from __future__ import annotations

import inspect
from itertools import takewhile, product, accumulate
from enum import Enum
from copy import deepcopy
from collections import defaultdict
import re
import os
import json
from typing import (
    Generator,
    Generic,
    Mapping,
    Tuple,
    TypedDict,
    runtime_checkable,
    Type,
    Optional,
    Callable,
    Union,
    Dict,
    List,
    Any,
    TypeVar,
    Literal,
    overload,
    NamedTuple,
    TYPE_CHECKING
)
from typing_extensions import Self, Required

from dotenv import dotenv_values

from azure.core.credentials import (
    SupportsTokenInfo,
    AzureKeyCredential,
    AzureSasCredential,
    AzureNamedKeyCredential
)
from azure.core.credentials_async import AsyncSupportsTokenInfo
from azure.core.settings import PrioritizedSetting, _unset

from .resources._identifiers import ResourceIdentifiers
from ._parameters import DEFAULT_NAME, LOCATION, AZD_TAGS
from ._setting import StoredPrioritizedSetting
from ._bicep.expressions import Guid, Output, Expression, Parameter, ResourceSymbol, ResourceGroup, Default, MISSING
from ._bicep.utils import serialize, generate_suffix, resolve_value, serialize_dict, clean_name

if TYPE_CHECKING:
    from .resources.resourcegroup import ResourceGroup
    from .resources._extension import RoleAssignment
    from ._component import AzureInfrastructure


ClientType = TypeVar("ClientType")
CredentialTypes = Union[
    AsyncSupportsTokenInfo,
    SupportsTokenInfo,
    Callable[[], SupportsTokenInfo],
    Callable[[], AsyncSupportsTokenInfo],
    Literal['default', 'managedidentity'],
]


def _load_dev_environment(name: Optional[str] = None, label: Optional[str] = None) -> Dict[str, str]:
    azd_dir = os.path.join(os.getcwd(), ".azure")
    if name and not name.endswith('.env'):
        if not os.path.isdir(azd_dir):
            return {}
        env_name = name + (f"-{label}" if label else "")
        env_path = os.path.join(azd_dir, env_name, ".env")
    elif name:
        env_path = name
    else:
        scriptname = os.path.splitext(os.path.basename(inspect.stack()[-1][0].f_code.co_filename))[0]
        scriptenv = os.path.join(azd_dir, scriptname, ".env")
        if os.path.isdir(azd_dir) and os.path.isfile(scriptenv):
            env_path = scriptenv
        else:
            env_path = ".env"
    values = dotenv_values(env_path)
    return values


def _build_envs(services: List[str], attributes: List[str]) -> List[str]:
    all_vars = product(services, attributes)
    return ["_".join(['AZURE'] + list(var)).upper() for var in all_vars]


_EMPTY_DEFAULT = {}
_EMPTY_DEFAULT_EXTENSIONS = {}


class ResourceReference(TypedDict, total=False):
    name: Union[str, Parameter[str]]
    resource_group: 'ResourceGroup'
    subscription: Union[str, Parameter[str]]


class ExtensionResources(TypedDict, total=False):
    managed_identity_roles: Union[Parameter[List[Union['RoleAssignment', str]]], List[Union[Parameter[Union[str, 'RoleAssignment']], 'RoleAssignment', str]]]
    user_roles: Union[Parameter[List[Union['RoleAssignment', str]]], List[Union[Parameter[Union[str, 'RoleAssignment']], 'RoleAssignment', str]]]
    # lock
    # diagnostics
    # private endpoint
    # secret store?


ResourcePropertiesType = TypeVar("ResourcePropertiesType", bound=Mapping[str, Any])

class FieldType(NamedTuple, Generic[ResourcePropertiesType]):
    resource: str
    version: str
    properties: ResourcePropertiesType
    symbol: ResourceSymbol
    outputs: Dict[str, Output]
    resource_group: Optional[ResourceSymbol]
    extensions: ExtensionResources
    existing: bool
    name: Optional[Union[str, Parameter[str]]]
    add_defaults: Optional[Callable[[FieldType, Dict[str, Parameter]], None]]  # TODO: Clean this up?
    

FieldsType = Dict[str, FieldType]

class Resource(Generic[ResourcePropertiesType]):
    DEFAULTS: Mapping[str, Any] = _EMPTY_DEFAULT
    DEFAULT_EXTENSIONS = _EMPTY_DEFAULT_EXTENSIONS
    identifier: ResourceIdentifiers
    resource: str
    version: str
    properties: ResourcePropertiesType
    extensions: ExtensionResources
    parent: Optional[Resource]

    def __init__(self, properties: Optional[Dict[str, Any]] = None, /, **kwargs) -> None:
        """This constructor should not be used directly."""
        self.properties: ResourcePropertiesType = properties or {}
        self.extensions: ExtensionResources = kwargs.pop('extensions', {})
        self.identifier = kwargs.pop('identifier')
        self.parent: Optional[Resource] = kwargs.pop('parent', None)
        self._resource: str = kwargs.pop('resource', "")
        self._subresource: Optional[str] = kwargs.pop('subresource', '')
        self._version: str = kwargs.pop('resource_version', "")
        self._existing: bool = kwargs.pop('existing', False)
        if self.parent and not self._subresource:
            raise ValueError('Parent must be specified with subresource.')

        # Suffix and prefix are used to environment variable/config setting names
        # The prefix identifies the service/resource and the suffix is unique to this
        # specific resource (using either the name or name parameter if present).
        self._prefixes: List[str] = kwargs.pop('service_prefix', [])
        self._suffix = kwargs.pop('suffix', None)

        # These determine how resource properties are handled when building up the bicep
        # definitions for the same resource declared in multiple places. Anything in the
        # 'properties' field of a resource will error on conflict
        self._properties_to_merge = kwargs.pop('properties_to_merge', ['properties', 'tags'])

        self._settings: Dict[str, StoredPrioritizedSetting] = {
            "name": StoredPrioritizedSetting(
                'name',
                env_vars=_build_envs(self._prefixes, ['NAME']),
                system_hook=self._get_default_name,
                suffix=self._suffix,
            ),
            "resource_id": StoredPrioritizedSetting(
                name='resource_id',
                env_vars=_build_envs(self._prefixes, ['ID', 'RESOURCE_ID']),
                system_hook=self._build_resource_id,
                suffix=self._suffix
            ),
        }
        if self.parent:
            self._settings['resource_group'] = self.parent._settings['resource_group']
            self._settings['subscription'] = self.parent._settings['subscription']
        elif 'resource_group' in self.properties:
            self._settings['resource_group'] = self.properties['resource_group']._settings['name']
            self._settings['subscription'] = self.properties['resource_group']._settings['subscription']
        else:
            self._settings['resource_group'] = StoredPrioritizedSetting(
                name='resource_group',
                env_vars=_build_envs(self._prefixes, ['RESOURCE_GROUP']),
                suffix=self._suffix,
            )
            self._settings['subscription'] = StoredPrioritizedSetting(
                name='subscription',
                env_var='AZURE_SUBSCRIPTION_ID',
                suffix=self._suffix,
                default=self.properties.get('subscription', _unset)
            )
        if kwargs:
            raise TypeError(f"Resource {self.__class__.__name__} got unexpected kwargs: {list(kwargs.keys())}")


    def __repr__(self) -> str:
        name = f'\'{self.properties["name"]}\'' if 'name' in self.properties else "<default>"
        return f"{self.__class__.__name__}({name})"

    def __eq__(self, value: Any) -> bool:
        """Resources are considered equal if they (and their parents) have the same type and same name."""
        try:
            parent_eq = True
            if self.parent:
                parent_eq = self.parent == value.parent
            return parent_eq and value.resource == self.resource and value.properties.get('name') == self.properties.get('name')
        except:
            return False

    @property
    def resource(self) -> str:
        return self._resource

    @property
    def version(self) -> str:
        return self._version

    @classmethod
    def reference(
            cls,
            resource: str,
            *,
            name: Optional[Union[str, Parameter[str]]] = None,
            resource_group: Optional[Union[str, Parameter[str], 'ResourceGroup']] = None,
            subscription: Optional[Union[str, Parameter[str]]] = None,
            parent: Optional[Resource] = None,
    ) -> Self[ResourceReference]:
        if parent and resource_group:
            raise ValueError("Cannot specify both parent and resource_group.")
        resource_type, resource_version = resource.split('@')
        properties = ResourceReference(name=name) if name else {}
        if resource_group:
            if isinstance(resource_group, (str, Parameter)):
                from .resources.resourcegroup import ResourceGroup
                resource_group = ResourceGroup.reference(name=resource_group, subscription=subscription)
            properties['resource_group'] = resource_group
        elif subscription:
            # We're assuming 'subscription' will only be passed in in the case of rg-agnostic
            # resources, like a resourcegroup. Otherwise 'subscription' must be provided
            # on the 'resource_group' parameter.
            properties['subscription'] = subscription
        return cls(
            properties,
            resource=resource_type,
            resource_version=resource_version,
            parent=parent,
            existing=True
        )

    def _build_suffix(self, value: Optional[Union[str, Parameter]]) -> str:
        if value:
            if isinstance(value, str):
                if self.parent:
                    return self.parent._suffix + '_' + clean_name(value).upper()
                return '_' + clean_name(value).upper()
            if self.parent:
                return self.parent._suffix + '_' + clean_name(value.value).upper()
            return '_' + clean_name(value.value).upper()
        elif self.parent:
            return self.parent._suffix
        return ""

    def _build_symbol(self) -> ResourceSymbol:
        if not self.resource:
            raise TypeError("Empty Resource object cannot be provisioned.")
        resource_ref = self.resource.split("/")[-1].lower()
        if resource_ref.endswith("ies"):
            resource_ref = resource_ref.rstrip("ies") + "y"
        else:
            resource_ref = resource_ref.rstrip('s')
        symbol = f"{resource_ref}{self._suffix.lower()}" if self._suffix else resource_ref
        principal_id = None
        if self.properties.get('identity', {}).get('type', "").startswith('SystemAssigned'):
            principal_id = "principalId"
        return ResourceSymbol(symbol, principal_id=principal_id)

    def _build_resource_id(self, *, config_store: Optional[Mapping[str, Any]]) -> str:
        if not self._resource:
            raise ValueError("No resource specified.")
        name = self._settings['name'](config_store=config_store)
        if self.parent:
            return f"{self.parent._build_resource_id(config_store=config_store)}/{self._subresource}/{name}"
        sub_prefix = f"/subscriptions/{self._settings['subscription'](config_store=config_store)}"
        rg_prefix = f"/resourceGroups/{self._settings['resource_group'](config_store=config_store)}"
        return sub_prefix + rg_prefix + f"/providers/{self._resource}/{name}"

    def _get_default_name(self, *, config_store: Mapping[str, Any]) -> str:
        try:
            return self.properties['name']
        except KeyError:
            pass
        try:
            # TODO: How to access stored defaults?
            return self.DEFAULTS['name']
        except KeyError:
            pass
        raise RuntimeError("Resource name not known.")

    def _outputs(
            self,
             *,
             symbol: ResourceSymbol,
             suffix: Optional[str] = None,
             **kwargs
    ) -> Dict[str, Output]:
        suffix = suffix or self._suffix
        outputs = {
            'resource_id': Output(f"AZURE_{self._prefixes[0].upper()}_ID{suffix}", "id", symbol),
            'name': Output(f"AZURE_{self._prefixes[0].upper()}_NAME{suffix}", "name", symbol),
        }
        rg_output = f"AZURE_{self._prefixes[0].upper()}_RESOURCE_GROUP{suffix}"
        outputs['resource_group'] = Output(rg_output, ResourceGroup().name)
        if self._existing:
            try:
                rg_name = self._settings['resource_group']()  # TODO: Is it a problem that there's no config?
                outputs['resource_group'] = Output(rg_output, rg_name)
            except RuntimeError:
                pass
        return outputs

    def _merge_properties(
            self,
            current_properties: Dict[str, Any],
            new_properties: Dict[str, Any],
            **kwargs
        ) -> Dict[str, Any]:
        for key, value in new_properties.items():
            if key in current_properties:
                if key in self._properties_to_merge:
                    self._merge_properties(current_properties[key], value, **kwargs)
                elif current_properties[key] != value:
                    raise ValueError(f"{repr(self)} cannot set '{key}' to '{value}', already set to: '{current_properties[key]}'.")
            else:
                current_properties[key] = value
        return {}

    def _find_all_resource_match(
            self,
            fields: FieldsType,
            *,
            resource: Optional[str] = None, # TODO: Replace this to use ResourceIdentifier
            resource_group: Optional[ResourceSymbol] = None,
            name: Optional[Union[str, Expression]] = None,
            parent: Optional[ResourceSymbol] = None,
    ) -> Generator[FieldType, None, None]:
        resource = resource or self.resource
        for field in (f for f in reversed(list(fields.values())) if f.resource == resource):
            if name and resource_group:
                if field.properties.get('name') == name and field.resource_group == resource_group:
                    yield field
            elif name and parent:
                if field.properties.get('name') == name and field.properties['parent'] == parent:
                    yield field
            elif resource_group:
                if field.resource_group == resource_group:
                    yield field
            elif parent:
                if field.properties['parent'] == parent:
                    yield field
            elif name:
                if field.properties.get('name') == name:
                    yield field
            else:
                yield field

    def _find_last_resource_match(
            self,
            fields: FieldsType,
            *,
            resource: Optional[str] = None,
            resource_group: Optional[ResourceSymbol] = None,
            name: Optional[Union[str, Expression]] = None,
            parent: Optional[ResourceSymbol] = None,
    ) -> Optional[FieldType]:
        matches = self._find_all_resource_match(
            fields,
            resource=resource,
            resource_group=resource_group,
            name=name,
            parent=parent)
        try:
            return next(matches)
        except StopIteration:
            return None

    def _find_resource_group(
            self,
            fields: FieldsType,
            parameters: Dict[str, Parameter],
            *,
            name: Optional[str] = None,
            module_name: Optional[str] = None
    ) -> Optional[ResourceSymbol]:
        # TODO: This might be no longer needed, always one resource group per deployment
        match = self._find_last_resource_match(
            fields,
            resource="Microsoft.Resources/resourceGroups",
            name=name
        )
        if match:
            return match.symbol
        return None

    def _find_identity(
            self,
            fields: FieldsType,
            parameters: Dict[str, Parameter],
            *,
            module_name: Optional[str] = None,
    ) -> Optional[ResourceSymbol]:
        # TODO: This is probably no longer needed - use default parameters instead.
        match = self._find_last_resource_match(
            fields,
            resource="Microsoft.ManagedIdentity/userAssignedIdentities",
        )
        if match:
            return match.symbol
        return None

    def _get_field_id(self, symbol: ResourceSymbol, parents: Tuple[ResourceSymbol, ...]) -> str:
        if self.parent:
            prefix = self.parent._get_field_id(parents[0], parents[1:])
            return f"{prefix}.{symbol.value}"
        return symbol.value

    def _resolve_resource(self, parameters, component):
        from ._component import ComponentField
        name = self.properties.get('name')
        if isinstance(name, ComponentField):
            resolved = name.get(component)
            if isinstance(resolved, Resource):
                return resolved._resolve_resource(parameters, component)
        return self._resolve_properties(self.properties, parameters, component)

    def _resolve_properties(
            self,
            properties: Dict[str, Any],
            parameters: Dict[str, Parameter],
            component: AzureInfrastructure = None
    ) -> Dict[str, Any]:
        # TODO: Better design here? We need to gather Parameters both
        # with and without resolving ComponentFields.
        from ._component import ComponentField
        new_props = {}
        for key, value in properties.items():
            if component and isinstance(value, ComponentField):
                new_props[key] = value.get(component)
            elif isinstance(value, Parameter) and value.name:
                parameters[value.name] = value
                new_props[key] = value
            elif isinstance(value, list):
                resolved_items = []
                for item in value:
                    if component and isinstance(item, ComponentField):
                        resolved_items.append(item.get(component))
                    elif isinstance(item, Parameter) and item.name:
                        parameters[item.name] = item
                        resolved_items.append(item)
                    else:
                        try:
                            resolved_items.append(self._resolve_properties(item, parameters, component))
                            continue
                        except (AttributeError, TypeError):
                            resolved_items.append(item)
                new_props[key] = resolved_items
            else:
                try:
                    new_props[key] = self._resolve_properties(value, parameters, component)
                    continue
                except (AttributeError, TypeError):
                    new_props[key] = value
        return new_props
                   
    def _add_defaults(self, field: FieldType, parameters: Dict[str, Parameter]):
        for key, value in self.DEFAULTS.items():
            if field.properties.get(key):
                if key in self._properties_to_merge:
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
        self._resolve_properties(field.properties, parameters)
        if 'managed_identity_roles' not in field.extensions:
            field.extensions['managed_identity_roles'] = self.DEFAULT_EXTENSIONS.get('managed_identity_roles', [])
        if 'user_roles' not in field.extensions:
            field.extensions['user_roles'] = self.DEFAULT_EXTENSIONS.get('user_roles', [])

    def __bicep__(
            self,
            fields: FieldsType,
            *,
            parameters: Dict[str, Parameter],
            infra_component: Optional[AzureInfrastructure] = None,
            module_name: Optional[str] = None,
    ) -> Tuple[ResourceSymbol, ...]:
        properties = self._resolve_resource(parameters, infra_component)
        extensions = defaultdict(list)
        extensions.update(self.extensions)
        parents: Tuple[ResourceSymbol] = ()
        if self.parent:
            if 'parent' in properties:
                parents = (properties['parent'],)
            else:
                parents = self.parent.__bicep__(
                    fields,
                    parameters=parameters,
                    infra_component=infra_component,
                    module_name=module_name,
                )
        if self._suffix is None:
            # TODO: We're doing this delayed because if it's a ComponentField, it would
            # fail if we do it in the constructor (before __set_name__ is called).
            self._suffix = self._build_suffix(properties.get('name'))
            for resource_setting in self._settings.values():
                resource_setting.suffix = self._suffix

        if self._existing:
            if 'name' not in properties and 'name' not in self.DEFAULTS:
                raise ValueError(f"Reference to existing resource {repr(self)} is missing 'name'.")
            ref_properties = {'name': properties.get('name', self.DEFAULTS['name'])}
            rg = None
            if parents:
                ref_properties['parent'] = parents[0] 
            elif 'resource_group' in properties:
                rg = properties['resource_group'].__bicep__(
                    fields,
                    parameters=parameters,
                    infra_component=infra_component,
                    module_name=module_name,
                )[0]
                ref_properties['scope'] = rg
            symbol = self._build_symbol()
            outputs = self._outputs(
                symbol=symbol,
                resource_group=rg,
                parents=parents,
            )
            field = FieldType(
                resource=self.resource,
                properties=ref_properties,
                symbol=symbol,
                outputs=outputs,
                resource_group=rg,
                version=self.version,
                extensions=extensions,
                existing=True,
                name=ref_properties['name'],
                add_defaults=None
            )
            fields[self._get_field_id(symbol, parents)] = field
            return (symbol, *parents)

        rg = self._find_resource_group(fields, parameters, module_name=module_name)
        if not parents:
            field = self._find_last_resource_match(fields, resource_group=rg, name=properties.get('name'))
        else:
            field = self._find_last_resource_match(fields, parent=parents[0], name=properties.get('name'))

        if field:
            params = field.properties
            symbol = field.symbol
            outputs = field.outputs
            if 'managed_identity_roles' in self.extensions:
                # TODO: Need to confirm the behaviour here as I think this might be mutating the original copy
                # of extensions.
                # We don't really care if this causes duplicate roles because they should be
                # cleaned up when exported to bicep.
                field.extensions['managed_identity_roles'].extend(extensions['managed_identity_roles'])
            if 'user_roles' in self.extensions:
                field.extensions['user_roles'].extend(extensions['user_roles'])
        else:
            params = {}
            if self.parent:
                params['parent'] = parents[0]
            outputs = {}
            symbol = self._build_symbol()
            field = FieldType(
                resource=self.resource,
                properties=params,
                symbol=symbol,
                outputs=outputs,
                resource_group=rg,
                version=self.version,
                extensions=extensions,
                existing=False,
                name=properties.get('name'),
                add_defaults=self._add_defaults
            )
            fields[self._get_field_id(symbol, parents)] = field

        output_config = self._merge_properties(
            params,
            properties,
            fields=fields,
            parameters=parameters,
            symbol=symbol,
            resource_group=rg,
        )
        resource_outputs = self._outputs(
            symbol=symbol,
            resource_group=rg,
            parents=parents,
            **output_config
        )
        outputs.update(resource_outputs)
        return (symbol, *parents)

    def get_client(
            self,
            cls: Callable[..., ClientType],
            /,
            *,
            options: Optional[Dict[str, Any]] = None,
            config_store: Optional[Mapping[str, Any]] = None,
            env_name: Optional[str] = None,
    ) -> ClientType:
        raise TypeError(f"Resource '{repr(self)}' has no compatible Client endpoint.")


class _ClientResource(Resource[ResourcePropertiesType]):
    def __init__(self, properties=None, /, **kwargs) -> None:
        settings_passthrough = 'settings' in kwargs
        super().__init__(properties, **kwargs)
        if not settings_passthrough:
            # TODO: Add public getters and setters for these?
            self._settings.update(
                {
                    'audience': StoredPrioritizedSetting(
                        name='audience',
                        env_vars=_build_envs(self._prefixes, ['AUDIENCE']),
                        suffix=self._suffix
                    ),
                    'endpoint': StoredPrioritizedSetting(
                        name='endpoint',
                        env_vars=_build_envs(self._prefixes, ['ENDPOINT']),
                        system_hook=self._build_endpoint,
                        suffix=self._suffix
                    ),
                    'api_version': StoredPrioritizedSetting(
                        name='api_version',
                        env_vars=_build_envs(self._prefixes, ['API_VERSION']),
                        suffix=self._suffix
                    ),
                    'client_options': StoredPrioritizedSetting(
                        name='client_options',
                        default={},
                        suffix=self._suffix
                    ),
                    'credential': StoredPrioritizedSetting(
                        name='credential',
                        default='default',
                    )
                }

            )

    def _build_endpoint(self) -> str:
        raise NotImplementedError("This must be implemented by child resources.")

    def _build_credential(self, use_async: bool, *, config_store: Mapping[str, Any]) -> Union[SupportsTokenInfo, AsyncSupportsTokenInfo]:
        # TODO: This needs work - can't close the credential, it also probably shouldn't be stored in the setting.
        value = self._settings['credential'](config_store=config_store)
        try:
            value = value.lower()
            if value == 'default':
                if use_async:
                    from azure.identity.aio import DefaultAzureCredential
                else:
                    from azure.identity import DefaultAzureCredential
                credential = DefaultAzureCredential()
                self._settings['credential'].set_value(credential)
                return credential
            if value == 'managedidentity':
                if use_async:
                    from azure.identity.aio import ManagedIdentityCredential
                else:
                    from azure.identity import ManagedIdentityCredential
                credential = ManagedIdentityCredential()
                self._settings['credential'].set_value(credential)
                return credential
        except AttributeError:
            pass
        try:
            constructed_value = value()
            self._settings['credential'].set_value(constructed_value)
            return constructed_value
        except TypeError:
            if isinstance(value, (SupportsTokenInfo, AsyncSupportsTokenInfo)):
                self._settings['credential'].set_value(value)
                return value
        raise ValueError(f'Cannot convert {value} to credential type.')

    def get_client(
            self,
            cls: Callable[..., ClientType],
            /,
            *,
            transport: Any = None,
            api_version: Optional[str] = None,
            audience: Optional[str] = None,
            config_store: Optional[Mapping[str, Any]] = None,
            env_name: Optional[str] = None,  # TODO: remove
            use_async: Optional[bool] = None,
            **client_options,
    ) -> ClientType:
        if env_name:
           if config_store:
               raise ValueError("Cannot specify both 'config_store' and 'env_name'.")
           config_store = _load_dev_environment(env_name)
        elif config_store is None:
            config_store = _load_dev_environment()

        if hasattr(cls, 'from_resource'):
            return cls.from_resource(self, config_store, transport=transport, **client_options)
        if hasattr(cls, '_from_resource'):
            return cls._from_resource(self, config_store, transport=transport, **client_options)

        endpoint: str = self._settings['endpoint'](config_store=config_store)
        # TODO: AI endpoints!!!
        endpoint = endpoint.replace('cognitiveservices.azure.com', 'openai.azure.com')
        client_kwargs = {}
        client_kwargs.update(self._settings['client_options'](config_store=config_store))
        client_kwargs.update(client_options)
        try:
            client_kwargs['api_version'] = self._settings['api_version'](api_version, config_store=config_store)
        except RuntimeError:
            pass
        try:
            # TODO: Overwrite this in the deployment resource
            #client_kwargs['credential_scopes'] = self._settings['audience'](audience, config_store=config_store)
            client_kwargs['audience'] = self._settings['audience'](audience, config_store=config_store)
        except RuntimeError:
            pass
        if 'credential' not in client_kwargs:
            if use_async is None:
                try:
                    use_async = inspect.iscoroutinefunction(getattr(cls, 'close'))
                except AttributeError:
                    raise TypeError(f"Cannot determine whether cls type '{cls.__name__}' is async or not. Please specify 'use_async' keyword argument.")
            client_kwargs['credential'] = self._build_credential(use_async, config_store=config_store)
        client = cls(endpoint, **client_kwargs)
        client.__resource_settings__ = self
        return client
