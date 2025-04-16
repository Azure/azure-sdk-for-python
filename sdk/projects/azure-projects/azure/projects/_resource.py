# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from __future__ import annotations

import inspect
from itertools import product
from collections import defaultdict
import os
from typing import (
    Literal,
    Mapping,
    MutableMapping,
    Tuple,
    Optional,
    Type,
    Union,
    Dict,
    List,
    Any,
    Sequence,
    Protocol,
    AsyncContextManager,
    ContextManager,
    overload,
    runtime_checkable,
    TYPE_CHECKING,
)
from typing_extensions import Self, NamedTuple, TypedDict, TypeVar

from dotenv import dotenv_values

from azure.core.settings import _unset

from .resources._identifiers import ResourceIdentifiers
from ._utils import (
    run_coroutine_sync,
    resolve_properties,
    find_last_resource_match,
    find_resource_group,
)
from ._setting import StoredPrioritizedSetting
from ._bicep.expressions import (
    Output,
    Parameter,
    ResourceSymbol,
    ResourceGroup as RGSymbol,
)
from ._bicep.utils import clean_name

if TYPE_CHECKING:
    from azure.core.credentials import SupportsTokenInfo
    from azure.core.credentials_async import AsyncSupportsTokenInfo

    from .resources.resourcegroup import ResourceGroup
    from .resources._extension import RoleAssignment
    from ._component import AzureInfrastructure


def _load_dev_environment(name: Optional[str] = None, label: Optional[str] = None) -> Dict[str, Optional[str]]:
    azd_dir = os.path.join(os.getcwd(), ".azure")
    if name and not name.endswith(".env"):
        if not os.path.isdir(azd_dir):
            return {}
        env_name = name + (f"-{label}" if label else "")
        env_path = os.path.join(azd_dir, env_name, ".env")
    elif name:
        env_path = name
    else:
        script_name = os.path.splitext(os.path.basename(inspect.stack()[-1][0].f_code.co_filename))[0]
        script_env = os.path.join(azd_dir, script_name, ".env")
        if os.path.isdir(azd_dir) and os.path.isfile(script_env):
            env_path = script_env
        else:
            env_path = ".env"
    values = dotenv_values(env_path)
    return values


def _build_envs(services: List[str], attributes: List[str]) -> List[str]:
    all_vars = product(services, attributes)
    return ["_".join(["AZURE"] + list(var)).upper() for var in all_vars]


@runtime_checkable
class SyncClient(Protocol, ContextManager["SyncClient"]):
    def close(self) -> None: ...


@runtime_checkable
class AsyncClient(Protocol, AsyncContextManager["AsyncClient"]):  # pylint: disable=async-client-bad-name
    async def close(self) -> None: ...


class FieldType(NamedTuple):
    resource: str
    identifier: ResourceIdentifiers
    version: str
    properties: Dict[str, Any]
    symbol: ResourceSymbol
    outputs: Dict[str, List[Output]]
    resource_group: Optional[ResourceSymbol]
    extensions: "ExtensionResources"
    existing: bool
    name: Optional[Union[str, Parameter]]
    defaults: Optional[Dict[str, Any]]


class ResourceReference(TypedDict, total=False):
    name: Union[str, Parameter]
    resource_group: "ResourceGroup[ResourceReference]"
    subscription: Union[str, Parameter]
    parent: Resource


class ExtensionResources(TypedDict, total=False):
    managed_identity_roles: Union[
        Parameter,
        Sequence[Union[Parameter, "RoleAssignment", str]],
    ]
    user_roles: Union[
        Parameter,
        Sequence[Union[Parameter, "RoleAssignment", str]],
    ]
    # lock
    # diagnostics
    # private endpoint
    # secret store?


FieldsType = Dict[str, FieldType]
ClientType = TypeVar("ClientType", bound=Union[SyncClient, AsyncClient])
_EMPTY_DEFAULT: MutableMapping[str, Any] = {}
_EMPTY_DEFAULT_EXTENSIONS: ExtensionResources = {}


class Resource:  # pylint: disable=too-many-instance-attributes
    DEFAULTS: MutableMapping[str, Any] = _EMPTY_DEFAULT
    DEFAULT_EXTENSIONS: ExtensionResources = _EMPTY_DEFAULT_EXTENSIONS
    identifier: ResourceIdentifiers
    properties: Mapping[str, Any]
    extensions: ExtensionResources
    parent: Optional[Resource]

    def __init__(self, properties: Optional[Mapping[str, Any]] = None, /, **kwargs) -> None:
        """This constructor should not be used directly."""
        self.properties = properties or {}
        self.extensions: ExtensionResources = kwargs.pop("extensions", {})
        self.identifier = kwargs.pop("identifier")
        self.parent: Optional[Resource] = kwargs.pop("parent", self.properties.get("parent"))
        self._subresource: Optional[str] = kwargs.pop("subresource", "")
        self._existing: bool = kwargs.pop("existing", False)
        if self.parent and not self._subresource:
            raise ValueError("Parent must be specified with subresource.")

        # Suffix and prefix are used to environment variable/config setting names
        # The prefix identifies the service/resource and the suffix is unique to this
        # specific resource (using either the name or name parameter if present).
        self._prefixes: List[str] = kwargs.pop("service_prefix", [])
        self._env_suffix = kwargs.pop("env_suffix", None)
        if self._env_suffix:
            self._env_suffix = f"_{self._env_suffix.upper()}"

        # These determine how resource properties are handled when building up the bicep
        # definitions for the same resource declared in multiple places. Anything in the
        # 'properties' field of a resource will error on conflict
        # TODO: Should be able to remove this.
        self._properties_to_merge: List[str] = kwargs.pop("properties_to_merge", ["properties", "tags"])

        self._settings: Dict[str, StoredPrioritizedSetting] = {
            "name": StoredPrioritizedSetting(
                "name",
                env_vars=_build_envs(self._prefixes, ["NAME"]),
                hook=self._get_default_name,
                suffix=self._env_suffix,
            ),
            "resource_id": StoredPrioritizedSetting(
                name="resource_id",
                env_vars=_build_envs(self._prefixes, ["ID", "RESOURCE_ID"]),
                hook=self._build_resource_id,
                suffix=self._env_suffix,
            ),
        }
        if self.parent:
            self._settings["resource_group"] = self.parent._settings["resource_group"]
            self._settings["subscription"] = self.parent._settings["subscription"]
        elif "resource_group" in self.properties:
            self._settings["resource_group"] = self.properties["resource_group"]._settings["name"]
            self._settings["subscription"] = self.properties["resource_group"]._settings["subscription"]
        else:
            self._settings["resource_group"] = StoredPrioritizedSetting(
                name="resource_group",
                env_vars=_build_envs(self._prefixes, ["RESOURCE_GROUP"]),
                suffix=self._env_suffix,
            )
            self._settings["subscription"] = StoredPrioritizedSetting(
                name="subscription",
                env_var="AZURE_SUBSCRIPTION_ID",
                suffix=self._env_suffix,
                default=self.properties.get("subscription", _unset),
            )
        if kwargs:
            raise TypeError(f"Resource {self.__class__.__name__} got unexpected kwargs: {list(kwargs.keys())}")

    def __repr__(self) -> str:
        name = f'\'{self.properties["name"]}\'' if "name" in self.properties else "<default>"
        return f"{self.__class__.__name__}({name})"

    def __eq__(self, value: Any) -> bool:
        # Resources are considered equal if they (and their parents) have the same type and same name.
        try:
            parent_eq = True
            if self.parent:
                parent_eq = self.parent == value.parent
            return (
                parent_eq
                and value.resource == self.resource
                and value.properties.get("name") == self.properties.get("name")
            )
        except Exception:  # pylint: disable=broad-exception-caught
            return False

    @property
    def resource(self) -> str:
        raise NotImplementedError("This must be implemented by child resources.")

    @property
    def version(self) -> str:
        # TODO: Support version override
        raise NotImplementedError("This must be implemented by child resources.")

    @classmethod
    def reference(
        cls,
        *,
        name: Optional[Union[str, Parameter]] = None,
        resource_group: Optional[Union[str, Parameter, "ResourceGroup[ResourceReference]"]] = None,
        subscription: Optional[Union[str, Parameter]] = None,
        parent: Optional[Resource] = None,
    ) -> Self:
        if parent and resource_group:
            raise ValueError("Cannot specify both parent and resource_group.")
        properties = ResourceReference(name=name) if name else {}
        if resource_group:
            if isinstance(resource_group, (str, Parameter)):
                from .resources.resourcegroup import ResourceGroup

                resource_group = ResourceGroup.reference(name=resource_group, subscription=subscription)
            properties["resource_group"] = resource_group
        elif subscription:
            # We're assuming 'subscription' will only be passed in in the case of rg-agnostic
            # resources, like a resourcegroup. Otherwise 'subscription' must be provided
            # on the 'resource_group' parameter.
            properties["subscription"] = subscription
        return cls(properties, parent=parent, existing=True)

    def _build_symbol(self, suffix: Optional[Union[str, Parameter]]) -> ResourceSymbol:
        suffix_str = ""
        if suffix:
            suffix_str = "_" + clean_name(suffix).lower()
        resource_ref = self.resource.split("/")[-1].lower()
        if resource_ref.endswith("ies"):
            resource_ref = resource_ref.rstrip("ies") + "y"
        else:
            resource_ref = resource_ref.rstrip("s")
        symbol = f"{resource_ref}{suffix_str}"
        principal_id = self.properties.get("identity", {}).get("type", "").startswith("SystemAssigned")
        return ResourceSymbol(symbol, principal_id=principal_id)

    def _build_resource_id(self, *, config_store: Optional[Mapping[str, Any]]) -> str:
        if not self.resource:
            raise ValueError("No resource specified.")
        name = self._settings["name"](config_store=config_store)
        if self.parent:
            return f"{self.parent._build_resource_id(config_store=config_store)}/{self._subresource}/{name}"  # pylint: disable=protected-access
        sub_prefix = f"/subscriptions/{self._settings['subscription'](config_store=config_store)}"
        rg_prefix = f"/resourceGroups/{self._settings['resource_group'](config_store=config_store)}"
        return sub_prefix + rg_prefix + f"/providers/{self.resource}/{name}"

    def _get_default_name(self, *, config_store: Optional[Mapping[str, Any]]) -> str:  # pylint: disable=unused-argument
        try:
            # TODO: Test what this will do if "name" is a ComponentField - either resource or string.
            return self.properties["name"]
        except KeyError:
            pass
        raise RuntimeError("Resource name not known.")

    def _outputs(
        self, *, symbol: ResourceSymbol, suffix: str, **kwargs  # pylint: disable=unused-argument
    ) -> Dict[str, List[Output]]:
        outputs = defaultdict(list)
        outputs["resource_id"] = [Output(f"AZURE_{self._prefixes[0].upper()}_ID{suffix}", "id", symbol)]
        outputs["name"] = [Output(f"AZURE_{self._prefixes[0].upper()}_NAME{suffix}", "name", symbol)]

        rg_output = f"AZURE_{self._prefixes[0].upper()}_RESOURCE_GROUP{suffix}"
        outputs["resource_group"] = [Output(rg_output, RGSymbol().name)]
        if self._existing:
            try:
                rg_name = self._settings["resource_group"]()  # TODO: Is it a problem that there's no config?
                outputs["resource_group"] = [Output(rg_output, rg_name)]
            except RuntimeError:
                pass
        return outputs

    def _get_field_id(self, symbol: ResourceSymbol, parents: Tuple[ResourceSymbol, ...]) -> str:
        if self.parent:
            prefix = self.parent._get_field_id(parents[0], parents[1:])  # pylint: disable=protected-access
            return f"{prefix}.{symbol.value}"
        return symbol.value

    def _merge_properties(
        self,
        current_properties: Dict[str, Any],
        new_properties: Dict[str, Any],
        **kwargs,  # pylint: disable=unused-argument
    ) -> Dict[str, Any]:
        for key, value in new_properties.items():
            if key in current_properties:
                if current_properties[key] != value:
                    raise ValueError(
                        f"{repr(self)} cannot set '{key}' to '{value}', already set to: '{current_properties[key]}'."
                    )
            else:
                current_properties[key] = value
        return current_properties

    def _merge_resource(self, current_properties: Dict[str, Any], new_properties: Dict[str, Any], **kwargs) -> None:
        for key, value in new_properties.items():
            if key in ["properties", "tags"]:
                merged = self._merge_properties(current_properties.get(key, {}), value, **kwargs)
                if merged:
                    current_properties[key] = merged
            elif key in current_properties and current_properties[key] != value:
                raise ValueError(
                    f"{repr(self)} cannot set '{key}' to '{value}', already set to: '{current_properties[key]}'."
                )
            else:
                current_properties[key] = value

    def _resolve_resource(self, parameters, component):
        from ._component import ComponentField

        name = self.properties.get("name")
        if isinstance(name, ComponentField):
            resolved = name.get(component)
            if isinstance(resolved, Resource):
                return resolved._resolve_resource(parameters, component)  # pylint: disable=protected-access
        return resolve_properties(self.properties, parameters, component)

    def __bicep__(  # pylint: disable=too-many-statements
        self,
        fields: FieldsType,
        *,
        parameters: Dict[str, Parameter],
        infra_component: Optional[AzureInfrastructure] = None,
        depends_on: Optional[List[ResourceSymbol]] = None,
        attrname: Optional[str] = None,
    ) -> Tuple[ResourceSymbol, ...]:
        suffix = f"_{attrname.upper()}" if attrname else ""
        properties = self._resolve_resource(parameters, infra_component)
        extensions: ExtensionResources = defaultdict(list)  # type: ignore[assignment]  # Doesn't like defaultdict
        extensions.update(self.extensions)
        parents: Tuple[ResourceSymbol, ...] = ()
        if self.parent:
            if "parent" in properties:
                parents = (properties["parent"],)
            else:
                parents = self.parent.__bicep__(
                    fields, parameters=parameters, infra_component=infra_component, attrname=attrname
                )

        if self._existing:
            if "name" not in properties and "name" not in self.DEFAULTS:
                raise ValueError(f"Reference to existing resource {repr(self)} is missing 'name'.")
            ref_properties = {"name": properties.get("name") or self.DEFAULTS["name"]}
            rg = None
            if parents:
                ref_properties["parent"] = parents[0]
            elif "resource_group" in properties:
                rg = properties["resource_group"].__bicep__(
                    fields,
                    parameters=parameters,
                    infra_component=infra_component,
                )[0]
                ref_properties["scope"] = rg
            symbol = self._build_symbol(ref_properties["name"])
            outputs = self._outputs(
                symbol=symbol,
                suffix=suffix,
                resource_group=rg,
                parents=parents,
            )
            field = FieldType(
                resource=self.resource,
                identifier=self.identifier,
                properties=ref_properties,
                symbol=symbol,
                outputs=outputs,
                resource_group=rg,
                version=self.version,
                extensions=extensions,
                existing=True,
                name=ref_properties["name"],
                defaults=None,
            )
            fields[self._get_field_id(symbol, parents)] = field
            return (symbol, *parents)

        # TODO: Is this going to pick up an existing RG that we don't want to deploy to?
        # We can probably remove this and just default using the current RG scope.
        rg = find_resource_group(fields)
        if not parents:
            field_match = find_last_resource_match(
                fields, resource=self.identifier, resource_group=rg, name=properties.get("name")
            )
        else:
            field_match = find_last_resource_match(
                fields, resource=self.identifier, parent=parents[0], name=properties.get("name")
            )

        if field_match:
            params = field_match.properties
            symbol = field_match.symbol
            outputs = field_match.outputs
            if "managed_identity_roles" in self.extensions:
                # TODO: Need to confirm the behaviour here as I think this might be mutating the original copy
                # of extensions.
                # We don't really care if this causes duplicate roles because they should be
                # cleaned up when exported to bicep.
                # TODO: Should maybe replace the namedtuple with a slotted-dataclass so we can mutate the
                # value and assign a fresh list here.
                field_match.extensions["managed_identity_roles"].extend(  # type: ignore[union-attr]  # TODO
                    extensions["managed_identity_roles"]
                )
            if "user_roles" in self.extensions:
                field_match.extensions["user_roles"].extend(  # type: ignore[union-attr]  # TODO
                    extensions["user_roles"]
                )
        else:
            params = {}
            if depends_on:
                params["dependsOn"] = depends_on
            if self.parent:
                params["parent"] = parents[0]

            outputs = {}
            symbol = self._build_symbol(properties.get("name"))
            field = FieldType(
                resource=self.resource,
                identifier=self.identifier,
                properties=params,
                symbol=symbol,
                outputs=outputs,
                resource_group=rg,
                version=self.version,
                extensions=extensions,
                existing=False,
                name=properties.get("name"),
                defaults={
                    "resource": self.DEFAULTS,
                    "extensions": self.DEFAULT_EXTENSIONS,
                },
            )
            fields[self._get_field_id(symbol, parents)] = field
        self._merge_resource(
            params,
            properties,
            fields=fields,
            parameters=parameters,
            symbol=symbol,
            resource_group=rg,
        )
        if attrname or not field_match:
            # TODO: Figure out correct behaviour for parent outputs here.
            # attrname will be None in the case of resolving a parent bicep, which is fine?
            resource_outputs = self._outputs(symbol=symbol, suffix=suffix, resource_group=rg, parents=parents)
            for key, value in resource_outputs.items():
                outputs[key] = list(set(outputs.get(key, []) + value))

        return (symbol, *parents)

    def get_client(self, cls: Type[ClientType], /, **kwargs) -> ClientType:
        raise TypeError(f"Resource '{repr(self)}' has no compatible Client endpoint.")


class _ClientResource(Resource):
    def __init__(self, properties: Optional[Mapping[str, Any]] = None, /, **kwargs) -> None:
        settings_passthrough = "settings" in kwargs
        super().__init__(properties, **kwargs)
        if not settings_passthrough:
            # TODO: Add public getters and setters for these?
            self._settings.update(
                {
                    "audience": StoredPrioritizedSetting(
                        name="audience", env_vars=_build_envs(self._prefixes, ["AUDIENCE"]), suffix=self._env_suffix
                    ),
                    "endpoint": StoredPrioritizedSetting(
                        name="endpoint",
                        env_vars=_build_envs(self._prefixes, ["ENDPOINT"]),
                        hook=self._build_endpoint,
                        suffix=self._env_suffix,
                    ),
                    "api_version": StoredPrioritizedSetting(
                        name="api_version",
                        env_vars=_build_envs(self._prefixes, ["API_VERSION"]),
                        suffix=self._env_suffix,
                    ),
                }
            )

    @property
    def audience(self) -> str:
        return self._settings["audience"]()

    @audience.setter
    def audience(self, value: str) -> None:
        self._settings["audience"].set_value(value)

    @property
    def api_version(self) -> str:
        return self._settings["api_version"]()

    @api_version.setter
    def api_version(self, value: str) -> None:
        self._settings["api_version"].set_value(value)

    def _build_endpoint(self, *, config_store: Optional[Mapping[str, Any]]) -> str:
        raise NotImplementedError("This must be implemented by child resources.")

    def _build_credential(
        self,
        cls: Type[ClientType],
        *,
        use_async: Optional[bool],
        credential: Optional[Union["SupportsTokenInfo", "AsyncSupportsTokenInfo"]],
    ) -> Union["SupportsTokenInfo", "AsyncSupportsTokenInfo"]:
        # TODO: This needs work - how to close the credential.
        if credential:
            return credential
        if use_async is None:
            try:
                use_async = inspect.iscoroutinefunction(getattr(cls, "close"))
            except AttributeError:
                raise TypeError(
                    f"Cannot determine whether cls type '{cls.__name__}' is async or not. "
                    "Please specify 'use_async' keyword argument."
                ) from None
        if use_async:
            from azure.identity.aio import DefaultAzureCredential as AsyncDefaultAzureCredential

            return AsyncDefaultAzureCredential()
        from azure.identity import DefaultAzureCredential

        return DefaultAzureCredential()

    async def _build_client(self, cls, endpoint, **kwargs):
        client = cls(endpoint, **kwargs)
        try:
            return await client
        except TypeError:
            return client

    @overload
    def get_client(
        self,
        cls: Type[ClientType],
        /,
        *,
        transport: Any = None,
        credential: Optional[Union["SupportsTokenInfo", "AsyncSupportsTokenInfo"]] = None,
        api_version: Optional[str] = None,
        audience: Optional[str] = None,
        config_store: Optional[Mapping[str, Any]] = None,
        use_async: Optional[bool] = None,
        return_credential: Literal[False] = False,
        **client_options,
    ) -> ClientType: ...
    @overload
    def get_client(  # pylint: disable=arguments-differ
        self,
        cls: Type[ClientType],
        /,
        *,
        transport: Any = None,
        credential: Optional[Union["SupportsTokenInfo", "AsyncSupportsTokenInfo"]] = None,
        api_version: Optional[str] = None,
        audience: Optional[str] = None,
        config_store: Optional[Mapping[str, Any]] = None,
        use_async: Optional[bool] = None,
        return_credential: Literal[True],
        **client_options,
    ) -> Tuple[ClientType, Union["SupportsTokenInfo", "AsyncSupportsTokenInfo"]]: ...
    def get_client(
        self,
        cls,
        /,
        *,
        transport=None,
        credential=None,
        api_version=None,
        audience=None,
        config_store=None,
        use_async=None,
        return_credential=False,
        **client_options,
    ):
        if config_store is None:
            # TODO: replace with simple dotenv load?
            config_store = _load_dev_environment()

        endpoint = self._settings["endpoint"](config_store=config_store)
        client_kwargs = {}
        client_kwargs.update(client_options)
        try:
            client_kwargs["api_version"] = self._settings["api_version"](api_version, config_store=config_store)
        except RuntimeError:
            pass
        try:
            client_kwargs["audience"] = self._settings["audience"](audience, config_store=config_store)
        except RuntimeError:
            pass

        credential = self._build_credential(cls, use_async=use_async, credential=credential)
        if transport is not None:
            client_kwargs["transport"] = transport
        client = run_coroutine_sync(self._build_client(cls, endpoint, credential=credential, **client_kwargs))
        if return_credential:
            return client, credential
        return client
