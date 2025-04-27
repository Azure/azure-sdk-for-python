# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=arguments-differ

from collections import defaultdict
from typing import (
    TYPE_CHECKING,
    Dict,
    Generic,
    List,
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
    from .types import BlobServiceResource, BlobsCorsRule

    from azure.core.credentials import SupportsTokenInfo
    from azure.core.credentials_async import AsyncSupportsTokenInfo
    from azure.storage.blob import BlobServiceClient
    from azure.storage.blob.aio import BlobServiceClient as AsyncBlobServiceClient


class BlobStorageKwargs(StorageAccountKwargs, total=False):
    automatic_snapshot_policy_enabled: Union[bool, Parameter]
    """Automatic Snapshot is enabled if set to true."""
    change_feed_enabled: bool
    """The blob service properties for change feed events. Indicates whether change feed event logging is
    enabled for the Blob service.
    """
    change_feed_retention_in_days: int
    """Indicates whether change feed event logging is enabled for the Blob service. Indicates the duration of
    changeFeed retention in days. If left blank, it indicates an infinite retention of the change feed.
    """
    container_delete_retention_policy_allow_permanent_delete: bool
    """This property when set to true allows deletion of the soft deleted blob versions and snapshots. This property
    cannot be used with blob restore policy. This property only applies to blob service and does not apply to
    containers or file share.
    """
    container_delete_retention_policy_days: int
    """Indicates the number of days that the deleted item should be retained."""
    container_delete_retention_policy_enabled: bool
    """The blob service properties for container soft delete. Indicates whether DeleteRetentionPolicy is enabled."""
    cors_rules: Union[List[Union["BlobsCorsRule", Parameter]], Parameter]
    """Specifies CORS rules for the Blob service. You can include up to five CorsRule elements in the request. If no
    CorsRule elements are included in the request body, all CORS rules will be deleted, and CORS will be disabled
    for the Blob service.
    """
    default_service_version: str
    """Indicates the default version to use for requests to the Blob service if an incoming request's version is not
    specified. Possible values include version 2008-10-27 and all more recent versions.
    """
    delete_retention_policy_allow_permanent_delete: bool
    """This property when set to true allows deletion of the soft deleted blob versions and snapshots. This property
    cannot be used with blob restore policy. This property only applies to blob service and does not apply to
    containers or file share.
    """
    delete_retention_policy_days: int
    """Indicates the number of days that the deleted blob should be retained."""
    delete_retention_policy_enabled: bool
    """The blob service properties for blob soft delete."""
    is_versioning_enabled: Union[bool, Parameter]
    """Use versioning to automatically maintain previous versions of your blobs."""
    last_access_time_tracking_policy_enabled: bool
    """The blob service property to configure last access time based tracking policy. When set to true last access
    time based tracking is enabled.
    """
    restore_policy_days: int
    """How long this blob can be restored. It should be less than DeleteRetentionPolicy days."""
    restore_policy_enabled: bool
    """The blob service properties for blob restore policy. If point-in-time restore is enabled, then versioning,
    change feed, and blob soft delete must also be enabled.
    """


_DEFAULT_BLOB_SERVICE: "BlobServiceResource" = {"name": "default"}
_DEFAULT_BLOB_SERVICE_EXTENSIONS: ExtensionResources = {
    "managed_identity_roles": ["Storage Blob Data Contributor"],
    "user_roles": ["Storage Blob Data Contributor"],
}
BlobServiceResourceType = TypeVar("BlobServiceResourceType", bound=Mapping[str, Any], default="BlobServiceResource")
ClientType = TypeVar("ClientType", default="BlobServiceClient")


class BlobStorage(_ClientResource, Generic[BlobServiceResourceType]):
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
            # TODO: Finish full typing
            if "automatic_snapshot_policy_enabled" in kwargs:
                properties["properties"]["automaticSnapshotPolicyEnabled"] = kwargs.pop(
                    "automatic_snapshot_policy_enabled"
                )
            # if 'change_feed_enabled' in kwargs:
            #     properties['changeFeedEnabled'] = kwargs.pop('change_feed_enabled')
            # if 'change_feed_retention_in_days' in kwargs:
            #     properties['changeFeedRetentionInDays'] = kwargs.pop('change_feed_retention_in_days')
            # if 'container_delete_retention_policy_allow_permanent_delete' in kwargs:
            # properties['containerDeleteRetentionPolicyAllowPermanentDelete'] = kwargs.pop(
            #     'container_delete_retention_policy_allow_permanent_delete'
            # )
            # if 'container_delete_retention_policy_days' in kwargs:
            #     properties['containerDeleteRetentionPolicyDays']=kwargs.pop('container_delete_retention_policy_days')
            # if 'container_delete_retention_policy_enabled' in kwargs:
            # properties['containerDeleteRetentionPolicyEnabled'] = kwargs.pop(
            #     'container_delete_retention_policy_enabled'
            # )
            if "cors_rules" in kwargs:
                properties["properties"]["cors"] = {"corsRules": kwargs.pop("cors_rules")}
            # if 'default_service_version' in kwargs:
            #     properties['defaultServiceVersion'] = kwargs.pop('default_service_version')
            # if 'delete_retention_policy_allow_permanent_delete' in kwargs:
            # properties['deleteRetentionPolicyAllowPermanentDelete'] = kwargs.pop(
            #     'delete_retention_policy_allow_permanent_delete'
            # )
            # if 'delete_retention_policy_days' in kwargs:
            #     blob_service_params['deleteRetentionPolicyDays'] = kwargs.pop('delete_retention_policy_days')
            # if 'delete_retention_policy_enabled' in kwargs:
            #     blob_service_params['deleteRetentionPolicyEnabled'] = kwargs.pop('delete_retention_policy_enabled')
            # if 'diagnostic_settings' in kwargs:
            #     blob_service_params['diagnosticSettings'] = kwargs.pop('diagnostic_settings')
            if "is_versioning_enabled" in kwargs:
                properties["properties"]["isVersioningEnabled"] = kwargs.pop("is_versioning_enabled")
            # if 'last_access_time_tracking_policy_enabled' in kwargs:
            # properties['lastAccessTimeTrackingPolicyEnabled'] = kwargs.pop(
            #     'last_access_time_tracking_policy_enabled'
            # )
            # if 'restore_policy_days' in kwargs:
            #     blob_service_params['restorePolicyDays'] = kwargs.pop('restore_policy_days')
            # if 'restore_policy_enabled' in kwargs:
            #     blob_service_params['restorePolicyEnabled'] = kwargs.pop('restore_policy_enabled')

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
        from .types import VERSION

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
    ) -> Dict[str, List[Output]]:
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
