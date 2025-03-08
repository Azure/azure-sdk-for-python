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
    Dict,
    List,
    Literal,
    Mapping,
    Union,
    Optional,
)
from typing_extensions import TypeVar, Unpack, TypedDict

from ..resourcegroup import ResourceGroup
from .._identifiers import ResourceIdentifiers
from .._extension import RoleAssignment
from ..._parameters import GLOBAL_PARAMS
from ..._bicep.expressions import Output, ResourceSymbol, Parameter
from ..._resource import _ClientResource, ResourceReference, ExtensionResources

if TYPE_CHECKING:
    from .types import KeyVaultResource, KeyVaultNetworkRuleSet


class KeyVaultKwargs(TypedDict, total=False):
    access_policies: Union[List[Union["AccessPolicy", Parameter]], Parameter]
    """All access policies to create."""
    create_mode: Union[Literal["default", "recover"], Parameter]
    """The vault's create mode to indicate whether the vault need to be recovered or not. - recover or default."""
    # diagnostic_settings: List['DiagnosticSetting']
    # """The diagnostic settings of the service."""
    enable_purge_protection: Union[bool, Parameter]
    """Provide 'true' to enable Key Vault's purge protection feature."""
    enable_rbac_authorization: Union[bool, Parameter]
    """Property that controls how data actions are authorized. When true, the key vault will use Role Based Access
    Control (RBAC) for authorization of data actions, and the access policies specified in vault properties will be
    ignored. When false, the key vault will use the access policies specified in vault properties, and any policy
    stored on Azure Resource Manager will be ignored. Note that management actions are always authorized with RBAC.
    """
    enable_soft_delete: Union[bool, Parameter]
    """Switch to enable/disable Key Vault's soft delete feature."""
    enable_vault_for_deployment: Union[bool, Parameter]
    """Specifies if the vault is enabled for deployment by script or compute."""
    enable_vault_for_disk_encryption: Union[bool, Parameter]
    """Specifies if the azure platform has access to the vault for enabling disk encryption scenarios."""
    enable_vault_for_template_deployment: Union[bool, Parameter]
    """Specifies if the vault is enabled for a template deployment."""
    location: Union[bool, Parameter]
    """Location for all resources."""
    # lock: 'Lock'
    # """The lock settings of the service."""
    network_acls: Union["KeyVaultNetworkRuleSet", Parameter]
    """A collection of rules governing the accessibility from specific network locations."""
    # private_endpoints: List['PrivateEndpoint']
    # """Configuration details for private endpoints. For security reasons, it is recommended to use private endpoints
    # whenever possible.
    # """
    public_network_access: Literal["", "Disabled", "Enabled"]
    """Whether or not public network access is allowed for this resource. For security reasons it should be disabled.
    If not specified, it will be disabled by default if private endpoints are set and networkAcls are not set.
    """
    roles: Union[
        Parameter,
        List[
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
        List[
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
    soft_delete_retention: Union[bool, Parameter]
    """softDelete data retention days. It accepts >=7 and <=90."""
    tags: Union[Dict[str, Union[str, Parameter]], Parameter]
    """Resource tags."""


KeyVaultResourceType = TypeVar("KeyVaultResourceType", default="KeyVaultResource")
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


class KeyVault(_ClientResource[KeyVaultResourceType]):
    DEFAULTS: "KeyVaultResource" = _DEFAULT_KEY_VAULT
    DEFAULT_EXTENSIONS: ExtensionResources = _DEFAULT_KEY_VAULT_EXTENSIONS
    properties: KeyVaultResourceType
    parent: None

    def __init__(
        self,
        properties: Optional["KeyVaultResource"] = None,
        /,
        name: Optional[str] = None,
        **kwargs: Unpack[KeyVaultKwargs],
    ) -> None:
        existing = kwargs.pop("existing", False)
        extensions: ExtensionResources = defaultdict(list)
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
            # TODO: Finish full typing
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
        from .types import VERSION

        return VERSION

    @classmethod
    def reference(
        cls,
        *,
        name: Union[str, Parameter],
        resource_group: Optional[Union[str, Parameter, ResourceGroup[ResourceReference]]] = None,
    ) -> "KeyVault[ResourceReference]":
        return super().reference(
            name=name,
            resource_group=resource_group,
        )

    def _build_endpoint(self, *, config_store: Mapping[str, Any]) -> str:
        return f"https://{self._settings['name'](config_store=config_store)}.vault.azure.net/"

    def _outputs(self, *, symbol: ResourceSymbol, **kwargs) -> Dict[str, Output]:
        outputs = super()._outputs(symbol=symbol, **kwargs)
        outputs["endpoint"] = Output(f"AZURE_KEYVAULT_ENDPOINT{self._suffix}", "properties.vaultUri", symbol)
        return outputs
