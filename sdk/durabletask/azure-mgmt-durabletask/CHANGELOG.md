# Release History

## 1.2.0b1 (2026-10-20)

### Features Added

  - Client `DurableTaskMgmtClient` added operation group `detectors`
  - Client `DurableTaskMgmtClient` added operation group `failover_instances`
  - Client `DurableTaskMgmtClient` added operation group `task_queues`
  - Client `DurableTaskMgmtClient` added operation group `transparent_data_encryptions`
  - Model `Scheduler` added property `identity`
  - Model `SchedulerUpdate` added property `identity`
  - Model `TaskHubProperties` added property `capabilities`
  - Added model `Detector`
  - Added model `DetectorDataset`
  - Added model `DetectorMetadata`
  - Added model `DetectorProperties`
  - Added model `DetectorRenderingProperties`
  - Added enum `DetectorRenderingType`
  - Added model `DetectorStatus`
  - Added enum `DetectorStatusId`
  - Added model `DetectorTable`
  - Added model `DetectorTableColumn`
  - Added enum `DetectorType`
  - Added model `FailoverInstance`
  - Added model `FailoverInstanceProperties`
  - Added enum `FailoverState`
  - Added model `ManagedServiceIdentity`
  - Added enum `ManagedServiceIdentityType`
  - Added enum `ReplicationRole`
  - Added model `TaskQueue`
  - Added model `TaskQueueProperties`
  - Added model `TaskQueueThroughput`
  - Added model `TaskQueueUpdate`
  - Added model `TransparentDataEncryption`
  - Added enum `TransparentDataEncryptionKeySource`
  - Added model `TransparentDataEncryptionProperties`
  - Added model `UserAssignedIdentity`
  - Operation group `SchedulersOperations` added method `restart`
  - Added operation group `DetectorsOperations`
  - Added operation group `FailoverInstancesOperations`
  - Added operation group `TaskQueuesOperations`
  - Added operation group `TransparentDataEncryptionsOperations`

## 1.1.0 (2026-03-09)

### Features Added

  - Model `SchedulerProperties` added property `public_network_access`
  - Model `SchedulerProperties` added property `private_endpoint_connections`
  - Model `SchedulerPropertiesUpdate` added property `public_network_access`
  - Added model `OptionalPropertiesUpdateableProperties`
  - Added model `PrivateEndpoint`
  - Added model `PrivateEndpointConnection`
  - Added model `PrivateEndpointConnectionProperties`
  - Added enum `PrivateEndpointConnectionProvisioningState`
  - Added model `PrivateEndpointConnectionUpdate`
  - Added enum `PrivateEndpointServiceConnectionStatus`
  - Added model `PrivateLinkResourceProperties`
  - Added model `PrivateLinkServiceConnectionState`
  - Added enum `PublicNetworkAccess`
  - Added model `SchedulerPrivateLinkResource`
  - Operation group `SchedulersOperations` added method `begin_create_or_update_private_endpoint_connection`
  - Operation group `SchedulersOperations` added method `begin_delete_private_endpoint_connection`
  - Operation group `SchedulersOperations` added method `begin_update_private_endpoint_connection`
  - Operation group `SchedulersOperations` added method `get_private_endpoint_connection`
  - Operation group `SchedulersOperations` added method `get_private_link`
  - Operation group `SchedulersOperations` added method `list_private_endpoint_connections`
  - Operation group `SchedulersOperations` added method `list_private_links`

## 1.0.0 (2025-09-25)

### Features Added

  - Model `DurableTaskMgmtClient` added parameter `cloud_setting` in method `__init__`
  - Added enum `SchedulerSkuName`

## 1.0.0b2 (2025-04-24)

### Features Added

  - Client `DurableTaskMgmtClient` added operation group `retention_policies`
  - Added enum `PurgeableOrchestrationState`
  - Added model `RetentionPolicy`
  - Added model `RetentionPolicyDetails`
  - Added model `RetentionPolicyProperties`
  - Added operation group `RetentionPoliciesOperations`

## 1.0.0b1 (2025-03-25)

### Other Changes

  - Initial version
