# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=arguments-differ

from collections import defaultdict
from typing import TYPE_CHECKING, TypedDict, Generic, Literal, Mapping, Tuple, Union, Optional, Any, cast
from typing_extensions import TypeVar, Unpack

from .._identifiers import ResourceIdentifiers
from ..._parameters import GLOBAL_PARAMS
from ..._utils import find_resource_match
from ..._bicep.expressions import Parameter, ResourceSymbol, Subscription
from ..._resource import Resource, FieldsType, FieldType, ResourceReference, ExtensionResources

if TYPE_CHECKING:
    from ._types import ResourceGroupResource
    from ..._component import AzureInfrastructure


_DEFAULT_RESOURCE_GROUP: "ResourceGroupResource" = {
    "name": GLOBAL_PARAMS["defaultName"],
    "location": GLOBAL_PARAMS["location"],
    "tags": GLOBAL_PARAMS["azdTags"],
}


class ResourceGroupKwargs(TypedDict, total=False):
    # lock: 'Lock'
    # """The lock settings of the service."""
    location: Union[str, Parameter]
    """Location of the Resource Group. It uses the deployment's location when not provided."""
    tags: Union[dict[str, Union[str, Parameter]], Parameter]
    """Tags of the Resource Group."""


ResourceGroupResourceType = TypeVar(
    "ResourceGroupResourceType", bound=Mapping[str, Any], default="ResourceGroupResource"
)


class ResourceGroup(Resource, Generic[ResourceGroupResourceType]):
    """A class representing an Azure Resource Group.

    This class allows you to define and manage Azure Resource Groups, which serve as containers
    for organizing and managing Azure resources.

    :ivar DEFAULTS: Default values for the resource group properties
    :vartype DEFAULTS: ResourceGroupResource
    :ivar properties: Properties of the resource group
    :vartype properties: ResourceGroupResourceType
    :ivar extensions: Extension resources associated with this resource group (roles, etc.)
    :vartype extensions: ExtensionResources
    :ivar parent: Parent resource, None for resource groups as they are top-level resources
    :vartype parent: None
    :ivar identifier: Resource identifier for the resource group
    :vartype identifier: ResourceIdentifiers
    :ivar resource: The Azure resource type string "Microsoft.Resources/resourceGroups"
    :vartype resource: str
    :ivar version: The API version of the resource
    :vartype version: str

    :param properties: Optional dictionary containing resource group properties
    :type properties: ResourceGroupResource | None
    :param name: Name of the resource group
    :type name: str | Parameter | None
    :keyword location: Location of the Resource Group. Uses the deployment's location when not provided
    :paramtype location: str | Parameter
    :keyword tags: Tags to be applied to the Resource Group
    :paramtype tags: dict[str, str | Parameter] | Parameter
    """
    DEFAULTS: "ResourceGroupResource" = _DEFAULT_RESOURCE_GROUP  # type: ignore[assignment]
    properties: ResourceGroupResourceType
    parent: None

    def __init__(
        self,
        properties: Optional["ResourceGroupResource"] = None,
        /,
        name: Optional[Union[str, Parameter]] = None,
        **kwargs: Unpack["ResourceGroupKwargs"],
    ) -> None:
        extensions: ExtensionResources = defaultdict(list)  # type: ignore  # Doesn't like the default dict.
        # 'existing' is passed by the reference classmethod.
        existing = kwargs.pop("existing", False)  # type: ignore[typeddict-item]
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
    def reference(  # type: ignore[override]  # Parameter subset and renames
        cls,
        *,
        name: Union[str, Parameter],
        subscription: Optional[Union[str, Parameter]] = None,
    ) -> "ResourceGroup[ResourceReference]":
        existing = super().reference(name=name, subscription=subscription)
        return cast(ResourceGroup[ResourceReference], existing)

    @property
    def resource(self) -> Literal["Microsoft.Resources/resourceGroups"]:
        return "Microsoft.Resources/resourceGroups"

    @property
    def version(self) -> str:
        from ._types import VERSION

        return VERSION

    def _build_resource_id(self, *, config_store: Optional[Mapping[str, Any]]) -> str:
        prefix = f"/subscriptions/{self._settings['subscription'](config_store=config_store)}/providers/"
        return prefix + f"{self.resource}/{self._settings['name'](config_store=config_store)}"

    def __bicep__(  # pylint: disable=unused-argument
        self,
        fields: FieldsType,
        *,
        parameters: dict[str, Parameter],
        infra_component: Optional["AzureInfrastructure"] = None,
        **kwargs,
    ) -> Tuple[ResourceSymbol, ...]:
        properties, _ = self._resolve_resource(infra_component)
        if self._existing:
            ref_properties = {"name": properties["name"]}
            if properties.get("subscription"):
                ref_properties["scope"] = Subscription(properties["subscription"])
            symbol = self._build_symbol(ref_properties["name"])
            field = FieldType(
                resource=self.resource,
                identifier=self.identifier,
                properties=ref_properties,
                symbol=symbol,
                outputs={},
                resource_group=symbol,
                version=self.version,
                extensions={},
                existing=True,
                name=properties["name"],
                defaults=None,
            )
            fields[self._get_field_id(symbol, ())] = field
            return (symbol,)

        field_match = find_resource_match(fields, resource=self.identifier, name=properties.get("name"))
        if field_match:
            params = field_match.properties
            symbol = field_match.symbol
        else:
            params = {}
            symbol = self._build_symbol(properties.get("name"))
            field = FieldType(
                resource=self.resource,
                identifier=self.identifier,
                properties=params,
                symbol=symbol,
                outputs={},
                resource_group=symbol,
                version=self.version,
                extensions={},
                existing=False,
                name=properties.get("name"),
                defaults={
                    "resource": self.DEFAULTS,
                    "extensions": self.DEFAULT_EXTENSIONS,
                },
            )
            fields[self._get_field_id(symbol, ())] = field
        self._merge_resource(params, properties, symbol=symbol, resource_group=symbol)
        return (symbol,)
