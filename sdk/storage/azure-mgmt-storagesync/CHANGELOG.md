# Release History

## 2.0.0b2 (2026-07-06)

### Features Added

  - Model `CheckNameAvailabilityParameters` added property `type`
  - Model `CloudEndpoint` added property `properties`
  - Model `CloudEndpointCreateParameters` added property `properties`
  - Model `OperationResourceMetricSpecification` added property `lock_aggregation_type`
  - Model `PrivateEndpointConnection` added property `properties`
  - Model `PrivateLinkResource` added property `properties`
  - Model `RegisteredServer` added property `properties`
  - Model `RegisteredServerCreateParameters` added property `properties`
  - Model `ServerEndpoint` added property `properties`
  - Model `ServerEndpointCreateParameters` added property `properties`
  - Model `StorageSyncService` added property `properties`
  - Model `StorageSyncService` added property `identity`
  - Model `StorageSyncServiceCreateParameters` added property `identity`
  - Model `StorageSyncServiceCreateParameters` added property `properties`
  - Model `StorageSyncServiceCreateParameters` added property `id`
  - Model `StorageSyncServiceCreateParameters` added property `name`
  - Model `StorageSyncServiceCreateParameters` added property `type`
  - Model `StorageSyncServiceCreateParameters` added property `system_data`
  - Model `StorageSyncServiceUpdateParameters` added property `identity`
  - Model `StorageSyncServiceUpdateParameters` added property `properties`
  - Model `SyncGroup` added property `properties`
  - Model `Workflow` added property `properties`
  - Added model `CloudEndpointCreateParametersProperties`
  - Added model `CloudEndpointProperties`
  - Added model `ErrorAdditionalInfo`
  - Added model `ErrorDetail`
  - Added model `ErrorResponse`
  - Added model `ManagedServiceIdentity`
  - Added enum `ManagedServiceIdentityType`
  - Added model `PostBackupResponseProperties`
  - Added model `PrivateEndpointConnectionProperties`
  - Added model `PrivateLinkResourceProperties`
  - Added model `RegisteredServerCreateParametersProperties`
  - Added model `RegisteredServerProperties`
  - Added model `RegisteredServerUpdateParameters`
  - Added model `RegisteredServerUpdateProperties`
  - Added enum `ServerAuthType`
  - Added model `ServerEndpointCreateParametersProperties`
  - Added model `ServerEndpointProperties`
  - Added model `ServerEndpointProvisioningStatus`
  - Added model `ServerEndpointProvisioningStepStatus`
  - Added model `ServerEndpointUpdateProperties`
  - Added enum `ServerProvisioningStatus`
  - Added model `StorageSyncServiceCreateParametersProperties`
  - Added model `StorageSyncServiceProperties`
  - Added model `StorageSyncServiceUpdateProperties`
  - Added model `SyncGroupProperties`
  - Added enum `Type`
  - Added model `UserAssignedIdentity`
  - Added model `WorkflowProperties`
  - Model `CloudEndpointsOperations` added method `restore_heartbeat`
  - Model `RegisteredServersOperations` added method `begin_update`

### Breaking Changes

  - Deleted or renamed model `MicrosoftStorageSync`
  - Model `CloudEndpoint` deleted or renamed its instance variable `storage_account_resource_id`
  - Model `CloudEndpoint` deleted or renamed its instance variable `azure_file_share_name`
  - Model `CloudEndpoint` deleted or renamed its instance variable `storage_account_tenant_id`
  - Model `CloudEndpoint` deleted or renamed its instance variable `partnership_id`
  - Model `CloudEndpoint` deleted or renamed its instance variable `friendly_name`
  - Model `CloudEndpoint` deleted or renamed its instance variable `backup_enabled`
  - Model `CloudEndpoint` deleted or renamed its instance variable `provisioning_state`
  - Model `CloudEndpoint` deleted or renamed its instance variable `last_workflow_id`
  - Model `CloudEndpoint` deleted or renamed its instance variable `last_operation_name`
  - Model `CloudEndpoint` deleted or renamed its instance variable `change_enumeration_status`
  - Model `CloudEndpointCreateParameters` deleted or renamed its instance variable `storage_account_resource_id`
  - Model `CloudEndpointCreateParameters` deleted or renamed its instance variable `azure_file_share_name`
  - Model `CloudEndpointCreateParameters` deleted or renamed its instance variable `storage_account_tenant_id`
  - Model `CloudEndpointCreateParameters` deleted or renamed its instance variable `friendly_name`
  - Model `PostBackupResponse` deleted or renamed its instance variable `cloud_endpoint_name`
  - Model `PrivateEndpointConnection` deleted or renamed its instance variable `private_endpoint`
  - Model `PrivateEndpointConnection` deleted or renamed its instance variable `private_link_service_connection_state`
  - Model `PrivateEndpointConnection` deleted or renamed its instance variable `provisioning_state`
  - Model `PrivateLinkResource` deleted or renamed its instance variable `group_id`
  - Model `PrivateLinkResource` deleted or renamed its instance variable `required_members`
  - Model `PrivateLinkResource` deleted or renamed its instance variable `required_zone_names`
  - Model `RegisteredServer` deleted or renamed its instance variable `server_certificate`
  - Model `RegisteredServer` deleted or renamed its instance variable `agent_version`
  - Model `RegisteredServer` deleted or renamed its instance variable `agent_version_status`
  - Model `RegisteredServer` deleted or renamed its instance variable `agent_version_expiration_date`
  - Model `RegisteredServer` deleted or renamed its instance variable `server_os_version`
  - Model `RegisteredServer` deleted or renamed its instance variable `server_management_error_code`
  - Model `RegisteredServer` deleted or renamed its instance variable `last_heart_beat`
  - Model `RegisteredServer` deleted or renamed its instance variable `provisioning_state`
  - Model `RegisteredServer` deleted or renamed its instance variable `server_role`
  - Model `RegisteredServer` deleted or renamed its instance variable `cluster_id`
  - Model `RegisteredServer` deleted or renamed its instance variable `cluster_name`
  - Model `RegisteredServer` deleted or renamed its instance variable `server_id`
  - Model `RegisteredServer` deleted or renamed its instance variable `storage_sync_service_uid`
  - Model `RegisteredServer` deleted or renamed its instance variable `last_workflow_id`
  - Model `RegisteredServer` deleted or renamed its instance variable `last_operation_name`
  - Model `RegisteredServer` deleted or renamed its instance variable `discovery_endpoint_uri`
  - Model `RegisteredServer` deleted or renamed its instance variable `resource_location`
  - Model `RegisteredServer` deleted or renamed its instance variable `service_location`
  - Model `RegisteredServer` deleted or renamed its instance variable `friendly_name`
  - Model `RegisteredServer` deleted or renamed its instance variable `management_endpoint_uri`
  - Model `RegisteredServer` deleted or renamed its instance variable `monitoring_endpoint_uri`
  - Model `RegisteredServer` deleted or renamed its instance variable `monitoring_configuration`
  - Model `RegisteredServer` deleted or renamed its instance variable `server_name`
  - Model `RegisteredServerCreateParameters` deleted or renamed its instance variable `server_certificate`
  - Model `RegisteredServerCreateParameters` deleted or renamed its instance variable `agent_version`
  - Model `RegisteredServerCreateParameters` deleted or renamed its instance variable `server_os_version`
  - Model `RegisteredServerCreateParameters` deleted or renamed its instance variable `last_heart_beat`
  - Model `RegisteredServerCreateParameters` deleted or renamed its instance variable `server_role`
  - Model `RegisteredServerCreateParameters` deleted or renamed its instance variable `cluster_id`
  - Model `RegisteredServerCreateParameters` deleted or renamed its instance variable `cluster_name`
  - Model `RegisteredServerCreateParameters` deleted or renamed its instance variable `server_id`
  - Model `RegisteredServerCreateParameters` deleted or renamed its instance variable `friendly_name`
  - Model `ServerEndpoint` deleted or renamed its instance variable `server_local_path`
  - Model `ServerEndpoint` deleted or renamed its instance variable `cloud_tiering`
  - Model `ServerEndpoint` deleted or renamed its instance variable `volume_free_space_percent`
  - Model `ServerEndpoint` deleted or renamed its instance variable `tier_files_older_than_days`
  - Model `ServerEndpoint` deleted or renamed its instance variable `friendly_name`
  - Model `ServerEndpoint` deleted or renamed its instance variable `server_resource_id`
  - Model `ServerEndpoint` deleted or renamed its instance variable `provisioning_state`
  - Model `ServerEndpoint` deleted or renamed its instance variable `last_workflow_id`
  - Model `ServerEndpoint` deleted or renamed its instance variable `last_operation_name`
  - Model `ServerEndpoint` deleted or renamed its instance variable `sync_status`
  - Model `ServerEndpoint` deleted or renamed its instance variable `offline_data_transfer`
  - Model `ServerEndpoint` deleted or renamed its instance variable `offline_data_transfer_storage_account_resource_id`
  - Model `ServerEndpoint` deleted or renamed its instance variable `offline_data_transfer_storage_account_tenant_id`
  - Model `ServerEndpoint` deleted or renamed its instance variable `offline_data_transfer_share_name`
  - Model `ServerEndpoint` deleted or renamed its instance variable `cloud_tiering_status`
  - Model `ServerEndpoint` deleted or renamed its instance variable `recall_status`
  - Model `ServerEndpoint` deleted or renamed its instance variable `initial_download_policy`
  - Model `ServerEndpoint` deleted or renamed its instance variable `local_cache_mode`
  - Model `ServerEndpoint` deleted or renamed its instance variable `initial_upload_policy`
  - Model `ServerEndpoint` deleted or renamed its instance variable `server_name`
  - Model `ServerEndpointCreateParameters` deleted or renamed its instance variable `server_local_path`
  - Model `ServerEndpointCreateParameters` deleted or renamed its instance variable `cloud_tiering`
  - Model `ServerEndpointCreateParameters` deleted or renamed its instance variable `volume_free_space_percent`
  - Model `ServerEndpointCreateParameters` deleted or renamed its instance variable `tier_files_older_than_days`
  - Model `ServerEndpointCreateParameters` deleted or renamed its instance variable `friendly_name`
  - Model `ServerEndpointCreateParameters` deleted or renamed its instance variable `server_resource_id`
  - Model `ServerEndpointCreateParameters` deleted or renamed its instance variable `offline_data_transfer`
  - Model `ServerEndpointCreateParameters` deleted or renamed its instance variable `offline_data_transfer_share_name`
  - Model `ServerEndpointCreateParameters` deleted or renamed its instance variable `initial_download_policy`
  - Model `ServerEndpointCreateParameters` deleted or renamed its instance variable `local_cache_mode`
  - Model `ServerEndpointCreateParameters` deleted or renamed its instance variable `initial_upload_policy`
  - Model `ServerEndpointUpdateParameters` deleted or renamed its instance variable `cloud_tiering`
  - Model `ServerEndpointUpdateParameters` deleted or renamed its instance variable `volume_free_space_percent`
  - Model `ServerEndpointUpdateParameters` deleted or renamed its instance variable `tier_files_older_than_days`
  - Model `ServerEndpointUpdateParameters` deleted or renamed its instance variable `offline_data_transfer`
  - Model `ServerEndpointUpdateParameters` deleted or renamed its instance variable `offline_data_transfer_share_name`
  - Model `ServerEndpointUpdateParameters` deleted or renamed its instance variable `local_cache_mode`
  - Model `StorageSyncService` deleted or renamed its instance variable `incoming_traffic_policy`
  - Model `StorageSyncService` deleted or renamed its instance variable `storage_sync_service_status`
  - Model `StorageSyncService` deleted or renamed its instance variable `storage_sync_service_uid`
  - Model `StorageSyncService` deleted or renamed its instance variable `provisioning_state`
  - Model `StorageSyncService` deleted or renamed its instance variable `last_workflow_id`
  - Model `StorageSyncService` deleted or renamed its instance variable `last_operation_name`
  - Model `StorageSyncService` deleted or renamed its instance variable `private_endpoint_connections`
  - Model `StorageSyncServiceCreateParameters` deleted or renamed its instance variable `incoming_traffic_policy`
  - Model `StorageSyncServiceUpdateParameters` deleted or renamed its instance variable `incoming_traffic_policy`
  - Model `SyncGroup` deleted or renamed its instance variable `unique_id`
  - Model `SyncGroup` deleted or renamed its instance variable `sync_group_status`
  - Model `Workflow` deleted or renamed its instance variable `last_step_name`
  - Model `Workflow` deleted or renamed its instance variable `status`
  - Model `Workflow` deleted or renamed its instance variable `operation`
  - Model `Workflow` deleted or renamed its instance variable `steps`
  - Model `Workflow` deleted or renamed its instance variable `last_operation_id`
  - Model `Workflow` deleted or renamed its instance variable `command_name`
  - Model `Workflow` deleted or renamed its instance variable `created_timestamp`
  - Model `Workflow` deleted or renamed its instance variable `last_status_timestamp`
  - Deleted or renamed model `CloudEndpointArray`
  - Deleted or renamed model `OperationDisplayResource`
  - Deleted or renamed model `OperationEntityListResult`
  - Deleted or renamed model `PrivateEndpointConnectionListResult`
  - Deleted or renamed model `ProgressType`
  - Deleted or renamed model `Reason`
  - Deleted or renamed model `RegisteredServerArray`
  - Deleted or renamed model `ResourcesMoveInfo`
  - Deleted or renamed model `ServerEndpointArray`
  - Deleted or renamed model `StorageSyncServiceArray`
  - Deleted or renamed model `SubscriptionState`
  - Deleted or renamed model `SyncGroupArray`
  - Deleted or renamed model `WorkflowArray`
  - Deleted or renamed method `CloudEndpointsOperations.restoreheartbeat`
  - Deleted or renamed model `MicrosoftStorageSyncOperationsMixin`

## 1.0.1 (2026-05-14)

### Other Changes

  - Regenerated with latest code generator tool

## 2.0.0b1 (2022-10-31)

### Features Added

  - Added operation CloudEndpointsOperations.afs_share_metadata_certificate_public_keys
  - Added operation group MicrosoftStorageSyncOperationsMixin
  - Model CloudEndpoint has a new parameter change_enumeration_status
  - Model CloudEndpoint has a new parameter system_data
  - Model CloudEndpointCreateParameters has a new parameter system_data
  - Model OperationResourceMetricSpecification has a new parameter supported_aggregation_types
  - Model PrivateEndpointConnection has a new parameter system_data
  - Model PrivateLinkResource has a new parameter system_data
  - Model ProxyResource has a new parameter system_data
  - Model RegisteredServer has a new parameter system_data
  - Model RegisteredServerCreateParameters has a new parameter system_data
  - Model Resource has a new parameter system_data
  - Model ServerEndpoint has a new parameter initial_upload_policy
  - Model ServerEndpoint has a new parameter system_data
  - Model ServerEndpointBackgroundDataDownloadActivity has a new parameter started_timestamp
  - Model ServerEndpointCloudTieringStatus has a new parameter low_disk_mode
  - Model ServerEndpointCreateParameters has a new parameter initial_upload_policy
  - Model ServerEndpointCreateParameters has a new parameter system_data
  - Model ServerEndpointSyncActivityStatus has a new parameter session_minutes_remaining
  - Model StorageSyncApiError has a new parameter innererror
  - Model StorageSyncService has a new parameter system_data
  - Model SyncGroup has a new parameter system_data
  - Model SyncGroupCreateParameters has a new parameter system_data
  - Model TrackedResource has a new parameter system_data
  - Model Workflow has a new parameter system_data

### Breaking Changes

  - Model StorageSyncApiError no longer has parameter inner_error

## 1.0.0 (2021-04-07)

 - GA release

## 1.0.0b1 (2020-12-03)

This is beta preview version.

This version uses a next-generation code generator that introduces important breaking changes, but also important new features (like unified authentication and async programming).

**General breaking changes**

- Credential system has been completly revamped:

  - `azure.common.credentials` or `msrestazure.azure_active_directory` instances are no longer supported, use the `azure-identity` classes instead: https://pypi.org/project/azure-identity/
  - `credentials` parameter has been renamed `credential`

- The `config` attribute no longer exists on a client, configuration should be passed as kwarg. Example: `MyClient(credential, subscription_id, enable_logging=True)`. For a complete set of
  supported options, see the [parameters accept in init documentation of azure-core](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#available-policies)
- You can't import a `version` module anymore, use `__version__` instead
- Operations that used to return a `msrest.polling.LROPoller` now returns a `azure.core.polling.LROPoller` and are prefixed with `begin_`.
- Exceptions tree have been simplified and most exceptions are now `azure.core.exceptions.HttpResponseError` (`CloudError` has been removed).
- Most of the operation kwarg have changed. Some of the most noticeable:

  - `raw` has been removed. Equivalent feature can be found using `cls`, a callback that will give access to internal HTTP response for advanced user
  - For a complete set of
  supported options, see the [parameters accept in Request documentation of azure-core](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#available-policies)

**General new features**

- Type annotations support using `typing`. SDKs are mypy ready.
- This client has now stable and official support for async. Check the `aio` namespace of your package to find the async client.
- This client now support natively tracing library like OpenCensus or OpenTelemetry. See this [tracing quickstart](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/core/azure-core-tracing-opentelemetry) for an overview.

## 0.2.0 (2020-01-09)

**Features**

  - Model ServerEndpoint has a new parameter recall_status
  - Model ServerEndpoint has a new parameter cloud_tiering_status
  - Model CloudEndpointCreateParameters has a new parameter
    friendly_name
  - Added operation CloudEndpointsOperations.trigger_change_detection
  - Added operation group OperationStatusOperations

**General Breaking Changes**

This version uses a next-generation code generator that might introduce
breaking changes if from some import. In summary, some modules were
incorrectly visible/importable and have been renamed. This fixed several
issues caused by usage of classes that were not supposed to be used in
the first place. StorageSyncManagementClient cannot be imported from
azure.mgmt.storagesync.storage_sync_management_client anymore (import
from azure.mgmt.storagesync works like before)
StorageSyncManagementClientConfiguration import has been moved from
azure.mgmt.storagesync.storage_sync_management_client to
azure.mgmt.storagesync A model MyClass from a "models" sub-module cannot
be imported anymore using azure.mgmt.storagesync.models.my_class
(import from azure.mgmt.storagesync.models works like before) An
operation class MyClassOperations from an operations sub-module cannot
be imported anymore using
azure.mgmt.storagesync.operations.my_class_operations (import from
azure.mgmt.storagesync.operations works like before) Last but not least,
HTTP connection pooling is now enabled by default. You should always use
a client as a context manager, or call close(), or use no more than one
client per process.

## 0.1.0 (2019-04-05)

  - Initial Release
