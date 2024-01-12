# Release History

## 1.3.0 (2023-12-18)

### Features Added

  - Added operation BackupInstancesOperations.begin_trigger_cross_region_restore
  - Added operation BackupInstancesOperations.begin_validate_cross_region_restore
  - Added operation group FetchCrossRegionRestoreJobOperations
  - Added operation group FetchCrossRegionRestoreJobsOperations
  - Added operation group FetchSecondaryRecoveryPointsOperations
  - Model AzureBackupDiscreteRecoveryPoint has a new parameter recovery_point_state
  - Model BackupVault has a new parameter replicated_regions
  - Model JobExtendedInfo has a new parameter warning_details

## 1.2.0 (2023-07-21)

### Features Added

  - Model AzureBackupJob has a new parameter rehydration_priority
  - Model AzureBackupRecoveryPointBasedRestoreRequest has a new parameter identity_details
  - Model AzureBackupRecoveryTimeBasedRestoreRequest has a new parameter identity_details
  - Model AzureBackupRestoreRequest has a new parameter identity_details
  - Model AzureBackupRestoreWithRehydrationRequest has a new parameter identity_details
  - Model BackupInstance has a new parameter identity_details
  - Model BackupVault has a new parameter secure_score
  - Model Datasource has a new parameter resource_properties
  - Model DatasourceSet has a new parameter resource_properties
  - Model DeletedBackupInstance has a new parameter identity_details
  - Model DppIdentityDetails has a new parameter user_assigned_identities
  - Model FeatureSettings has a new parameter cross_region_restore_settings
  - Model KubernetesClusterBackupDatasourceParameters has a new parameter backup_hook_references
  - Model KubernetesClusterRestoreCriteria has a new parameter restore_hook_references

## 1.1.0 (2023-06-16)

### Features Added

  - Added operation group DppResourceGuardProxyOperations

## 1.0.0 (2023-02-15)

### Features Added

  - Model AzureBackupDiscreteRecoveryPoint has a new parameter expiry_time
  - Model BackupVault has a new parameter feature_settings
  - Model PatchBackupVaultInput has a new parameter feature_settings
  - Model TargetDetails has a new parameter target_resource_arm_id

### Breaking Changes

  - Client name is changed from `DataProtectionClient` to `DataProtectionMgmtClient`
  - Model ResourceGuardResource no longer has parameter identity
  - Removed operation group BackupInstancesExtensionRoutingOperations
  - Removed operation group DppResourceGuardProxyOperations
  - Renamed operation BackupVaultsOperations.delete to BackupVaultsOperations.begin_delete

## 1.0.0b4 (2023-01-17)

### Features Added

  - Added operation group BackupInstancesExtensionRoutingOperations
  - Added operation group DppResourceGuardProxyOperations
  - Model PolicyParameters has a new parameter backup_datasource_parameters_list
  - Model ResourceGuardResource has a new parameter identity

### Breaking Changes

  - Model AzureBackupDiscreteRecoveryPoint no longer has parameter expiry_time
  - Model BackupVault no longer has parameter feature_settings
  - Model PatchBackupVaultInput no longer has parameter feature_settings
  - Model TargetDetails no longer has parameter target_resource_arm_id

## 1.0.0b3 (2022-12-29)

### Features Added

  - Model AzureBackupDiscreteRecoveryPoint has a new parameter expiry_time
  - Model BackupVault has a new parameter feature_settings
  - Model PatchBackupVaultInput has a new parameter feature_settings
  - Model TargetDetails has a new parameter target_resource_arm_id

### Breaking Changes

  - Model ResourceGuardResource no longer has parameter identity
  - Removed operation group BackupInstancesExtensionRoutingOperations
  - Removed operation group DppResourceGuardProxyOperations

## 1.0.0b2 (2022-10-11)

### Features Added

  - Added operation BackupInstancesOperations.begin_resume_backups
  - Added operation BackupInstancesOperations.begin_resume_protection
  - Added operation BackupInstancesOperations.begin_stop_protection
  - Added operation BackupInstancesOperations.begin_suspend_backups
  - Added operation BackupInstancesOperations.begin_sync_backup_instance
  - Added operation BackupInstancesOperations.get_backup_instance_operation_result
  - Added operation group BackupInstancesExtensionRoutingOperations
  - Added operation group DeletedBackupInstancesOperations
  - Added operation group DppResourceGuardProxyOperations
  - Added operation group OperationStatusBackupVaultContextOperations
  - Added operation group OperationStatusResourceGroupContextOperations
  - Model AzureBackupRecoveryPointBasedRestoreRequest has a new parameter source_resource_id
  - Model AzureBackupRecoveryTimeBasedRestoreRequest has a new parameter source_resource_id
  - Model AzureBackupRestoreRequest has a new parameter source_resource_id
  - Model AzureBackupRestoreWithRehydrationRequest has a new parameter source_resource_id
  - Model BackupInstance has a new parameter validation_type
  - Model BackupInstanceResource has a new parameter tags
  - Model BackupVault has a new parameter is_vault_protected_by_resource_guard
  - Model BackupVault has a new parameter monitoring_settings
  - Model BackupVault has a new parameter security_settings
  - Model PatchResourceRequestInput has a new parameter properties
  - Model SecretStoreResource has a new parameter value

## 1.0.0b1 (2021-10-19)

* Initial Release
