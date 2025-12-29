# Release History

## 3.0.0 (2025-10-15)

### Features Added

  - Model `OracleDatabaseMgmtClient` added parameter `cloud_setting` in method `__init__`
  - Client `OracleDatabaseMgmtClient` added operation group `network_anchors`
  - Client `OracleDatabaseMgmtClient` added operation group `resource_anchors`
  - Client `OracleDatabaseMgmtClient` added operation group `db_systems`
  - Client `OracleDatabaseMgmtClient` added operation group `db_versions`
  - Model `CloudExadataInfrastructureProperties` added property `exascale_config`
  - Model `CloudVmClusterProperties` added property `exascale_db_storage_vault_id`
  - Model `CloudVmClusterProperties` added property `storage_management_type`
  - Model `DbSystemShapeProperties` added property `shape_attributes`
  - Model `ExadbVmClusterProperties` added property `shape_attribute`
  - Model `ExascaleDbStorageVaultProperties` added property `exadata_infrastructure_id`
  - Model `ExascaleDbStorageVaultProperties` added property `attached_shape_attributes`
  - Added model `AutonomousDatabaseLifecycleAction`
  - Added enum `AutonomousDatabaseLifecycleActionEnum`
  - Added enum `BaseDbSystemShapes`
  - Added model `ConfigureExascaleCloudExadataInfrastructureDetails`
  - Added model `DbSystem`
  - Added model `DbSystemBaseProperties`
  - Added enum `DbSystemDatabaseEditionType`
  - Added enum `DbSystemLifecycleState`
  - Added model `DbSystemOptions`
  - Added model `DbSystemProperties`
  - Added enum `DbSystemSourceType`
  - Added model `DbSystemUpdate`
  - Added model `DbSystemUpdateProperties`
  - Added model `DbVersion`
  - Added model `DbVersionProperties`
  - Added enum `DiskRedundancyType`
  - Added model `DnsForwardingRule`
  - Added enum `ExadataVmClusterStorageManagementType`
  - Added model `ExascaleConfigDetails`
  - Added model `NetworkAnchor`
  - Added model `NetworkAnchorProperties`
  - Added model `NetworkAnchorUpdate`
  - Added model `NetworkAnchorUpdateProperties`
  - Added model `ResourceAnchor`
  - Added model `ResourceAnchorProperties`
  - Added model `ResourceAnchorUpdate`
  - Added enum `ShapeAttribute`
  - Added enum `ShapeFamilyType`
  - Added enum `StorageManagementType`
  - Added enum `StorageVolumePerformanceMode`
  - Model `AutonomousDatabasesOperations` added method `begin_action`
  - Model `CloudExadataInfrastructuresOperations` added method `begin_configure_exascale`
  - Model `DbSystemShapesOperations` added parameter `shape_attribute` in method `list_by_location`
  - Model `GiVersionsOperations` added parameter `shape_attribute` in method `list_by_location`
  - Added operation group `DbSystemsOperations`
  - Added operation group `DbVersionsOperations`
  - Added operation group `NetworkAnchorsOperations`
  - Added operation group `ResourceAnchorsOperations`

### Breaking Changes

  - Deleted or renamed client operation group `OracleDatabaseMgmtClient.list_actions`
  - Model `AutonomousDatabaseBaseProperties` renamed its instance variable `scheduled_operations` to `scheduled_operations_list`
  - Model `AutonomousDatabaseCloneProperties` renamed its instance variable `scheduled_operations` to `scheduled_operations_list`
  - Model `AutonomousDatabaseCrossRegionDisasterRecoveryProperties` renamed its instance variable `scheduled_operations` to `scheduled_operations_list`
  - Model `AutonomousDatabaseFromBackupTimestampProperties` renamed its instance variable `scheduled_operations` to `scheduled_operations_list`
  - Model `AutonomousDatabaseProperties` renamed its instance variable `scheduled_operations` to `scheduled_operations_list`
  - Model `AutonomousDatabaseUpdateProperties` renamed its instance variable `scheduled_operations` to `scheduled_operations_list`
  - Deleted or renamed operation group `ListActionsOperations`

## 2.0.0 (2025-06-05)

### Features Added

  - Client `OracleDatabaseMgmtClient` added operation group `list_actions`
  - Client `OracleDatabaseMgmtClient` added operation group `gi_minor_versions`
  - Client `OracleDatabaseMgmtClient` added operation group `flex_components`
  - Client `OracleDatabaseMgmtClient` added operation group `exadb_vm_clusters`
  - Client `OracleDatabaseMgmtClient` added operation group `exascale_db_nodes`
  - Client `OracleDatabaseMgmtClient` added operation group `exascale_db_storage_vaults`
  - Model `AutonomousDatabaseBaseProperties` added property `time_disaster_recovery_role_changed`
  - Model `AutonomousDatabaseBaseProperties` added property `remote_disaster_recovery_configuration`
  - Model `AutonomousDatabaseCloneProperties` added property `time_disaster_recovery_role_changed`
  - Model `AutonomousDatabaseCloneProperties` added property `remote_disaster_recovery_configuration`
  - Model `AutonomousDatabaseProperties` added property `time_disaster_recovery_role_changed`
  - Model `AutonomousDatabaseProperties` added property `remote_disaster_recovery_configuration`
  - Model `CloudExadataInfrastructureProperties` added property `defined_file_system_configuration`
  - Model `CloudExadataInfrastructureProperties` added property `database_server_type`
  - Model `CloudExadataInfrastructureProperties` added property `storage_server_type`
  - Model `CloudExadataInfrastructureProperties` added property `compute_model`
  - Model `CloudVmClusterProperties` added property `file_system_configuration_details`
  - Model `CloudVmClusterProperties` added property `compute_model`
  - Model `CloudVmClusterUpdateProperties` added property `file_system_configuration_details`
  - Enum `DataBaseType` added member `CLONE_FROM_BACKUP_TIMESTAMP`
  - Enum `DataBaseType` added member `CROSS_REGION_DISASTER_RECOVERY`
  - Model `DbServerProperties` added property `compute_model`
  - Model `DbSystemShapeProperties` added property `shape_name`
  - Model `DbSystemShapeProperties` added property `compute_model`
  - Model `DbSystemShapeProperties` added property `are_server_types_supported`
  - Model `DbSystemShapeProperties` added property `display_name`
  - Model `OracleSubscriptionProperties` added property `azure_subscription_ids`
  - Model `OracleSubscriptionProperties` added property `add_subscription_operation_state`
  - Model `OracleSubscriptionProperties` added property `last_operation_status_detail`
  - Model `PeerDbDetails` added property `peer_db_ocid`
  - Model `PeerDbDetails` added property `peer_db_location`
  - Added enum `AddSubscriptionOperationState`
  - Added model `AutonomousDatabaseCrossRegionDisasterRecoveryProperties`
  - Added model `AutonomousDatabaseFromBackupTimestampProperties`
  - Added model `AzureSubscriptions`
  - Added model `DbActionResponse`
  - Added model `DbNodeDetails`
  - Added model `DefinedFileSystemConfiguration`
  - Added model `DisasterRecoveryConfigurationDetails`
  - Added model `ExadbVmCluster`
  - Added enum `ExadbVmClusterLifecycleState`
  - Added model `ExadbVmClusterProperties`
  - Added model `ExadbVmClusterStorageDetails`
  - Added model `ExadbVmClusterUpdate`
  - Added model `ExadbVmClusterUpdateProperties`
  - Added model `ExascaleDbNode`
  - Added model `ExascaleDbNodeProperties`
  - Added model `ExascaleDbStorageDetails`
  - Added model `ExascaleDbStorageInputDetails`
  - Added model `ExascaleDbStorageVault`
  - Added enum `ExascaleDbStorageVaultLifecycleState`
  - Added model `ExascaleDbStorageVaultProperties`
  - Added model `ExascaleDbStorageVaultTagsUpdate`
  - Added model `FileSystemConfigurationDetails`
  - Added model `FlexComponent`
  - Added model `FlexComponentProperties`
  - Added model `GiMinorVersion`
  - Added model `GiMinorVersionProperties`
  - Added enum `GridImageType`
  - Added enum `HardwareType`
  - Added model `RemoveVirtualMachineFromExadbVmClusterDetails`
  - Added enum `ShapeFamily`
  - Added enum `SystemShapes`
  - Model `AutonomousDatabaseBackupsOperations` added method `list_by_parent`
  - Model `AutonomousDatabasesOperations` added method `begin_change_disaster_recovery_configuration`
  - Model `DbNodesOperations` added method `list_by_parent`
  - Model `DbServersOperations` added method `list_by_parent`
  - Model `DbSystemShapesOperations` added parameter `zone` in method `list_by_location`
  - Model `GiVersionsOperations` added parameter `shape` in method `list_by_location`
  - Model `GiVersionsOperations` added parameter `zone` in method `list_by_location`
  - Model `OracleSubscriptionsOperations` added method `begin_add_azure_subscriptions`
  - Model `VirtualNetworkAddressesOperations` added method `list_by_parent`
  - Added operation group `ExadbVmClustersOperations`
  - Added operation group `ExascaleDbNodesOperations`
  - Added operation group `ExascaleDbStorageVaultsOperations`
  - Added operation group `FlexComponentsOperations`
  - Added operation group `GiMinorVersionsOperations`
  - Added operation group `ListActionsOperations`

### Breaking Changes

  - This version introduces new hybrid models which have dual dictionary and model nature. And please follow https://aka.ms/azsdk/python/migrate/hybrid-models for migration.
  - Deleted or renamed model `UpdateAction`
  - Deleted or renamed model `ValidationError`
  - Deleted or renamed model `ValidationResult`
  - Deleted or renamed model `ValidationStatus`
  - Deleted or renamed method `AutonomousDatabaseBackupsOperations.list_by_autonomous_database`
  - Deleted or renamed method `DbNodesOperations.list_by_cloud_vm_cluster`
  - Deleted or renamed method `DbServersOperations.list_by_cloud_exadata_infrastructure`
  - Deleted or renamed method `VirtualNetworkAddressesOperations.list_by_cloud_vm_cluster`

## 1.0.0 (2024-07-04)

### Other Changes

  - First GA

## 1.0.0b2 (2024-06-21)

### Features Added

  - Added operation AutonomousDatabasesOperations.begin_restore
  - Added operation AutonomousDatabasesOperations.begin_shrink
  - Added operation group SystemVersionsOperations
  - Model AutonomousDatabaseBackupProperties has a new parameter autonomous_database_ocid
  - Model AutonomousDatabaseBackupProperties has a new parameter backup_type
  - Model AutonomousDatabaseBackupProperties has a new parameter database_size_in_tbs
  - Model AutonomousDatabaseBackupProperties has a new parameter size_in_tbs
  - Model AutonomousDatabaseBackupProperties has a new parameter time_started
  - Model AutonomousDatabaseBaseProperties has a new parameter long_term_backup_schedule
  - Model AutonomousDatabaseBaseProperties has a new parameter next_long_term_backup_time_stamp
  - Model AutonomousDatabaseCloneProperties has a new parameter long_term_backup_schedule
  - Model AutonomousDatabaseCloneProperties has a new parameter next_long_term_backup_time_stamp
  - Model AutonomousDatabaseProperties has a new parameter long_term_backup_schedule
  - Model AutonomousDatabaseProperties has a new parameter next_long_term_backup_time_stamp
  - Model AutonomousDatabaseUpdateProperties has a new parameter long_term_backup_schedule

### Breaking Changes

  - Model AutonomousDatabaseBackupProperties no longer has parameter autonomous_database_id
  - Model AutonomousDatabaseBackupProperties no longer has parameter database_size_in_t_bs
  - Model AutonomousDatabaseBackupProperties no longer has parameter size_in_t_bs
  - Model AutonomousDatabaseBackupProperties no longer has parameter type

## 1.0.0b1 (2024-05-27)

* Initial Release
