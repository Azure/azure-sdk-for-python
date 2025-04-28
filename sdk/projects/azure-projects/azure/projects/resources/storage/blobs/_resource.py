# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=arguments-differ

from collections import defaultdict
from typing import (
    TYPE_CHECKING,
    Generic,
    Literal,
    Mapping,
    Tuple,
    Type,
    Union,
    Optional,
    Any,
    cast,
    overload,
)
from typing_extensions import TypeVar, Unpack

from ...._component import ComponentField
from ..._identifiers import ResourceIdentifiers
from ...resourcegroup import ResourceGroup
from ...._bicep.expressions import Output, Parameter, ResourceSymbol
from ...._resource import _ClientResource, ExtensionResources, ResourceReference
from .._resource import StorageAccount, StorageAccountKwargs

if TYPE_CHECKING:
    from ._types import BlobServiceResource, BlobServiceCorsRule

    from azure.core.credentials import SupportsTokenInfo
    from azure.core.credentials_async import AsyncSupportsTokenInfo
    from azure.storage.blob import BlobServiceClient
    from azure.storage.blob.aio import BlobServiceClient as AsyncBlobServiceClient


class BlobStorageKwargs(StorageAccountKwargs, total=False):
    automatic_snapshot_policy_enabled: Union[bool, Parameter]
    """Automatic Snapshot is enabled if set to true."""
    cors_rules: Union[list[Union["BlobServiceCorsRule", Parameter]], Parameter]
    """Specifies CORS rules for the Blob service. You can include up to five CorsRule elements in the request. If no
    CorsRule elements are included in the request body, all CORS rules will be deleted, and CORS will be disabled
    for the Blob service.
    """
    default_service_version: str
    """Indicates the default version to use for requests to the Blob service if an incoming request's version is not
    specified. Possible values include version 2008-10-27 and all more recent versions.
    """
    is_versioning_enabled: Union[bool, Parameter]
    """Use versioning to automatically maintain previous versions of your blobs."""


_DEFAULT_BLOB_SERVICE: "BlobServiceResource" = {"name": "default"}
_DEFAULT_BLOB_SERVICE_EXTENSIONS: ExtensionResources = {
    "managed_identity_roles": ["Storage Blob Data Contributor"],
    "user_roles": ["Storage Blob Data Contributor"],
}
BlobServiceResourceType = TypeVar("BlobServiceResourceType", bound=Mapping[str, Any], default="BlobServiceResource")
ClientType = TypeVar("ClientType", default="BlobServiceClient")


class BlobStorage(_ClientResource, Generic[BlobServiceResourceType]):
    """Azure Storage Blob Service resource that manages blob storage configuration and access.

    :param properties: Optional properties for configuring the blob service.
    :type properties: BlobServiceResource | None
    :param account: The storage account name, parameter, field reference or StorageAccount instance.
    :type account: str | Parameter | ComponentField | StorageAccount | None

    :keyword automatic_snapshot_policy_enabled: Enables automatic snapshot creation for the blob service
    :paramtype automatic_snapshot_policy_enabled: bool | Parameter
    :keyword cors_rules: CORS rules for the Blob service (up to 5 rules)
    :paramtype cors_rules: List[BlobServiceCorsRule | Parameter] | Parameter
    :keyword default_service_version: Default API version for Blob service requests
    :paramtype default_service_version: str
    :keyword is_versioning_enabled: Enable blob versioning
    :paramtype is_versioning_enabled: bool | Parameter
    :keyword access_tier: Storage tier for billing. Required for BlobStorage accounts
    :paramtype access_tier: Literal["Cool", "Hot", "Premium"] | Parameter
    :keyword enable_hierarchical_namespace: Enable hierarchical namespace. Required for SFTP or NFS v3
    :paramtype enable_hierarchical_namespace: bool | Parameter
    :keyword allow_blob_public_access: Enable/disable public access for blobs/containers
    :paramtype allow_blob_public_access: bool | Parameter
    :keyword allow_cross_tenant_replication: Allow/disallow cross AAD tenant object replication
    :paramtype allow_cross_tenant_replication: bool | Parameter
    :keyword allowed_copy_scope: Restrict copy scope to AAD tenant or Private Links
    :paramtype allowed_copy_scope: Literal["AAD", "PrivateLink"] | Parameter
    :keyword allow_shared_key_access: Allow requests to be authorized with account access key
    :paramtype allow_shared_key_access: bool | Parameter
    :keyword azure_files_identity_auth: Identity based authentication settings for Azure Files
    :paramtype azure_files_identity_auth: AzureFilesIdentityBasedAuthentication | Parameter
    :keyword default_to_oauth_authentication: Set OAuth as default authentication
    :paramtype default_to_oauth_authentication: bool | Parameter
    :keyword dns_endpoint_type: Type of DNS endpoint
    :paramtype dns_endpoint_type: Literal["AzureDnsZone", "Standard"] | Parameter
    :keyword enable_nfs_v3: Enable NFS 3.0 support
    :paramtype enable_nfs_v3: bool | Parameter
    :keyword enable_sftp: Enable SFTP support
    :paramtype enable_sftp: bool | Parameter
    :keyword encryption: Server-side encryption settings
    :paramtype encryption: StorageEncryption | Parameter
    :keyword is_local_user_enabled: Enable local users feature
    :paramtype is_local_user_enabled: bool | Parameter
    :keyword kind: Type of Storage Account
    :paramtype kind: Literal["BlobStorage", "BlockBlobStorage", "FileStorage", "Storage", "StorageV2"] | Parameter
    :keyword large_file_shares_state: Enable/disable large file shares
    :paramtype large_file_shares_state: Literal["Disabled", "Enabled"] | Parameter
    :keyword location: Azure region location
    :paramtype location: str | Parameter
    :keyword managed_identities: Managed identity configuration
    :paramtype managed_identities: ManagedIdentity | None
    :keyword minimum_tls_version: Minimum TLS version
    :paramtype minimum_tls_version: Literal["TLS1_2", "TLS1_3"] | Parameter
    :keyword network_acls: Network access rules configuration
    :paramtype network_acls: StorageNetworkRuleSet | Parameter
    :keyword public_network_access: Public network access configuration
    :paramtype public_network_access: Literal["Disabled", "Enabled", "SecuredByPerimeter"] | Parameter
    :keyword sas_expiration_period: SAS token expiration period (DD.HH:MM:SS)
    :paramtype sas_expiration_period: str | Parameter
    :keyword sku: Storage Account SKU
    :paramtype sku: Literal["Premium_LRS", "Premium_ZRS", "Standard_GRS", "Standard_GZRS", "Standard_LRS", "Standard_RAGRS", "Standard_RAGZRS", "Standard_ZRS"] | Parameter
    :keyword supports_https_traffic_only: Allow only HTTPS traffic
    :paramtype supports_https_traffic_only: bool | Parameter
    :keyword tags: Resource tags
    :paramtype tags: Dict[str, str | Parameter] | Parameter

    :ivar DEFAULTS: Default configuration for blob service.
    :vartype DEFAULTS: BlobServiceResource
    :ivar DEFAULT_EXTENSIONS: Default role assignments for managed identities and users.
    :vartype DEFAULT_EXTENSIONS: ExtensionResources
    :ivar properties: Properties specific to this blob service instance.
    :vartype properties: BlobServiceResourceType
    :ivar parent: The parent storage account for this blob service.
    :vartype parent: StorageAccount
    :ivar endpoints: The service endpoints from the parent resource.
    :vartype endpoints: Dict[str, str]
    :ivar extensions: Extension resources like role assignments.
    :vartype extensions: ExtensionResources
    :ivar settings: Configuration settings for the resource.
    :vartype settings: Dict[str, Setting]
    """
    DEFAULTS: "BlobServiceResource" = _DEFAULT_BLOB_SERVICE  # type: ignore[assignment]
    DEFAULT_EXTENSIONS: ExtensionResources = _DEFAULT_BLOB_SERVICE_EXTENSIONS
    properties: BlobServiceResourceType
    parent: StorageAccount  # type: ignore[reportIncompatibleVariableOverride]

    def __init__(
        self,
        properties: Optional["BlobServiceResource"] = None,
        /,
        account: Optional[Union[str, Parameter, ComponentField, StorageAccount]] = None,
        **kwargs: Unpack["BlobStorageKwargs"],
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
            if "automatic_snapshot_policy_enabled" in kwargs:
                properties["properties"]["automaticSnapshotPolicyEnabled"] = kwargs.pop(
                    "automatic_snapshot_policy_enabled"
                )
            if "cors_rules" in kwargs:
                properties["properties"]["cors"] = {"corsRules": kwargs.pop("cors_rules")}
            if "default_service_version" in kwargs:
                properties["properties"]["defaultServiceVersion"] = kwargs.pop("default_service_version")
            if "is_versioning_enabled" in kwargs:
                properties["properties"]["isVersioningEnabled"] = kwargs.pop("is_versioning_enabled")

        if account and "parent" in kwargs:
            raise ValueError("Cannot specify both 'account' and 'parent'.")
        # 'parent' is passed by the reference classmethod.
        parent = kwargs.pop("parent", None)  # type: ignore[typeddict-item]
        if not parent:
            if isinstance(account, StorageAccount):
                parent = account
            else:
                # Blobs kwargs have already been popped.
                parent = StorageAccount(name=account, **kwargs)  # type: ignore[misc]
                for key in StorageAccountKwargs.__annotations__:
                    kwargs.pop(key, None)  # type: ignore[misc]  # Not using string literal key.
        super().__init__(
            properties,
            existing=existing,
            parent=parent,
            subresource="blobServices",
            service_prefix=["blobs", "storage"],
            identifier=ResourceIdentifiers.blob_storage,
            **kwargs,
        )

    @property
    def resource(self) -> Literal["Microsoft.Storage/storageAccounts/blobServices"]:
        return "Microsoft.Storage/storageAccounts/blobServices"

    @property
    def version(self) -> str:
        from ._types import VERSION

        return VERSION

    @classmethod
    def reference(  # type: ignore[override]  # Parameter subset and renames
        cls,
        *,
        account: Union[str, Parameter, StorageAccount[ResourceReference]],
        resource_group: Optional[Union[str, Parameter, ResourceGroup[ResourceReference]]] = None,
    ) -> "BlobStorage[ResourceReference]":
        parent: Optional[StorageAccount[ResourceReference]] = None
        if isinstance(account, (str, Parameter)):
            parent = StorageAccount.reference(
                name=account,
                resource_group=resource_group,
            )
        elif isinstance(account, StorageAccount) and resource_group:
            raise ValueError("Cannot provide a 'StorageAccount' instance with 'resource_group' value.")
        else:
            parent = account
        existing = super().reference(parent=parent)
        existing._settings["name"].set_value("default")  # pylint: disable=protected-access
        return cast(BlobStorage[ResourceReference], existing)

    def __repr__(self) -> str:
        name = f'\'{self.parent.properties["name"]}\'' if "name" in self.parent.properties else "<default>"
        return f"{self.__class__.__name__}({name})"

    def _build_symbol(self, suffix: Optional[Union[str, Parameter]]) -> ResourceSymbol:
        return super()._build_symbol(self.parent.properties.get("name"))

    def _get_default_name(self, *, config_store: Optional[Mapping[str, Any]]) -> str:  # pylint: disable=unused-argument
        return "default"

    def _build_endpoint(self, *, config_store: Optional[Mapping[str, Any]]) -> str:
        return f"https://{self.parent._settings['name'](config_store=config_store)}.blob.core.windows.net/"  # pylint: disable=protected-access

    def _outputs(  # type: ignore[override]  # Parameter subset
        self, *, parents: Tuple[ResourceSymbol, ...], suffix: str, **kwargs
    ) -> dict[str, list[Output]]:
        return {
            "endpoint": [
                Output(
                    f"AZURE_BLOBS_ENDPOINT{suffix}",
                    "properties.primaryEndpoints.blob",
                    parents[0],
                )
            ]
        }

    @overload
    def get_client(
        self,
        /,
        *,
        transport: Any = None,
        credential: Any = None,
        api_version: Optional[str] = None,
        audience: Optional[str] = None,
        config_store: Optional[Mapping[str, Any]] = None,
        use_async: Optional[Literal[False]] = None,
        **client_options,
    ) -> "BlobServiceClient": ...
    @overload
    def get_client(
        self,
        /,
        *,
        transport: Any = None,
        credential: Any = None,
        api_version: Optional[str] = None,
        audience: Optional[str] = None,
        config_store: Optional[Mapping[str, Any]] = None,
        use_async: Literal[True],
        **client_options,
    ) -> "AsyncBlobServiceClient": ...
    @overload
    def get_client(
        self,
        cls: Type[ClientType],
        /,
        *,
        transport: Any = None,
        credential: Any = None,
        api_version: Optional[str] = None,
        audience: Optional[str] = None,
        config_store: Optional[Mapping[str, Any]] = None,
        use_async: Optional[bool] = None,
        return_credential: Literal[False] = False,
        **client_options,
    ) -> ClientType: ...
    @overload
    def get_client(
        self,
        cls: Type[ClientType],
        /,
        *,
        transport: Any = None,
        credential: Any = None,
        api_version: Optional[str] = None,
        audience: Optional[str] = None,
        config_store: Optional[Mapping[str, Any]] = None,
        use_async: Optional[bool] = None,
        return_credential: Literal[True],
        **client_options,
    ) -> Tuple[ClientType, Union["SupportsTokenInfo", "AsyncSupportsTokenInfo"]]: ...
    def get_client(
        self,
        cls=None,
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
        if cls is None:
            if use_async:
                from azure.storage.blob.aio import BlobServiceClient as AsyncBlobServiceClient

                cls = AsyncBlobServiceClient
            else:
                from azure.storage.blob import BlobServiceClient as SyncBlobServiceClient

                cls = SyncBlobServiceClient
                use_async = False
        return super().get_client(
            cls,
            transport=transport,
            credential=credential,
            api_version=api_version,
            audience=audience,
            config_store=config_store,
            use_async=use_async,
            return_credential=return_credential,
            **client_options,
        )
