from typing import TYPE_CHECKING, Callable, Dict, List, Literal, Mapping, Tuple, Union, Unpack, overload, Optional, Any, Type
from typing_extensions import TypeVar
from collections import defaultdict

from ...._component import ComponentField
from ..._identifiers import ResourceIdentifiers
from ...resourcegroup import ResourceGroup
from ...._bicep.expressions import Output, Parameter, ResourceSymbol
from ...._resource import _ClientResource, ExtensionResources, ResourceReference
from .. import StorageAccount, StorageAccountKwargs

if TYPE_CHECKING:
    from .types import BlobServiceResource, BlobsCorsRule
    from azure.storage.blob import BlobServiceClient


class BlobStorageKwargs(StorageAccountKwargs):
    automatic_snapshot_policy_enabled: Union[bool, Parameter[bool]]
    """Automatic Snapshot is enabled if set to true."""
    change_feed_enabled: bool
    """The blob service properties for change feed events. Indicates whether change feed event logging is enabled for the Blob service."""
    change_feed_retention_in_days: int
    """Indicates whether change feed event logging is enabled for the Blob service. Indicates the duration of changeFeed retention in days. If left blank, it indicates an infinite retention of the change feed."""
    container_delete_retention_policy_allow_permanent_delete: bool
    """This property when set to true allows deletion of the soft deleted blob versions and snapshots. This property cannot be used with blob restore policy. This property only applies to blob service and does not apply to containers or file share."""
    container_delete_retention_policy_days: int
    """Indicates the number of days that the deleted item should be retained."""
    container_delete_retention_policy_enabled: bool
    """The blob service properties for container soft delete. Indicates whether DeleteRetentionPolicy is enabled."""
    cors_rules: Union[List[Union['BlobsCorsRule', Parameter['BlobsCorsRule']]], Parameter[List['BlobsCorsRule']]]
    """Specifies CORS rules for the Blob service. You can include up to five CorsRule elements in the request. If no CorsRule elements are included in the request body, all CORS rules will be deleted, and CORS will be disabled for the Blob service."""
    default_service_version: str
    """Indicates the default version to use for requests to the Blob service if an incoming request's version is not specified. Possible values include version 2008-10-27 and all more recent versions."""
    delete_retention_policy_allow_permanent_delete: bool
    """This property when set to true allows deletion of the soft deleted blob versions and snapshots. This property cannot be used with blob restore policy. This property only applies to blob service and does not apply to containers or file share."""
    delete_retention_policy_days: int
    """Indicates the number of days that the deleted blob should be retained."""
    delete_retention_policy_enabled: bool
    """The blob service properties for blob soft delete."""
    is_versioning_enabled: Union[bool, Parameter[bool]]
    """Use versioning to automatically maintain previous versions of your blobs."""
    last_access_time_tracking_policy_enabled: bool
    """The blob service property to configure last access time based tracking policy. When set to true last access time based tracking is enabled."""
    restore_policy_days: int
    """How long this blob can be restored. It should be less than DeleteRetentionPolicy days."""
    restore_policy_enabled: bool
    """The blob service properties for blob restore policy. If point-in-time restore is enabled, then versioning, change feed, and blob soft delete must also be enabled."""


_DEFAULT_BLOB_SERVICE: 'BlobServiceResource' = {'name': 'default'}
_DEFAULT_BLOB_SERVICE_EXTENSIONS: ExtensionResources = {
    'managed_identity_roles': ['Storage Blob Data Contributor'],
    'user_roles': ['Storage Blob Data Contributor']
}
BlobServiceResourceType = TypeVar('BlobServiceResourceType', default='BlobServiceResource')
ClientType = TypeVar("ClientType", default='BlobServiceClient')
 
 
class BlobStorage(_ClientResource[BlobServiceResourceType]):
    DEFAULTS: 'BlobServiceResource' = _DEFAULT_BLOB_SERVICE
    DEFAULT_EXTENSIONS: ExtensionResources = _DEFAULT_BLOB_SERVICE_EXTENSIONS
    resource: Literal["Microsoft.Storage/storageAccounts/blobServices"]
    properties: BlobServiceResourceType

    def __init__(
            self,
            properties: Optional['BlobServiceResource'] = None,
            /,
            account: Optional[Union[str, Parameter[str], ComponentField, StorageAccount]] = None,
            **kwargs: Unpack['BlobStorageKwargs']
    ) -> None:
        existing = kwargs.pop('existing', False)
        extensions: ExtensionResources = defaultdict(list)
        if 'roles' in kwargs:
            extensions['managed_identity_roles'] = kwargs.pop('roles')
        if 'user_roles' in kwargs:
            extensions['user_roles'] = kwargs.pop('user_roles')
        if not existing:
            properties = properties or {}
            if 'properties' not in properties:
                properties['properties'] = {}
            # TODO: Finish full typing
            if 'automatic_snapshot_policy_enabled' in kwargs:
                properties['properties']['automaticSnapshotPolicyEnabled'] = kwargs.pop('automatic_snapshot_policy_enabled')
            # if 'change_feed_enabled' in kwargs:
            #     blob_service_params['changeFeedEnabled'] = kwargs.pop('change_feed_enabled')
            # if 'change_feed_retention_in_days' in kwargs:
            #     blob_service_params['changeFeedRetentionInDays'] = kwargs.pop('change_feed_retention_in_days')
            # if 'container_delete_retention_policy_allow_permanent_delete' in kwargs:
            #     blob_service_params['containerDeleteRetentionPolicyAllowPermanentDelete'] = kwargs.pop('container_delete_retention_policy_allow_permanent_delete')
            # if 'container_delete_retention_policy_days' in kwargs:
            #     blob_service_params['containerDeleteRetentionPolicyDays'] = kwargs.pop('container_delete_retention_policy_days')
            # if 'container_delete_retention_policy_enabled' in kwargs:
            #     blob_service_params['containerDeleteRetentionPolicyEnabled'] = kwargs.pop('container_delete_retention_policy_enabled')
            if 'cors_rules' in kwargs:
                properties['properties']['cors'] = {}
                properties['properties']['cors']['corsRules'] = kwargs.pop('cors_rules')
            #     blob_service_params['corsRules'] = kwargs.pop('cors_rules')
            # if 'default_service_version' in kwargs:
            #     blob_service_params['defaultServiceVersion'] = kwargs.pop('default_service_version')
            # if 'delete_retention_policy_allow_permanent_delete' in kwargs:
            #     blob_service_params['deleteRetentionPolicyAllowPermanentDelete'] = kwargs.pop('delete_retention_policy_allow_permanent_delete')
            # if 'delete_retention_policy_days' in kwargs:
            #     blob_service_params['deleteRetentionPolicyDays'] = kwargs.pop('delete_retention_policy_days')
            # if 'delete_retention_policy_enabled' in kwargs:
            #     blob_service_params['deleteRetentionPolicyEnabled'] = kwargs.pop('delete_retention_policy_enabled')
            # if 'diagnostic_settings' in kwargs:
            #     blob_service_params['diagnosticSettings'] = kwargs.pop('diagnostic_settings')
            if 'is_versioning_enabled' in kwargs:
                properties['properties']['isVersioningEnabled'] = kwargs.pop('is_versioning_enabled')
            # if 'last_access_time_tracking_policy_enabled' in kwargs:
            #     blob_service_params['lastAccessTimeTrackingPolicyEnabled'] = kwargs.pop('last_access_time_tracking_policy_enabled')
            # if 'restore_policy_days' in kwargs:
            #     blob_service_params['restorePolicyDays'] = kwargs.pop('restore_policy_days')
            # if 'restore_policy_enabled' in kwargs:
            #     blob_service_params['restorePolicyEnabled'] = kwargs.pop('restore_policy_enabled')

        parent = kwargs.pop('parent', None)
        if account and 'parent' in kwargs:
            raise ValueError("Cannot specify both 'account' and 'parent'.")
        if not parent:
            parent = account if isinstance(account, StorageAccount) else StorageAccount(name=account, **kwargs)
            for key in StorageAccountKwargs.__optional_keys__:
                kwargs.pop(key, None)
        super().__init__(
            properties,
            extensions=extensions,
            existing=existing,
            parent=parent,
            subresource="blobServices",
            service_prefix=["blobs", "storage"],
            identifier=ResourceIdentifiers.blob_storage,
            **kwargs
        )

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

    @classmethod
    def reference(
            cls,
            *,
            account: Union[str, Parameter[str], StorageAccount, ComponentField],
            resource_group: Optional[Union[str, Parameter[str], ResourceGroup]] = None,
    ) -> 'BlobStorage[ResourceReference]':
        from .types import RESOURCE, VERSION
        resource = f"{RESOURCE}@{VERSION}"
        if isinstance(account, (str, Parameter)):
            parent = StorageAccount.reference(
                name=account,
                resource_group=resource_group,
            )
        elif isinstance(account, StorageAccount) and resource_group:
            raise ValueError("Cannot provide a 'StorageAccount' instance with 'resource_group' value.")
        else:
            parent = account
        existing = super().reference(
            resource=resource,
            parent=parent,
        )
        existing._settings['name'].set_value('default')
        return existing

    def __repr__(self) -> str:
        name = f'\'{self.parent.properties["name"]}\'' if 'name' in self.parent.properties else "<default>"
        return f"{self.__class__.__name__}({name})"

    def _build_endpoint(self, *, config_store: Mapping[str, Any]) -> str:
        return f"https://{self.parent._settings['name'](config_store=config_store)}.blob.core.windows.net/"

    def _outputs(
            self,
             *,
             parents: Tuple[ResourceSymbol, ...],
             **kwargs
    ) -> Dict[str, Output]:
        return {'endpoint': Output(f"AZURE_BLOBS_ENDPOINT{self.parent._suffix}", "properties.primaryEndpoints.blob", parents[0])}

    def get_client(
            self,
            cls: Optional[Callable[..., ClientType]] = None,
            /,
            *,
            transport: Any = None,
            api_version: Optional[str] = None,
            audience: Optional[str] = None,
            config_store: Optional[Mapping[str, Any]] = None,
            env_name: Optional[str] = None,
            use_async: Optional[bool] = None,
            **client_options,
    ) -> ClientType:
        if cls is None:
            if use_async:
                from azure.storage.blob.aio import BlobServiceClient
                cls = BlobServiceClient
            else:
                from azure.storage.blob import BlobServiceClient
                cls = BlobServiceClient
                use_async = False
        return super().get_client(
            cls,
            transport=transport,
            api_version=api_version,
            audience=audience,
            config_store=config_store,
            env_name=env_name,
            **client_options
        )
