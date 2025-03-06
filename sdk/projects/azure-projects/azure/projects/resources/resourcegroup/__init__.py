# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from collections import defaultdict
from typing import TYPE_CHECKING, Dict, List, Literal, Mapping, Tuple, Type, TypedDict, Union, Optional, Any, overload
from typing_extensions import TypeVar, Unpack

from .._identifiers import ResourceIdentifiers
from ..._parameters import GLOBAL_PARAMS
from ..._bicep.expressions import (
    Expression,
    Output,
    Parameter,
    ResourceSymbol,
    Variable,
    UniqueString,
    Subscription,
)
from ..._bicep.utils import generate_name, generate_suffix
from ..._parameters import LOCATION, DEFAULT_NAME, AZD_TAGS
from ..._resource import Resource, FieldsType, FieldType, ResourceReference, ExtensionResources

if TYPE_CHECKING:
    from .types import ResourceGroupResource


_DEFAULT_RESOURCE_GROUP: "ResourceGroupResource" = {
    "name": GLOBAL_PARAMS["defaultName"],
    "location": GLOBAL_PARAMS["location"],
    "tags": GLOBAL_PARAMS["azdTags"],
}


class ResourceGroupKwargs(TypedDict, total=False):
    # lock: 'Lock'
    # """The lock settings of the service."""
    location: Union[str, Parameter[str]]
    """Location of the Resource Group. It uses the deployment's location when not provided."""
    tags: Union[Dict[str, Union[str, Parameter[str]]], Parameter[Dict[str, str]]]
    """Tags of the Resource Group."""


ResourceGroupResourceType = TypeVar("ResourceGroupResourceType", bound=Dict[str, Any], default="ResourceGroupResource")


class ResourceGroup(Resource[ResourceGroupResourceType]):
    DEFAULTS: "ResourceGroupResource" = _DEFAULT_RESOURCE_GROUP
    resource: Literal["Microsoft.Resources/resourceGroups"]
    properties: ResourceGroupResourceType

    def __init__(
        self,
        properties: Optional["ResourceGroupResource"] = None,
        /,
        name: Optional[Union[str, Parameter[str]]] = None,
        **kwargs: Unpack["ResourceGroupKwargs"],
    ) -> None:
        extensions: ExtensionResources = defaultdict(list)
        existing = kwargs.pop("existing", False)
        if not existing:
            properties = properties or {}
            if name:
                properties["name"] = name
            if "location" in kwargs:
                properties["location"] = kwargs.pop("location")
            if "tags" in kwargs:
                properties["tags"] = kwargs.pop("tags")
        super().__init__(
            properties,
            extensions=extensions,
            service_prefix=["resource_group"],
            existing=existing,
            identifier=ResourceIdentifiers.resource_group,
            **kwargs,
        )

    @classmethod
    def reference(
        cls,
        *,
        name: Union[str, Parameter[str]],
        subscription: Optional[Union[str, Parameter[str]]] = None,
    ) -> "ResourceGroup[ResourceReference]":
        from .types import RESOURCE, VERSION

        resource = f"{RESOURCE}@{VERSION}"
        existing = super().reference(resource=resource, name=name, subscription=subscription)
        return existing

    @property
    def resource(self) -> str:
        if self._resource:
            return self._resource
        from .types import RESOURCE

        self._resource = RESOURCE
        return self._resource

    @property
    def version(self) -> str:
        if self._version:
            return self._version
        from .types import VERSION

        self._version = VERSION
        return self._version

    def _build_resource_id(self, *, config_store: Mapping[str, Any]) -> str:
        prefix = f"/subscriptions/{self._settings['subscription'](config_store=config_store)}/providers/"
        return prefix + f"{self._resource}/{self._settings['name'](config_store=config_store)}"

    def __bicep__(
        self,
        fields: FieldsType,
        *,
        parameters: Dict[str, Parameter],
        infra_component: Optional["AzureInfrastructure"] = None,
        **kwargs,
    ) -> Tuple[ResourceSymbol, ...]:
        properties = self._resolve_resource(parameters, infra_component)
        if self._suffix is None:
            # TODO: We're doing this delayed because if it's a ComponentField, it would
            # fail if we do it in the constructor (before __set_name__ is called).
            self._suffix = self._build_suffix(properties.get("name"))
            for resource_setting in self._settings.values():
                resource_setting.suffix = self._suffix

        if self._existing:
            ref_properties = {"name": properties["name"]}
            if properties.get("subscription"):
                ref_properties["scope"] = Subscription(properties["subscription"])
            symbol = self._build_symbol()
            field = FieldType(
                resource=self.resource,
                properties=ref_properties,
                symbol=symbol,
                outputs={},
                resource_group=symbol,
                version=self.version,
                extensions={},
                existing=True,
                name=properties["name"],
                add_defaults=None,
            )
            fields[self._get_field_id(symbol, ())] = field
            return (symbol,)

        field = self._find_last_resource_match(fields, name=properties.get("name"))
        if field:
            params = field.properties
            symbol = field.symbol
        else:
            params = {}
            symbol = self._build_symbol()
            field = FieldType(
                resource=self.resource,
                properties=params,
                symbol=symbol,
                outputs={},
                resource_group=symbol,
                version=self.version,
                extensions={},
                existing=False,
                name=properties.get("name"),
                add_defaults=self._add_defaults,
            )
            fields[self._get_field_id(symbol, ())] = field
        self._merge_properties(params, properties, symbol=symbol, resource_group=symbol)
        return (symbol,)
