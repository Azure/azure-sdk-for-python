# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=arguments-differ

from collections import defaultdict
from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
    TypedDict,
    Literal,
    Mapping,
    Union,
    Optional,
    cast,
)
from typing_extensions import TypeVar, Unpack

from ..resourcegroup import ResourceGroup
from .._identifiers import ResourceIdentifiers
from .._extension import RoleAssignment
from ..._parameters import GLOBAL_PARAMS
from ..._bicep.expressions import Output, ResourceSymbol, Parameter
from ..._resource import _ClientResource, ResourceReference, ExtensionResources

if TYPE_CHECKING:
    from ._types import KeyVaultResource, KeyVaultNetworkRuleSet


class KeyVaultKwargs(TypedDict, total=False):
    location: Union[str, Parameter]
    """Location for all resources."""
    # lock: 'Lock'
    # """The lock settings of the service."""
    network_acls: Union["KeyVaultNetworkRuleSet", Parameter]
    """A collection of rules governing the accessibility from specific network locations."""
    # private_endpoints: List['PrivateEndpoint']
    # """Configuration details for private endpoints. For security reasons, it is recommended to use private endpoints
    # whenever possible.
    # """
    public_network_access: Union[Literal["", "Disabled", "Enabled"], Parameter]
    """Whether or not public network access is allowed for this resource. For security reasons it should be disabled.
    If not specified, it will be disabled by default if private endpoints are set and networkAcls are not set.
    """
    roles: Union[
        Parameter,
        list[
            Union[
                Parameter,
                "RoleAssignment",
                Literal[
                    "Contributor",
                    "Key Vault Administrator",
                    "Key Vault Contributor",
                    "Key Vault Reader",
                    "Key Vault Secrets Officer",
                    "Key Vault Secrets User",
                    "Owner",
                    "Reader",
                    "Role Based Access Control Administrator",
                    "User Access Administrator",
                ],
            ]
        ],
    ]
    """Array of role assignments to create."""
    user_roles: Union[
        Parameter,
        list[
            Union[
                Parameter,
                "RoleAssignment",
                Literal[
                    "Contributor",
                    "Key Vault Administrator",
                    "Key Vault Contributor",
                    "Key Vault Reader",
                    "Key Vault Secrets Officer",
                    "Key Vault Secrets User",
                    "Owner",
                    "Reader",
                    "Role Based Access Control Administrator",
                    "User Access Administrator",
                ],
            ]
        ],
    ]
    """Array of Role assignments to create for user principal ID"""
    sku: Union[Literal["premium", "standard"], Parameter]
    """Specifies the SKU for the vault."""
    tags: Union[dict[str, Union[str, Parameter]], Parameter]
    """Resource tags."""


KeyVaultResourceType = TypeVar("KeyVaultResourceType", bound=Mapping[str, Any], default="KeyVaultResource")
ClientType = TypeVar("ClientType")
_DEFAULT_KEY_VAULT: "KeyVaultResource" = {
    "name": GLOBAL_PARAMS["defaultName"],
    "properties": {
        "sku": {"family": "A", "name": "standard"},
        "publicNetworkAccess": "Enabled",  # TODO: Set up proper default network acls on all resources
        "tenantId": GLOBAL_PARAMS["tenantId"],
        "accessPolicies": [],
        "enableRbacAuthorization": True,
    },
    "location": GLOBAL_PARAMS["location"],
    "tags": GLOBAL_PARAMS["azdTags"],
}
_DEFAULT_KEY_VAULT_EXTENSIONS: ExtensionResources = {
    "managed_identity_roles": ["Key Vault Administrator"],
    "user_roles": ["Key Vault Administrator"],
}


class KeyVault(_ClientResource, Generic[KeyVaultResourceType]):
    """Azure Key Vault resource representation.

    A class representing an Azure Key Vault instance that provides secure storage of secrets, keys, and certificates.

    :ivar DEFAULTS: Default configuration settings for the Key Vault resource
    :vartype DEFAULTS: KeyVaultResource
    :ivar DEFAULT_EXTENSIONS: Default role assignments and extensions configuration
    :vartype DEFAULT_EXTENSIONS: ExtensionResources
    :ivar properties: Properties of the Key Vault resource
    :vartype properties: KeyVaultResourceType
    :ivar parent: Parent resource (None for KeyVault as it's a top-level resource)
    :vartype parent: None

    :param properties: Optional dictionary containing the KeyVault resource properties
    :type properties: Optional[KeyVaultResource]
    :param name: Optional name for the KeyVault resource
    :type name: Optional[str]
    :keyword location: Location for all resources
    :paramtype location: Union[str, Parameter]
    :keyword network_acls: A collection of rules governing the accessibility from specific network locations
    :paramtype network_acls: Union[KeyVaultNetworkRuleSet, Parameter]
    :keyword public_network_access: Whether or not public network access is allowed for this resource
    :paramtype public_network_access: Union[Literal["", "Disabled", "Enabled"], Parameter]
    :keyword roles: Array of role assignments to create
    :paramtype roles: Union[Parameter, list[Union[Parameter, RoleAssignment, str]]]
    :keyword user_roles: Array of Role assignments to create for user principal ID
    :paramtype user_roles: Union[Parameter, list[Union[Parameter, RoleAssignment, str]]]
    :keyword sku: Specifies the SKU for the vault
    :paramtype sku: Union[Literal["premium", "standard"], Parameter]
    :keyword tags: Resource tags
    :paramtype tags: Union[dict[str, Union[str, Parameter]], Parameter]
    """

    DEFAULTS: "KeyVaultResource" = _DEFAULT_KEY_VAULT  # type: ignore[assignment]
    DEFAULT_EXTENSIONS: ExtensionResources = _DEFAULT_KEY_VAULT_EXTENSIONS
    properties: KeyVaultResourceType
    parent: None  # type: ignore[reportIncompatibleVariableOverride]

    def __init__(
        self,
        properties: Optional["KeyVaultResource"] = None,
        /,
        name: Optional[str] = None,
        **kwargs: Unpack[KeyVaultKwargs],
    ) -> None:
        # 'existing' is passed by the reference classmethod.
        existing = kwargs.pop("existing", False)  # type: ignore[typeddict-item]
        extensions: ExtensionResources = defaultdict(list)  # type: ignore  # Doesn't like the default dict.
        if "roles" in kwargs:
            extensions["managed_identity_roles"] = kwargs.pop("roles")
        if "user_roles" in kwargs:
            extensions["user_roles"] = kwargs.pop("user_roles")
        if not existing:
            properties = properties or {}
            if "properties" not in properties:
                properties["properties"] = {}
            if name:
                properties["name"] = name
            if "location" in kwargs:
                properties["location"] = kwargs.pop("location")
            if "network_acls" in kwargs:
                properties["properties"]["networkAcls"] = kwargs.pop("network_acls")
            if "public_network_access" in kwargs:
                properties["properties"]["publicNetworkAccess"] = kwargs.pop("public_network_access")
            if "sku" in kwargs:
                properties["properties"]["sku"] = {"family": "A", "name": kwargs.pop("sku")}
            if "tags" in kwargs:
                properties["tags"] = kwargs.pop("tags")
        super().__init__(
            properties,
            extensions=extensions,
            existing=existing,
            identifier=ResourceIdentifiers.keyvault,
            service_prefix=["keyvault", "key_vault"],
            **kwargs,
        )

    @property
    def resource(self) -> Literal["Microsoft.KeyVault/vaults"]:
        return "Microsoft.KeyVault/vaults"

    @property
    def version(self) -> str:
        from ._types import VERSION

        return VERSION

    @classmethod
    def reference(  # type: ignore[override]  # Parameter subset and renames
        cls,
        *,
        name: Union[str, Parameter],
        resource_group: Optional[Union[str, Parameter, ResourceGroup[ResourceReference]]] = None,
    ) -> "KeyVault[ResourceReference]":
        existing = super().reference(
            name=name,
            resource_group=resource_group,
        )
        return cast(KeyVault[ResourceReference], existing)

    def _build_endpoint(self, *, config_store: Optional[Mapping[str, Any]]) -> str:
        return f"https://{self._settings['name'](config_store=config_store)}.vault.azure.net/"

    def _outputs(self, *, symbol: ResourceSymbol, suffix: str, **kwargs) -> dict[str, list[Output]]:
        outputs = super()._outputs(symbol=symbol, suffix=suffix, **kwargs)
        outputs["endpoint"].append(Output(f"AZURE_KEYVAULT_ENDPOINT{suffix}", "properties.vaultUri", symbol))
        return outputs
