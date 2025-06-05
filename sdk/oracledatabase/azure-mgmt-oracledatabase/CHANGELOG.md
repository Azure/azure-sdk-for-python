# Release History

## 2.0.0 (2025-06-05)

### Features Added

  - Client `OracleDatabaseMgmtClient` added method `send_request`
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
  - Added model `ExadbVmClustersOperations`
  - Added model `ExascaleDbNodesOperations`
  - Added model `ExascaleDbStorageVaultsOperations`
  - Added model `FlexComponentsOperations`
  - Added model `GiMinorVersionsOperations`
  - Added model `ListActionsOperations`

### Breaking Changes

  - Model `ActivationLinks` deleted or renamed its instance variable `additional_properties`
  - Model `AddRemoveDbNode` deleted or renamed its instance variable `additional_properties`
  - Model `AllConnectionStringType` deleted or renamed its instance variable `additional_properties`
  - Model `ApexDetailsType` deleted or renamed its instance variable `additional_properties`
  - Model `AutonomousDatabase` deleted or renamed its instance variable `additional_properties`
  - Model `AutonomousDatabaseBackup` deleted or renamed its instance variable `additional_properties`
  - Model `AutonomousDatabaseBackupProperties` deleted or renamed its instance variable `additional_properties`
  - Model `AutonomousDatabaseBackupUpdate` deleted or renamed its instance variable `additional_properties`
  - Model `AutonomousDatabaseBackupUpdateProperties` deleted or renamed its instance variable `additional_properties`
  - Model `AutonomousDatabaseBaseProperties` deleted or renamed its instance variable `additional_properties`
  - Model `AutonomousDatabaseCharacterSet` deleted or renamed its instance variable `additional_properties`
  - Model `AutonomousDatabaseCharacterSetProperties` deleted or renamed its instance variable `additional_properties`
  - Model `AutonomousDatabaseCloneProperties` deleted or renamed its instance variable `additional_properties`
  - Model `AutonomousDatabaseNationalCharacterSet` deleted or renamed its instance variable `additional_properties`
  - Model `AutonomousDatabaseNationalCharacterSetProperties` deleted or renamed its instance variable `additional_properties`
  - Model `AutonomousDatabaseProperties` deleted or renamed its instance variable `additional_properties`
  - Model `AutonomousDatabaseStandbySummary` deleted or renamed its instance variable `additional_properties`
  - Model `AutonomousDatabaseUpdate` deleted or renamed its instance variable `additional_properties`
  - Model `AutonomousDatabaseUpdateProperties` deleted or renamed its instance variable `additional_properties`
  - Model `AutonomousDatabaseWalletFile` deleted or renamed its instance variable `additional_properties`
  - Model `AutonomousDbVersion` deleted or renamed its instance variable `additional_properties`
  - Model `AutonomousDbVersionProperties` deleted or renamed its instance variable `additional_properties`
  - Model `CloudAccountDetails` deleted or renamed its instance variable `additional_properties`
  - Model `CloudExadataInfrastructure` deleted or renamed its instance variable `additional_properties`
  - Model `CloudExadataInfrastructureProperties` deleted or renamed its instance variable `additional_properties`
  - Model `CloudExadataInfrastructureUpdate` deleted or renamed its instance variable `additional_properties`
  - Model `CloudExadataInfrastructureUpdateProperties` deleted or renamed its instance variable `additional_properties`
  - Model `CloudVmCluster` deleted or renamed its instance variable `additional_properties`
  - Model `CloudVmClusterProperties` deleted or renamed its instance variable `additional_properties`
  - Model `CloudVmClusterUpdate` deleted or renamed its instance variable `additional_properties`
  - Model `CloudVmClusterUpdateProperties` deleted or renamed its instance variable `additional_properties`
  - Model `ConnectionStringType` deleted or renamed its instance variable `additional_properties`
  - Model `ConnectionUrlType` deleted or renamed its instance variable `additional_properties`
  - Model `CustomerContact` deleted or renamed its instance variable `additional_properties`
  - Model `DataCollectionOptions` deleted or renamed its instance variable `additional_properties`
  - Model `DayOfWeek` deleted or renamed its instance variable `additional_properties`
  - Model `DayOfWeekUpdate` deleted or renamed its instance variable `additional_properties`
  - Model `DbIormConfig` deleted or renamed its instance variable `additional_properties`
  - Model `DbNode` deleted or renamed its instance variable `additional_properties`
  - Model `DbNodeAction` deleted or renamed its instance variable `additional_properties`
  - Model `DbNodeProperties` deleted or renamed its instance variable `additional_properties`
  - Model `DbServer` deleted or renamed its instance variable `additional_properties`
  - Model `DbServerPatchingDetails` deleted or renamed its instance variable `additional_properties`
  - Model `DbServerProperties` deleted or renamed its instance variable `additional_properties`
  - Model `DbSystemShape` deleted or renamed its instance variable `additional_properties`
  - Model `DbSystemShapeProperties` deleted or renamed its instance variable `additional_properties`
  - Model `DnsPrivateView` deleted or renamed its instance variable `additional_properties`
  - Model `DnsPrivateViewProperties` deleted or renamed its instance variable `additional_properties`
  - Model `DnsPrivateZone` deleted or renamed its instance variable `additional_properties`
  - Model `DnsPrivateZoneProperties` deleted or renamed its instance variable `additional_properties`
  - Model `ErrorAdditionalInfo` deleted or renamed its instance variable `additional_properties`
  - Model `ErrorDetail` deleted or renamed its instance variable `additional_properties`
  - Model `ErrorResponse` deleted or renamed its instance variable `additional_properties`
  - Model `EstimatedPatchingTime` deleted or renamed its instance variable `additional_properties`
  - Model `ExadataIormConfig` deleted or renamed its instance variable `additional_properties`
  - Model `GenerateAutonomousDatabaseWalletDetails` deleted or renamed its instance variable `additional_properties`
  - Model `GiVersion` deleted or renamed its instance variable `additional_properties`
  - Model `GiVersionProperties` deleted or renamed its instance variable `additional_properties`
  - Model `LongTermBackUpScheduleDetails` deleted or renamed its instance variable `additional_properties`
  - Model `MaintenanceWindow` deleted or renamed its instance variable `additional_properties`
  - Model `Month` deleted or renamed its instance variable `additional_properties`
  - Model `NsgCidr` deleted or renamed its instance variable `additional_properties`
  - Model `Operation` deleted or renamed its instance variable `additional_properties`
  - Model `OperationDisplay` deleted or renamed its instance variable `additional_properties`
  - Model `OracleSubscription` deleted or renamed its instance variable `additional_properties`
  - Model `OracleSubscriptionProperties` deleted or renamed its instance variable `additional_properties`
  - Model `OracleSubscriptionUpdate` deleted or renamed its instance variable `additional_properties`
  - Model `OracleSubscriptionUpdateProperties` deleted or renamed its instance variable `additional_properties`
  - Model `PeerDbDetails` deleted or renamed its instance variable `additional_properties`
  - Model `Plan` deleted or renamed its instance variable `additional_properties`
  - Model `PlanUpdate` deleted or renamed its instance variable `additional_properties`
  - Model `PortRange` deleted or renamed its instance variable `additional_properties`
  - Model `PrivateIpAddressProperties` deleted or renamed its instance variable `additional_properties`
  - Model `PrivateIpAddressesFilter` deleted or renamed its instance variable `additional_properties`
  - Model `ProfileType` deleted or renamed its instance variable `additional_properties`
  - Model `ProxyResource` deleted or renamed its instance variable `additional_properties`
  - Model `Resource` deleted or renamed its instance variable `additional_properties`
  - Model `RestoreAutonomousDatabaseDetails` deleted or renamed its instance variable `additional_properties`
  - Model `SaasSubscriptionDetails` deleted or renamed its instance variable `additional_properties`
  - Model `ScheduledOperationsType` deleted or renamed its instance variable `additional_properties`
  - Model `ScheduledOperationsTypeUpdate` deleted or renamed its instance variable `additional_properties`
  - Model `SystemData` deleted or renamed its instance variable `additional_properties`
  - Model `SystemVersion` deleted or renamed its instance variable `additional_properties`
  - Model `SystemVersionProperties` deleted or renamed its instance variable `additional_properties`
  - Model `TrackedResource` deleted or renamed its instance variable `additional_properties`
  - Model `VirtualNetworkAddress` deleted or renamed its instance variable `additional_properties`
  - Model `VirtualNetworkAddressProperties` deleted or renamed its instance variable `additional_properties`
  - Deleted or renamed model `SystemVersionsFilter`
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
